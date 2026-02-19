from datetime import datetime
import os
from typing import List, Dict, Any
import requests

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

# Groq API key – replace with your key from https://console.groq.com/keys
# WARNING: Do not commit real keys to public repositories
GROQ_API_KEY_HARDCODED = "YOUR_GROQ_API_KEY_HERE"

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

# Drug + gene + phenotype → risk / severity / CPIC-aligned dosing recommendations
PGX_RULES: Dict[tuple, Dict[str, Any]] = {
    ("CODEINE", "CYP2D6", "PM"): {
        "risk_label": "Toxic",
        "severity": "high",
        "recommendation": "Avoid codeine; consider non‑CYP2D6 opioid per CPIC guidance.",
        "dosing": {
            "action": "avoid",
            "initial_dose": None,
            "alternative_drugs": ["Morphine", "Hydromorphone", "Oxycodone", "Hydrocodone", "Tramadol"],
            "monitoring": ["Respiratory depression", "Sedation", "Opioid toxicity signs"],
            "cpic_guideline": "CPIC Codeine-CYP2D6 (2014, updated 2021)",
            "notes": "Poor metabolizers have reduced conversion to active morphine, leading to poor analgesia. Consider alternative opioids that do not require CYP2D6 activation."
        }
    },
    ("CODEINE", "CYP2D6", "UM"): {
        "risk_label": "Toxic",
        "severity": "high",
        "recommendation": "Avoid codeine; risk of life‑threatening opioid toxicity.",
        "dosing": {
            "action": "avoid",
            "initial_dose": None,
            "alternative_drugs": ["Morphine", "Hydromorphone", "Oxycodone", "Hydrocodone"],
            "monitoring": ["Respiratory depression", "Life-threatening toxicity", "Excessive sedation"],
            "cpic_guideline": "CPIC Codeine-CYP2D6 (2014, updated 2021)",
            "notes": "Ultra-rapid metabolizers convert codeine to morphine rapidly, increasing risk of life-threatening respiratory depression. Avoid codeine entirely."
        }
    },
    ("CODEINE", "CYP2D6", "IM"): {
        "risk_label": "Ineffective",
        "severity": "moderate",
        "recommendation": "Consider alternative to codeine or higher monitoring for poor analgesia.",
        "dosing": {
            "action": "consider_alternative",
            "initial_dose": "Standard dose, but monitor for efficacy",
            "alternative_drugs": ["Morphine", "Oxycodone", "Hydrocodone"],
            "monitoring": ["Analgesic response", "Need for dose escalation", "Adverse effects"],
            "cpic_guideline": "CPIC Codeine-CYP2D6 (2014, updated 2021)",
            "notes": "Intermediate metabolizers may have reduced efficacy. Consider alternative opioids or monitor closely for inadequate pain control."
        }
    },
    ("CODEINE", "CYP2D6", "NM"): {
        "risk_label": "Safe",
        "severity": "none",
        "recommendation": "Use standard dosing with routine clinical monitoring.",
        "dosing": {
            "action": "standard_dose",
            "initial_dose": "Standard dosing as per product label",
            "alternative_drugs": None,
            "monitoring": ["Pain control", "Adverse effects", "Opioid tolerance"],
            "cpic_guideline": "CPIC Codeine-CYP2D6 (2014, updated 2021)",
            "notes": "Normal metabolizers have typical codeine-to-morphine conversion. Standard dosing is appropriate."
        }
    },
    ("CLOPIDOGREL", "CYP2C19", "PM"): {
        "risk_label": "Ineffective",
        "severity": "high",
        "recommendation": "Avoid clopidogrel; use alternative P2Y12 inhibitor per CPIC guidance.",
        "dosing": {
            "action": "avoid",
            "initial_dose": None,
            "alternative_drugs": ["Prasugrel 10 mg daily", "Ticagrelor 90 mg twice daily"],
            "monitoring": ["Platelet function", "Cardiovascular events", "Bleeding risk"],
            "cpic_guideline": "CPIC Clopidogrel-CYP2C19 (2013, updated 2022)",
            "notes": "Poor metabolizers have significantly reduced clopidogrel activation, leading to increased risk of cardiovascular events. Use alternative P2Y12 inhibitors."
        }
    },
    ("CLOPIDOGREL", "CYP2C19", "IM"): {
        "risk_label": "Ineffective",
        "severity": "moderate",
        "recommendation": "Consider alternative antiplatelet agent or enhanced platelet monitoring per CPIC guidance.",
        "dosing": {
            "action": "consider_alternative",
            "initial_dose": "Standard dose (75 mg daily), but consider alternatives",
            "alternative_drugs": ["Prasugrel 10 mg daily", "Ticagrelor 90 mg twice daily"],
            "monitoring": ["Platelet function testing", "Cardiovascular events", "Bleeding risk"],
            "cpic_guideline": "CPIC Clopidogrel-CYP2C19 (2013, updated 2022)",
            "notes": "Intermediate metabolizers may have reduced clopidogrel efficacy. Consider alternative P2Y12 inhibitors or enhanced monitoring."
        }
    },
    ("WARFARIN", "CYP2C9", "PM"): {
        "risk_label": "Toxic",
        "severity": "high",
        "recommendation": "Start at substantially reduced dose and titrate slowly with INR monitoring per CPIC guidance.",
        "dosing": {
            "action": "reduce_dose",
            "initial_dose": "Reduce by 30-50% from standard starting dose (typically 2-3 mg daily instead of 5 mg)",
            "alternative_drugs": ["Direct oral anticoagulants (DOACs) - consider if appropriate"],
            "monitoring": ["INR weekly until stable, then monthly", "Bleeding signs", "Thromboembolic events"],
            "cpic_guideline": "CPIC Warfarin-CYP2C9/VKORC1 (2017, updated 2023)",
            "notes": "Poor metabolizers have reduced warfarin clearance, requiring lower doses. Start at 30-50% of standard dose and titrate based on INR."
        }
    },
    ("WARFARIN", "CYP2C9", "IM"): {
        "risk_label": "Adjust Dosage",
        "severity": "moderate",
        "recommendation": "Use lower initial warfarin dose and close INR monitoring per CPIC guidance.",
        "dosing": {
            "action": "reduce_dose",
            "initial_dose": "Reduce by 20-30% from standard starting dose (typically 3-4 mg daily instead of 5 mg)",
            "alternative_drugs": None,
            "monitoring": ["INR every 1-2 weeks until stable", "Bleeding signs"],
            "cpic_guideline": "CPIC Warfarin-CYP2C9/VKORC1 (2017, updated 2023)",
            "notes": "Intermediate metabolizers may require lower warfarin doses. Start at reduced dose and monitor INR closely."
        }
    },
    ("WARFARIN", "CYP2C9", "NM"): {
        "risk_label": "Safe",
        "severity": "none",
        "recommendation": "Use standard dosing with routine clinical monitoring.",
        "dosing": {
            "action": "standard_dose",
            "initial_dose": "Standard starting dose (typically 5 mg daily) with INR-guided titration",
            "alternative_drugs": None,
            "monitoring": ["INR until stable", "Bleeding signs"],
            "cpic_guideline": "CPIC Warfarin-CYP2C9/VKORC1 (2017, updated 2023)",
            "notes": "Normal metabolizers have typical warfarin clearance. Standard dosing with INR monitoring is appropriate."
        }
    },
    ("SIMVASTATIN", "SLCO1B1", "PM"): {
        "risk_label": "Toxic",
        "severity": "high",
        "recommendation": "Avoid high‑dose simvastatin; use lower dose or alternative statin per CPIC guidance.",
        "dosing": {
            "action": "reduce_dose",
            "initial_dose": "Maximum 20 mg daily (avoid 40-80 mg doses)",
            "alternative_drugs": ["Pravastatin", "Rosuvastatin", "Atorvastatin"],
            "monitoring": ["Creatine kinase (CK) levels", "Muscle symptoms", "Myopathy signs"],
            "cpic_guideline": "CPIC Simvastatin-SLCO1B1 (2014, updated 2022)",
            "notes": "Poor function variants increase simvastatin exposure and myopathy risk. Limit to 20 mg daily or use alternative statin."
        }
    },
    ("SIMVASTATIN", "SLCO1B1", "IM"): {
        "risk_label": "Adjust Dosage",
        "severity": "moderate",
        "recommendation": "Use reduced simvastatin dose and monitor for myopathy per CPIC guidance.",
        "dosing": {
            "action": "reduce_dose",
            "initial_dose": "Maximum 40 mg daily (avoid 80 mg dose)",
            "alternative_drugs": ["Pravastatin", "Rosuvastatin"],
            "monitoring": ["Creatine kinase (CK) levels", "Muscle symptoms"],
            "cpic_guideline": "CPIC Simvastatin-SLCO1B1 (2014, updated 2022)",
            "notes": "Intermediate function variants may increase simvastatin exposure. Limit dose to 40 mg daily and monitor for myopathy."
        }
    },
    ("SIMVASTATIN", "SLCO1B1", "NM"): {
        "risk_label": "Safe",
        "severity": "none",
        "recommendation": "Use standard dosing with routine clinical monitoring.",
        "dosing": {
            "action": "standard_dose",
            "initial_dose": "Standard dosing as per product label (up to 80 mg daily if needed)",
            "alternative_drugs": None,
            "monitoring": ["LDL-C", "Creatine kinase (CK) if symptoms", "Muscle symptoms"],
            "cpic_guideline": "CPIC Simvastatin-SLCO1B1 (2014, updated 2022)",
            "notes": "Normal function variants. Standard simvastatin dosing is appropriate."
        }
    },
    ("AZATHIOPRINE", "TPMT", "PM"): {
        "risk_label": "Toxic",
        "severity": "critical",
        "recommendation": "Avoid standard azathioprine doses; consider alternative or drastic dose reduction per CPIC guidance.",
        "dosing": {
            "action": "avoid_or_severe_reduction",
            "initial_dose": "Reduce by 90% (typically 0.5-1 mg/kg/day instead of 2-3 mg/kg/day) OR avoid entirely",
            "alternative_drugs": ["6-mercaptopurine (with same precautions)", "Mycophenolate mofetil", "Methotrexate"],
            "monitoring": ["Complete blood count (CBC) weekly for first month, then monthly", "Myelosuppression signs", "Infection risk"],
            "cpic_guideline": "CPIC Azathioprine-TPMT (2011, updated 2018)",
            "notes": "Poor metabolizers have severe deficiency leading to life-threatening myelosuppression. Reduce dose by 90% or avoid entirely. Consider alternatives."
        }
    },
    ("AZATHIOPRINE", "TPMT", "IM"): {
        "risk_label": "Adjust Dosage",
        "severity": "high",
        "recommendation": "Reduce starting dose (30–80%) and monitor closely for myelosuppression per CPIC guidance.",
        "dosing": {
            "action": "reduce_dose",
            "initial_dose": "Reduce by 30-50% (typically 1-1.5 mg/kg/day instead of 2-3 mg/kg/day)",
            "alternative_drugs": ["Mycophenolate mofetil", "Methotrexate"],
            "monitoring": ["Complete blood count (CBC) every 1-2 weeks initially, then monthly", "Myelosuppression signs"],
            "cpic_guideline": "CPIC Azathioprine-TPMT (2011, updated 2018)",
            "notes": "Intermediate metabolizers have reduced TPMT activity. Reduce starting dose by 30-50% and monitor CBC closely for myelosuppression."
        }
    },
    ("FLUOROURACIL", "DPYD", "PM"): {
        "risk_label": "Toxic",
        "severity": "critical",
        "recommendation": "Avoid standard fluorouracil dosing; consider alternative regimen per CPIC guidance.",
        "dosing": {
            "action": "avoid",
            "initial_dose": None,
            "alternative_drugs": ["Capecitabine (with same precautions)", "Alternative chemotherapy regimens"],
            "monitoring": ["Complete blood count", "Gastrointestinal toxicity", "Neurological symptoms", "Severe toxicity signs"],
            "cpic_guideline": "CPIC Fluoropyrimidines-DPYD (2013, updated 2020)",
            "notes": "Poor metabolizers have severe DPD deficiency leading to life-threatening toxicity. Avoid fluorouracil and capecitabine. Use alternative chemotherapy."
        }
    },
    ("FLUOROURACIL", "DPYD", "IM"): {
        "risk_label": "Adjust Dosage",
        "severity": "high",
        "recommendation": "Substantially reduce starting dose and monitor for severe toxicity per CPIC guidance.",
        "dosing": {
            "action": "reduce_dose",
            "initial_dose": "Reduce by 50% from standard dose",
            "alternative_drugs": ["Alternative chemotherapy regimens"],
            "monitoring": ["Complete blood count weekly", "Gastrointestinal toxicity", "Severe toxicity signs"],
            "cpic_guideline": "CPIC Fluoropyrimidines-DPYD (2013, updated 2020)",
            "notes": "Intermediate metabolizers have reduced DPD activity. Reduce starting dose by 50% and monitor closely for severe toxicity."
        }
    },
    ("FLUOROURACIL", "DPYD", "NM"): {
        "risk_label": "Safe",
        "severity": "none",
        "recommendation": "Use standard dosing with routine clinical monitoring.",
        "dosing": {
            "action": "standard_dose",
            "initial_dose": "Standard dose per chemotherapy regimen",
            "alternative_drugs": None,
            "monitoring": ["Complete blood count", "Gastrointestinal toxicity", "Routine toxicity monitoring"],
            "cpic_guideline": "CPIC Fluoropyrimidines-DPYD (2013, updated 2020)",
            "notes": "Normal metabolizers have typical DPD enzyme function. Standard fluorouracil dosing is appropriate."
        }
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
    Generate explanation text via Groq API (free tier available).
    If the LLM is unavailable or fails, return a neutral, non-clinical
    placeholder message (no rule-based clinical logic or error text).
    """
    rs_text = ", ".join(rsids_for_gene) if rsids_for_gene else "no specific pharmacogenomic variants listed"

    # Get Groq API key: env var first, then fallback to hardcoded
    groq_api_key = os.getenv("GROQ_API_KEY", "").strip() or GROQ_API_KEY_HARDCODED
    groq_model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")  # Fast, free model

    if not groq_api_key or groq_api_key == "YOUR_GROQ_API_KEY_HERE" or not GROQ_AVAILABLE:
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
        
        # Call Groq API
        client = Groq(api_key=groq_api_key)
        
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            model=groq_model,
            temperature=0.2,
            max_tokens=500,
        )
        
        llm_text = chat_completion.choices[0].message.content
        
        if not llm_text:
            raise ValueError("Empty response from Groq API")
        
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
            "source": f"groq_{groq_model}",
        }
    except Exception as exc:
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
    
    # Extract CPIC dosing recommendations if available
    dosing_recommendations = None
    if rule and "dosing" in rule:
        dosing_recommendations = rule["dosing"]

    llm_expl = build_llm_explanation(
        upper_drug,
        primary_gene,
        diplotype,
        phenotype,
        gene_specific_rsids,
        recommendation_text,
        risk_label,
    )

    response_data = {
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
    
    # Add CPIC dosing recommendations if available
    if dosing_recommendations:
        response_data["cpic_dosing_recommendations"] = dosing_recommendations
    
    return response_data


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

