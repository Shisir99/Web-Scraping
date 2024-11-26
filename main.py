from typing import Optional, Dict, List
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import logging
import time
import os
import json

API_KEY = "qwertyuiop"  # Replace with your actual secret key
DATA_FILE_PATH = "scraped_data.json"
IMAGE_DIR = "images"  # Directory to save images

# Simulated in-memory DB
in_memory_db = {}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

class Notifier:
    @staticmethod
    def notify(scraped: int, updated: int):
        message = f"Scraping completed! {scraped} products scraped, {updated} updated."
        logger.info(message)

class Scraper:
    def __init__(self, base_url: str, proxy: Optional[str] = None, max_retries: int = 3, retry_delay: int = 5):
        self.base_url = base_url
        self.proxy = proxy
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def create_session(self) -> requests.Session:
        session = requests.Session()
        retry = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def fetch_page(self, url: str) -> Optional[str]:
        session = self.create_session()
        proxies = {"http": self.proxy, "https": self.proxy} if self.proxy else None

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"Attempt {attempt} to fetch {url}")
                response = session.get(url, proxies=proxies)
                response.raise_for_status()
                logger.info(f"Successfully fetched page: {url}")
                return response.text
            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching {url} on attempt {attempt}: {e}")
                if attempt < self.max_retries:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Failed to fetch {url} after {self.max_retries} attempts.")
        return None

    def extract_product_data(self, page_html: str) -> List[Dict[str, str]]:
        soup = BeautifulSoup(page_html, 'html.parser')
        product_containers = soup.find_all('div', class_='product-inner')

        products = []

        os.makedirs(IMAGE_DIR, exist_ok=True)

        for product in product_containers:
            try:
                title = product.find('h2', class_='woo-loop-product__title').text.strip()
                price_element = product.find('span', class_='woocommerce-Price-amount')

                if price_element:
                    price_text = price_element.text.strip()
                    # Remove currency symbol and commas, then convert to float
                    price = float(price_text.replace('₹', '').replace(',', '').strip())
                else:
                    price = None

                image_element = product.find('img', class_='attachment-woocommerce_thumbnail')
                image_url = image_element.get('data-lazy-src') if image_element else 'Image Not Found'

                # Download the image if URL is valid
                image_path = None
                if image_url != "Image Not Found":
                    image_name = os.path.basename(image_url)
                    image_path = os.path.join(IMAGE_DIR, image_name)
                    try:
                        img_data = requests.get(image_url).content
                        with open(image_path, 'wb') as img_file:
                            img_file.write(img_data)
                        # logger.info(f"Image saved: {image_path}")
                    except Exception as e:
                        logger.error(f"Failed to download image {image_url}: {e}")
                        image_path = None

                products.append({
                    "product_title": title, 
                    "product_price": price, 
                    "path_to_image": image_path
                })
            except Exception as e:
                logger.error(f"Error extracting product: {e}")
        return products

    def scrape(self, max_pages: int) -> Dict[str, int]:
        scraped_count = 0
        updated_count = 0
        all_products = [] 

        for page in range(1, max_pages + 1):
            page_url = f"{self.base_url}/shop/page/{page}/"
            logger.info(f"Scraping page: {page_url}")

            page_html = self.fetch_page(page_url)
            if not page_html:
                logger.warning(f"Skipping page {page_url} due to fetch failure.")
                continue

            products = self.extract_product_data(page_html)
            scraped_count += len(products)
            all_products.extend(products)

            # Update in-memory DB
            for product in products:
                title = product["product_title"]
                if title in in_memory_db and in_memory_db[title]["product_price"] == product["product_price"]:
                    continue  # Skip if price hasn't changed
                in_memory_db[title] = product
                updated_count += 1

        save_to_json_file(all_products)

        return {"scraped": scraped_count, "updated": updated_count}


def save_to_json_file(data: list, file_path: str = DATA_FILE_PATH):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            existing_data = json.load(f)
    else:
        existing_data = []

    # Update the file with new data
    existing_data.extend(data)
    with open(file_path, 'w') as f:
        json.dump(existing_data, f, indent=4)
    logger.info(f"Data saved to {file_path}")


class Authentication:
    @staticmethod
    def validate(api_key: str = Header(...)):
        if api_key != API_KEY:
            raise HTTPException(status_code=401, detail="Unauthorized")
        return api_key


class ScrapingConfig(BaseModel):
    max_pages: Optional[int] = 2
    proxy: Optional[str] = None  # Proxy support


@app.post("/scrape/")
async def scrape_endpoint(config: ScrapingConfig, api_key: str = Depends(Authentication.validate)):
    """Endpoint to trigger the scraping process."""
    scraper = Scraper(base_url="https://dentalstall.com", proxy=config.proxy)
    results = scraper.scrape(config.max_pages)

    # Notify results
    Notifier.notify(scraped=results["scraped"], updated=results["updated"])

    return {
        "message": "Scraping completed successfully.",
        "scraped": results["scraped"],
        "updated": results["updated"]
    }


if __name__ == "__main__":
    scraper = Scraper(base_url="https://dentalstall.com", proxy=None)
    results = scraper.scrape(max_pages=5)
    Notifier.notify(scraped=results["scraped"], updated=results["updated"])
