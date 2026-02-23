# -*- coding: utf-8 -*-
from pathlib import Path
import pandas as pd
import numpy as np
import os
from scipy.stats import chi2_contingency

TABLE_DESCRIBE = "describe_column.csv"
TABLE_MANUAL_DESCRIBE = "force_describe_column.csv"
DEFAULT_DATA_DIR = str(Path.home() / "data")
FILE_EXTENSION = "csv"


def get_config():
    """return configuration variable"""
    config = {
        "table_describ": TABLE_DESCRIBE,
        "force_table_describ": TABLE_MANUAL_DESCRIBE,
        "data_dir": DEFAULT_DATA_DIR,
        "file_ext": FILE_EXTENSION,
    }
    return config


def csv_to_dataframe():
    """return a dictionnary of dataframe from files in repertorie 'raw' of data_path"""
    config = get_config()
    dataframes_dic = {}
    data_path = config["data_dir"] + "/raw"

    files = list(Path(data_path).glob("*." + config["file_ext"]))

    for file in files:
        df = pd.read_csv(os.path.join(data_path, file.name))
        dataframes_dic[file.name] = df

    print("dataframes dic:", dataframes_dic.keys())
    return dataframes_dic


def describe_field(df, table_name, origin="original"):
    """return a datafrme with standard statistical information"""
    nb_row = df.shape[0]

    df_field_describ = pd.DataFrame(
        {
            "name": df.columns,
            "table": table_name,
            "dtype": df.dtypes.values,
            "origin": origin,
            "key": "",  # PRIMARY, FOREIGN
            "nb_row": nb_row,
            "unique": df.nunique(),
            "notnull": df.notnull().sum().values,
            "isna": df.isna().sum().values,
        }
    )
    # Ajout des statistiques standard par la fonction describe() pour les champs numérique
    df_describe_numeric = df.describe().T.reset_index().drop(columns=["count"])
    df_field_describ = df_field_describ.merge(
        df_describe_numeric, left_on="name", right_on="index", how="left"
    ).drop(columns=["index"])
    return df_field_describ


def create_describe_field(dataframes_dic):
    """create the dataframe description
    Input: {dataframe_name: dataframe, ...}
    Output: text format csv
    """
    config = get_config()
    created = False

    for df_name, df_data in dataframes_dic.items():
        df_field_describ = describe_field(df_data, df_name)

        if not created:
            df_describ = df_field_describ
            created = True
        else:
            df_describ = pd.concat([df_describ, df_field_describ], ignore_index=True)

    df_field_describ = assign_key(df_field_describ)
    df_describ.to_csv(config["data_dir"] + "/" + config["table_describ"], index=False)


def load_describe_field():
    """load the description file to dataframe"""
    config = get_config()
    df_field_describ = pd.read_csv(config["data_dir"] + "/" + config["table_describ"])
    return df_field_describ


def load_force_describe_field():
    """load the forced description file to dataframe"""
    config = get_config()
    
    file_path = Path(config["data_dir"] + "/" + config["force_table_describ"])

    if file_path.exists():
        df_force_field_describ = pd.read_csv(str(file_path))
    else:
        # return void dataframe
        columns = ["name", "table", "categ", "categ_value", "categ_unit"]
        df_force_field_describ = pd.DataFrame({col: pd.Series(dtype="object") for col in columns})
        df_force_field_describ.to_csv(str(file_path), index=False)
        
    return df_force_field_describ


def save_describe_field(df_field_describ):
    """load the description file to dataframe"""
    config = get_config()
    path_field_describ = config["data_dir"] + "/" + config["table_describ"]
    df_field_describ.to_csv(path_field_describ, index=False)


def assign_target(df_field_describ, target_name="TARGET", target_table=""):
    """function to assign the target column"""
    for index, row in df_field_describ.iterrows():
        if row["name"] == target_name:
            if target_table != "" and row["table"] != target_table:
                continue
            df_field_describ.at[index, "key"] = "TARGET"

    return df_field_describ


