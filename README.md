
# Web Scraping Tool

This is a Python-based web scraping tool built using **FastAPI**, **BeautifulSoup**, and **Requests**. It scrapes product data from a website and saves it locally as a JSON file. The tool also downloads product images and saves them to a designated folder.

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
