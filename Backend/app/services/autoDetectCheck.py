import requests
import os
import argparse
from urllib.parse import urlparse
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("AIorNOT_KEY")

# Base URL for the API
BASE_URL = "https://api.aiornot.com/v1"

# Headers for authentication
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json"
}

def is_url(string):
    """
    Check if a string is a valid URL.
    Args:
        string (str): The string to check.
    Returns:
        bool: True if string is a URL, False otherwise.
    """
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def auto_detect_and_check(input_str):
    """
    Automatically detect whether the input is a URL or a file path and check it
    using the AIORNOT API. It supports image and audio files.

    Args:
        input_str (str): A URL or file path to analyze.

    Returns:
        dict: The API response with analysis results, or None if input is invalid.
    """
    # If the input is a valid URL, assume it's an image URL and check it.
    if is_url(input_str):
        return check_image_url(input_str)

    # If it's not a URL, ensure that the file exists on disk.
    if not os.path.exists(input_str):
        print(f"Error: The input '{input_str}' is not a valid URL or an existing file path.")
        return None

    # Determine file type based on the extension.
    file_extension = os.path.splitext(input_str)[1].lower()
    # Define supported audio and image extensions.
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.apng']

    if file_extension in image_extensions:
        return check_image_file(input_str)
    else:
        print(f"Error: Unsupported file type '{file_extension}'.")
        print("Supported image types: " + ", ".join(image_extensions))
        return None


# Dummy implementations of the API functions for context.
# Replace these with your actual implementations.
def check_image_url(image_url):
    """
    Check if an image from a URL is AI-generated

    Args:
        image_url (str): URL of the image to analyze

    Returns:
        dict: API response with analysis results
    """
    endpoint = f"{BASE_URL}/reports/image"

    # JSON payload for URL-based check
    payload = {
        "object": image_url
    }

    # Set content type for JSON
    json_headers = headers.copy()
    json_headers["Content-Type"] = "application/json"

    print(f"Analyzing image from URL: {image_url}")

    # Make the API call
    response = requests.post(endpoint, headers=json_headers, json=payload)

    # Check if the request was successful
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


def check_image_file(file_path):
    """
    Check if an image file is AI-generated

    Args:
        file_path (str): Path to the local image file

    Returns:
        dict: API response with analysis results
    """
    endpoint = f"{BASE_URL}/reports/image"

    # Set content type for multipart/form-data
    form_headers = headers.copy()

    # Get file extension to determine mime type
    file_extension = os.path.splitext(file_path)[1].lower()

    # Map common image extensions to MIME types
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.svg': 'image/svg+xml',
        '.apng': 'image/apng'
    }

    mime_type = mime_types.get(file_extension, 'image/jpeg')

    print(f"Analyzing image file: {file_path}")

    # Prepare the file
    try:
        with open(file_path, 'rb') as image_file:
            files = {
                'object': (os.path.basename(file_path), image_file, mime_type)
            }

            # Make the API call
            response = requests.post(endpoint, headers=form_headers, files=files)

        # Check if the request was successful
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None
    except FileNotFoundError:
        print(f"Error: File not found - {file_path}")
        return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

# Example usage:
if __name__ == "__main__":
    # Example with a URL:
    result_url = auto_detect_and_check("https://example.com/sample_image.jpg")
    print("Result from URL:", result_url)

    # Example with a local file (adjust the path to one that exists on your system):
    result_file = auto_detect_and_check("local_image.jpg")
    print("Result from file:", result_file)
