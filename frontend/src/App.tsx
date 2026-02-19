import React, { useState } from "react";

type RiskSeverity = "none" | "low" | "moderate" | "high" | "critical";

interface RiskAssessment {
  risk_label: string;
  confidence_score: number;
  severity: RiskSeverity;
}

interface Variant {
  rsid: string;
  [key: string]: unknown;
}

interface PharmacogenomicProfile {
  primary_gene: string;
  diplotype: string;
  phenotype: string;
  detected_variants: Variant[];
}

interface ClinicalRecommendation {
  summary?: string;
  [key: string]: unknown;
}

interface LlmExplanation {
  summary: string;
  mechanism?: string;
  source?: string;
  cited_variants?: string[];
  [key: string]: unknown;
}

interface QualityMetrics {
  vcf_parsing_success: boolean;
  [key: string]: unknown;
}

interface CpicDosingRecommendations {
  action: string;
  initial_dose: string | null;
  alternative_drugs: string[] | null;
  monitoring: string[];
  cpic_guideline: string;
  notes: string;
}

interface DrugResult {
  patient_id: string;
  drug: string;
  timestamp: string;
  risk_assessment: RiskAssessment;
  pharmacogenomic_profile: PharmacogenomicProfile;
  clinical_recommendation: ClinicalRecommendation;
  llm_generated_explanation: LlmExplanation;
  cpic_dosing_recommendations?: CpicDosingRecommendations;
  quality_metrics: QualityMetrics;
}

