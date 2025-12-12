import React from "react";
import { Job } from "../api";

interface Props {
  jobs: Job[];
  outputBucketUrlPrefix: string;
}

export const JobList: React.FC<Props> = ({ jobs, outputBucketUrlPrefix }) => {
  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">Job history &amp; assets</h2>
        <span className="card-caption">Step 2 · Outputs</span>
      </div>
      <p className="card-support-text">
        Track each run and quickly open generated <strong>Mermaid</strong>, <strong>Markdown</strong>, <strong>PDF</strong>,
        <strong> ARC PPT</strong> and <strong>Confluence HTML</strong> artifacts.
      </p>
      <div className="table-wrapper">
        <div className="table-wrapper-inner">
          <table>
            <thead>
              <tr>
                <th>Job</th>
                <th>Status</th>
                <th>Created</th>
                <th>Diagram</th>
                <th>Markdown</th>
                <th>PDF</th>
                <th>ARC PPT</th>
                <th>Confluence</th>
              </tr>
            </thead>
            <tbody>
              {jobs.map((job) => (
                <tr key={job.job_id}>
                  <td className="job-id-cell">{job.job_id}</td>
                  <td>
                    <StatusPill status={job.status} />
                  </td>
                  <td>{new Date(job.created_at).toLocaleString()}</td>
                  <td>
                    {job.output_diagram_s3_key && (
                      <a
                        className="link-chip"
                        href={`${outputBucketUrlPrefix}${job.output_diagram_s3_key}`}
                        target="_blank"
                        rel="noreferrer"
                      >
                        Mermaid
                      </a>
                    )}
                  </td>
                  <td>
                    {job.output_doc_s3_key && (
                      <a
                        className="link-chip"
                        href={`${outputBucketUrlPrefix}${job.output_doc_s3_key}`}
                        target="_blank"
                        rel="noreferrer"
                      >
                        Markdown
                      </a>
                    )}
                  </td>
                  <td>
                    {job.output_pdf_s3_key && (
                      <a
                        className="link-chip"
                        href={`${outputBucketUrlPrefix}${job.output_pdf_s3_key}`}
                        target="_blank"
                        rel="noreferrer"
                      >
                        PDF
                      </a>
                    )}
                  </td>
                  <td>
                    {job.output_ppt_s3_key && (
                      <a
                        className="link-chip"
                        href={`${outputBucketUrlPrefix}${job.output_ppt_s3_key}`}
                        target="_blank"
                        rel="noreferrer"
                      >
                        ARC PPT
                      </a>
                    )}
                  </td>
                  <td>
                    {job.output_confluence_html_s3_key && (
                      <a
                        className="link-chip"
                        href={`${outputBucketUrlPrefix}${job.output_confluence_html_s3_key}`}
                        target="_blank"
                        rel="noreferrer"
                      >
                        HTML
                      </a>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

const StatusPill: React.FC<{ status: string }> = ({ status }) => {
  const normalized = status.toUpperCase();

  let pillClass = "status-pill pending";
  let label = status;

  if (normalized.includes("ERROR") || normalized.includes("FAILED")) {
    pillClass = "status-pill failed";
  } else if (normalized.includes("RUNNING") || normalized.includes("PROGRESS")) {
    pillClass = "status-pill running";
  } else if (normalized.includes("COMPLETE")) {
    pillClass = "status-pill completed";
  }

  return (
    <span className={pillClass}>
      <span className="status-pill-dot" />
      {label}
    </span>
  );
};
