from elasticsearch import Elasticsearch
import json

# Connect to Elasticsearch
# Replace with your host and port
ELASTICSEARCH_HOST = "http://localhost:9200"
API_KEY = "nice try"

es = Elasticsearch(
    ELASTICSEARCH_HOST,
    api_key=API_KEY,
)


# Path to NDJSON file
ndjson_file_path = "scuba_data.ndjson"

# Upload each JSON line to the index
with open(ndjson_file_path, "r", encoding="utf-8") as f:
    for line_number, line in enumerate(f, start=1):
        try:
            doc = json.loads(line.strip())
            es.index(index="test_v10", document=doc)
        except json.JSONDecodeError as e:
            print(f"Line {line_number} is not valid JSON: {e}")
        except Exception as e:
            print(f"Error indexing line {line_number}: {e}")
