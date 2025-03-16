import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import re


from nltk.corpus import stopwords
from flask import Blueprint, request, jsonify

def __basic_tokenisation(text):
    sentences = re.split('[.!?]', text)
    return sentences


def __dynamic_max_df(sentences, base_threshold=0.85, min_threshold=0.5):
    num_sentences = len(sentences)

    if num_sentences <= 5:
        return 1.0  # Ignore common word filtering for very short texts
    elif num_sentences <= 10:
        return max(base_threshold, 0.95)  # Allow frequent words more
    else:
        return max(min_threshold, base_threshold - (num_sentences * 0.01))  # Reduce max_df dynamically


def __remove_redundant_keywords(keywords, redundancy_threshold=15):
    """
    with TF-IDF and allowing bigrams, we get output like "money account" and "account" in the same result
    so we remove "account" and "money" from keywords
    """
    if len(keywords) <= redundancy_threshold:
        return keywords
    
    keywords = [re.sub(r'[^a-zA-Z0-9\s]', '', kw).strip() for kw in keywords]

    keywords = sorted(keywords, key=len, reverse=True)  # Sort by length (longest first)
    unique_keywords = []

    for keyword in keywords:
        if not any(keyword in longer_kw for longer_kw in unique_keywords):
            unique_keywords.append(keyword)

    return unique_keywords

def __stop_words_removing_processor(sentences):
    """
    Parses input manually without using tf-idf;
    used for small input by users.
    Excludes stop words and words that contain numbers.
    """
    pre_tf_idf_keywords = []
    #stop_words = set(stopwords.words('english'))

    for sentence in sentences:
        words = sentence.split()
        filtered_words = [
            word.lower() for word in words
          #  if word.lower() not in stop_words and not any(char.isdigit() for char in word)
        ]
        pre_tf_idf_keywords.append(filtered_words)
    return pre_tf_idf_keywords

def tf_idf_keywords(user_text,redundancy_threshold=15):
    """
    used to find keywords in user text of the news. will return highlighted keywords.
    """
    # Tokenize into sentences
    sentences = __basic_tokenisation(user_text)  # split into words
    if len(sentences) >= 1:
        extracted = __stop_words_removing_processor(sentences)

    else:
        print(sentences)
        extracted = [[word.lower() for word in sentences]]
    all_top_words = set()
    print("stopwords at work")

    for sentence in extracted:
        all_top_words.update(word for word in sentence)

    if len(sentences) > 1:

        max_df = __dynamic_max_df(sentences)
        # Use TF-IDF to identify important sentences
        vectorizer = TfidfVectorizer(
            stop_words="english",
            token_pattern=r"(?u)\b[A-Za-z0-9]{3,}\b",  # Ignores numbers and short words (<3 letters)
            ngram_range=(1, 2),  # Capture bigrams and trigrams
            max_df=max_df,  # Ignore very common words
            min_df=1,  # ignore words only appearing once
            max_features=30  # only keep top 30 words
        )
        print("vectoriser at work")

        tfidf_matrix = vectorizer.fit_transform(sentences)

        feature_names = vectorizer.get_feature_names_out()


        for i in range(len(sentences)):
            scores = tfidf_matrix[i].toarray()[0]
            top_indices = np.argsort(scores)[-3:][::-1]  # Get top 3 words
            all_top_words.update(feature_names[j] for j in top_indices)

    return __remove_redundant_keywords(list(all_top_words), redundancy_threshold)


verify_blueprint = Blueprint("verify_blueprint", __name__)

@verify_blueprint.route("/", methods=["POST"])
def verify_claim():
    data = request.get_json()
    user_text = data.get("text", "")
    redundancy_threshold = data.get("redundancy_threshold", 15)
    # find term keywords using TF - IDF then do the search
    keywords = tf_idf_keywords(user_text,redundancy_threshold)
    return jsonify({
        "keywords": keywords  # Convert set to list for JSON response
    })