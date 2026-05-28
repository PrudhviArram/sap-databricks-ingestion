import pandas as pd

# ============================================
# Azure Blob Storage details
# ============================================

storage_account = "sapdataingest"
container_name = "sap-ingest-container"

# SAS token with read permissions, valid until 2026-06-27
from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient

# Using Service Principal tp fetch the secret from Azure Key Vault
credential = ClientSecretCredential(
    tenant_id="333c5841-d65f-498a-b748-1419a017eed7",
    client_id="e44158a4-5da6-47e8-acae-a45d36c5f732", # Application ID
    client_secret="Xvg8Q~v_J1B~Dc8DKKJXD6kuDBg53Y3tJaWOebmP"   # store THIS in dbutils.secrets
)

vault_url = "https://dbDemoKeyVault.vault.azure.net"
client = SecretClient(vault_url=vault_url, credential=credential)

# Fetch your secret
sas_token = client.get_secret("storage-sas-token").value

# File path in container
file_name = "input/20260528/financials.csv"

# Construct HTTPS URL
file_url = (
    f"https://{storage_account}.blob.core.windows.net/"
    f"{container_name}/{file_name}?{sas_token}"
)

print("Reading file from:")
print(file_url)

# ============================================
# Read CSV using pandas
# ============================================

pdf = pd.read_csv(file_url)

print("Pandas DataFrame loaded successfully")

# ============================================
# Convert pandas DataFrame to Spark DataFrame
# ============================================

df = spark.createDataFrame(pdf)

# Display data
#display(df)

# Print schema
#df.printSchema()

# Show rows
#df.show(10, truncate=False)

df.write.mode("overwrite").saveAsTable("sap_financials_demo")

# test github actions