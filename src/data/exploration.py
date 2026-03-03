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
    """return configuration variables"""
    config = {
        "table_describ": TABLE_DESCRIBE,
        "force_table_describ": TABLE_MANUAL_DESCRIBE,
        "data_dir": DEFAULT_DATA_DIR,
        "file_ext": FILE_EXTENSION,
    }
    return config


def csv_to_dataframe():
    """return a dictionnary of dataframe from files in directory 'raw' of data_path"""
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
            "key": "_",  # PRIMARY, FOREIGN
            "level": 0,
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


def create_describe_file(dataframes_dic):
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


def load_describe_file():
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


def save_describe_file(df_field_describ):
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

def get_target_name(df_field_describ):
    """ get the name of the the target """
    target_name = str(df_field_describ.loc[(df_field_describ["key"] == "TARGET"), "name"].iloc[0])
    return target_name


def get_mcd(df_field_describ):
    """
    Build a simplified Conceptual Data Model (CDM) representation
    - Identify the root table of the dataset
    - Identify the join keys for pandas merges

    Parameters
    ----------
    df_field_describ : pandas.DataFrame

    Returns
    -------
    dict
        {
            'table_name.csv': {
                'target': str,        # target variable if applicable, otherwise ''
                'level': int,         # hierarchical level (1 = directly linked to root table)
                'foreign_name': str,  # foreign key field name
                'foreign_table': str  # referenced table name
            },
            ...
        }

    """

   # Filter
    IS_TARGET = (df_field_describ["key"] == "TARGET")
    IS_PRIMARY = (df_field_describ["key"] == "PRIMARY")
    IS_FOREIGN = (df_field_describ["key"] == "FOREIGN")
    
    # Table
    target_table = df_field_describ.loc[IS_TARGET, ["table", "name"]]
    # level 0, the table with the target
    level = 1
    mcd = {}
    if len(target_table) == 1:
        # Save the table wit the target
        dic_target_table = target_table.iloc[0].to_dict()
        mcd[dic_target_table["table"]] = {"target": dic_target_table["name"], "level": level, "foreign_name": "", "foreign_table": ""}
    
        # Save the primary key of the table target
        IS_TARGET_TABLE = (df_field_describ["table"] == dic_target_table["table"])
        target_primary = df_field_describ.loc[(IS_TARGET_TABLE & IS_PRIMARY), ["name"]]
        if len(target_primary) == 1:
            dic_target_primary = target_primary.iloc[0].to_dict()
            mcd[dic_target_table["table"]]["primary"] = dic_target_primary["name"]
    
            # Search the table linked to target table
            tables_ok = list(mcd.keys())
            foreign_name = dic_target_primary["name"]
            foreign_table = dic_target_table["table"]
            
            IS_FOREIGN_NAME = (df_field_describ["name"] == foreign_name)
            IS_NOT_TABLE_OK = (~df_field_describ["table"].isin(tables_ok))
    
            foreign_key = df_field_describ.loc[IS_FOREIGN_NAME & IS_FOREIGN & IS_NOT_TABLE_OK, ["table", "name"]]
    
            if len(foreign_key) > 0:
                level += 1
                for index, row in foreign_key.iterrows():
                    mcd[row["table"]] = {"target": "", "level": level, "foreign_name": foreign_name, "foreign_table": foreign_table}
    return mcd
                

def assign_level(df_field_describ):
    """ Save the level of group by with the MCD """
    mcd = get_mcd(df_field_describ)
    
    for index, row in df_field_describ.iterrows():
        if row["table"] in list(mcd.keys()) and mcd[row["table"]].get("level"):
            df_field_describ.at[index, "level"] = mcd[row["table"]]["level"]
        
    return df_field_describ
    

def assign_key(df_field_describ):
    """ function to assign the database key of column:  PRIMARY, FOREIGN """
    primary_keys = []

    for index, row in df_field_describ.iterrows():
        if row["nb_row"] == row["unique"] and "int" in str(row["dtype"]):
            df_field_describ.at[index, "key"] = "PRIMARY"
            primary_keys.append(row["name"])

    for index, row in df_field_describ.iterrows():
        if row["name"] in primary_keys and row["key"] != "PRIMARY":
            df_field_describ.at[index, "key"] = "FOREIGN"
            
    return df_field_describ


def add_field_describe(df_field_describ, field_list=[], default_value=""):
    """ add column on df_field_describ if not exist
        return new df_field_describ """
    for field in field_list:
        if field not in df_field_describ.columns:
            df_field_describ[field] = default_value
            
    return df_field_describ


def assign_category(df_field_describ):
    """ function to assign the data category of column:  BINARY, NUMERIC, CATEGORY,"""

    # add fields on df_field_describ
    df_field_describ = add_field_describe(df_field_describ, ['categ', 'categ_value'], "_" )

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


def assign_category_value(df_field_describ, dataframes_dic):
    """ define the first value of binary to int 1 """
    # Filter
    NO_CATEG_VALUE = (df_field_describ["categ_value"] == "_")
    IS_BINARY = (df_field_describ["categ"] == "BINARY")
    
    update_fields = df_field_describ.loc[(IS_BINARY & NO_CATEG_VALUE), ["table", "name"]]
    for index, row in update_fields.iterrows():
        first_value = dataframes_dic[row["table"]][row["name"]].sort_values().unique().tolist()[-1]

        update_mask = ((df_field_describ["table"] == row["table"]) & (df_field_describ["name"] == row["name"]))
        df_field_describ.loc[update_mask, "categ_value"] = first_value
        
    return df_field_describ

    
