import csv
import yaml
import json
import re
import argparse
import sys
from datetime import datetime
from urllib.parse import urlparse
import os

class CSVValidator:
    def __init__(self, mapping_path):
        self.mapping = self._load_mapping(mapping_path)
        self.fields_config = self.mapping.get('fields', {})
        self.errors = []

    def _load_mapping(self, path):
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading YAML mapping: {e}")
            sys.exit(1)

    def log_error(self, row, field, message):
        self.errors.append({
            "row": row,
            "field": field,
            "message": message
        })

    def validate_type(self, value, expected_type, row, field):
        if not value:
            return True
        
        try:
            if expected_type == 'int':
                int(value)
            elif expected_type == 'date':
                try:
                    datetime.fromisoformat(value.replace('Z', '+00:00'))
                except ValueError:
                    if not re.match(r'^\d{4}(-\d{2}){0,2}$', value):
                        raise ValueError
            elif expected_type in ['url', 'uri']:
                result = urlparse(value)
                if not all([result.scheme, result.netloc]):
                    raise ValueError
            elif expected_type == 'object':
                data = json.loads(value)
                if not isinstance(data, (dict, list)):
                    raise ValueError
                self._validate_object_keys(data, field, row)
        except (ValueError, json.JSONDecodeError):
            self.log_error(row, field, f"Invalid {expected_type} format: '{value}'")
            return False
        return True

    def _validate_object_keys(self, data, field, row):
        items = data if isinstance(data, list) else [data]
        
        required_keys = {
            'agent': ['value', 'role'],
            'agent_linked_data': ['value', 'uri', 'role'],
            'classification': ['value', 'authority']
        }

        if field in required_keys:
            for item in items:
                for key in required_keys[field]:
                    if key not in item:
                        self.log_error(row, field, f"Object missing required key: '{key}'")

    def validate_csv(self, csv_path):
        self.errors = []
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames

                for h in headers:
                    if h not in self.fields_config:
                        self.log_error(0, h, "Unknown column found in CSV not present in mapping.")

                for field_name, config in self.fields_config.items():
                    if config.get('min', 0) >= 1 and field_name not in headers:
                        self.log_error(0, field_name, "Missing required column.")

                for row_num, row_data in enumerate(reader, start=1):
                    for field_name, value in row_data.items():
                        if field_name not in self.fields_config:
                            continue

                        config = self.fields_config[field_name]
                        val_stripped = value.strip()

                        if config.get('min', 0) >= 1 and not val_stripped:
                            self.log_error(row_num, field_name, "Missing required value.")
                            continue

                        if config.get('max') == 1 and val_stripped:
                            if val_stripped.startswith('['):
                                try:
                                    if len(json.loads(val_stripped)) > 1:
                                        self.log_error(row_num, field_name, "Cardinality error: Multiple values found but max is 1.")
                                except: pass

                        self.validate_type(val_stripped, config.get('type', 'str'), row_num, field_name)

        except Exception as e:
            print(f"Failed to process CSV: {e}")
            return False

        return self.errors

def main(return_json=False):
    # parser = argparse.ArgumentParser(description="Validate CSV against Archipelago YAML mapping.")
    # parser.add_argument("csv", default="./output_csvs")
    # parser.add_argument("yaml", default="./mappings/main.yml")
    # parser.add_argument("--json", action="store_true", help="Output errors as JSON")
    
    # args = parser.parse_args()
    file_errors = {}
    validator = CSVValidator("./mappings/main.yml")
    for file_name in os.listdir(os.path.join("./output_csvs")):
        if file_name.endswith(".csv"):
            errors = validator.validate_csv(os.path.join("./output_csvs",file_name))
            file_errors[file_name] = errors
    if not file_errors:
        print("Validation Successful: No errors found.")
        sys.exit(0)
    # print(os.listdir(os.path.join("./output_csvs")))
    # print(file_errors)
    if return_json:
        print(json.dumps(file_errors, indent=2))
    else:
        for file_name,errors in file_errors.items():
            for err in errors:
                loc = f"File_name: {file_name} Row {err['row']}" if err['row'] > 0 else f"File_name: {file_name} Header"
                print(f"{loc} - field \"{err['field']}\": {err['message']}")

    
    sys.exit(1)

if __name__ == "__main__":
    main()