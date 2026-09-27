import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass


class ScraperError(RuntimeError):
    """Raised when a target page cannot be fetched or parsed."""


@dataclass
class ScrapedData:
    """Useful page data passed from the scraper to the email generator."""

    url: str
    text: str
    title: str
    description: str
    headings: list[str]


def scrape_website(url: str) -> ScrapedData:
    """
    Scrapes the text content from a given URL.
    Returns visible text and common page metadata from the target.
    """
    # We use a user-agent header to pretend we are a real browser.
    # This helps avoid getting blocked by some websites.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Send an HTTP GET request to the URL
        if not url or not url.strip():
            raise ScraperError("A target URL is required.")

        response = requests.get(url.strip(), headers=headers, timeout=10)
        
        # Check if the request was successful (status code 200)
        response.raise_for_status()
        
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove non-content elements before extracting text.
        for script in soup(["script", "style"]):
            script.extract()
            
        # Extract the text from the parsed HTML
        text = soup.get_text(separator=' ', strip=True)
        
        # Clean up the text by removing extra spaces
        # We split the text into words and join them back with a single space
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        title = soup.title.get_text(" ", strip=True) if soup.title else ""
        description_tag = soup.find("meta", attrs={"name": "description"})
        description = description_tag.get("content", "").strip() if description_tag else ""
        headings = [heading.get_text(" ", strip=True) for heading in soup.find_all(["h1", "h2", "h3"])]

        if not text:
            raise ScraperError("The page returned no readable text.")

        return ScrapedData(
            url=response.url,
            text=text,
            title=title,
            description=description,
            headings=headings,
        )
        
    except requests.exceptions.RequestException as e:
        raise ScraperError(f"Could not fetch the target page: {e}") from e
    except ScraperError:
        raise
    except Exception as e:
        raise ScraperError(f"Could not parse the target page: {e}") from e
