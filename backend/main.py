from datetime import datetime
import os
from typing import List, Dict, Any
import requests

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="PharmaGuide Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPPORTED_DRUGS = [
    "CODEINE",
    "WARFARIN",
    "CLOPIDOGREL",
    "SIMVASTATIN",
    "AZATHIOPRINE",
    "FLUOROURACIL",
]

# Drug → primary pharmacogene
DRUG_PRIMARY_GENE: Dict[str, str] = {
    "CODEINE": "CYP2D6",
    "CLOPIDOGREL": "CYP2C19",
    "WARFARIN": "CYP2C9",
    "SIMVASTATIN": "SLCO1B1",
    "AZATHIOPRINE": "TPMT",
    "FLUOROURACIL": "DPYD",
}

# Very small demo PGx knowledge base.
# Maps gene → rsID → qualitative functional effect.
PGX_VARIANT_EFFECTS: Dict[str, Dict[str, str]] = {
    "CYP2C19": {
        "rs4244285": "LOF",  # *2
        "rs4986893": "LOF",  # *3
        "rs12248560": "GOF",  # *17
    },
    "CYP2C9": {
        "rs1799853": "LOF",  # *2
        "rs1057910": "LOF",  # *3
    },
    "CYP2D6": {
        "rs3892097": "LOF",  # *4
        "rs5030655": "LOF",  # *3
    },
    "SLCO1B1": {
        "rs4149056": "LOF",  # *5
    },
    "TPMT": {
        "rs1800460": "LOF",  # *3A
        "rs1142345": "LOF",
    },
    "DPYD": {
        "rs3918290": "LOF",  # *2A
        "rs55886062": "LOF",  # D949V
    },
}

# Drug + gene + phenotype → risk / severity / CPIC-like text
PGX_RULES: Dict[tuple, Dict[str, str]] = {
    ("CODEINE", "CYP2D6", "PM"): {
        "risk_label": "Toxic",
        "severity": "high",
        "recommendation": "Avoid codeine; consider non‑CYP2D6 opioid per CPIC guidance.",
    },
    ("CODEINE", "CYP2D6", "UM"): {
        "risk_label": "Toxic",
        "severity": "high",
        "recommendation": "Avoid codeine; risk of life‑threatening opioid toxicity.",
    },
    ("CODEINE", "CYP2D6", "IM"): {
        "risk_label": "Ineffective",
        "severity": "moderate",
        "recommendation": "Consider alternative to codeine or higher monitoring for poor analgesia.",
    },
    ("CLOPIDOGREL", "CYP2C19", "PM"): {
        "risk_label": "Ineffective",
        "severity": "high",
        "recommendation": "Avoid clopidogrel; use alternative P2Y12 inhibitor (e.g., prasugrel, ticagrelor).",
    },
    ("CLOPIDOGREL", "CYP2C19", "IM"): {
        "risk_label": "Ineffective",
        "severity": "moderate",
        "recommendation": "Consider alternative antiplatelet agent or enhanced platelet monitoring.",
    },
    ("WARFARIN", "CYP2C9", "PM"): {
        "risk_label": "Toxic",
        "severity": "high",
        "recommendation": "Start at substantially reduced dose and titrate slowly with INR monitoring.",
    },
    ("WARFARIN", "CYP2C9", "IM"): {
        "risk_label": "Adjust Dosage",
        "severity": "moderate",
        "recommendation": "Use lower initial warfarin dose and close INR monitoring.",
    },
    ("SIMVASTATIN", "SLCO1B1", "PM"): {
        "risk_label": "Toxic",
        "severity": "high",
        "recommendation": "Avoid high‑dose simvastatin; use lower dose or alternative statin.",
    },
    ("SIMVASTATIN", "SLCO1B1", "IM"): {
        "risk_label": "Adjust Dosage",
        "severity": "moderate",
        "recommendation": "Use reduced simvastatin dose and monitor for myopathy.",
    },
    ("AZATHIOPRINE", "TPMT", "PM"): {
        "risk_label": "Toxic",
        "severity": "critical",
        "recommendation": "Avoid standard azathioprine doses; consider alternative or drastic dose reduction.",
    },
    ("AZATHIOPRINE", "TPMT", "IM"): {
        "risk_label": "Adjust Dosage",
        "severity": "high",
        "recommendation": "Reduce starting dose (30–80%) and monitor closely for myelosuppression.",
    },
    ("FLUOROURACIL", "DPYD", "PM"): {
        "risk_label": "Toxic",
        "severity": "critical",
        "recommendation": "Avoid standard fluorouracil dosing; consider alternative regimen.",
    },
    ("FLUOROURACIL", "DPYD", "IM"): {
        "risk_label": "Adjust Dosage",
        "severity": "high",
        "recommendation": "Substantially reduce starting dose and monitor for severe toxicity.",
    },
}


