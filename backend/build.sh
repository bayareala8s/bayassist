#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIST_DIR="$ROOT_DIR/dist"
SRC_DIR="$ROOT_DIR/src"

rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR"

pip install --target "$ROOT_DIR/.venv_layer" -r "$ROOT_DIR/requirements.txt"

build_lambda () {
  local name="$1"
  local handler_file="$2"
  local zip_path="$DIST_DIR/$name.zip"

  rm -rf /tmp/lambda_build
  mkdir -p /tmp/lambda_build

  cp -r "$ROOT_DIR/.venv_layer"/* /tmp/lambda_build/ || true
  cp -r "$SRC_DIR/common" /tmp/lambda_build/common
  cp "$SRC_DIR/$handler_file" /tmp/lambda_build/

  (cd /tmp/lambda_build && zip -r "$zip_path" .) >/dev/null
  echo "Built $zip_path"
}

build_lambda "api" "api_handler.py"
build_lambda "preprocessor" "preprocessor_lambda.py"
build_lambda "diagram" "diagram_lambda.py"
build_lambda "document" "document_lambda.py"
build_lambda "pdf" "pdf_lambda.py"
build_lambda "arc_ppt" "arc_ppt_lambda.py"
build_lambda "confluence_exporter" "confluence_exporter_lambda.py"
