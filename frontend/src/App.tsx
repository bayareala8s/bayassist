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
    <div style={{ padding: "2rem", fontFamily: "system-ui" }}>
      <h1>BayAssist – AI Architecture Assistant</h1>
      <p>Turn Terraform into architecture diagrams and documents in minutes.</p>
      <UploadForm onJobCreated={() => setRefreshToggle((n) => n + 1)} />
      <JobList jobs={jobs} outputBucketUrlPrefix={OUTPUT_BUCKET_URL} />
    </div>
  );
};
