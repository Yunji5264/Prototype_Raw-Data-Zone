import pandas as pd
import geopandas as gpd
import json
import unidecode
from numpy import integer
from pandas.core.dtypes.inference import is_integer
from shapely.geometry import box, Point, shape
from data_load import *
from class_predefine import *

# find possible hierarchies for a dataset
def get_spatial_hierarchy(granularity, hierarchies):
    spatial_hierarchies_list = []
    for x in hierarchies:
        hierarchy = [[item[0],item[1]] for item in hS_F[x] if item[0] <= granularity]
        spatial_hierarchies_list.append(hierarchy)
        spatial_hierarchies_list = [list(x) for x in set(list_to_tuple(x) for x in spatial_hierarchies_list)]
    # Turn frozenset to dictionary

    return spatial_hierarchies_list

# find geo parameters for a gdf
def find_geo_para(gdf):
    geo_parameter = []

    # Include geometry column if present
    if 'geometry' in gdf.columns:
        geo_parameter.append('geometry')  # Add geometry explicitly

    for col in gdf.columns:
        if len(set(gdf[col])) > 0 and col != 'geometry':  # Exclude geometry from regular checks
            # check if all elements in the column are strings
            if gdf[col].apply(lambda x: isinstance(x, str)).all():
                for code, world_list in world_lists:
                    # check if all values in the column match the entries in world_list
                    if all(clean_string(str(value)).upper() in world_list for value in gdf[col] if value != ''):
                        geo_parameter.append(col)  # Add code and column if match found

    return geo_parameter


# find geo scope of a gdf
def find_geo_scope(gdf):
    gdf = gdf[gdf.is_valid]
    # get the scope of the geojson
    bounding_box = gdf.total_bounds
    # change Bounding Box into GeoDataFrame
    bbox = gpd.GeoDataFrame({'geometry': [box(*bounding_box)]}, crs=world.crs)
    # check Bounding Box for intersecting countries/regions/department/city
    # countries_in_bbox = gpd.sjoin(world, bbox, how='inner', predicate='intersects')
    countries_in_bbox = gpd.sjoin(world, bbox, how='inner', predicate='intersects')
    #find scope
    go_on = True
    #from biggest to smallest
    level = 0
    while level < 5 and go_on:
        # find from which level there are multiple values
        set_level = {name for name in countries_in_bbox['NAME_' + str(level)] if name != ''}
        set_level_next = {name for name in countries_in_bbox['NAME_' + str(level + 1)] if name != ''}
        if len(set_level) < len(set_level_next):
            go_on = False
            if len(set_level) == 1 and len(set_level_next) != 1 and len(set_level_next) < 10 :
                level += 1
        elif len(set_level) > len(set_level_next) :
            go_on = False
            if len(set_level) > 10 :
                level -= 1
        else :
            level += 1
    # get the list of geoscope
    geoscope = {name for name in countries_in_bbox['NAME_' + str(level)] if name != ''}
    # get the possible hierarchies
    hierarchies = [0, 1]

    return geoscope, hierarchies, level

# Function to check if all values match a world_list
def check_column_values(col_values, world_list):
    return all(unidecode.unidecode(str(value)).upper() in world_list for value in col_values if value != '')

def split_code_name(lst):
    result_code = []
    result_name = []
    for item in lst:
        # 使用正则表达式将邮编和城市名称分开
        match = re.match(r"(\d+)\s+(.+)", item)
        if match and match.lastindex >= 2:
            code = match.group(1)  # 邮编部分
            name = match.group(2)  # 地区名称部分
            result_code.append(code)
            result_name.append(name)
    return result_code, result_name

#find the geo information for a non gdf dataset
def find_geo(df):
    geo_parameter = []
    granularity = -1
    scope = 6
    scope_col_name = ''
    scopes = []
    hierarchies = []
    temporal_params = []
    code_pattern = r'(\d+)'  # Postal code pattern
    name_pattern = r'[A-Za-z\s]+'  # Name pattern

    # Iterate through columns
    for col in df.columns:
        for hier, number, keywords in hSpatial:
            for keyword in keywords:
                # Check if keyword exists in column name
                if unidecode.unidecode(col).upper() == keyword :
                    temporal_params.append((hier, number, col))
                    granularity = max(granularity, number)
        if df[col].apply(lambda x: isinstance(x, str)).all():
            col_values = df[col].dropna()
            for hier, number, keywords in hSpatial:
                for keyword in keywords:
                    # Check if keyword exists in column name
                    if keyword in unidecode.unidecode(col).upper():
                        temporal_params.append((hier, number, col))
                        granularity = max(granularity, number)

            if temporal_params:
                geo_parameter.extend(temporal_params)
            else:
                # Handle the case where column doesn't match keywords but might contain geographic data
                try:
                    col_values_code, col_values_name = split_code_name(col_values)
                except:
                    col_values_code, col_values_name = [], []

                for code, world_list in world_lists:
                    if check_column_values(col_values, world_list) or (
                            col_values_name and check_column_values(col_values_name, world_list)):
                        geo_parameter.append((0, code, col))

    if geo_parameter:
        granularity = max(param[1] for param in geo_parameter)
        scope = min(param[1] for param in geo_parameter)
        scope_col_name = [param[2] for param in geo_parameter if param[1] == scope]
        hierarchies = set(param[0] for param in geo_parameter)

        geo_parameter = set(param[2] for param in geo_parameter)

        for col in scope_col_name:
            if col in df.columns:
                scopes.append({col: set(df[col].tolist())})

    return list(geo_parameter), granularity, scope_col_name, scope, hierarchies


