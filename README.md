# 🧬 PharmaGuard – AI-Powered Pharmacogenomic Risk Assessment

PharmaGuard is an end-to-end **HealthTech project** that converts raw genomic data (VCF files) into **actionable drug risk insights**. The system reads pharmacogenomic variants, trains a machine learning model, and predicts whether a drug is **Safe**, requires **Dosage Adjustment**, or is **Potentially Toxic** for a patient.

This project is designed to be **hackathon-ready**, beginner-friendly, and scalable for real-world clinical use.


# 🚨 Problem Statement

Pharmacogenomic data is increasingly available, but it is:

* Stored in complex **VCF (Variant Call Format)** files
* Not directly usable by clinical systems
* Underutilized in real-time drug decision-making

As a result, patients face:

* Adverse drug reactions (ADRs)
* Incorrect dosing
* Delayed or unsafe treatment decisions


# 💡 Solution Overview

**PharmaGuard** bridges the gap between genomics and clinical decisions by:

* Reading raw VCF files
* Extracting clinically relevant genetic variants
* Converting genotypes into phenotypes
* Training a supervised ML model on pharmacogenomic patterns
* Predicting drug risk for new patient data
* Producing a structured, explainable JSON output


# ✨ Key Features

* 📂 Direct VCF file ingestion
* 🧬 Pharmacogenomic feature extraction
* 🤖 Machine Learning–based risk prediction
* 🔍 Train–test split on VCF-derived dataset
* 📊 Explainable and structured output
* 🔌 API-ready architecture


# 🧪 Sample Output

```json
{
  "patient_id": "PATIENT_001",
  "drug": "Warfarin",
  "risk_assessment": {
    "risk_label": "Toxic",
    "confidence_score": 0.93,
    "severity": "critical"
  },
  "pharmacogenomic_profile": {
    "primary_gene": "CYP2C9",
    "diplotype": "*3/*3",
    "phenotype": "PM"
  }
}


## 🚀 How to Run the Project

### 1️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```


Upload a VCF file and receive risk predictions.

> Labels are derived using clinically inspired pharmacogenomic rules for hackathon feasibility.


# 🧬 Sample VCF File

A synthetic VCF file (`sample_pharmaguard.vcf`) is included for testing.

It contains:

* Multiple patients
* Clinically relevant PGx genes (CYP2C9, CYP2D6, VKORC1)
* Valid VCF v4.2 format


# 🔮 Future Scope

* Integration with real clinical PGx datasets
* Support for more genes and drug classes
* EHR / hospital system integration
* Advanced explainability using LLMs
* Regulatory dashboards for drug safety monitoring


# 🏆 Hackathon Note

This project is intentionally:

* Modular
* Explainable
* Demo-friendly

It demonstrates **clear problem understanding**, **working ML**, and **real-world relevance** — exactly what hackathon judges look for.


# 📜 License

This project is for educational and hackathon use only.

---

**PharmaGuard – From raw genomes to safer medicines.**
