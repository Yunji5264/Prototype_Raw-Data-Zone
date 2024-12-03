import json
import os
from data_load import *


def write_metadata_to_file(metadata_file, metadata_entry):
    # If the file exists, read the existing data
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        # If the file does not exist, create an empty list
        data = []

    # Append the new metadata entry to the list
    data.append(metadata_entry)

    # Write the data to metadata.json file
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"Metadata for {metadata_entry['titleDataset']} written to {metadata_file}")

def create_metadata(file_path, codeDataset, titleDataset, url, updateFrequency, typeDataset, themeDataset, parameters, complementaryInfo, measures, spatioGranularityMin, temporalGranularityMin, spatioScope, temporalScope, hierarchies):
    # Create a metadata entry for a single file
    metadata_entry = {
        "codeDataset": codeDataset,
        "titleDataset": titleDataset,
        # "url": url,
        "url": file_path,
        "updateFrequency": updateFrequency,
        "typeDataset": typeDataset,
        "themeDataset": themeDataset,
        "parameters": parameters,
        "complementaryInfo": complementaryInfo,
        "measures": measures,
        "spatioGranularityMin": spatioGranularityMin,
        "temporalGranularityMin": temporalGranularityMin,
        "spatioScope": spatioScope,
        "temporalScope": temporalScope,
        "hierarchies": hierarchies
    }
    write_metadata_to_file(metadata_file, metadata_entry)

