import requests
from bs4 import BeautifulSoup
from flask import Blueprint, request, jsonify
import io
import PyPDF2
import concurrent.futures

scrape_content_blueprint = Blueprint("scrape_content_blueprint", __name__)


def extract_main_content(url, headers=None):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an error for bad responses (e.g. 404, 500)
        content_type = response.headers.get('Content-Type', '')

        # Process based on content type
        if 'html' in content_type.lower():
            try:
                soup = BeautifulSoup(response.text, "html.parser")
            except Exception as e:
                # If default parser fails, try a different parser
                soup = BeautifulSoup(response.text, "lxml")

            # Try extracting common content elements from news sites
            content_selectors = [
                "article",  # Many sites wrap content in <article> tags
                "div.story-body", "div.post-content",  # BBC, blogs, medium, etc.
                "div.entry-content", "div.article-content", "div.main-content",
                "section.article-body", "div.content__article-body",  # Common structures
                "p"  # Last fallback: Grab all paragraphs
            ]

            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    # Concatenate text from all found elements
                    print("Content scrap successful (HTML)")
                    extracted_text = " ".join([el.get_text(strip=True) for el in elements])
                    if extracted_text:
                        return extracted_text

            return "Main content not found in HTML."

        elif 'xml' in content_type.lower():
            # Process XML content
            soup = BeautifulSoup(response.text, "xml")
            extracted_text = soup.get_text(strip=True)
            if extracted_text:
                print("Content scrap successful (XML)")
                return extracted_text
            else:
                return "Main content not found in XML."

        # PDF branch
        elif 'pdf' in content_type.lower() or url.lower().endswith('.pdf'):
            try:
                pdf_data = io.BytesIO(response.content)
                reader = PyPDF2.PdfReader(pdf_data, strict=False)
                extracted_text = ""
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        extracted_text += text + "\n"
                if extracted_text:
                    print("Content scrap successful (PDF)")
                    return extracted_text
                else:
                    return "Main content not found in PDF."
            except Exception as pdf_error:
                return f"Error processing PDF: {str(pdf_error)}"

        else:
            return f"Content is neither HTML, XML, nor PDF. Detected content type: {content_type}"

    except requests.exceptions.RequestException as e:
        return f"Error retrieving content: {str(e)}"
    except Exception as e:
        return f"Error processing content: {str(e)}"


@scrape_content_blueprint.route("/", methods=["POST"])
def scrape_content():
    """Fetches and extracts the main body of an article from a given URL concurrently."""
    data = request.get_json()
    urls = data.get("results")  # list of dicts: {title: title, url: url, reliability: r}

    return_data = []

    if not urls:
        return jsonify({"error": "No URL data provided"}), 400

    # Use a ThreadPoolExecutor to process URLs concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        # Submit tasks for each URL extraction
        future_to_item = {
            executor.submit(extract_main_content, item.get("url")): item for item in urls if item.get("url")
        }

        for future in concurrent.futures.as_completed(future_to_item):
            item = future_to_item[future]
            try:
                content = future.result()
            except Exception as exc:
                content = f"Error during extraction: {exc}"
            return_data.append({
                "url": item.get("url"),
                "title": item.get("title"),
                "reliability": item.get("reliability"),
                "article_content": content
            })

    return jsonify({"results": return_data})