def get_y_by_table(dataframes_dic, df_field_describ, table):
    """ return the y dataframe serie by table, return void dataframe if not possible """
    # Get the description of table : MCD
    mcd = get_mcd(df_field_describ)
    target_name = get_target_name(df_field_describ)
    
    if not mcd.get(table):
        # table is not in the mcd analyse, TODO, only 1 level deep merge at this time
        y = pd.DataFrame()
        
    elif mcd[table].get("level", 0) == 1:
        y = dataframes_dic[table][mcd[table]["target"]]
        
    elif mcd[table].get("level", 0) == 2:
        # create target link with merge table

        y = dataframes_dic[table].merge(
            dataframes_dic[mcd[table]["foreign_table"]][[target_name, mcd[table]["foreign_name"]]],
            left_on=mcd[table]["foreign_name"],
            right_on=mcd[table]["foreign_name"],
            how='left'
        )[target_name]
        
    else:
        y = pd.DataFrame()
        
    return y


def get_dic_table_by_filter(df_field_describ, df_filter):
    """ return dic with table and columns by dataframe filter """
    
    update_name = df_field_describ.loc[df_filter, ["name","table"]]
    
    # Group by table
    table_update = {}
    for index, row in update_name.iterrows():
        if row["table"] not in list(table_update.keys()):
            table_update[row["table"]] = []
        table_update[row["table"]].append(row["name"])
        
    return table_update


def compute_KHI2(dataframes_dic, df_field_describ):
    """ compute KI2 and save p-value on df_field_describ """
    
    # add field p_value on df_field_describ
    df_field_describ = add_field_describe(df_field_describ, ['p_value'], 0.0 )
     
    # Select the binary field with no p_value
    IS_KHI2 = (df_field_describ["categ"].isin(["BINARY", "CATEGORICAL"]))
    NO_P_VALUE = (df_field_describ["p_value"] == 0.0)
    table_update_khi2 = get_dic_table_by_filter(df_field_describ, (IS_KHI2 & NO_P_VALUE))
        
    # compute KHI2 by table
    for table in list(table_update_khi2.keys()):
        
        y = get_y_by_table(dataframes_dic, df_field_describ, table)
        if y.empty:
            continue
        
        for name in table_update_khi2[table]:

            x = dataframes_dic[table][name]
        
            crosstab = pd.crosstab(x, y)
            chi2, p, _, _ = chi2_contingency(crosstab)

            update_mask = ((df_field_describ["table"] == table) & (df_field_describ["name"] == name))
            df_field_describ.loc[update_mask, "p_value"] = round(p, 4) or 0.0001
            
    return df_field_describ


def compute_corr(dataframes_dic, df_field_describ):
    """ compute correlation and save on df_field_describ """
    
    # add fields on df_field_describ
    df_field_describ = add_field_describe(df_field_describ, ['correlation'], 0.0 )
    
    target_name = get_target_name(df_field_describ)

    # Select the field with no correlation
    IS_NUMERIC = (df_field_describ["categ"] == "NUMERIC")
    IS_BINARY = (df_field_describ["categ"] == "BINARY")
    IS_CATEGORICAL = (df_field_describ["categ"] == "CATEGORICAL")
    NO_CORR = (df_field_describ["correlation"] == 0.0)
    
    table_update_corr = get_dic_table_by_filter(
        df_field_describ,
        ((IS_NUMERIC | IS_BINARY | IS_CATEGORICAL) & NO_CORR)
        )
        
    # compute Correlation by table
    for table in list(table_update_corr.keys()):
        print('-------table---------', table)

        y = get_y_by_table(dataframes_dic, df_field_describ, table)
        if y.empty:
            continue
        
        for name in table_update_corr[table]:
            if name == target_name:
                continue
            
            FILTER_NAME = ((df_field_describ["table"] == table) & (df_field_describ["name"] == name))
            categ = df_field_describ.loc[FILTER_NAME, ["categ", "categ_value", "dtype"]].iloc[0].to_dict()
            
            x = dataframes_dic[table][name]
            df = pd.concat([y, x], axis=1)
            
            if categ["categ"] == "NUMERIC":
                correlation_matrix = df.corr()
                corr = correlation_matrix.loc[target_name, name]
                df_field_describ.loc[FILTER_NAME, "correlation"] = round(corr, 4)
                
            else:
                # For Categorical column, get the max correlation of each correlation value
                dummies = pd.get_dummies(df[name], drop_first=False)
                corr_with_target = dummies.corrwith(df[target_name])
                
                max_corr_value = corr_with_target.abs().idxmax()
                max_corr = corr_with_target.loc[max_corr_value]
                            
                df_field_describ.loc[FILTER_NAME, "correlation"] = round(max_corr, 4)
                df_field_describ.loc[FILTER_NAME, "categ_value"] = max_corr_value
            
            
    return df_field_describ

    
if __name__ == "__main__":
    
    dataframes_dic = csv_to_dataframe()
    #create_describe_file(dataframes_dic)
    
    
    df_field_describ = load_describe_file()
    #df_field_describ = assign_target(df_field_describ)
    #df_field_describ = assign_key(df_field_describ)
    #df_field_describ = assign_level(df_field_describ)
    #df_field_describ = assign_category(df_field_describ)
    #df_field_describ = assign_category_value(df_field_describ, dataframes_dic)
    df_field_describ = compute_KHI2(dataframes_dic, df_field_describ)
    df_field_describ = compute_corr(dataframes_dic, df_field_describ)
      
    save_describe_file(df_field_describ)

