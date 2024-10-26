import os
import zipfile
import xml.etree.ElementTree as ET

import pandas as pd

from info_spatial import *
from info_temporal import *
from info_theme import *
from metadata_creation import *
from general_functions import *
from class_predefine import *

code_dataset = 0


# Analyze information from an Excel file
def excel_EL(file_path):
    # Read Excel file
    df = pd.read_excel(file_path, header=None, nrows=1000)
    # Count rows with data
    row_counts = df.count(axis=1)
    # Check if the DataFrame is empty
    if row_counts.empty:
        raise ValueError("DataFrame is empty or contains no valid data.")
    # Find the row with the fewest null values
    max_row_count = row_counts.max()
    if max_row_count == 0:
        raise ValueError("All rows are empty.")
    # Set this row as the header and retrieve the table below it
    first_row = row_counts.idxmax()
    # Read data from the title line
    df = pd.read_excel(file_path, header=first_row)
    # Get spatial information: parameters, granularity, and scope
    geo_para, granularityS, geo_scope, hierarchiesS = table_geo(df)
    tem_para, tem_scope, granularityT, hierarchiesT = df_tem(file_path, df)
    measures = []
    ci = []

    # Filter out columns that are not spatial or temporal parameters
    cols = [col for col in df.columns if col not in geo_para and col not in tem_para]

    # User interaction to select measures
    root = tk.Tk()
    app = MeasureSelectionApp(root, cols)
    root.mainloop()

    # Get complementary info and measures from user input
    ci, measures = app.get_ci_m()

    return geo_para, geo_scope, granularityS, hierarchiesS, tem_para, tem_scope, granularityT, hierarchiesT, ci, measures, True


# Analyze information from a CSV file
def csv_EL(file_path):
    # Read CSV with various encodings and delimiters
    try:
        df = pd.read_csv(file_path, low_memory=False, on_bad_lines='skip')
    except:
        df = pd.read_csv(file_path, encoding='latin1', low_memory=False, on_bad_lines='skip')
    if df.shape[1] == 1:
        try:
            df = pd.read_csv(file_path, sep=';', low_memory=False, on_bad_lines='skip')
        except:
            df = pd.read_csv(file_path, encoding='latin1', sep=';', low_memory=False, on_bad_lines='skip')

    # Extract spatial information
    geo_para, granularityS, geo_scope, hierarchiesS = table_geo(df)
    tem_para, tem_scope, granularityT, hierarchiesT = df_tem(file_path, df)
    measures = []
    ci = []

    # Filter out columns that are not spatial or temporal parameters
    cols = [col for col in df.columns if col not in geo_para and col not in tem_para]

    # User interaction to select measures
    root = tk.Tk()
    app = MeasureSelectionApp(root, cols)
    root.mainloop()

    # Get complementary info and measures from user input
    ci, measures = app.get_ci_m()

    return geo_para, geo_scope, granularityS, hierarchiesS, tem_para, tem_scope, granularityT, hierarchiesT, ci, measures, True


# Analyze information from a GeoJSON file
def geojson_EL(file_path):
    # Read GeoJSON data
    gdf = gpd.read_file(file_path)
    geo_para, granularityS, geo_scope, hierarchiesS = gdf_geo(gdf)
    tem_para, tem_scope, granularityT, hierarchiesT = gdf_tem(file_path)

    # Load GeoJSON data for attribute extraction
    with open(file_path, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)

    # Use sets to store measures and complementary info (ci)
    measures = set()
    ci = set()

    # Retrieve properties from each feature in the GeoJSON
    for feature in geojson_data['features']:
        properties = feature.get('properties', {})

    # Filter out columns for user selection
    cols = [key for key in properties.keys()]

    # User interaction to select measures
    root = tk.Tk()
    app = MeasureSelectionApp(root, cols)
    root.mainloop()

    # Get complementary info and measures from user input
    ci, measures = app.get_ci_m()

    return geo_para, geo_scope, granularityS, hierarchiesS, tem_para, tem_scope, granularityT, hierarchiesT, ci, measures, True


# Analyze information from a Shapefile (.shp)
def shapefile_EL(zip_file_path):
    extracted_folder = os.getcwd()
    # Unzip the file
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extracted_folder)

    # Find Shapefile within extracted files
    shapefile_path = None
    for root, dirs, files in os.walk(extracted_folder):
        for file in files:
            if file.endswith('.shp'):
                shapefile_path = os.path.join(root, file)
                break

    if shapefile_path:
        gdf = gpd.read_file(shapefile_path)
        geo_para, granularityS, geo_scope, hierarchiesS = gdf_geo(gdf)
        tem_para, tem_scope, granularityT, hierarchiesT = gdf_tem(file_path)

        # Filter out columns for user selection
        cols = [col for col in gdf.columns if col not in geo_para and col not in tem_para]

        # User interaction to select measures
        root = tk.Tk()
        app = MeasureSelectionApp(root, cols)
        root.mainloop()

        # Get complementary info and measures from user input
        ci, measures = app.get_ci_m()

        return geo_para, geo_scope, granularityS, hierarchiesS, tem_para, tem_scope, granularityT, hierarchiesT, ci, measures, True


# Recursively traverse through XML nodes
def recursive_traverse(node, level=0):
    indent = " " * (level * 4)  # Set indent for visual representation
    print(f"{indent}Tag: {node.tag}, Attributes: {node.attrib}, Text: {node.text.strip() if node.text else 'None'}")

    # Traverse child nodes
    for child in node:
        recursive_traverse(child, level + 1)


def xml_EL(file_path):
    # Analyze XML file
    tree = ET.parse(file_path)
    root = tree.getroot()
    # Traverse XML structure
    recursive_traverse(root)


# Determine file type and process accordingly
def find_type(path):
    file_extension = os.path.splitext(path)[1]
    match file_extension:
        case '.xlsx':
            return excel_EL(path)
        case '.csv':
            return csv_EL(path)
        case '.geojson':
            return geojson_EL(path)
        case '.zip':
            return shapefile_EL(path)
        case _:
            return False, False, False, False, False, False, False, False, False, False, False


# Retrieve all files within the specified path
def get_all_files(file_path):
    file_list = []
    # Traverse directory
    for root, dirs, files in os.walk(file_path):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list


if __name__ == "__main__":
    # Set the data source path
    all_files = get_all_files(data_source)

    # Process each file within the source
    for file_path in all_files:
        print(file_path)
        code_dataset += 1
        geo_para, geo_scope, granularityS, hierarchiesS, tem_para, tem_scope, granularityT, hierarchiesT, ci, measures, treat = find_type(
            file_path)

        if treat:
            root = tk.Tk()
            app = ThemeSelectionApp(root, theme_folder_structure, file_path, measures, ci)
            root.mainloop()

            # Retrieve final theme after Tkinter closes
            theme = app.get_final_theme()
            ci, measures = app.get_measures_and_themes()

            metadata_entry = create_metadata_entry(file_path, code_dataset, os.path.basename(file_path), '', '',
                                                   os.path.splitext(file_path)[1], theme,
                                                   [list(geo_para), list(tem_para)], list(ci), list(measures),
                                                   granularityS, granularityT, geo_scope, tem_scope,
                                                   [hierarchiesS, hierarchiesT])
            write_metadata_to_file(metadata_file, metadata_entry)