def parse_vcf_bytes(data: bytes) -> Dict[str, Any]:
    try:
        text = data.decode("utf-8", errors="ignore")
        lines = text.splitlines()
        genes = set()
        rsids = set()
        gene_rsids: Dict[str, List[str]] = {}
        patient_id = "PATIENT_UNKNOWN"

        for line in lines:
            if not line or line.startswith("##"):
                continue
            if line.startswith("#CHROM"):
                cols = line.strip().split("\t")
                if len(cols) > 9:
                    patient_id = cols[9] or "PATIENT_UNKNOWN"
                continue

            parts = line.strip().split("\t")
            if len(parts) < 8:
                continue
            info_field = parts[7] or ""
            info_parts = info_field.split(";")
            gene = None
            rsid = None
            for p in info_parts:
                if p.startswith("GENE="):
                    gene = p.replace("GENE=", "")
                if p.startswith("RS="):
                    rsid = p.replace("RS=", "")
            if gene:
                genes.add(gene)
            if rsid:
                rsids.add(rsid)
            if gene and rsid:
                gene_rsids.setdefault(gene, []).append(rsid)

        return {
            "success": True,
            "patient_id": patient_id,
            "genes": list(genes),
            "rsids": list(rsids),
            "gene_rsids": gene_rsids,
        }
    except Exception as exc:  # noqa: BLE001
        return {"success": False, "error": str(exc)}


def infer_gene_phenotype(gene: str, rsids_for_gene: List[str]) -> Dict[str, str]:
    """
    Very simplified star-allele / phenotype inference for demo purposes.
    """
    if not gene or not rsids_for_gene:
        return {"diplotype": "*1/*1", "phenotype": "NM"}

    effects = PGX_VARIANT_EFFECTS.get(gene, {})
    lof_present = any(effects.get(r) == "LOF" for r in rsids_for_gene)
    gof_present = any(effects.get(r) == "GOF" for r in rsids_for_gene)

    if lof_present and gof_present:
        diplotype = "*1/*2"
        phenotype = "IM"
    elif lof_present:
        diplotype = "*2/*2"
        phenotype = "PM"
    elif gof_present:
        diplotype = "*1/*17"
        phenotype = "RM"
    else:
        diplotype = "*1/*1"
        phenotype = "NM"

    return {"diplotype": diplotype, "phenotype": phenotype}


