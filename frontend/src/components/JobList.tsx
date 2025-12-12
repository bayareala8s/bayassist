import React from "react";
import { Job } from "../api";

interface Props {
  jobs: Job[];
  outputBucketUrlPrefix: string;
}

export const JobList: React.FC<Props> = ({ jobs, outputBucketUrlPrefix }) => {
  return (
    <div className="card" style={{ marginTop: "1.5rem" }}>
      <h2>Job History</h2>
      <table>
        <thead>
          <tr>
            <th>Job ID</th>
            <th>Status</th>
            <th>Created</th>
            <th>Diagram</th>
            <th>Markdown</th>
            <th>PDF</th>
            <th>ARC PPT</th>
            <th>Confluence HTML</th>
          </tr>
        </thead>
        <tbody>
          {jobs.map((job) => (
            <tr key={job.job_id}>
              <td style={{ maxWidth: 160, wordBreak: "break-all" }}>{job.job_id}</td>
              <td>{job.status}</td>
              <td>{new Date(job.created_at).toLocaleString()}</td>
              <td>
                {job.output_diagram_s3_key && (
                  <a
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
                    href={`${outputBucketUrlPrefix}${job.output_ppt_s3_key}`}
                    target="_blank"
                    rel="noreferrer"
                  >
                    PPT
                  </a>
                )}
              </td>
              <td>
                {job.output_confluence_html_s3_key && (
                  <a
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
  );
};
