
# COMMAND ----------
dbutils.widgets.text("file_type", "csv", "Enter File Type (csv/json/tsv)")
dbutils.widgets.text("input_path", "", "Enter ADLS Input Path")
dbutils.widgets.text("target_table", "", "Enter Target Delta Table Name")

file_type = dbutils.widgets.get("file_type").lower()
input_path = dbutils.widgets.get("input_path")
target_table = dbutils.widgets.get("target_table")

# COMMAND ----------
# MAGIC %md ### 2. Generic Reader Function

# COMMAND ----------
def read_file(path, f_type):
    print(f"Reading {f_type} file from: {path}")
    if f_type == "csv":
        return spark.read.format("csv").option("header", "true").option("inferSchema", "true").load(path)
    elif f_type == "tsv":
        return spark.read.format("csv").option("header", "true").option("delimiter", "\t").option("inferSchema", "true").load(path)
    elif f_type == "json":
        return spark.read.format("json").option("multiLine", "true").option("inferSchema", "true").load(path)
    else:
        raise ValueError(f"Unsupported file type: {f_type}")

# COMMAND ----------
# MAGIC %md ### 3. Execute Ingestion

# COMMAND ----------
try:
    if not input_path or not target_table:
        print("Waiting for valid input parameters...")
    else:
        df = read_file(input_path, file_type)
        display(df.limit(5))
        
        print(f"Writing data to Delta Table: {target_table}")
        df.write.format("delta").mode("append").saveAsTable(target_table)
        print("Ingestion successful!")
except Exception as e:
    print(f"Error occurred: {str(e)}")
    raise e