def build_llm_explanation(
    drug: str,
    gene: str,
    diplotype: str,
    phenotype: str,
    rsids_for_gene: List[str],
    recommendation: str,
    risk_label: str,
) -> Dict[str, Any]:
    """
    Generate explanation text via Ollama LLM when available.
    If the LLM is unavailable or fails, return a neutral, non-clinical
    placeholder message (no rule-based clinical logic or error text).
    """
    rs_text = ", ".join(rsids_for_gene) if rsids_for_gene else "no specific pharmacogenomic variants listed"

    # Get Ollama configuration from environment variables
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2:3b")  # Default to llama3.2:3b for 8GB RAM
    
    if not ollama_base_url:
        return {
            "summary": (
                "A narrative explanation could not be generated automatically. "
                "Please interpret the structured risk assessment and clinical recommendation above in context."
            ),
            "mechanism": "No mechanistic narrative is available.",
            "cited_variants": rsids_for_gene,
            "source": "llm_not_configured_placeholder",
        }

    try:
        system_prompt = (
            "You are an expert clinical pharmacogenomics assistant. "
            "You provide accurate, evidence-based explanations of pharmacogenomic test results. "
            "Always cite specific variants (rsIDs) and explain biological mechanisms clearly. "
            "Do not invent facts or make unsupported claims."
        )
        
        user_prompt = (
            "You are an expert clinical pharmacogenomics assistant. "
            "Generate a detailed explanation for the following pharmacogenomic assessment.\n\n"
            "REQUIREMENTS:\n"
            "- Provide a comprehensive clinical summary (2-3 sentences)\n"
            "- Explain the biological mechanism: how the genetic variants affect enzyme/transporter function "
            "and drug metabolism/pharmacokinetics\n"
            "- Cite specific rsIDs mentioned in the data\n"
            "- Reference CPIC guidelines where relevant\n"
            "- Be factual, accurate, and avoid speculation\n"
            "- Keep total response under 250 words\n\n"
            "PATIENT DATA:\n"
            f"Drug: {drug}\n"
            f"Primary Gene: {gene}\n"
            f"Diplotype: {diplotype}\n"
            f"Phenotype: {phenotype}\n"
            f"Detected Variants (rsIDs): {rs_text}\n"
            f"Risk Assessment: {risk_label}\n"
            f"Clinical Recommendation: {recommendation}\n\n"
            "Generate a clear, professional explanation suitable for clinical use."
        )
        
        # Call Ollama API
        api_url = f"{ollama_base_url}/api/chat"
        payload = {
            "model": ollama_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "options": {
                "temperature": 0.2,
                "num_predict": 500,  # max tokens
            },
            "stream": False,
        }
        
        response = requests.post(api_url, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        llm_text = result.get("message", {}).get("content", "")
        
        if not llm_text:
            raise ValueError("Empty response from Ollama")
        
        # Split into summary and mechanism if possible, otherwise use full text for both
        sentences = llm_text.split(". ")
        if len(sentences) >= 3:
            summary = ". ".join(sentences[:2]) + "."
            mechanism = ". ".join(sentences[2:])
        else:
            summary = llm_text
            mechanism = llm_text
        
        return {
            "summary": summary.strip(),
            "mechanism": mechanism.strip(),
            "cited_variants": rsids_for_gene,
            "source": f"ollama_{ollama_model}",
        }
    except (requests.RequestException, ValueError, KeyError) as exc:
        return {
            "summary": (
                "A narrative explanation could not be generated at this time. "
                "Use the structured risk assessment and recommendation above to guide interpretation."
            ),
            "mechanism": "Mechanistic narrative unavailable due to a transient generation issue.",
            "cited_variants": rsids_for_gene,
            "source": "llm_error_placeholder",
        }


def build_drug_assessment(drug: str, vcf_summary: Dict[str, Any]) -> Dict[str, Any]:
    upper_drug = drug.strip().upper()
    now = datetime.utcnow().isoformat() + "Z"

    rsids: List[str] = vcf_summary.get("rsids", [])
    genes: List[str] = vcf_summary.get("genes", [])
    gene_rsids: Dict[str, List[str]] = vcf_summary.get("gene_rsids", {})

    primary_gene = DRUG_PRIMARY_GENE.get(upper_drug, genes[0] if genes else "Unknown")
    gene_specific_rsids = gene_rsids.get(primary_gene, [])

    inferred = infer_gene_phenotype(primary_gene, gene_specific_rsids)
    diplotype = inferred["diplotype"]
    phenotype = inferred["phenotype"]

    # Default risk
    risk_label = "Safe"
    severity = "none"
    confidence_score = 0.6

    if upper_drug not in SUPPORTED_DRUGS or primary_gene == "Unknown":
        risk_label = "Unknown"
        severity = "low"
        confidence_score = 0.3
    else:
        rule = PGX_RULES.get((upper_drug, primary_gene, phenotype))
        if rule:
            risk_label = rule["risk_label"]
            severity = rule["severity"]
            confidence_score = 0.9

    rule = PGX_RULES.get((upper_drug, primary_gene, phenotype))
    recommendation_text = (
        rule["recommendation"]
        if rule
        else "Use standard dosing with routine clinical monitoring."
    )

    llm_expl = build_llm_explanation(
        upper_drug,
        primary_gene,
        diplotype,
        phenotype,
        gene_specific_rsids,
        recommendation_text,
        risk_label,
    )

    return {
        "patient_id": vcf_summary.get("patient_id", "PATIENT_UNKNOWN"),
        "drug": upper_drug,
        "timestamp": now,
        "risk_assessment": {
            "risk_label": risk_label,
            "confidence_score": confidence_score,
            "severity": severity,
        },
        "pharmacogenomic_profile": {
            "primary_gene": primary_gene,
            "diplotype": diplotype,
            "phenotype": phenotype,
            "detected_variants": [{"rsid": r} for r in rsids],
        },
        "clinical_recommendation": {
            "summary": recommendation_text,
        },
        "llm_generated_explanation": llm_expl,
        "quality_metrics": {
            "vcf_parsing_success": vcf_summary.get("success", False),
            "variant_count": len(rsids),
            "gene_count": len(genes),
        },
    }


@app.post("/api/analyze")
async def analyze(
    vcf_file: UploadFile = File(...),
    drugs: str = Form(...),
) -> Dict[str, Any]:
    if not vcf_file:
        raise HTTPException(status_code=400, detail="VCF file is required.")

    if not drugs.strip():
        raise HTTPException(
            status_code=400, detail="At least one drug name is required."
        )

    if vcf_file.size and vcf_file.size > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=400, detail="VCF file must be 5 MB or smaller."
        )

    content = await vcf_file.read()
    vcf_summary = parse_vcf_bytes(content)
    if not vcf_summary.get("success"):
        raise HTTPException(
            status_code=400,
            detail=f"Failed to parse VCF: {vcf_summary.get('error', 'Unknown error')}",
        )

    drug_list = [d.strip() for d in drugs.split(",") if d.strip()]
    if not drug_list:
        raise HTTPException(status_code=400, detail="No valid drug names provided.")

    results = [build_drug_assessment(drug, vcf_summary) for drug in drug_list]
    return {"results": results}


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}

