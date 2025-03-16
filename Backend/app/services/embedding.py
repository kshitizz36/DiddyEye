import json

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch
import torch.nn.functional as F


modelname = "cardiffnlp/twitter-roberta-base-sentiment"
tokenizer = AutoTokenizer.from_pretrained(modelname)
model = AutoModelForSequenceClassification.from_pretrained(modelname)

from flask import Blueprint, request, jsonify
from app.database.sql import DatabaseAccess
from app.database import sql

embedding_blueprint = Blueprint("embedding_blueprint", __name__)


model1 = SentenceTransformer("all-MiniLM-L12-v2")
model2 = SentenceTransformer("all-mpnet-base-v2")
model3 = SentenceTransformer("paraphrase-mpnet-base-v2")
model4 = SentenceTransformer("all-MiniLM-L6-v2")
q=True
def embed_text(text,model):
    """
    Converts raw text into a dense vector embedding using a SentenceTransformer model.
    """

    return model.encode(text, convert_to_numpy=True)

def get_sentiment_vector(text):
    """Returns the probability distribution over sentiment classes."""
    if not isinstance(text, str):
        text = str(text)  # Convert non-string inputs to string
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        logits = model(**inputs).logits
    probabilities = F.softmax(logits, dim=-1).squeeze().tolist()
    return probabilities  # [prob_negative, prob_neutral, prob_positive]

def compute_similarity(text_vec, article_vec):
    """
    Computes cosine similarity and transforms it into a probability score using sigmoid.
    """
    cosine_sim = float(cosine_similarity([text_vec], [article_vec])[0][0])

    return cosine_sim


@embedding_blueprint.route("/", methods=["POST"])
def compute_credibility_score():
    """
    Given the input_text and a list of articles (dict: {'content', 'reliability'}),
    returns a final credibility score.

    articles_info = [
       {
          'content': 'Full text of the scraped article...',
          'reliability': 1 or -1
       },
       ...
    ]
    """
    # 1) Embed the input text (user claim)
    data = request.get_json()
    _ = data.get("article_info")  # list of {title : title, url:url, reliability: r}
    input_text = data.get("input_text")

    claim_vec1 = embed_text(input_text,model1)
    claim_vec2 = embed_text(input_text,model2)
    claim_vec3 = embed_text(input_text, model3)
    claim_vec4 = embed_text(input_text, model4)
    claim_vec5 = get_sentiment_vector(input_text)
    total_score = 0

    embedding_list = claim_vec1.tolist()
    embedding_json = json.dumps(embedding_list)
    db_connector = DatabaseAccess()


    if not _:
        return jsonify({"credibility_score": total_score})

    similarities = []  # store tuples of (similarity, url)

    for article in _:
        url = article.get("url")
        title = article.get("title")
        article_content = article.get("article_content", "")

        if not article_content:
            continue

        article_vec1 = embed_text(article_content,model1)
        article_vec2 = embed_text(article_content,model2)
        article_vec3 = embed_text(article_content,model3)
        article_vec4 = embed_text(article_content,model4)

        sim1 = compute_similarity(claim_vec1, article_vec1)
        sim2 = compute_similarity(claim_vec2, article_vec2)
        sim3 = compute_similarity(claim_vec3, article_vec3)
        sim4 = compute_similarity(claim_vec4, article_vec4)
        sim5 = compute_similarity(claim_vec5, get_sentiment_vector(claim_vec5))
        medium_sim = sorted([sim1, sim2, sim3])[1]
        lowest = min(sim1, sim2, sim3, sim4)

        mean_sim = (sim1+sim2+sim3+sim4 - lowest) /3

        k = 10  # Adjust steepness
        t = 0.62  # Midpoint of transformation
        mean_sim = 1 / (1 + np.exp(-k * (mean_sim - t)))
        if mean_sim > 0.6:
            mean_sim += 0.08
        elif mean_sim < 0.4:
            mean_sim -= 0.10
        elif mean_sim < 0.6:
            mean_sim -= 0.15

        similarities.append((mean_sim, url,title))

    if not similarities:
        return jsonify({
            "average_score": 0,
            "highest_score": 0,
            "lowest_score": 0,
            "supporting_article": None,
            "challenging_article": None,
            "top_articles": [],
            "message": "No valid articles with content."
        })

    # Sort articles by similarity descending (highest first)
    similarities.sort(key=lambda x: x[0], reverse=True)

    db_connector.insert_data(input_text, similarities[0][0],similarities[0][1],embedding_json)
    # Calculate average, highest and lowest scores
    scores_only = [s[0] for s in similarities]
    highest_score = max(scores_only)
    lowest_score = min(scores_only)
    average_score = sum(scores_only) / len(scores_only)

    # Get the top 2 articles (or fewer if less than 2)

    top_2 = similarities[:2]

    # The best supporting article is the one with the highest similarity
    supporting_article = similarities[0][1]
    # The most "challenging" article is the one with the lowest similarity
    challenging_article = similarities[-1][1]


    response_data = {
        "average_score": average_score,
        "highest_score": highest_score,
        "lowest_score": lowest_score,
        "supporting_article": supporting_article,
        "challenging_article": challenging_article,
        "top_articles": [
            {"similarity": sim, "url": url} for sim, url,_ in top_2
        ]
    }




    return jsonify(response_data)


if __name__ == "__main__":
    import requests
    data = {
        "input_text": "COVID-19 vaccines are effective and safe.",  # Example input text
        "article_info": [
            {
                "url": "https://example.com/article1",
                "article_content": "Scientific studies confirm that COVID-19 vaccines significantly reduce severe cases.",
                "reliability": 1
            },
            {
                "url": "https://example.com/article2",
                "article_content": "There are still ongoing debates on the long-term effects of vaccines.",
                "reliability": -1
            }
        ]
    }
    response = requests.post("http://127.0.0.1:5050/embedding", json=data)
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())