def assign_key(df_field_describ):
    """function to assign the database key of column:  PRIMARY, FOREIGN"""
    primary_keys = []

    for index, row in df_field_describ.iterrows():
        if row["nb_row"] == row["unique"] and "int" in str(row["dtype"]):
            df_field_describ.at[index, "key"] = "PRIMARY"
            primary_keys.append(row["name"])
            print("PRIMARY:", row["name"], row["table"])

    for index, row in df_field_describ.iterrows():
        if row["name"] in primary_keys and row["key"] != "PRIMARY":
            df_field_describ.at[index, "key"] = "FOREIGN"
            print("FOREIGN:", row["name"], row["table"])

    return df_field_describ


def assign_category(df_field_describ):
    """function to assign the data category of column:  BINARY, NUMERIC, CATEGORY,"""

    # add filed on df_field_describ
    for field in ['categ', 'categ_value']:
        if field not in df_field_describ.columns:
            df_field_describ[field] = "_"

    # Filter
    NO_CATEG = (df_field_describ["categ"] == "_")
    IS_TARGET = (df_field_describ["key"] == "TARGET")
    IS_KEY = (df_field_describ["key"].isin(["PRIMARY", "FOREIGN"]))
    IS_OBJECT = (df_field_describ["dtype"].astype('str').str.contains("object", na=False))
    IS_INT = (df_field_describ["dtype"].astype('str').str.contains("int", na=False))
    IS_FLOAT = (df_field_describ["dtype"].astype('str').str.contains("float", na=False))
    IS_VOID = ((df_field_describ["unique"] == 0) | (df_field_describ["unique"] == 1))
    UNIQUE_2 = (df_field_describ["unique"] == 2)
    UNIQUE_1_PERCENT = ((df_field_describ["unique"] / df_field_describ["nb_row"]) < 0.01)
    
    # update categ
    df_field_describ.loc[(NO_CATEG & IS_TARGET), "categ"] = "TARGET"
    df_field_describ.loc[(NO_CATEG & IS_KEY), "categ"] = "KEY"
    df_field_describ.loc[(NO_CATEG & IS_VOID), "categ"] = "VOID"
    df_field_describ.loc[(NO_CATEG & IS_FLOAT), "categ"] = "NUMERIC"
    df_field_describ.loc[(NO_CATEG & UNIQUE_2 & IS_OBJECT), "categ"] = "BINARY"
    df_field_describ.loc[(NO_CATEG & UNIQUE_2 & IS_INT), "categ"] = "BINARY"
    df_field_describ.loc[(NO_CATEG & UNIQUE_1_PERCENT & IS_OBJECT), "categ"] = "CATEGORICAL"
    #df_field_describ.loc[(NO_CATEG & UNIQUE_1_PERCENT & IS_INT), "categ"] = "CATEGORICAL"
    
    # Force update categ by manual value
    df_force_field_describ = load_force_describe_field()
    
    for index, row in df_force_field_describ.iterrows():
        if row["name"] and row["table"] and row["categ"]:
            mask = ((df_field_describ["name"] == row["name"]) & (df_field_describ["table"] == row["table"]))
            df_field_describ.loc[(mask), "categ"] = row["categ"]
        
    return df_field_describ

def get_target_table(df_field_describ):
    """ return the table and his primary key with the target """
    
    result = df_field_describ.loc[(df_field_describ["key"] == "TARGET"), "table"]
    
    if len(result) != 1:
        raise ValueError("TARGET must be only once.")
        
    target_table = result.iloc[0]    
    
    result = df_field_describ.loc[
        ((df_field_describ["key"] == "PRIMARY") & (df_field_describ["table"] == target_table)), 
        "name"]
    
    if len(result) != 1:
        raise ValueError("PRIMARY KEY must be only once.")
    
    target_primary = result.iloc[0]    
    return target_table, target_primary
    

def compute_KHI2(dataframes_dic, df_field_describ):
    """ compute KI2 and save p-value on df_field_describ """
    
    # add filed on df_field_describ
    for field in ['p_value']:
        if field not in df_field_describ.columns:
            df_field_describ[field] = ""
            
    # Get target table
    
    
if __name__ == "__main__":
    
    dataframes_dic = csv_to_dataframe()
    #create_describe_field(dataframes_dic)
    
    df_field_describ = load_describe_field()
    #df_field_describ = assign_target(df_field_describ)
    #df_field_describ = assign_key(df_field_describ)
    #df_field_describ = assign_category(df_field_describ)
    print(get_target_table(df_field_describ))
    
    
    save_describe_field(df_field_describ)

