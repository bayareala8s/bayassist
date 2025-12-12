import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export interface Job {
  job_id: string;
  status: string;
  created_at: string;
  updated_at: string;
  output_diagram_s3_key?: string;
  output_doc_s3_key?: string;
  output_pdf_s3_key?: string;
  output_ppt_s3_key?: string;
  output_confluence_html_s3_key?: string;
}

export async function uploadTerraform(file: File, type: "diagrams" | "document") {
  const reader = new FileReader();

  const fileContentBase64: string = await new Promise((resolve, reject) => {
    reader.onload = () => {
      const result = reader.result;
      if (result instanceof ArrayBuffer) {
        const bytes = new Uint8Array(result);
        let binary = "";
        for (let i = 0; i < bytes.byteLength; i++) {
          binary += String.fromCharCode(bytes[i]);
        }
        resolve(btoa(binary));
      } else {
        reject("Unsupported result");
      }
    };
    reader.onerror = reject;
    reader.readAsArrayBuffer(file);
  });

  const res = await axios.post(
    `${API_BASE_URL}/generate/${type}`,
    {
      filename: file.name,
      fileContent: fileContentBase64,
    },
    {
      headers: { "Content-Type": "application/json" },
    }
  );

  return res.data;
}

export async function listJobs(): Promise<Job[]> {
  const res = await axios.get(`${API_BASE_URL}/jobs`);
  return res.data.jobs;
}

export async function getJob(jobId: string): Promise<Job> {
  const res = await axios.get(`${API_BASE_URL}/jobs/${jobId}`);
  return res.data;
}
