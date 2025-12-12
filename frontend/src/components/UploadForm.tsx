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
      <h2>Upload Terraform / Code</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <input
            type="file"
            accept=".tf,.zip,.json,.yaml,.yml"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
        </div>
        <div style={{ marginTop: "0.5rem" }}>
          <label>
            <input
              type="radio"
              value="diagrams"
              checked={jobType === "diagrams"}
              onChange={() => setJobType("diagrams")}
            />
            {" "}Generate Diagrams + Doc
          </label>
          <label style={{ marginLeft: "1rem" }}>
            <input
              type="radio"
              value="document"
              checked={jobType === "document"}
              onChange={() => setJobType("document")}
            />
            {" "}Document Only
          </label>
        </div>
        <button type="submit" disabled={!file || loading} style={{ marginTop: "0.5rem" }}>
          {loading ? "Submitting..." : "Generate"}
        </button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
};
