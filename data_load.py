import configparser
from os import remove

import pandas as pd
import geopandas as gpd
import unicodedata
import unicodedata
import re


# get into config.ini
config = configparser.ConfigParser()
config.read('config.ini')

# get the data source path in config.ini
data_source = config['Paths']['data_source']

# get the world geographic information
#world = gpd.read_file(config['Paths']['countries_path2'])
#continent = gpd.read_file(config['Paths']['continents_path'])
#ity = gpd.read_file(config['Paths']['cities_path'])
world = gpd.read_file(config['Paths']['countries_path'])
regions = gpd.read_file(config['Paths']['regions_path'])
departements = gpd.read_file(config['Paths']['departements_path'])
arrondissements = gpd.read_file(config['Paths']['arrondissements_path'])
cantons = gpd.read_file(config['Paths']['cantons_path'])
communes = gpd.read_file(config['Paths']['communes_path'])
france = gpd.read_file(config['Paths']['france_path'])
communes_france = gpd.read_file(config['Paths']['communes_france_path'])


#
# # connect communes to cantons
# communes_cantons = gpd.sjoin(communes, cantons, how='left', predicate='intersects', rsuffix='_cantons')
# communes_cantons = communes_cantons.rename(columns={'code_left': 'code_cantons', 'nom_left': 'nom_cantons'})
#
# # 与 arrondissements 进行空间连接
# communes_arrons = gpd.sjoin(communes_cantons, arrondissements, how='left', predicate='intersects', rsuffix='_arrons')
# communes_arrons = communes_arrons.rename(columns={'code_left': 'code_arrons', 'nom_left': 'nom_arrons'})
#
# # 与 departements 进行空间连接
# communes_departements = gpd.sjoin(communes_arrons, departements, how='left', predicate='intersects', rsuffix='_departements')
# communes_departements = communes_departements.rename(columns={'code_left': 'code_departements', 'nom_left': 'nom_departements'})
#
# # 与 regions 进行空间连接
# communes_regions = gpd.sjoin(communes_departements, regions, how='left', predicate='intersects', rsuffix='_regions')
# communes_regions = communes_regions.rename(columns={'code_left': 'code_regions', 'nom_left': 'nom_regions'})
#
# # 与 france 进行空间连接
# communes_france = gpd.sjoin(communes_regions, france, how='left', predicate='intersects', rsuffix='_france')
# communes_france = communes_france.rename(columns={'code_left': 'code_france', 'nom_left': 'nom_france'})



# test_cf = gpd.sjoin(communes, france, how='left', predicate='intersects', rsuffix='_france')


# ['UID', 'GID_0', 'NAME_0', 'VARNAME_0', 'GID_1', 'NAME_1', 'VARNAME_1',
#  'NL_NAME_1', 'ISO_1', 'HASC_1', 'CC_1', 'TYPE_1', 'ENGTYPE_1',
#  'VALIDFR_1', 'GID_2', 'NAME_2', 'VARNAME_2', 'NL_NAME_2', 'HASC_2',
#  'CC_2', 'TYPE_2', 'ENGTYPE_2', 'VALIDFR_2', 'GID_3', 'NAME_3',
#  'VARNAME_3', 'NL_NAME_3', 'HASC_3', 'CC_3', 'TYPE_3', 'ENGTYPE_3',
#  'VALIDFR_3', 'GID_4', 'NAME_4', 'VARNAME_4', 'CC_4', 'TYPE_4',
#  'ENGTYPE_4', 'VALIDFR_4', 'GID_5', 'NAME_5', 'CC_5', 'TYPE_5',
#  'ENGTYPE_5', 'GOVERNEDBY', 'SOVEREIGN', 'DISPUTEDBY', 'REGION',
#  'VARREGION', 'COUNTRY', 'CONTINENT', 'SUBCONT', 'geometry']

