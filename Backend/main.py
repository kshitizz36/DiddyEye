# main.py

import sys
import os

# Get absolute path to the parent directory (where both Backend and TelegramBot are)
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Add the parent directory to Python's module search path
sys.path.append(parent_dir)

# Now your import will work
from TelegramBot.bot import start_bot

# Rest of your imports and code...

from flask import Flask
from app.services.tf_idf import verify_blueprint
from app.services.scraper import scrape_blueprint

from app.services.content_scraper import scrape_content_blueprint
from app.services.embedding import embedding_blueprint
from app.services.explanation import explanation_blueprint


def create_app():
    app = Flask(__name__)
    #test
    # Register your blueprint for the /verify endpoint
    app.register_blueprint(verify_blueprint, url_prefix="/verify")
    app.register_blueprint(scrape_blueprint, url_prefix="/scrape")
    app.register_blueprint(scrape_content_blueprint, url_prefix="/scrape_content")
    # (Optional) configure app settings, load env, etc.
    app.register_blueprint(embedding_blueprint, url_prefix="/embedding")
    app.register_blueprint(explanation_blueprint, url_prefix="/explanation")
    return app

if __name__ == "__main__":

    from TelegramBot.bot import start_bot
    import threading

    app = create_app()

    thread1 = threading.Thread(target=start_bot)
    thread2 = threading.Thread(target=app.run, kwargs={
        "debug": True,
        "host": "0.0.0.0",
        "port": 5050,
        "use_reloader": False
    })

    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()
