import pandas as pd
import argparse
import json

def excel_to_json(excel_file, json_file):
    # Read the entire Excel file
    df = pd.read_excel(excel_file, sheet_name=None)
    
    # Convert each sheet to a JSON format
    json_data = {sheet: data.to_json(orient='records', force_ascii=False) for sheet, data in df.items()}
    
    # Parse the JSON data to a Python object
    json_object = {sheet: json.loads(data) for sheet, data in json_data.items()}
    
    # Write the formatted JSON data to a file
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_object, f, ensure_ascii=False, indent=4)
    
    print(f"Successfully converted {excel_file} to {json_file}")

def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description='Convert Excel file to JSON file')
    parser.add_argument('excel_file', type=str, help='Input Excel file name')
    parser.add_argument('json_file', type=str, help='Output JSON file name')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Call the conversion function
    excel_to_json(args.excel_file, args.json_file)

if __name__ == '__main__':
    main()

