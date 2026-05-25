#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../apps/backend"
uvicorn app.main:app --reload
