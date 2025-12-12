# BayAssist – AI Architecture & Documentation Assistant (MVP)

This repo contains an MVP implementation of **BayAssist**, ready to deploy to AWS:

- AWS Lambda + Step Functions backend (Python 3.11)
- API Gateway HTTP API
- S3 + DynamoDB for storage
- Terraform IaC
- React + Vite frontend

## High-Level Flow

1. User uploads Terraform / code via UI.
2. API Lambda stores input in S3 and creates a job in DynamoDB.
3. Step Functions orchestrates:
   - Preprocessor Lambda -> builds a topology JSON
   - Diagram Lambda -> generates Mermaid diagrams using Bedrock Claude
   - Document Lambda -> generates Markdown architecture doc using Bedrock Claude
   - PDF Lambda -> converts Markdown to PDF
   - ARC PPT Lambda -> generates a PPTX ARC review deck
   - Confluence Exporter Lambda -> converts Markdown to Confluence-friendly HTML
4. Outputs are written to S3 and surfaced in the UI.

## Prereqs

- Terraform >= 1.6
- AWS account with:
  - Bedrock access and a Claude 3.5 Sonnet model ID
- Node.js >= 18 for frontend build
- Python 3.11 for backend packaging

## Deploy Backend (One-Time)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./build.sh

cd ../infra
terraform init
terraform apply
```

Note the Terraform outputs:

- `api_base_url`
- `output_bucket_name`

You will use these when configuring the frontend (locally or in Amplify).

## Run Frontend Locally

```bash
cd frontend
npm install
echo "VITE_API_BASE_URL=<api_base_url>" > .env
echo "VITE_OUTPUT_BUCKET_URL=https://<output_bucket_name>.s3.<region>.amazonaws.com/" >> .env
npm run dev
```

Then open the dev URL in your browser.

This is useful for local development; for a customer-ready demo, use Amplify Hosting below.

## Frontend Hosting with AWS Amplify (Recommended for Demo)

1. Push this repo to a Git provider that Amplify supports (e.g. GitHub).
2. In the AWS console, go to **AWS Amplify → Host web app** and connect the repo/branch.
3. Amplify will detect `amplify.yml` at the repo root, which:
  - Runs `npm ci` and `npm run build` in the `frontend` folder.
  - Serves static files from `frontend/dist`.
4. In the Amplify app, configure **Environment variables**:

  - `VITE_API_BASE_URL` = value of `api_base_url` from Terraform.
  - `VITE_OUTPUT_BUCKET_URL` = `https://<output_bucket_name>.s3.<region>.amazonaws.com/`.

5. Save environment variables and trigger a build (Amplify usually rebuilds automatically).
6. After deploy completes, use the Amplify-provided URL as your demo URL.

## Quick Customer Demo Script

1. Ensure the backend is deployed and healthy (Terraform `apply` succeeded, Bedrock model ID is correct).
2. Create a small Terraform sample for the demo (or use `test/main.tf`):

  ```bash
  cd test
  zip demo-terraform.zip main.tf
  ```

3. Open the Amplify app URL in a browser.
4. In the UI:
  - Click **Upload Terraform / Code** and select `demo-terraform.zip` (or your own Terraform bundle).
  - Choose **Generate Diagrams + Doc**.
  - Click **Generate** and note the job ID that is returned.
5. After 30–90 seconds, look at **Job History**:
  - Status should progress from `PENDING` → `PREPROCESSED` → `DIAGRAM_DONE` → `COMPLETED_DOC` as the Step Functions flow runs.
  - Links should appear for **Mermaid**, **Markdown**, **PDF**, **ARC PPT**, and **Confluence HTML**.
6. Click each link to show the generated artifacts, which are served from the output S3 bucket.

## Important

- Update `MODEL_ID` in `backend/src/common/bedrock_client.py` to the actual Claude model ID enabled in your account.
- For production hardening, add:
  - VPC configuration
  - KMS encryption keys
  - WAF / custom domain for API Gateway
  - Okta/OIDC auth in front of the UI/API.