const SUPPORTED_DRUGS = [
  "CODEINE",
  "WARFARIN",
  "CLOPIDOGREL",
  "SIMVASTATIN",
  "AZATHIOPRINE",
  "FLUOROURACIL",
];

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const App: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [drugInput, setDrugInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<DrugResult[] | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files?.length) return;
    const selected = e.target.files[0];
    if (!selected.name.endsWith(".vcf")) {
      setError("Only .vcf files are supported.");
      setFile(null);
      return;
    }
    if (selected.size > 5 * 1024 * 1024) {
      setError("File size must be less than or equal to 5 MB.");
      setFile(null);
      return;
    }
    setError(null);
    setFile(selected);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const selected = e.dataTransfer.files?.[0];
    if (!selected) return;
    if (!selected.name.endsWith(".vcf")) {
      setError("Only .vcf files are supported.");
      setFile(null);
      return;
    }
    if (selected.size > 5 * 1024 * 1024) {
      setError("File size must be less than or equal to 5 MB.");
      setFile(null);
      return;
    }
    setError(null);
    setFile(selected);
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setResults(null);

    if (!file) {
      setError("Please upload a VCF file.");
      return;
    }
    if (!drugInput.trim()) {
      setError("Please enter at least one drug.");
      return;
    }

    const formData = new FormData();
    formData.append("vcf_file", file);
    formData.append("drugs", drugInput);

    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/analyze`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.error || "Failed to analyze VCF.");
        setLoading(false);
        return;
      }
      setResults(data.results as DrugResult[]);
    } catch (err: any) {
      setError(err.message || "Network error.");
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (severity: RiskSeverity, label: string) => {
    if (label.toLowerCase().includes("toxic")) return "#f97373"; // red
    switch (severity) {
      case "none":
      case "low":
        return "#4ade80"; // green
      case "moderate":
        return "#facc15"; // yellow
      case "high":
      case "critical":
        return "#f97373"; // red
      default:
        return "#e5e7eb"; // gray
    }
  };

  const handleCopyJson = () => {
    if (!results) return;
    const payload = JSON.stringify(results, null, 2);
    navigator.clipboard.writeText(payload).catch(() => {
      setError("Unable to copy to clipboard.");
    });
  };

  const handleDownloadJson = () => {
    if (!results) return;
    const blob = new Blob([JSON.stringify(results, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "pharmaguide_results.json";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="app-root">
      <header className="app-header">
        <h1>PharmaGuide</h1>
        <p>Pharmacogenomic risk assessment from VCF files</p>
      </header>

      <main className="app-main">
        <section className="card">
          <h2>1. Upload VCF File</h2>
          <div
            className="dropzone"
            onDrop={handleDrop}
            onDragOver={handleDragOver}
          >
            <p>
              Drag &amp; drop your <strong>.vcf</strong> file here, or click to
              browse.
            </p>
            <input
              type="file"
              accept=".vcf"
              onChange={handleFileChange}
              className="file-input"
            />
            <p className="hint">Max size: 5 MB. Format: VCF v4.2.</p>
            {file && (
              <p className="file-name">
                Selected: <strong>{file.name}</strong> (
                {(file.size / 1024).toFixed(1)} KB)
              </p>
            )}
          </div>
        </section>

        <section className="card">
          <h2>2. Select Drugs</h2>
          <p className="hint">
            Supported: {SUPPORTED_DRUGS.join(", ")}. You can enter comma-separated
            values or any subset.
          </p>
          <form onSubmit={onSubmit} className="form">
            <input
              type="text"
              value={drugInput}
              onChange={(e) => setDrugInput(e.target.value)}
              placeholder="e.g. CODEINE, WARFARIN"
              className="text-input"
            />
            <button type="submit" className="primary-button" disabled={loading}>
              {loading ? "Analyzing..." : "Analyze"}
            </button>
          </form>
          {error && <p className="error">{error}</p>}
        </section>

        {results && (
          <section className="card">
            <div className="results-header">
              <h2>3. Results</h2>
              <div className="results-actions">
                <button onClick={handleCopyJson} className="secondary-button">
                  Copy JSON
                </button>
                <button onClick={handleDownloadJson} className="secondary-button">
                  Download JSON
                </button>
              </div>
            </div>

            <div className="results-list">
              {results.map((r) => (
                <details key={`${r.patient_id}-${r.drug}`} className="result-item">
                  <summary className="result-summary">
                    <div className="result-main">
                      <span className="drug-name">{r.drug}</span>
                      <span
                        className="risk-chip"
                        style={{
                          backgroundColor: getRiskColor(
                            r.risk_assessment.severity,
                            r.risk_assessment.risk_label
                          ),
                        }}
                      >
                        {r.risk_assessment.risk_label}
                      </span>
                    </div>
                    <div className="result-sub">
                      <span>Patient: {r.patient_id}</span>
                      <span>
                        Confidence: {(r.risk_assessment.confidence_score * 100).toFixed(0)}%
                      </span>
                      <span>Severity: {r.risk_assessment.severity}</span>
                    </div>
                  </summary>

                  <div className="result-details">
                    <section>
                      <h3>Pharmacogenomic Profile</h3>
                      <p>Primary gene: {r.pharmacogenomic_profile.primary_gene}</p>
                      <p>Diplotype: {r.pharmacogenomic_profile.diplotype}</p>
                      <p>Phenotype: {r.pharmacogenomic_profile.phenotype}</p>
                      <p>
                        Detected variants:{" "}
                        {r.pharmacogenomic_profile.detected_variants.length > 0
                          ? r.pharmacogenomic_profile.detected_variants
                              .map((v) => v.rsid)
                              .join(", ")
                          : "None"}
                      </p>
                    </section>

                    <section>
                      <h3>Clinical Recommendation</h3>
                      <p>{r.clinical_recommendation.summary}</p>
                    </section>

                    {r.cpic_dosing_recommendations && (
                      <section>
                        <h3>CPIC Dosing Recommendations</h3>
                        <div style={{ 
                          backgroundColor: "#f9fafb", 
                          padding: "1rem", 
                          borderRadius: "8px",
                          border: "1px solid #e5e7eb"
                        }}>
                          <div style={{ marginBottom: "1rem" }}>
                            <h4 style={{ fontSize: "0.95em", fontWeight: "600", marginBottom: "0.5rem", color: "#374151" }}>
                              Action Required
                            </h4>
                            <p style={{ 
                              fontWeight: "600",
                              color: r.cpic_dosing_recommendations.action === "avoid" ? "#dc2626" : 
                                     r.cpic_dosing_recommendations.action === "avoid_or_severe_reduction" ? "#dc2626" :
                                     r.cpic_dosing_recommendations.action === "reduce_dose" ? "#f59e0b" : "#059669"
                            }}>
                              {r.cpic_dosing_recommendations.action === "avoid" ? "⚠️ Avoid Drug" :
                               r.cpic_dosing_recommendations.action === "avoid_or_severe_reduction" ? "⚠️ Avoid or Severe Dose Reduction Required" :
                               r.cpic_dosing_recommendations.action === "reduce_dose" ? "📉 Reduce Dose" :
                               r.cpic_dosing_recommendations.action === "consider_alternative" ? "🔄 Consider Alternative" :
                               r.cpic_dosing_recommendations.action}
                            </p>
                          </div>

                          {r.cpic_dosing_recommendations.initial_dose && (
                            <div style={{ marginBottom: "1rem" }}>
                              <h4 style={{ fontSize: "0.95em", fontWeight: "600", marginBottom: "0.5rem", color: "#374151" }}>
                                Recommended Initial Dose
                              </h4>
                              <p style={{ fontFamily: "monospace", fontSize: "0.9em", color: "#1f2937" }}>
                                {r.cpic_dosing_recommendations.initial_dose}
                              </p>
                            </div>
                          )}

                          {r.cpic_dosing_recommendations.alternative_drugs && r.cpic_dosing_recommendations.alternative_drugs.length > 0 && (
                            <div style={{ marginBottom: "1rem" }}>
                              <h4 style={{ fontSize: "0.95em", fontWeight: "600", marginBottom: "0.5rem", color: "#374151" }}>
                                Alternative Drugs
                              </h4>
                              <ul style={{ marginLeft: "1.5rem", marginTop: "0.25rem" }}>
                                {r.cpic_dosing_recommendations.alternative_drugs.map((alt, idx) => (
                                  <li key={idx} style={{ marginBottom: "0.25rem", fontSize: "0.9em" }}>
                                    {alt}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {r.cpic_dosing_recommendations.monitoring && r.cpic_dosing_recommendations.monitoring.length > 0 && (
                            <div style={{ marginBottom: "1rem" }}>
                              <h4 style={{ fontSize: "0.95em", fontWeight: "600", marginBottom: "0.5rem", color: "#374151" }}>
                                Required Monitoring
                              </h4>
                              <ul style={{ marginLeft: "1.5rem", marginTop: "0.25rem" }}>
                                {r.cpic_dosing_recommendations.monitoring.map((monitor, idx) => (
                                  <li key={idx} style={{ marginBottom: "0.25rem", fontSize: "0.9em" }}>
                                    {monitor}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}

                          <div style={{ marginBottom: "1rem" }}>
                            <h4 style={{ fontSize: "0.95em", fontWeight: "600", marginBottom: "0.5rem", color: "#374151" }}>
                              CPIC Guideline Reference
                            </h4>
                            <p style={{ fontSize: "0.85em", color: "#6b7280", fontStyle: "italic" }}>
                              {r.cpic_dosing_recommendations.cpic_guideline}
                            </p>
                          </div>

                          {r.cpic_dosing_recommendations.notes && (
                            <div>
                              <h4 style={{ fontSize: "0.95em", fontWeight: "600", marginBottom: "0.5rem", color: "#374151" }}>
                                Clinical Notes
                              </h4>
                              <p style={{ fontSize: "0.9em", color: "#4b5563", lineHeight: "1.5" }}>
                                {r.cpic_dosing_recommendations.notes}
                              </p>
                            </div>
                          )}
                        </div>
                      </section>
                    )}

                    <section>
                      <h3>LLM-Generated Explanation</h3>
                      {r.llm_generated_explanation.source && (
                        <p className="hint" style={{ fontSize: "0.85em", color: "#6b7280" }}>
                          Generated by: {r.llm_generated_explanation.source}
                        </p>
                      )}
                      <div style={{ marginTop: "0.5rem" }}>
                        <h4 style={{ fontSize: "1em", fontWeight: "600", marginBottom: "0.5rem" }}>
                          Summary
                        </h4>
                        <p>{r.llm_generated_explanation.summary}</p>
                      </div>
                      {r.llm_generated_explanation.mechanism && 
                       r.llm_generated_explanation.mechanism !== r.llm_generated_explanation.summary && (
                        <div style={{ marginTop: "1rem" }}>
                          <h4 style={{ fontSize: "1em", fontWeight: "600", marginBottom: "0.5rem" }}>
                            Biological Mechanism
                          </h4>
                          <p>{r.llm_generated_explanation.mechanism}</p>
                        </div>
                      )}
                      {r.llm_generated_explanation.cited_variants && 
                       Array.isArray(r.llm_generated_explanation.cited_variants) &&
                       r.llm_generated_explanation.cited_variants.length > 0 && (
                        <div style={{ marginTop: "1rem" }}>
                          <h4 style={{ fontSize: "1em", fontWeight: "600", marginBottom: "0.5rem" }}>
                            Cited Variants
                          </h4>
                          <p style={{ fontFamily: "monospace", fontSize: "0.9em" }}>
                            {r.llm_generated_explanation.cited_variants.join(", ")}
                          </p>
                        </div>
                      )}
                    </section>

                    <section>
                      <h3>Quality Metrics</h3>
                      <p>
                        VCF parsing success:{" "}
                        {r.quality_metrics.vcf_parsing_success ? "Yes" : "No"}
                      </p>
                    </section>
                  </div>
                </details>
              ))}
            </div>
          </section>
        )}
      </main>

      <footer className="app-footer">
        <span>Demo only. Not for clinical use.</span>
      </footer>
    </div>
  );
};

