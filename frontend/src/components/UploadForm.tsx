import React, { useState } from "react";
import { uploadTerraform } from "../api";

interface Props {
  onJobCreated: () => void;
}

export const UploadForm: React.FC<Props> = ({ onJobCreated }) => {
  const [file, setFile] = useState<File | null>(null);
  const [jobType, setJobType] = useState<"diagrams" | "document">("diagrams");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    try {
      setLoading(true);
      setMessage(null);
      const res = await uploadTerraform(file, jobType);
      setMessage(`Job submitted: ${res.jobId}`);
      onJobCreated();
    } catch (err) {
      console.error(err);
      setMessage("Error submitting job");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">Upload Terraform or Blueprint</h2>
        <span className="card-caption">Step 1 · Input</span>
      </div>
      <p className="card-support-text">
        Drop a single <code>.tf</code> file or a small <code>.zip</code> of Terraform to generate a full
        architecture view.
      </p>
      <form onSubmit={handleSubmit}>
        <div style={{ marginTop: "0.9rem" }}>
          <input
            className="input-file"
            type="file"
            accept=".tf,.zip,.json,.yaml,.yml"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
        </div>
        <div className="radio-row">
          <label className="radio-pill">
            <input
              type="radio"
              value="diagrams"
              checked={jobType === "diagrams"}
              onChange={() => setJobType("diagrams")}
            />
            Generate diagrams + doc
          </label>
          <label className="radio-pill">
            <input
              type="radio"
              value="document"
              checked={jobType === "document"}
              onChange={() => setJobType("document")}
            />
            Document only
          </label>
        </div>
        <p className="helper-text">
          Recommended for demos: <strong>Generate diagrams + doc</strong> to produce Mermaid, Markdown, PDF, ARC PPT
          and Confluence HTML.
        </p>
        <button
          type="submit"
          disabled={!file || loading}
          className="button-primary"
          style={{ marginTop: "0.5rem" }}
        >
          {loading ? "Submitting job…" : "Generate architecture assets"}
        </button>
      </form>
      {message && (
        <p className={`status-message ${message.toLowerCase().includes("error") ? "error" : "success"}`}>
          {message}
        </p>
      )}
    </div>
  );
};
