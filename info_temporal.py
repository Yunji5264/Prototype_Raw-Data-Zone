import pandas as pd
import geopandas as gpd
import json
from numpy import integer
from pandas.core.dtypes.inference import is_integer
from shapely.geometry import box, Point, shape
from data_load import *
import re


def colname_contains_date(df):
    col_match = []
    level = -1
    hierarchies = []

    for col in df.columns:
    # check for date patterns
        for pattern in date_patterns:
            match = re.search(pattern, col)
            if match:
                col_match.append(match.group(0))
                level = 3
                hierarchies = [0,1]

        # check for month patterns
        for pattern in month_patterns:
            match = re.search(pattern, col)
            if match:
                col_match.append(match.group(0))
                level = 2
                hierarchies = [0]
        for month in months:
            match = re.search(month, col.lower())
            if match :
                col_match.append(match.group(0))
                level = 2
                hierarchies = [0]

        # check for year pattern
        match = re.search(year_pattern, col)
        if match:
            col_match.append(match.group(0))
            level = 0
            hierarchies = [0, 1]
    if level == -1:
        return False, False, False
    else:
        col_match = {'level '+ str(level) : col_match}
        return col_match, level, hierarchies

def filename_contains_date(file_path):
    filename = file_path.split('/')[-1]


    # check for date patterns
    for pattern in date_patterns:
        match = re.search(pattern, filename)
        if match:
            return ({"type": "date",
                "min_date": match.group(0),
                "max_date": match.group(0)},
                    3, [0,1])

    # check for month patterns
    for pattern in month_patterns:
        match = re.search(pattern, filename)
        if match:
            return ({"type": "month",
                "min_date": match.group(0),
                "max_date": match.group(0)},
                    2, [0])
    for month in months:
        match = re.search(month, filename.lower())
        if match:
            return ({"type": "month",
                "min_date": match.group(0),
                "max_date": match.group(0)},
                    2, [0])

    # check for year pattern
    match = re.search(year_pattern, filename)
    if match:
        return ({"type": "year",
                "min_date": match.group(0),
                "max_date": match.group(0)},
                0, [0,1])

    return False, False, False

def gdf_tem(file_path):
    scopeT, graT, hierarchies = filename_contains_date(file_path)
    paraT = ['File name']
    hierarchiesT = []
    if hierarchies :
        hierarchiesT = hier_T(graT, hierarchies)
    return paraT, scopeT, graT, hierarchiesT

def df_tem(file_path, df):
    graT = -1
    paraT = []
    date_columns_info = {}
    hierarchies = []

    # Define date, month, and year formats
    date_formats = ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y', '%Y%m%d']
    month_formats = ['%m/%Y', '%Y-%m', '%m-%Y', '%Y%m']
    year_formats = ['%Y']

    # Iterate through each column
    for col in df.columns:
        df_nona = df[col].replace('', pd.NA).dropna()

        # Attempt to convert the column to integer and then to string
        try:
            df_nona = df_nona.astype(int).astype(str)
        except:
            pass

        if len(df_nona) == 0:
            continue

        # Check if the column matches date, month, or year formats
        if check_and_store_date(df_nona, date_formats, 'date', col, date_columns_info, paraT):
            graT = max(graT,3)
            hierarchies = [0,1]
        elif check_and_store_date(df_nona, month_formats, 'month', col, date_columns_info, paraT):
            graT = max(graT, 2)
            hierarchies = [0]
        elif check_and_store_date(df_nona, year_formats, 'year', col, date_columns_info, paraT):
            graT = max(graT, 0)
            hierarchies = [0, 1]

    # If no date column is found, guess based on column names or file name
    if graT == -1:
        if colname_contains_date(df):
            date_columns_info, graT, hierarchies = colname_contains_date(df)
            paraT = ['Column names']
        elif filename_contains_date(file_path):
            date_columns_info, graT, hierarchies = filename_contains_date(file_path)
            paraT = ['File names']
    hierarchiesT = []
    if hierarchies:
        hierarchiesT = hier_T(graT, hierarchies)
    return paraT, date_columns_info, graT, hierarchiesT


def check_and_store_date(series, formats, date_type, col, date_columns_info, paraT):
    for date_format in formats:
        try:
            # Try to convert the column to datetime with the given format
            converted_col = pd.to_datetime(series, format=date_format, errors='raise')
            date_columns_info[col] = {
                'type': date_type,
                'min_date': str(converted_col.min()),
                'max_date': str(converted_col.max())
            }
            paraT.append(col)
            return True
        except (ValueError, TypeError):
            continue
    return False


def hier_T(graT, hierarchies) :
    hierarchyT = []
    for x in hierarchies :
        result = [[item[0], item[1]] for item in hT_F[x] if item[0] <= graT]
        hierarchyT.append(result)
    hierarchyT = [list(x) for x in set(list_to_tuple(x) for x in hierarchyT)]
    return hierarchyT
