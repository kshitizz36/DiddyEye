import requests
import os
from collections import Counter
from tf_idf import tf_idf_keywords  # Import your TF-IDF function

# Can ignore this, google fact checking is unreliable

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# List of highly trusted sources ranked by credibility
HIGH_CREDIBILITY_SOURCES = [
    "factcheck.org", "snopes.com", "politifact.com", "fullfact.org"
]

def google_fact_check(query):
    """Searches Google Fact Check API and returns a final verdict with ONE highly credible source."""
    if not GOOGLE_API_KEY:
        return "Error: Google API Key is missing."

    # Extract keywords dynamically
    keywords = tf_idf_keywords(query)
    if not keywords:
        return "Error: No significant keywords extracted for fact-checking."

    search_query = " ".join(keywords)

    # Call Google Fact Check API
    url = f"https://factchecktools.googleapis.com/v1alpha1/claims:search?query={search_query}&key={GOOGLE_API_KEY}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        verdicts = []
        sources = []

        if "claims" in data:
            for claim in data["claims"]:
                fact_text = claim.get("text", "No summary available.")
                reviewer = claim["claimReview"][0]["publisher"]["name"]
                review_url = claim["claimReview"][0].get("url", "")  # Ensure URL is present
                rating = claim["claimReview"][0].get("textualRating", "No rating provided.")

                if review_url:  # Only add sources with valid URLs
                    sources.append({
                        "reviewer": reviewer,
                        "rating": rating,
                        "fact_text": fact_text,
                        "url": review_url
                    })
                
                verdicts.append(rating)  # Collect all verdicts

        if not verdicts:
            return "No fact-check found."

        # Step 1: Determine the most common verdict
        final_verdict = Counter(verdicts).most_common(1)[0][0]

        # Step 2: Select ONE highly credible source
        best_source = None
        for source in sources:
            print("DEBUG: Checking source structure -->", source)  # Debugging line
            for domain in HIGH_CREDIBILITY_SOURCES:
                if domain in source.get("url", ""):  # Use .get() to prevent KeyError
                    best_source = source
                    break
            if best_source:
                break  # Stop once we find a top-tier source

        # Step 3: Format and return result
        if best_source:
            return (
                f"**Verdict:** {final_verdict}\n"
                f"**Source:** {best_source['reviewer']}\n"
                f"**Fact:** {best_source['fact_text']}\n"
                f"**Read more:** [{best_source['url']}]({best_source['url']})"
            )
        else:
            return f"**Verdict:** {final_verdict}\n No high-credibility source found."

    except requests.exceptions.RequestException as e:
        return f"API Request Error: {e}"

# Example usage
if __name__ == "__main__":
    user_claim = input("Enter a claim to fact-check: ")
    result = google_fact_check(user_claim)
    print(result)
