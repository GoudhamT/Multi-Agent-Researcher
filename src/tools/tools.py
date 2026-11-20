
from tavily import TavilyClient
from langchain.tools import tool
from backend.config.settings import settings
import requests
import trafilatura
import re

from bs4 import BeautifulSoup
from readability import Document
from urllib.parse import urlparse
client = TavilyClient(api_key=settings.TAVILY_API_KEY)


@tool
def tavily_search(query: str) -> list[dict]:
    """
    Search the web using Tavily and return the top 5 results.
    Each result includes URL, title, and the first 300 words of content.
    """

    response = client.search(
        query=query,
        max_results=5,
        search_depth="advanced"
    )

    extracted_results = []

    for result in response.get("results", []):
        content = result.get("content", "")

        # Limit content to first 300 words
        content = " ".join(content.split()[:300])

        extracted_results.append({
            "url": result.get("url"),
            "title": result.get("title"),
            "content": content
        })

    return extracted_results

@tool
def extract_webpage_content(url: str) -> str:
    """
    Extract readable main content from a webpage using its URL.

    Args:
        url: The webpage URL to extract content from.

    Returns:
        Extracted webpage text or an appropriate error message.
    """

    # Step 1: Validate URL
    try:
        parsed_url = urlparse(url)

        if parsed_url.scheme not in ("http", "https") or not parsed_url.netloc:
            return "Error: Invalid URL. Please provide a valid HTTP or HTTPS URL."

        # Step 2: Load webpage
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
            )
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        html_content = response.text

        if not html_content.strip():
            return "Error: The webpage returned empty content."

        # Step 3: Extract using Trafilatura
        content = trafilatura.extract(
            html_content,
            include_links=False,
            include_images=False,
            favor_precision=True
        )

        # Step 4: Fallback to Readability
        if not content or len(content.strip()) < 100:
            document = Document(html_content)
            readable_html = document.summary()

            soup = BeautifulSoup(readable_html, "html.parser")
            content = soup.get_text(separator=" ", strip=True)

        # Step 5: Fallback to BeautifulSoup
        if not content or len(content.strip()) < 100:
            soup = BeautifulSoup(html_content, "html.parser")

            # Remove unwanted HTML elements
            for element in soup([
                "script",
                "style",
                "nav",
                "header",
                "footer",
                "aside",
                "form"
            ]):
                element.decompose()

            content = soup.get_text(separator=" ", strip=True)

        # Step 6: Clean extracted text
        if not content or not content.strip():
            return "Error: Unable to extract readable content from this webpage."

        content = re.sub(r"\s+", " ", content).strip()

        return content

    except requests.exceptions.Timeout:
        return f"Error: Request timed out while loading {url}."

    except requests.exceptions.HTTPError as e:
        return f"Error: HTTP error while loading webpage: {e}"

    except requests.exceptions.ConnectionError:
        return f"Error: Unable to connect to webpage: {url}"

    except requests.exceptions.RequestException as e:
        return f"Error: Failed to load webpage: {str(e)}"

    except Exception as e:
        return f"Error: Content extraction failed: {str(e)}"
