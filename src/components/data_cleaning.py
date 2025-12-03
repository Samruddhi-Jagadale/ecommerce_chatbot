# data_cleaning.py
import os
import sys
import glob
import pandas as pd
from pandas import DataFrame
from dataclasses import dataclass
from src.utils.logger import logging
from src.utils.exception import Custom_exception

@dataclass
class DataCleaningConfig:
    is_airflow = os.getenv("IS_AIRFLOW", "false").lower() == "true"
    if is_airflow:
        input_path = "/opt/airflow/data/"
        output_path = "/opt/airflow/artifacts/data_cleaned.csv"
    else:
        input_path = "data"
        output_path = "artifacts/data_cleaned.csv"

class DataCleaner:
    """
    Remove 'na' values from the data and ensure required columns exist.
    Expected columns from hunnit_scraper.py:
      Title, Price, CompareAtPrice, SKU, VariantTitle, VariantOptions,
      Description, Features, ImageURLs, Category, Vendor, Tags, Availability, ProductURL
    """

    def __init__(self):
        self.data_cleaner_config = DataCleaningConfig()

    def load_data(self, file_path):
        try:
            logging.info(f"Loading data from {file_path}")
            dfs = []
            file_paths = glob.glob(os.path.join(file_path, "*.csv"))
            for f in file_paths:
                file = pd.read_csv(f)
                dfs.append(file)
            df = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
            logging.info("Data loaded successfully")
            return df
        except Exception as e:
            logging.error(f"Error in loading data: {str(e)}")
            raise Custom_exception(e, sys)

    def check_for_na(self, df: DataFrame):
        try:
            logging.info("Checking for 'na' values")
            df_na = df[df.applymap(lambda x: str(x).strip().lower() == 'na').any(axis=1)]
            print(f"Total number of records that has 'na': {len(df_na)}")
            columns_na = df.applymap(lambda x: str(x).strip().lower() == 'na').sum()
            print(f"\ncolumn wise presence of 'na' \n{columns_na}")
        except Exception as e:
            logging.error(f"Error in checking NA values: {str(e)}")
            raise Custom_exception(e, sys)

    def find_mode(self, df: DataFrame):
        try:
            df_without_na = df[~df.applymap(lambda x: str(x).strip().lower() == 'na').any(axis=1)]
            cols = df.select_dtypes(include=['object', 'category']).columns
            modes_dict = {}
            for col in cols:
                mode_values = df_without_na[col].mode()
                if not mode_values.empty:
                    modes_dict[col] = mode_values[0]
            return cols, modes_dict
        except Exception as e:
            logging.error(f"Error in calculating replacement values: {str(e)}")
            raise Custom_exception(e, sys)

    def handling_na(self, columns, replacement_value, df: DataFrame, path):
        try:
            logging.info("Replacing 'na' values with mode")
            df = df.replace('na', pd.NA)
            for col in columns:
                if col in df.columns:
                    df[col] = df[col].fillna(replacement_value.get(col, pd.NA))
            logging.info("Successfully replaced 'na' values")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            df.to_csv(path, index=False)
            return df
        except Exception as e:
            logging.error(f"Error in handling NA values: {str(e)}")
            raise Custom_exception(e, sys)

    def clean_data(self):
        try:
            logging.info("Starting data cleaning process")
            df = self.load_data(self.data_cleaner_config.input_path)
            if df.empty:
                logging.info("No files found to clean")
                return df
            self.check_for_na(df)
            cols, replace_value = self.find_mode(df)
            df_cleaned = self.handling_na(columns=cols,
                                          replacement_value=replace_value,
                                          df=df,
                                          path=self.data_cleaner_config.output_path)
            logging.info("Data cleaning process has been completed")
            return df_cleaned
        except Exception as e:
            logging.error(f"Error cleaning data: {str(e)}")
            raise Custom_exception(e, sys)
