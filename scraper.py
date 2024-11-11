import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict, Optional, Tuple
from time_utils import parse_detik_datetime

class DetikScraper:
    def __init__(self):
        self.base_url = "https://www.detik.com/search/searchall"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def _make_request(self, url: str, params: Dict) -> Tuple[Optional[requests.Response], Optional[str]]:
        """Make HTTP request with error handling"""
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response, None
        except requests.Timeout:
            return None, "Request timed out"
        except requests.ConnectionError:
            return None, "Connection error"
        except requests.RequestException as e:
            return None, f"Request failed: {str(e)}"

    def _parse_article(self, article_element) -> Tuple[Dict, Optional[str]]:
        """Parse single article element and extract required information"""
        try:
            # Extract title - using media__title as primary source
            title_element = article_element.find("h3", class_="media__title")
            if not title_element or not title_element.a:
                return {}, "Title element not found"
            
            title = title_element.a.text.strip()

            # Extract image URL
            image_element = article_element.find("img")
            image_url = image_element["src"] if image_element and "src" in image_element.attrs else ""

            # Extract body text from media__desc
            body_element = article_element.find("div", class_="media__desc")
            body_text = body_element.text.strip() if body_element else ""

            # Extract and parse publication time
            time_element = article_element.find("div", class_="media__date").find("span")
            pub_time = time_element.text.strip() if time_element else ""
            
            try:
                parsed_date = parse_detik_datetime(pub_time)
                formatted_date = parsed_date.isoformat()
            except ValueError as e:
                formatted_date = None

            return {
                "title": title,
                "image_url": image_url,
                "body_text": body_text,
                "publication_time": formatted_date,
            }, None

        except Exception as e:
            return {}, f"Error parsing article: {str(e)}"

    def search(self, query: str, max_pages: int = 3) -> Tuple[List[Dict], Optional[str]]:
        """
        Search detik.com and retrieve results from specified number of pages
        Returns: Tuple of (results_list, error_message)
        """
        all_results = []
        
        for page in range(1, max_pages + 1):
            params = {
                "query": query,
                "page": page
            }
            
            response, error = self._make_request(self.base_url, params)
            if error:
                return all_results, error

            try:
                soup = BeautifulSoup(response.text, 'html.parser')
            except Exception as e:
                return all_results, f"Error parsing HTML: {str(e)}"
            
            # Find all article elements
            articles = soup.find_all("article", class_="list-content__item")
            
            if not articles:
                break  # No more results found

            # Parse each article
            for article in articles:
                result, error = self._parse_article(article)
                if not error:
                    all_results.append(result)

            # Add delay between requests to be polite
            time.sleep(1)

        if not all_results:
            return [], "No results found"
            
        return all_results, None