def clean_string(input_str):
    # 规范化字符串，分解字母和变音符号
    nfkd_form = unicodedata.normalize('NFD', input_str)
    # 移除变音符号
    without_accents = ''.join([char for char in nfkd_form if not unicodedata.combining(char)])
    # 移除所有非字母和数字字符
    cleaned_str = re.sub(r'[^a-zA-Z0-9]', '', without_accents)
    return cleaned_str

regions_nfd = set({clean_string(name).upper() for name in set(regions['nom']) if name and name.strip()})


world_5 = set({clean_string(name).upper() for name in set(world['NAME_5']) | set(world['CC_5']) | set(communes['nom']) | set(communes['code']) if name and name.strip()})
world_4 = set({clean_string(name).upper() for name in set(world['NAME_4']) | set(world['CC_4']) | set(cantons['nom']) | set(cantons['code']) if name and name.strip()})
world_3 = set({clean_string(name).upper() for name in set(world['NAME_3']) | set(world['CC_3']) | set(arrondissements['nom']) | set(arrondissements['code']) if name and name.strip()})
world_2 = set({clean_string(name).upper() for name in set(world['NAME_2']) | set(world['CC_2']) | set(departements['nom']) | set(departements['code']) if name and name.strip()})
world_1 = set({clean_string(name).upper() for name in set(world['NAME_1']) | set(world['CC_1']) | set(regions['nom']) | set(regions['code']) if name and name.strip()})
world_0 = set({clean_string(name).upper() for name in set(world['NAME_0']) if name and name.strip()})

world_lists = [(0, world_0),
               (1, world_1),
               (2, world_2),
               (3, world_3),
               (4, world_4),
               (5, world_5)]


#get spatial hierarchy csv
spatialH = pd.read_csv(config['Paths']['path_spatial_hierarchies'])

hSpatial = [(0, 0, ['COUNTRY', 'PAYS']),
            (0, 1, ['REGION']),
            (0, 2, ['DEPARTEMENT', 'DEPT']),
            (0, 3, ['ARRONDISSEMENT']),
            (0, 4, ['CANTON']),
            (0, 5, ['COMMUNE', 'VILLE']),
            (0, 6, ['ADRESSE', 'ADDRESS']),
            (1, 0, ['COUNTRY', 'PAYS']),
            (1, 1, ['EPCI']),
            (1, 5, ['COMMUNE', 'VILLE']),
            (1, 6, ['ADRESSE', 'ADDRESS'])
            ]

months = [
        # 英语
        'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december',
        # 法语
        'janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre',
        # 德语
        'januar', 'februar', 'märz', 'april', 'mai', 'juni', 'juli', 'august', 'september', 'oktober', 'november', 'dezember',
        # 西班牙语
        'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre',
        # 其他语言可以继续添加
    ]
# use regex to show date pattern
date_patterns = [
    r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
    r'\d{8}',  # YYYYMMDD
    r'\d{2}-\d{2}-\d{4}',  # DD-MM-YYYY
    r'\d{2}-\d{2}-\d{2}',  # DD-MM-YY
    r'\d{2}\/\d{2}\/\d{4}',  # DD/MM/YYYY
    r'\d{2}\/\d{2}\/\d{2}',  # DD/MM/YY
]
# use regex to show month pattern
month_patterns = [
    r'\d{4}-\d{2}',  # YYYY-MM
    r'\d{4}\d{2}',  # YYYYMM
    r'\d{2}-\d{4}',  # MM-YYYY
    r'\d{2}\d{4}',  # MMYYYY
    r'\d{2}\/\d{4}',  # MM/YYYY
]
# use regex to show year pattern
year_pattern = r'\d{4}'  # YYYY

metadata_file = r'C:\Users\ADMrechbay20\Documents\Metadata\raw_data_metadata.json'

def list_to_tuple(lst):
    return tuple(list_to_tuple(i) if isinstance(i, list) else i for i in lst)

