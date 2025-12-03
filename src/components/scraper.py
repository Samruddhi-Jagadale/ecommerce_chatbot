# hunnit_scraper.py
import os
import sys
import time
import json
import uuid
import shutil
import pandas as pd
from typing import List, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from src.utils.logger import logging
from src.utils.exception import Custom_exception

def _init_driver(is_airflow: bool):
    """Initialize chrome webdriver with options similar to your Amazon scraper."""
    try:
        chrome_options = Options()
        if is_airflow:
            # airflow container paths
            unique_user_data_dir = f"/tmp/chrome_user_data_{uuid.uuid4()}"
            os.makedirs(unique_user_data_dir, exist_ok=True)
            chrome_options.add_argument(f"--user-data-dir={unique_user_data_dir}")
            chrome_options.binary_location = "/usr/bin/chromium"
            chrome_options.add_argument('--headless=new')
        else:
            unique_user_data_dir = None
            # keep non-headless by default locally so you can debug; caller may add headless flag if desired

        chrome_options.add_argument("--window-size=1920,1080")
        # recommended flags for headless scraping in some environments
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        if is_airflow:
            chromedriver_path = "/usr/bin/chromedriver"
        else:
            # change this path to your local chromedriver path
            chromedriver_path = "F:/Data Science/Projects/4.Ecommerce-Chatbot-Project/chromedriver.exe"

        driver = webdriver.Chrome(service=Service(chromedriver_path), options=chrome_options)
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        return driver, unique_user_data_dir
    except Exception as e:
        logging.error(f"Error initializing Chrome driver: {e}")
        raise

def _safe_get(driver, url):
    """Navigate to url with fallback."""
    try:
        driver.get(url)
    except Exception:
        try:
            driver.execute_script(f"window.location.href = '{url}';")
            time.sleep(2)
        except Exception as e:
            raise

def _extract_json_from_product_page(driver) -> Dict[str, Any]:
    """
    Extract product data from product detail page.
    Priority:
      1) script[type="application/json" and id startswith ProductJson-] -> parse JSON
      2) script[type="application/ld+json"] -> parse schema.org (fallback/additional)
    Returns combined dictionary with keys we care about.
    """
    result = {}
    try:
        # 1) ProductJson script (Shopify product JSON)
        try:
            prod_json_script = driver.find_element(By.XPATH, "//script[starts-with(@id, 'ProductJson-') and @type='application/json']")
            prod_json_text = prod_json_script.get_attribute("innerHTML").strip()
            if prod_json_text:
                prod = json.loads(prod_json_text)
                result['title'] = prod.get('title') or prod.get('name')
                # Shopify prices are often in paise; check magnitude and adjust if needed
                price_val = prod.get('price') or prod.get('price_min') or prod.get('price_max')
                if isinstance(price_val, (int, float)):
                    # heuristic: if value looks like paise (e.g., 149900) convert to rupees
                    if price_val > 10000:
                        result['price'] = price_val / 100.0
                    else:
                        result['price'] = price_val
                else:
                    result['price'] = price_val

                result['compare_at_price'] = prod.get('compare_at_price') or prod.get('compare_at_price_min')
                result['description'] = prod.get('description')
                result['vendor'] = prod.get('vendor')
                result['category'] = prod.get('type')
                result['tags'] = prod.get('tags', [])
                result['variants'] = prod.get('variants', [])
                result['handle'] = prod.get('handle')
                # images from product JSON
                images = []
                if isinstance(prod.get('images'), list) and prod.get('images'):
                    images = [img for img in prod.get('images')]
                # sometimes featured_media / featured_image exist
                if not images and prod.get('featured_image'):
                    src = prod['featured_image'].get('src')
                    if src:
                        images = [src]
                result['image_urls'] = images
        except NoSuchElementException:
            logging.info("No ProductJson script found on this page")

        # 2) schema.org JSON-LD (useful for standardized fields)
        try:
            ld_script = driver.find_element(By.XPATH, "//script[@type='application/ld+json']")
            ld_text = ld_script.get_attribute("innerHTML").strip()
            if ld_text:
                # sometimes there are multiple JSON objects/arrays; wrap safely
                parsed = json.loads(ld_text)
                # parsed could be a dict or list
                if isinstance(parsed, dict):
                    parsed_list = [parsed]
                else:
                    parsed_list = parsed

                for obj in parsed_list:
                    if obj.get('@type') and obj.get('@type').lower() == 'product':
                        # overwrite or fill missing fields
                        result.setdefault('title', obj.get('name'))
                        result.setdefault('description', obj.get('description'))
                        result.setdefault('image_urls', obj.get('image') if isinstance(obj.get('image'), list) else [obj.get('image')] if obj.get('image') else [])
                        # offers may contain price info
                        offers = obj.get('offers')
                        if offers:
                            # offers can be list or dict
                            if isinstance(offers, list):
                                first_offer = offers[0]
                            else:
                                first_offer = offers
                            price = first_offer.get('price')
                            if price:
                                # numeric or string
                                try:
                                    price_f = float(price)
                                    result.setdefault('price', price_f)
                                except Exception:
                                    result.setdefault('price', price)
                            result.setdefault('availability', first_offer.get('availability'))
                # fallback brand
                if isinstance(parsed_list[0], dict) and parsed_list[0].get('brand'):
                    brand = parsed_list[0]['brand'].get('name') if isinstance(parsed_list[0]['brand'], dict) else parsed_list[0]['brand']
                    result.setdefault('vendor', brand)
        except NoSuchElementException:
            logging.info("No ld+json script found on this page")

        # 3) Fallback selectors for description / features present on the page
        try:
            # common Hunnit feature list class observed in HTML: ul.m-key-features
            features_elems = driver.find_elements(By.CSS_SELECTOR, "ul.m-key-features li")
            if features_elems:
                features = [f.text.strip() for f in features_elems if f.text.strip()]
                if features:
                    result.setdefault('features', features)
        except Exception:
            pass

        # 4) Guarantee/normalize fields
        result.setdefault('title', result.get('title', 'na'))
        result.setdefault('description', result.get('description', 'na'))
        result.setdefault('image_urls', result.get('image_urls', []))
        result.setdefault('price', result.get('price', 'na'))
        result.setdefault('category', result.get('category', 'na'))
        result.setdefault('vendor', result.get('vendor', 'na'))
        result.setdefault('variants', result.get('variants', []))
        result.setdefault('tags', result.get('tags', []))

        return result
    except Exception as e:
        logging.error(f"Error extracting JSON from product page: {e}")
        raise

