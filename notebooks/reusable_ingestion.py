
# COMMAND ----------
dbutils.widgets.text("file_type", "csv", "csv")
dbutils.widgets.text("input_path", "", "abfss://sap-ingest-container@sapdataingest.dfs.core.windows.net/input/20260525")
dbutils.widgets.text("target_table", "", "sap_stock_demo_delta")

file_type = dbutils.widgets.get("file_type").lower()
input_path = dbutils.widgets.get("input_path")
target_table = dbutils.widgets.get("target_table")

# COMMAND ----------
# MAGIC %md ### 2. Generic Reader Function

# COMMAND ----------
def read_file(path, f_type):
    print(f"Reading {f_type} file from: {path}")

    # Define your storage credentials right here
    storage_account = "sapdataingest"
    # Replace this with your actual long access key string ending in ==
    storage_key = "JmW9/t45TrZn0nhzXECELO51A8LBGZpvQe2sDyMEZsVt9aaj5GEaPh1x9ym4IoVPFpdSkcTYbL/W+AStJKGuYg==" 
    
    # This option tells Spark exactly how to authenticate for this specific read request
    auth_option = f"fs.azure.account.key.sapdataingest.dfs.core.windows.net"

    if f_type == "csv":
        return spark.read.format("csv").option(auth_option, storage_key).option("header", "true").option("inferSchema", "true").load(path)
    elif f_type == "tsv":
        return spark.read.format("csv").option(auth_option, storage_key).option("header", "true").option("delimiter", "\t").option("inferSchema", "true").load(path)
    elif f_type == "json":
        return spark.read.format("json").option(auth_option, storage_key).option("multiLine", "true").option("inferSchema", "true").load(path)
    else:
        raise ValueError(f"Unsupported file type: {f_type}")

# COMMAND ----------
# MAGIC %md ### 3. Multi-Table Routing Framework via Native Spark Lookup

# COMMAND ----------
from pyspark.sql.functions import col, current_timestamp

try:
    if not input_path:
        print("Waiting for a valid ADLS directory path...")
    else:
        # Define storage account properties safely for credential validation
        storage_account = "sapdataingest"
        storage_key = "YOUR_AZURE_STORAGE_ACCESS_KEY" # Replace with your real key ending in ==
        
        # 1. Access the underlying Hadoop FileSystem API through Spark's gateway safely
        # This completely avoids the strict dbutils restriction on Serverless compute
        Path = spark._jvm.org.apache.hadoop.fs.Path
        FileSystem = spark._jvm.org.apache.hadoop.fs.FileSystem
        URI = spark._jvm.net.URI
        
        conf = spark._jsc.hadoopConfiguration()
        conf.set(f"fs.azure.account.key.{storage_account}.dfs.core.windows.net", storage_key)
        
        fs = FileSystem.get(URI(input_path), conf)
        status_list = fs.listStatus(Path(input_path))
        
        # 2. Map file categories to separate destination Delta tables
        sap_categories = {
            "Sales_Orders": "sap_sales_orders_delta",
            "Materials": "sap_materials_delta",
            "Financials": "sap_financials_delta"
        }
        
        # 3. Loop through files identified by Spark's file system layer
        processed_count = 0
        for status in status_list:
            file_path = status.getPath().toString()
            file_name = status.getPath().getName()
            
            # Match the file name pattern against our structural map categories
            for category, table_name in sap_categories.items():
                if category in file_name and file_name.endswith(f".{file_type}"):
                    print(f" Found matching source file: {file_name}")
                    print(f"   ↳ Ingesting into Delta Table: main.default.{table_name}")
                    
                    # Call your original serverless reader function
                    raw_df = read_file(file_path, file_type)
                    
                    # Add our tracking lineage metadata
                    final_df = raw_df.withColumn("source_file_path", col("_metadata.file_path")) \
                                     .withColumn("ingested_at_timestamp", current_timestamp())
                    
                    # Write separate tables with independent standalone schemas
                    final_df.write.format("delta") \
                                  .mode("overwrite") \
                                  .option("overwriteSchema", "true") \
                                  .saveAsTable(table_name)
                    
                    print(f"   ✅ Processed {final_df.count()} records cleanly.\n")
                    processed_count += 1
                    
        if processed_count == 0:
            print(f"No matching files found in target directory for format: {file_type}")
            
except Exception as e:
    print(f"Error occurred during multi-table routing: {str(e)}")
    raise e