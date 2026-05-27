import pandas as pd

# ============================================
# Azure Blob Storage details
# ============================================

storage_account = "sapdataingest"
container_name = "sap-ingest-container"

# SAS token
# DO NOT include leading '?'

# File path in container
file_name = "input/20260525/financials.csv"

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