def scrape_hunnit_products(keyword: str, num_products: int = 50) -> pd.DataFrame:
    """
    Scrape Hunnit.com for a keyword and return a DataFrame with one row per product/SKU.
    Each row will include: Title, Price, Description, Features, Image URLs, Category, Vendor, Tags,
    Variants, SKU (if variant-level), Compare price, Availability, Product URL
    """
    driver = None
    unique_user_data_dir = None
    try:
        is_airflow = os.getenv("IS_AIRFLOW", "false").lower() == 'true'
        logging.info(f"Running in {'Airflow' if is_airflow else 'local'} environment")

        driver, unique_user_data_dir = _init_driver(is_airflow)

        base_search_url = f"https://hunnit.com/search?q={keyword.replace(' ', '+')}"
        logging.info(f"Searching Hunnit: {base_search_url}")

        _safe_get(driver, base_search_url)
        time.sleep(2)

        # find product links on search results: anchor tags containing '/products/'
        product_links = []
        anchors = driver.find_elements(By.XPATH, "//a[contains(@href, '/products/')]")
        for a in anchors:
            try:
                href = a.get_attribute("href")
                # simple dedupe and ensure link is product page
                if href and '/products/' in href and href not in product_links:
                    product_links.append(href)
            except Exception:
                continue

        logging.info(f"Found {len(product_links)} product links on search results")

        data_rows = []
        visited = 0

        for product_url in product_links:
            if visited >= num_products:
                break
            try:
                logging.info(f"Visiting product: {product_url}")
                _safe_get(driver, product_url)
                time.sleep(1.5)  # allow page JS to populate

                extracted = _extract_json_from_product_page(driver)

                # If variants exist, create one row per variant (SKU-level) — as user requested SKU-level
                variants = extracted.get('variants') or []
                if variants:
                    for var in variants:
                        if visited >= num_products:
                            break
                        row = {
                            "Title": extracted.get('title'),
                            "Price": (var.get('price') or extracted.get('price')),
                            "CompareAtPrice": var.get('compare_at_price') or extracted.get('compare_at_price'),
                            "SKU": var.get('sku') or var.get('id'),
                            "VariantTitle": var.get('title'),
                            "VariantOptions": var.get('options'),
                            "Description": extracted.get('description'),
                            "Features": extracted.get('features', []),
                            "ImageURLs": extracted.get('image_urls'),
                            "Category": extracted.get('category'),
                            "Vendor": extracted.get('vendor'),
                            "Tags": extracted.get('tags'),
                            "Availability": var.get('available') if 'available' in var else extracted.get('availability'),
                            "ProductURL": product_url
                        }
                        data_rows.append(row)
                        visited += 1
                else:
                    # no variants: one row per product
                    if visited < num_products:
                        row = {
                            "Title": extracted.get('title'),
                            "Price": extracted.get('price'),
                            "CompareAtPrice": extracted.get('compare_at_price'),
                            "SKU": None,
                            "VariantTitle": None,
                            "VariantOptions": None,
                            "Description": extracted.get('description'),
                            "Features": extracted.get('features', []),
                            "ImageURLs": extracted.get('image_urls'),
                            "Category": extracted.get('category'),
                            "Vendor": extracted.get('vendor'),
                            "Tags": extracted.get('tags'),
                            "Availability": extracted.get('availability'),
                            "ProductURL": product_url
                        }
                        data_rows.append(row)
                        visited += 1

            except Exception as e:
                logging.error(f"Error scraping product {product_url}: {e}")
                continue

        df = pd.DataFrame(data_rows)
        logging.info(f"Scraped total {len(df)} rows")
        return df

    except Exception as e:
        logging.error(f"Error in scrape_hunnit_products: {e}")
        raise Custom_exception(e, sys)

    finally:
        if driver is not None:
            try:
                driver.quit()
                logging.info("Chrome driver closed successfully")
            except Exception as cleanup_error:
                logging.error(f"Error closing driver: {cleanup_error}")

        if unique_user_data_dir and os.path.exists(unique_user_data_dir):
            try:
                shutil.rmtree(unique_user_data_dir, ignore_errors=True)
                logging.info("Temporary directory cleaned up")
            except Exception as cleanup_error:
                logging.info(f"Error cleaning temp directory: {cleanup_error}")
