import React, { useEffect, useState } from "react";
import { UploadForm } from "./components/UploadForm";
import { JobList } from "./components/JobList";
import { listJobs, Job } from "./api";

const OUTPUT_BUCKET_URL = import.meta.env.VITE_OUTPUT_BUCKET_URL;

export const App: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [refreshToggle, setRefreshToggle] = useState(0);

  useEffect(() => {
    (async () => {
      const data = await listJobs();
      setJobs(data);
    })();
  }, [refreshToggle]);

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="app-title-row">
          <h1 className="app-title">BayAssist</h1>
          <span className="app-badge">AI Architecture Assistant</span>
        </div>
        <p className="app-subtitle">
          Turn raw <strong>Terraform</strong> and cloud configs into <strong>customer-ready diagrams</strong>,
          architecture docs, PDFs and ARC decks in just a few clicks.
        </p>
      </header>

      <main className="app-columns">
        <section>
          <UploadForm onJobCreated={() => setRefreshToggle((n) => n + 1)} />
        </section>
        <section>
          <JobList jobs={jobs} outputBucketUrlPrefix={OUTPUT_BUCKET_URL} />
        </section>
      </main>

      <footer className="app-footer">
        <span>
          Demo-ready: upload a Terraform sample, then open Markdown, PDF, PPT and HTML links above.
        </span>
        <span className="monospace-light">Powered by AWS, Step Functions &amp; Bedrock Claude</span>
      </footer>
    </div>
  );
};
