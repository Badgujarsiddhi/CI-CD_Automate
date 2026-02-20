from datetime import datetime
import logging
import os
from pathlib import Path
from typing import List, Dict, Any

# Load .env locally (Render will use dashboard env vars)
try:
    from dotenv import load_dotenv
    _env_path = Path(__file__).resolve().parent / ".env"
    load_dotenv(_env_path)
except ImportError:
    pass

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


# =============================
# ENV CONFIG
# =============================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")

if not GROQ_API_KEY:
    log.warning("⚠ GROQ_API_KEY not set. LLM explanation will be disabled.")


# =============================
# FASTAPI SETUP
# =============================

app = FastAPI(title="PharmaGuide Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================
# SUPPORTED DRUGS & RULES
# =============================

SUPPORTED_DRUGS = [
    "CODEINE",
    "WARFARIN",
    "CLOPIDOGREL",
    "SIMVASTATIN",
    "AZATHIOPRINE",
    "FLUOROURACIL",
]

DRUG_PRIMARY_GENE = {
    "CODEINE": "CYP2D6",
    "CLOPIDOGREL": "CYP2C19",
    "WARFARIN": "CYP2C9",
    "SIMVASTATIN": "SLCO1B1",
    "AZATHIOPRINE": "TPMT",
    "FLUOROURACIL": "DPYD",
}

PGX_VARIANT_EFFECTS = {
    "CYP2C19": {"rs4244285": "LOF", "rs4986893": "LOF", "rs12248560": "GOF"},
    "CYP2C9": {"rs1799853": "LOF", "rs1057910": "LOF"},
    "CYP2D6": {"rs3892097": "LOF", "rs5030655": "LOF"},
    "SLCO1B1": {"rs4149056": "LOF"},
    "TPMT": {"rs1800460": "LOF", "rs1142345": "LOF"},
    "DPYD": {"rs3918290": "LOF", "rs55886062": "LOF"},
}


# =============================
# VCF PARSER
# =============================

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
                cols = line.split("\t")
                if len(cols) > 9:
                    patient_id = cols[9]
                continue

            parts = line.split("\t")
            if len(parts) < 8:
                continue

            info_field = parts[7]
            for entry in info_field.split(";"):
                if entry.startswith("GENE="):
                    gene = entry.replace("GENE=", "")
                    genes.add(gene)
                if entry.startswith("RS="):
                    rsid = entry.replace("RS=", "")
                    rsids.add(rsid)

                    gene_rsids.setdefault(gene, []).append(rsid)

        return {
            "success": True,
            "patient_id": patient_id,
            "genes": list(genes),
            "rsids": list(rsids),
            "gene_rsids": gene_rsids,
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


# =============================
# PHENOTYPE INFERENCE
# =============================

def infer_gene_phenotype(gene: str, rsids_for_gene: List[str]):
    effects = PGX_VARIANT_EFFECTS.get(gene, {})
    lof = any(effects.get(r) == "LOF" for r in rsids_for_gene)
    gof = any(effects.get(r) == "GOF" for r in rsids_for_gene)

    if lof and gof:
        return "*1/*2", "IM"
    if lof:
        return "*2/*2", "PM"
    if gof:
        return "*1/*17", "RM"

    return "*1/*1", "NM"


# =============================
# LLM EXPLANATION
# =============================

def build_llm_explanation(drug, gene, diplotype, phenotype, rsids, recommendation, risk):

    if not GROQ_API_KEY or not GROQ_AVAILABLE:
        return {
            "summary": "LLM explanation not available.",
            "mechanism": "No mechanistic narrative generated.",
            "source": "llm_disabled"
        }

    try:
        client = Groq(api_key=GROQ_API_KEY)

        prompt = f"""
        Drug: {drug}
        Gene: {gene}
        Diplotype: {diplotype}
        Phenotype: {phenotype}
        Variants: {', '.join(rsids)}
        Risk: {risk}
        Recommendation: {recommendation}

        Explain mechanism and clinical significance clearly.
        """

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=400,
        )

        text = response.choices[0].message.content

        return {
            "summary": text,
            "mechanism": text,
            "source": f"groq_{GROQ_MODEL}"
        }

    except Exception as e:
        log.exception("LLM failed")
        return {
            "summary": "LLM failed to generate explanation.",
            "mechanism": str(e),
            "source": "llm_error"
        }


# =============================
# DRUG ASSESSMENT
# =============================

def build_drug_assessment(drug: str, vcf_summary: Dict[str, Any]):

    drug = drug.upper()
    rsids = vcf_summary.get("rsids", [])
    gene_rsids = vcf_summary.get("gene_rsids", {})

    primary_gene = DRUG_PRIMARY_GENE.get(drug, "Unknown")
    gene_specific = gene_rsids.get(primary_gene, [])

    diplotype, phenotype = infer_gene_phenotype(primary_gene, gene_specific)

    risk = "Safe"
    recommendation = "Standard dosing."

    if phenotype == "PM":
        risk = "High Risk"
        recommendation = "Consider dose reduction or alternative."

    llm_expl = build_llm_explanation(
        drug, primary_gene, diplotype, phenotype, gene_specific, recommendation, risk
    )

    return {
        "drug": drug,
        "risk": risk,
        "gene": primary_gene,
        "diplotype": diplotype,
        "phenotype": phenotype,
        "recommendation": recommendation,
        "llm_explanation": llm_expl
    }


# =============================
# API ENDPOINTS
# =============================

@app.post("/api/analyze")
async def analyze(vcf_file: UploadFile = File(...), drugs: str = Form(...)):

    content = await vcf_file.read()
    vcf_summary = parse_vcf_bytes(content)

    if not vcf_summary.get("success"):
        raise HTTPException(status_code=400, detail="Invalid VCF file.")

    drug_list = [d.strip() for d in drugs.split(",")]

    results = [build_drug_assessment(drug, vcf_summary) for drug in drug_list]

    return {"results": results}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/llm-status")
def llm_status():
    if not GROQ_API_KEY:
        return {"status": "API key not loaded"}

    try:
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": "Say OK"}],
            max_tokens=5
        )

        return {
            "status": "LLM working",
            "model_response": response.choices[0].message.content
        }

    except Exception as e:
        return {
            "status": "LLM error",
            "error": str(e)
        }