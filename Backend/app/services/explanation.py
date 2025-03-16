# explanation.py
import os
from openai import OpenAI
from flask import Blueprint, request, jsonify

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
from dotenv import load_dotenv

# Load environment variables (make sure OPENAI_API_KEY is set in your .env file)
load_dotenv()

explanation_blueprint = Blueprint("explanation_blueprint", __name__)


@explanation_blueprint.route("/", methods=["POST"])
def reasoning_route():
    """
    Expects a JSON payload with:
      - user_text: string (the user's claim)
      - supporting_texts: list of strings (content from supporting sources)
      - max_score: number (highest similarity score)
      - min_score: number (lowest similarity score)
      - temperature (optional): float (default 0.7)

    Returns:
      JSON with the generated reasoning summary.
    """
    data = request.get_json()
    user_text = data.get("user_text", "")
    supporting_texts = data.get("supporting_texts", [])
    max_score = data.get("max_score")
    min_score = data.get("min_score")
    temperature = data.get("temperature", 0.7)

    if not user_text or not supporting_texts or max_score is None or min_score is None:
        return jsonify({"error": "Missing required parameters"}), 400
    # Combine the supporting texts into one block, separated by newlines
    supporting_combined = "\n\n".join(supporting_texts)

    MAX_SUPPORTING_LENGTH = 3500  # set your desired character limit
    if len(supporting_combined) > MAX_SUPPORTING_LENGTH:
        supporting_combined = supporting_combined[:MAX_SUPPORTING_LENGTH] + "..."


    # Build the GPT prompt
    prompt = (
            "You are a fact-checking assistant on a telegram bot. Below is the user's claim, "
            "followed by content scraped from two best supporting source. "
            "You are also provided 2 scores, max scores, and min scores which are derived from cosine similarity comparison between the user texts"
            "with the articles that provides the best similarity score and the worst similarity score. respectively."
            "Here is the the way we gauge this scores: \n"
            "- if min score < -0.3: Highly unreliable. Sources suggest opposite of the claim. \n"
            "- if max score < 0.55: Unreliable. No credible sources back up the claim. \n"
            "- if max score > 0.5 and max score < 0.60: It is ambiguous whether the claim is reliable. Some credible sources support it slightly. \n"
            "- if max score > 0.60: There is strong evidence that the claim is reliable. \n\n"
            "Here are the scores, \n"
            f"max_score = {max_score} \n"
            f"min_score = {min_score} \n\n"
            "Now Consider the scores, and if necessary explain in clear terms how these sources supports or disproves the user's statements in a simple user friendly manner"
            "For example, if the user's claim is that Donald Trump is the current president, an article can indicate in a sentence that Donald Trump is the president by mentioning the words 'President Trump' "
            "This statement will support the user's claim and you must give the reasoning for supporting this claim and which article is from"
            "if you feel that the supported claims are insufficient and after you consider the max and min scores,you can choose to refute the claim or accept the claim.\n\n"
            f"User's claim:\n{user_text}\n\n"
            "Supporting sources:\n" + supporting_combined + "\n\n" + "Please provide a concise reasoning summary."
    )

    try:
        response = client.chat.completions.create(model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a factual, neutral assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature)
        reasoning_text = response.choices[0].message.content.strip()
        return jsonify({"reasoning_summary": reasoning_text})
    except Exception as e:
        return jsonify({"error": f"Error generating reasoning summary: {e}"}), 500


