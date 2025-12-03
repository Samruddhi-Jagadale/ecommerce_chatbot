import os 
import sys 

# ✔ you said your file name is still scraper.py
from src.components.scraper import scrape_hunnit_products

from src.utils.logger import logging
from src.utils.exception import Custom_exception

from dataclasses import dataclass


# -------- UPDATE YOUR HUNNIT KEYWORDS HERE --------
products_config = [
    {
        'keyword': 'mens shirts',
        'num_products': 500,
        'file_path': 'hunnit_shirts.csv',
    },
    {
        'keyword': 'sarees',
        'num_products': 500,
        'file_path': 'hunnit_sarees.csv',
    },
    {
        'keyword': 'watches',
        'num_products': 500,
        'file_path': 'hunnit_watches.csv',
    },
]
# --------------------------------------------------


@dataclass
class DataCollectionConfig:
    is_airflow = os.getenv("IS_AIRFLOW", "false").lower() == "true"

    if is_airflow:
        path = '/opt/airflow/data'
    else:
        path = 'data'   


class DataCollection:
    def __init__(self):
        self.data_collection_config = DataCollectionConfig()

    def initiate_data_collection(self):

        try:
            logging.info("Starting multi-product data collection for Hunnit.com")

            successful_products = []
            failed_products = []

            for product in products_config:
                try:
                    logging.info(
                        f"Collecting data for: {product['keyword']} "
                        f"Target: {product['num_products']}"
                    )

                    # ✔ Updated function call (your new scraper function)
                    data = scrape_hunnit_products(
                        keyword=product['keyword'],
                        num_products=product['num_products']
                    )

                    print("Data shape for", product['keyword'], ":", data.shape)
                    print("Sample data:\n", data.head())

                    file_path = os.path.join(self.data_collection_config.path, product['file_path'])
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    data.to_csv(file_path, index=False)

                    successful_products.append(product['keyword'])
                    logging.info(f"Successfully collected and saved: {product['keyword']}")

                except Exception as e:
                    logging.error(f"Failed to collect data for {product['keyword']}: {str(e)}")
                    failed_products.append(product['keyword'])
                    continue  

            logging.info(f"Completed. Success: {len(successful_products)}, Failed: {len(failed_products)}")

            if len(failed_products) == len(products_config):
                raise Exception("All products scraping failed")

            return f"Collected data for {len(successful_products)} of {len(products_config)} products"

        except Exception as e:
            logging.error(f"Error in data collection: {str(e)}")
            raise Custom_exception(e, sys)
