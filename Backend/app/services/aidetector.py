import requests
import os
import argparse
from urllib.parse import urlparse
from dotenv import load_dotenv
load_dotenv()

# Your API key from AIORNOT 
AIorNOT_KEY = os.getenv("AIORNOT_KEY")

# Base URL for the API
BASE_URL = "https://api.aiornot.com/v1"

# Headers for authentication
headers = {
    "Authorization": f"Bearer {AIorNOT_KEY}",
    "Accept": "application/json"
}

def is_url(string):
    """
    Check if a string is a valid URL
    
    Args:
        string (str): The string to check
        
    Returns:
        bool: True if string is a URL, False otherwise
    """
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except:
        return False

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

def check_voice_file(file_path):
    """
    Check if an audio file contains AI-generated voice
    
    Args:
        file_path (str): Path to the local audio file
        
    Returns:
        dict: API response with analysis results
    """
    endpoint = f"{BASE_URL}/reports/voice"
    
    # Set content type for multipart/form-data
    form_headers = headers.copy()
    
    # Get file extension to determine mime type
    file_extension = os.path.splitext(file_path)[1].lower()
    
    # Map common audio extensions to MIME types
    mime_types = {
        '.mp3': 'audio/mp3',
        '.wav': 'audio/wav',
        '.m4a': 'audio/m4a',
        '.ogg': 'audio/ogg',
        '.flac': 'audio/flac'
    }
    
    mime_type = mime_types.get(file_extension, 'audio/mp3')
    
    print(f"Analyzing audio file: {file_path}")
    
    # Prepare the file
    try:
        with open(file_path, 'rb') as audio_file:
            files = {
                'file': (os.path.basename(file_path), audio_file, mime_type)
            }
            
            # Make the API call (with longer timeout as per docs)
            response = requests.post(endpoint, headers=form_headers, files=files, timeout=90)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Extract usage information from headers
            usage = response.headers.get('X-API-USAGE')
            quota = response.headers.get('X-API-QUOTA-LIMIT')
            duration = response.headers.get('X-API-DURATION')
            
            if usage and quota:
                print(f"API Usage: {usage}/{quota}")
            if duration:
                print(f"Audio Duration: {duration} seconds")
                
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

def auto_detect_and_check(input_str):
    """
    Automatically detect if the input is a URL or file path and check accordingly
    
    Args:
        input_str (str): URL or file path to analyze
        
    Returns:
        dict: API response with analysis results
    """
    # Check if the input is a URL
    if is_url(input_str):
        return check_image_url(input_str)
    
    # If not a URL, check if it's a file
    if not os.path.exists(input_str):
        print(f"Error: The input '{input_str}' is not a valid URL or existing file path.")
        return None
        
    # Determine file type based on extension
    file_extension = os.path.splitext(input_str)[1].lower()
    
    # Audio file extensions
    audio_extensions = ['.mp3', '.wav', '.m4a', '.ogg', '.flac']
    
    # Image file extensions
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.apng']
    
    if file_extension in audio_extensions:
        return check_voice_file(input_str)
    elif file_extension in image_extensions:
        return check_image_file(input_str)
    else:
        print(f"Error: Unsupported file type '{file_extension}'.")
        print("Supported image types: .jpg, .jpeg, .png, .gif, .webp, .svg, .apng")
        print("Supported audio types: .mp3, .wav, .m4a, .ogg, .flac")
        return None

def display_results(result, input_type):
    """
    Display API results in a user-friendly format
    
    Args:
        result (dict): API response
        input_type (str): Type of input ('image' or 'voice')
    """
    if not result:
        return
    
    print("\n===== AIORNOT ANALYSIS RESULTS =====")
    
    if input_type == 'image':
        verdict = result["report"]["verdict"]
        print(f"Verdict: {verdict.upper()}")
        
        # Check if this is from a paid subscription with detailed results
        if "confidence" in result["report"].get("ai", {}):
            ai_confidence = result["report"]["ai"]["confidence"]
            human_confidence = result["report"]["human"]["confidence"]
            print(f"AI confidence: {ai_confidence:.2%}")
            print(f"Human confidence: {human_confidence:.2%}")
            
            # Check specific AI generators if available
            if "generator" in result["report"]:
                print("\nAI Generator Analysis:")
                for generator, details in result["report"]["generator"].items():
                    generator_name = generator.replace("_", " ").title()
                    confidence = details["confidence"]
                    is_detected = details["is_detected"]
                    
                    status = "DETECTED" if is_detected else "Not Detected"
                    print(f"  {generator_name}: {status} (confidence: {confidence:.2%})")
        
        # Display facets
        if "facets" in result:
            print("\nImage Quality Checks:")
            for facet, details in result["facets"].items():
                is_detected = details["is_detected"]
                status = "PASS" if (facet == "quality" and is_detected) or (facet == "nsfw" and not is_detected) else "FAIL"
                
                if facet == "quality":
                    print(f"  Image Quality: {status}")
                elif facet == "nsfw":
                    nsfw_status = "Not Detected" if not is_detected else "Detected"
                    print(f"  NSFW Content: {nsfw_status}")
    
    elif input_type == 'voice':
        verdict = result["report"]["verdict"]
        confidence = result["report"].get("confidence", 0)
        duration = result["report"].get("duration", 0)
        
        print(f"Verdict: {verdict.upper()}")
        print(f"Confidence: {confidence:.2%}")
        print(f"Audio Duration: {duration} seconds")
    
    print(f"Report ID: {result['id']}")
    print(f"Created At: {result['created_at']}")
    print("====================================")

def interactive_mode():
    """
    Run the program in interactive mode
    """
    print("==== AIORNOT API Detector ====")
    print("This program checks if content is AI-generated or human-created.")
    
    while True:
        input_str = input("\nEnter a URL or file path (or 'q' to quit): ").strip()
        
        if input_str.lower() in ('q', 'quit', 'exit'):
            break
            
        if not input_str:
            continue
            
        result = auto_detect_and_check(input_str)
        
        # Determine if it's an image or voice result
        if result:
            if "verdict" in result["report"] and isinstance(result["report"]["verdict"], str):
                input_type = 'voice' if "confidence" in result["report"] else 'image'
                display_results(result, input_type)

def main():
    """
    Main function to handle command-line arguments or run in interactive mode
    """
    parser = argparse.ArgumentParser(description='Check if content is AI-generated using AIORNOT API')
    parser.add_argument('input', nargs='?', help='URL or file path to check')
    parser.add_argument('--key', help='AIORNOT API key (overrides the default)')
    
    args = parser.parse_args()
    
    # Override API key if provided
    if args.key:
        global headers
        headers["Authorization"] = f"Bearer {args.key}"
    
    # If no input is provided, run in interactive mode
    if not args.input:
        interactive_mode()
    else:
        result = auto_detect_and_check(args.input)
        
        if result:
            input_type = 'voice' if "confidence" in result["report"] else 'image'
            display_results(result, input_type)

if __name__ == "__main__":
    main()