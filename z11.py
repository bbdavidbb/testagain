from datetime import datetime

import os
import re
import json


def clean_date_format(obj):
    if isinstance(obj, dict):
        return {k: clean_date_format(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_date_format(item) for item in obj]
    elif isinstance(obj, str):
        return re.sub(r'/Date\((\d+)\)/', r'\1', obj)
    else:
        return obj


def fix_object_id(the_list):
    for item in the_list:
        object_id = item.get("ObjectId")
        if isinstance(object_id, str):
            item["ObjectId"] = {
                "Application": object_id,
                "ServicePrincipal": ""
            }
    return the_list


def read_all_json_from_dir(directory):
    json_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, 'r', encoding='utf-8-sig') as f:
                        data = json.load(f)
                        cleaned = clean_date_format(data)  # Apply date cleanup
                        json_list.append(cleaned)
                except (json.JSONDecodeError, OSError) as e:
                    print(f"Error reading {full_path}: {e}")
    return json_list


def make_ecs_scuba_risky_json_list(json_list):
    stripped_json_list = []
    count = 0
    for scuba_file in json_list:
        current_dict = {}

        # make Scuba MetaData ECS readable
        temp_meta = scuba_file['MetaData']
        current_dict['time'] = temp_meta['TimestampZulu']
        current_dict['MetaData'] = temp_meta
        current_dict["Raw"] = {}

        # add risky json info
        temp_risk = fix_object_id(scuba_file["Raw"]["risky_applications"])
        current_dict["Raw"]["risky_applications"] = temp_risk
        current_dict["Raw"]["risky_third_party_service_principals"] = scuba_file["Raw"]["risky_third_party_service_principals"]
        stripped_json_list.append(current_dict)
        count += 1
    return stripped_json_list


# Example usage
directory_path = './directory'
json_list = read_all_json_from_dir(directory_path)
scuba_ecs_json_list = make_ecs_scuba_risky_json_list(json_list)


timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
# filename = f"scuba_data_{timestamp}.ndjson"
filename = "scuba_data.ndjson"

with open(filename, "w", encoding='utf-8') as f:
    for item in scuba_ecs_json_list:
        f.write(json.dumps(item) + "\n")

# # File paths
# input_file = 'ScubaResults_16f61e39-398d-48d0.json'
# output_file = 'ScubaResults_16f61e39-398d-48d0_nobom.json'

# # Read the file with BOM using utf-8-sig (which strips BOM automatically)
# with open(input_file, 'r', encoding='utf-8-sig') as f:
#     content = f.read()

# # Write the content back using utf-8 (no BOM)
# with open(output_file, 'w', encoding='utf-8') as f:
#     f.write(content)