# check if a dataframe can be transform into a gdf
def check_geopoint(df) :
    matching_columns = []
    # check if there're columns start as GEO
    geo_columns = [col for col in df.columns if col.upper().startswith('GEO')]
    if geo_columns:
        matching_columns.extend(geo_columns)
        return matching_columns
    # check if there're 'LAT' and 'LONG' at the same time
    lat_columns = [col for col in df.columns if col.upper().startswith('LAT')]
    long_columns = [col for col in df.columns if col.upper().startswith('LONG')]
    if lat_columns and long_columns:
        matching_columns.extend(long_columns)
        matching_columns.extend(lat_columns)
        return matching_columns
    # check if there're 'X' and 'Y' at the same time
    x_columns = [col for col in df.columns if col.upper() == 'X']
    y_columns = [col for col in df.columns if col.upper() == 'Y']
    if x_columns and y_columns:
        matching_columns.extend(x_columns)
        matching_columns.extend(y_columns)
        return matching_columns
    # check if there's a column with form geopoint
    for col in df.head().columns:
        geopoint = 0
        # go through all the cells
        for value in df.head()[col]:
            # check if there's a column for geopoint
            # geopint is in form "34.052235, -118.243683"
            if isinstance(value, str) and ',' in value :
                try:
                    float(value.replace(',', '.'))
                except:
                    try:
                        # 尝试用逗号分隔
                        lon, lat = value.split(',')
                        lon = float(lon)
                        lat = float(lat)
                        # 判断经度和纬度是否在有效范围内
                        if -180 <= lon <= 180 and -90 <= lat <= 90:
                            geopoint +=1
                        else:
                            geopoint = 0
                    except:
                        continue
        if geopoint > 0 :
            return col
    return False


# build a GeoDataFrame according to the information in table
def build_gdf(df, cols):
    geometry = []
    # see if it's a geopoint or seperately write in 2 columns
    if any(col.upper().startswith('GEO') for col in cols):
        for col in cols:
            # ensure there's no null
            if not any(value == '' for value in df[col]):
                for val in df[col].dropna():
                    try:
                        # for the form GeoJSON
                        geom = shape(json.loads(val))
                    except Exception as e:
                        try:
                            # for the form longitude, latitude
                            long, lat = map(float, val.split(','))
                            geom = Point(long, lat)
                        except Exception as inner_e:
                            geom = Point()
                    geometry.append(geom)
        # delete the null in geometry
        geometry = [geom for geom in geometry if not geom.is_empty]
    else:
        for x, y in zip(df[cols[0]], df[cols[1]]):
            if x not in [None, '', 'nan'] and pd.notna(x) and y not in [None, '', 'nan'] and pd.notna(y):
                try:
                    # change the ',' in float to '.'
                    x = float(str(x).replace(',', '.'))
                    y = float(str(y).replace(',', '.'))
                    geom = Point(x, y)
                except ValueError:
                    geom = Point(x, y)
            else :
                geom = Point()
            geometry.append(geom)
    # make sure the size of `geometry` is same as the row size `df`
    if len(geometry) != len(df):
        geometry = geometry[:len(df)]
    # 创建 GeoDataFrame 并设置 CRS
    gdf = gpd.GeoDataFrame(df, geometry=geometry)
    gdf.set_crs(epsg=3857, inplace=True)
    gdf = gdf.to_crs(epsg=4326)
    return gdf


def gdf_geo(gdf):
    # get spatial granularity
    granularityS = 6
    # get geoscope and spatial hierarchy
    geo_scope, hierarchies, scope = find_geo_scope(gdf)
    scope_desc = "Level " + str(scope)
    geo_scope = {scope_desc: set(geo_scope)}
    # get geo parameter
    geo_para = find_geo_para(gdf)
    hierarchiesS = get_spatial_hierarchy(granularityS, [0, 1])
    return geo_para, granularityS, list(geo_scope), hierarchiesS


def table_geo(df) :
    geo_para = []
    geo_scope = []
    geo_scope_pre = []
    hierarchiesS = []
    # check if there's info about geopoint
    geo_columns = check_geopoint(df)
    geopoint = False
    # if so
    if geo_columns:
        # spatial granularity is Geopoint
        granularityS = 6
        geopoint = True
        # make sure there's no null in the geopoint columns
        df = df[df[geo_columns].notnull().any(axis=1)]
        # build gdf and treat it as geojson and shapefile
        # create geodataframe
        gdf = build_gdf(df, geo_columns)
        # find geo scope
        try:
            geo_scope_pre, hierarchiesS, scope = find_geo_scope(gdf)
            scope_desc = "Level " + str(scope)
            geo_scope.append({scope_desc: set(df[scope].tolist())})

        except:
            print("can't get")
        # in case there's no value for geopoint
    # if granularity is not geopoint
    if len(geo_scope_pre) == 0 :
        # find spatial info
        geo_scope = []
        geo_para, granularityS, geo_scope_col, scope, hierarchies = find_geo(df)
        if geopoint :
            geo_para.append(geo_columns)
        for col in geo_scope_col:
            if col in df.columns:
                scope_desc = "Level " + str(scope) + ": " + col
                geo_scope.append({"Level " + str(scope): col})
            else:
                print("geo_scope cannot be built")
        hierarchiesS = get_spatial_hierarchy(granularityS, hierarchies)
    else :
        geo_para = find_geo(df)[0]
    return geo_para, granularityS, geo_scope, hierarchiesS