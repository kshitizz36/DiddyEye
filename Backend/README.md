# FakeInfoDetector Hackathon Project

FakeInfoDetector is an experimental project developed during a hackathon to help verify the authenticity of information. It features two main models: one for text-based claim verification and another for image authenticity detection.

---

## Overview

The project aims to combat misinformation by combining traditional text analysis techniques with modern AI-driven image detection. The two models work independently to assess the credibility of claims and visual content.

- **Model 1: Claim Verification**  
  Uses natural language processing to extract keywords from an input claim, finds credible sources via Google Custom Search, scrapes content from various formats (HTML, XML, PDF), embeds both the claim and the sourced content, and then compares their vector representations to assess reliability.

- **Model 2: Image Authenticity Detection**  
  Provides two services:
  - **AI Detector for Images:** Checks whether a given picture is AI-generated.
  - **URL Verification Service:** Uses AI to validate that the image URL points to a genuine image rather than a manipulated or AI-generated one.

---

## Features

- **Text Claim Verification (Model 1)**
  - **TF-IDF Keyword Extraction:** Identifies key terms from the input claim.
  - **Google Custom Search Integration:** Uses extracted keywords to locate credible online sources.
  - **Content Scraping:** Retrieves text content from various formats (HTML, XML, PDF).
  - **Embedding & Vector Comparison:** Embeds both the claim and scraped content to compare similarity and determine credibility.

- **Image Authenticity Detection (Model 2)**
  - **AI Image Detector:** Analyzes images to determine if they are AI-generated.
  - **URL Validation:** Checks if the provided image URL leads to a genuine image using AI-based verification.

---

## Requirements

- **Programming Language:** Python 3.x
- **Libraries & Tools:**
  - `scikit-learn` (for TF-IDF and vector operations)
  - `requests` (for HTTP requests)
  - `BeautifulSoup4` (for HTML/XML scraping)
  - PDF parsing libraries (e.g., `pdfminer.six` or similar)
  - Pre-trained models or APIs for AI image detection (as applicable)
  - Google Custom Search API client (ensure you have valid API credentials)
- **Other:** Internet connectivity for API requests and content scraping

---

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/FakeInfoDetector.git
   cd FakeInfoDetector
   ```

2. **Install Dependencies:**
   Create a virtual environment (optional but recommended) and install required packages:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. **Set Up API Credentials:**
    - Obtain your Google Custom Search API key and set up a Custom Search Engine.
    - Configure your environment variables or update the configuration file (e.g., `config.json`) with your API credentials.

---

## Usage

### Model 1: Claim Verification

1. **Prepare your input claim text.**
2. **Run the text verification script:**
   ```bash
   python model1/claim_verifier.py --claim "Your input claim here"
   ```
3. **Output:**  
   The script will output the similarity score between the input claim and the scraped content from credible sources, indicating the claim's reliability.

### Model 2: Image Authenticity Detection

1. **For Image AI Detection:**
   ```bash
   python model2/image_detector.py --image_path path/to/your/image.jpg
   ```
2. **For URL Verification:**
   ```bash
   python model2/url_validator.py --url "https://example.com/image.jpg"
   ```
3. **Output:**  
   Each service will return a verdict on whether the image appears to be AI-generated or manipulated.

---

## Project Structure

```
FakeInfoDetector/
├── model1/
│   ├── claim_verifier.py       # Script for text-based claim verification
│   ├── tfidf_extractor.py      # Module for TF-IDF based keyword extraction
│   ├── google_search.py        # Module for interacting with Google Custom Search
│   ├── scraper.py              # Module for scraping HTML, XML, and PDF content
│   └── embedder.py             # Module for embedding and vector comparison
├── model2/
│   ├── image_detector.py       # Service to detect AI-generated images
│   ├── url_validator.py        # Service to validate image URLs
│   └── ai_model.py             # AI model integration for image analysis
├── config/
│   └── config.json             # Configuration file for API keys and parameters
├── requirements.txt            # Python dependencies
└── README.md                   # This readme file
```

---

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your proposed changes. For major changes, open an issue first to discuss what you would like to change.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

## Acknowledgments

- Thanks to the Google Custom Search team for providing a robust API.
- Inspired by the growing need for reliable misinformation detection in today’s digital landscape.
- Special thanks to the hackathon organizers and the developer community for their valuable feedback.

---

*Note: This project is developed for hackathon demonstration purposes. Further improvements and rigorous testing are needed before considering production deployment.*
```