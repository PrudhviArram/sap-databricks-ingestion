#!/bin/bash

echo "=== Step 1: Generating SAP Simulated Files ==="
python "$(dirname "$0")/sap_generator.py"

# Add a check to see if Python actually ran successfully
if [ $? -eq 0 ]; then
    echo "Python generated files successfully!"
else
    echo "Python generation failed!"
    read -p "Press enter to exit..."
    exit 1
fi

TODAY=$(date +%Y%m%d)
LOCAL_DIR="./data/$TODAY"

# --- Azure Storage Configurations ---
AZURE_STORAGE_ACCOUNT="sapdataingest"
AZURE_STORAGE_KEY="JmW9/t45TrZn0nhzXECELO51A8LBGZpvQe2sDyMEZsVt9aaj5GEaPh1x9ym4IoVPFpdSkcTYbL/W+AStJKGuYg=="
AZURE_CONTAINER="sap-ingest-container"

echo "=== Step 2: Uploading files to Azure ADLS Storage ==="
echo "Local path being searched: $LOCAL_DIR"

# Run the upload and capture any hidden errors
az storage blob upload-batch \
  --account-name "$AZURE_STORAGE_ACCOUNT" \
  --account-key "$AZURE_STORAGE_KEY" \
  --destination "$AZURE_CONTAINER/input/$TODAY" \
  --source "$LOCAL_DIR" \
  --overwrite

if [ $? -eq 0 ]; then
    echo "Pipeline step complete! Files uploaded to Azure Cloud Storage!"
else
    echo "Azure upload failed!"
fi

# This keeps the terminal open so you can read the error message!
read -p "Press enter to close this window..."