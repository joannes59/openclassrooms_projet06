# -*- coding: utf-8 -*-
from pathlib import Path
import pandas as pd
import numpy as np
import os

TABLE_DESCRIBE = "describe_column.csv"
DEFAULT_DATA_DIR = str(Path.home() / "data")
FILE_EXTENSION = "csv"


def get_config():
    """return configuration variable"""
    config = {
        "table_describ": TABLE_DESCRIBE,
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

    for field in ['categ', 'categ_value']:
        if field not in df_field_describ.columns:
            df_field_describ[field] = "_"
    
    mask = (
        (df_field_describ["categ"] == "_")
        & (df_field_describ["unique"] == 2)
        & (df_field_describ["dtype"].astype('str').str.contains("object", na=False))
    )

    df_field_describ.loc[mask, "categ"] = "BINARY"

    return df_field_describ


if __name__ == "__main__":
    # dataframes_dic = csv_to_dataframe()
    # create_describe_field(dataframes_dic)
    df_field_describ = load_describe_field()
    # df_field_describ = assign_target(df_field_describ)
    # df_field_describ = assign_key(df_field_describ)
    df_field_describ = assign_category(df_field_describ)
    save_describe_field(df_field_describ)
