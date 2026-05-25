#!/bin/bash
set -e

echo "=== Step 1: Generating SAP Simulated Files ==="
python3 scripts/sap_generator.py

TODAY=$(date +%Y%m%d)
LOCAL_DIR="./sap_data/$TODAY"

echo "=== Step 2: Uploading files to Azure ADLS Storage ==="
# Replace these with your real Azure storage values later
AZURE_STORAGE_ACCOUNT="your_storage_account_name"
AZURE_CONTAINER="sap-ingest-container"

echo "Ready to upload batch from $LOCAL_DIR to Azure..."
# az storage blob upload-batch --account-name $AZURE_STORAGE_ACCOUNT --destination $AZURE_CONTAINER/input/$TODAY --source $LOCAL_DIR