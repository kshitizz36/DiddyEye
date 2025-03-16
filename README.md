# VerifAI Bot

VerifAI is an AI-driven Telegram bot desgined to combat misinfomration in private messaging apps such as Telegram. Developed for TechFest 2025, VerifAI utilizes Natural Language Processing and AI-Powered image analysis to detect falsehoods

---
## **The Problem**: The Rise of Online Falsehood
65% of adults in Singapore struggle to differentiate between real and fake online content. With false information spreading effortlessly through a single forward button, online falsehoods proliferate at an alarming rate. Meanwhile, existing fact-checking tools remain slow, unreliable, and require tedious manual verification. 

## **Solution**: VerifAI 
VerifAI combats misinformation by providing instant, automated fact-checking directly within Telegram. By combining advanced text analysis with AI-driven image detection, VerifAI independently verifies the credibility of text-based claims and detects AI-generated images, ensuring users can separate fact from fiction in real time.

- **Model 1: Claim Verification**  

  Uses natural language processing to extract keywords from an input claim, finds credible sources via Google Custom Search, scrapes content from various formats (HTML, XML, PDF), embeds both the claim and the sourced content, and then compares their vector representations to assess reliability.
  **Features**:
  - **TF-IDF Keyword Extraction:** Identifies key terms from the input claim.
  - **Google Custom Search Integration:** Uses extracted keywords to locate credible online sources.
  - **Content Scraping:** Retrieves text content from various formats (HTML, XML, PDF).
  - **Embedding & Vector Comparison:** Embeds both the claim and scraped content to compare similarity and determine credibility.
  - **Reliability Score** Provides a reliability score using cosine similarity
  - **Explanation of Reliability Score** Compares top sources with original claim and leverages OpenAI GPT4-o to provide users with an in-depth explanation of reliability score

- **Model 2: AI Generator Image Detector**

  With the rise of AI-generated images and online falsehood, manipulated content are harder to detect. VerifAI allows user to verify images, seperating real images from AI images.
  **Features**:
  - **AI-Genereated Image Detection** Determines whether an image is AI-generate and provides a statistical analysis
  - **Heatmap Visualization** Highlights manipulated areas in AI-generated images for better transparency

---

## Tech Stack 
![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white)
![scikit-learn](https://img.shields.io/badge/-Scikit%20Learn-F7931E?logo=scikit-learn&logoColor=white)
![BeautifulSoup](https://img.shields.io/badge/-BeautifulSoup-009688?logo=beautifulsoup&logoColor=white)
![OpenCV](https://img.shields.io/badge/-OpenCV-5C3EE8?logo=opencv&logoColor=white)
![TensorFlow](https://img.shields.io/badge/-TensorFlow-FF6F00?logo=tensorflow&logoColor=white)
![Pytesseract](https://img.shields.io/badge/-Pytesseract-7F7F7F?logo=tesseract&logoColor=white)
![Google Custom Search API](https://img.shields.io/badge/-Google%20Search%20API-4285F4?logo=google&logoColor=white)
![Telegram API](https://img.shields.io/badge/-Telegram%20API-26A5E4?logo=telegram&logoColor=white)
![OpenAI API](https://img.shields.io/badge/-OpenAI%20API-412991?logo=openai&logoColor=white)
![Flask](https://img.shields.io/badge/-Flask-000000?logo=flask&logoColor=white)
| **Category**                 | **Technology Used**                           |
|------------------------------|----------------------------------------------|
| **Programming Language**     | Python 3.10                                   |
| **Natural Language Processing** | `scikit-learn`, `TF-IDF`    |
| **Web Scraping & Data Extraction** | `BeautifulSoup4` |
| **Image Analysis**        | OpenCV, TensorFlow, Pytesseract              |
| **API Integrations**         | Google Custom Search API, Telegram API, Openai API      |
| **Bot Framework**            | Python Telegram Bot API                      |
| **Deployment**               | Flask             |
---

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/FakeInfoDetector.git
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

*Note: This project was developed as part of TechFest 2025 and is intended for experimental and demonstration purposes. While VerifAI provides real-time verification, it should not be considered a definitive authority on misinformation. Further development and testing are needed before deployment in production environments.*
```
