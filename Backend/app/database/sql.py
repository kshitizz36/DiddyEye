import json

import pymysql
from datetime import datetime
from sentence_transformers import SentenceTransformer
model1 = SentenceTransformer("all-MiniLM-L12-v2")
class DatabaseAccess:
    def __init__(self):
        try:
            self.conn = pymysql.connect(
                host="localhost",
                port=3306,
                user="root",
                password="Borahe13",
                database="VERIFAI"
            )
            self.cursor = self.conn.cursor()
        except pymysql.MySQLError as e:
            print(f"Error connecting to database: {e}")

    def insert_data(self,  input_text, sim_score, source_url,input_embedding):
        """Insert data into QueryData table"""
        try:
            query = """
                INSERT INTO QueryData (input, sim_score, source_url, input_embedding, date_minute)
                VALUES (%s, %s, %s, %s, %s)
            """
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Format datetime

            self.cursor.execute(query, (input_text, sim_score, source_url, input_embedding, current_time))
            self.conn.commit()
            print("Data inserted successfully!")

        except pymysql.MySQLError as e:
            print(f"Database error: {e}")

    def close_connection(self):
        """Close the database connection"""
        self.cursor.close()
        self.conn.close()


# Usage Example
if __name__ == "__main__":
    db = DatabaseAccess()
    input_embedding = model1.encode("Example query input", convert_to_numpy=True)

# Convert NumPy array to list

# Convert to JSON
    embedding_json = json.dumps(embedding_list)
    db.insert_data(
        input_text="Example query input",
        sim_score=0.85,
        source_url="https://example.com",
        input_embedding=embedding_json
    )
    db.close_connection()
