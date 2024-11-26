# Web Scraping Tool

This is a Python-based web scraping tool built using **FastAPI**, **BeautifulSoup**, and **Requests**. It scrapes product data from an e-commerce website and saves it locally as a JSON file. The tool also downloads product images and saves them to a designated folder.

---

## Features
- **Scraping Product Data:** Extracts product titles, prices, and image URLs.
- **Caching Mechanism:** Avoids updating products if their price hasn't changed.
- **Image Download:** Saves product images locally in the `images/` directory.
- **Retry Mechanism:** Retries fetching pages in case of server errors.
- **Customizable Configuration:**
  - Limit the number of pages to scrape.
  - Use a proxy for scraping.
- **Authentication:** API endpoint protected by static authentication using an API key.
- **Notifications:** Logs the number of products scraped and updated after each session.

---

## Requirements
- Python 3.8 or higher
- Dependencies listed in `requirements.txt`

---

## Installation

### Clone the Repository
```bash
git clone git@github.com:Shisir99/Web-Scraping.git
cd Web-Scraping
```

### Set Up Environment
Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
### Install Dependencies:
```bash
pip install -r requirements.txt
```
## Usage
Run the FastAPI Server
Start the API server:
```bash
uvicorn main:app --reload
```
The server will run at http://127.0.0.1:8000.

## API Endpoint
### POST /scrape/
Trigger the scraping process.
Request Body
```bash
{
  "max_pages": 2,         // (Optional) Number of pages to scrape (default: 2)
  "proxy": "http://proxy.server:port" // (Optional) Proxy to use for scraping
}
```
Swagger link: http://127.0.0.1:8000/docs#

Example cURL Request
```bash
curl -X POST "http://127.0.0.1:8000/scrape/" \
-H "api-key: qwertyuiop" \
-H "Content-Type: application/json" \
-d '{"max_pages": 3}'
```

## Customization
### Change API Key:
Update the API_KEY in the code:
```bash
API_KEY = "your_new_api_key"
```
### Change Data and Image Paths:
Update these constants in the code:
```bash
DATA_FILE_PATH = "path/to/scraped_data.json"
IMAGE_DIR = "path/to/images"
```




