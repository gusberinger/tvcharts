import sqlalchemy as db
from collections import defaultdict
from dotenv import dotenv_values
from flask import Flask, jsonify
import json

config = dotenv_values(".env")


engine = db.create_engine(f"mysql+pymysql://{config['USERNAME']}:{config['PASSWORD']}@localhost/series")
app = Flask(__name__)



with engine.connect() as connection:
    results = connection.execute("SELECT tconst, primaryTitle from titles where numVotes > 1000").fetchall()
    titles_search = [{"id": tconst, "title": title} for tconst, title in results]
    find_title = dict(results)




@app.route("/search/")
def get_search():
    title_json = jsonify(titles_search)
    title_json.headers.add('Access-Control-Allow-Origin', '*')
    return title_json


@app.route("/tconst/<tconst>")
def get_series(tconst : str) -> dict:
    with engine.connect() as connection:
        results = connection.execute(f"SELECT * FROM data WHERE parentTconst='{tconst}'")
        rows = results.fetchall()
    episode_info = defaultdict(lambda: {})
    result = {}
    result["title"] = find_title[tconst]
    result["episode_info"] = episode_info

    for row in rows:
        tconst, _, seasonNumber, episodeNumber, primaryTitle, averageRating, numVotes = row
        seasonNumber = int(seasonNumber)
        episodeNumber = int(episodeNumber)
        result["episode_info"][seasonNumber][episodeNumber] = {
            "title": primaryTitle,
            "tconst": tconst,
            "rating": averageRating,
            "votes": numVotes
        }
    return result

if __name__ == "__main__":
    app.run(debug=True)
