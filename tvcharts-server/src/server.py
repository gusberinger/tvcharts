from pathlib import Path
import requests
import sqlalchemy as db
from collections import defaultdict
import os
from flask import Flask, jsonify, make_response
from flask_cors import CORS

root_path = Path(__file__).parent
dump_path = root_path.joinpath("dump/")
db_path = dump_path.joinpath("db.sqlite")
engine = db.create_engine(f"sqlite:///{db_path}")
app = Flask(__name__)
CORS(app)


with engine.connect() as connection:
    search = connection.execute(
        "SELECT tconst, primaryTitle, startYear, endYear FROM search where numVotes > 1000"
    ).fetchall()
    search_json = [
        {"tconst": tconst, "title": title, "startYear": startYear, "endYear": endYear}
        for tconst, title, startYear, endYear in search
    ]
    find_title = dict([(x["tconst"], x["title"]) for x in search_json])


@app.route("/search/", methods=["GET"])
def get_search():
    search_jsonify = jsonify(search_json)
    search_jsonify.headers.add('Access-Control-Allow-Origin', '*')
    return search_jsonify


@app.route("/poster/<tconst>")
def get_poster(tconst: str, methods=["GET"]):
    api_key = os.environ.get("THE_MOVIEDB_API_KEY")
    url = f"https://api.themoviedb.org/3/find/{tconst}?api_key={api_key}&language=en-US&external_source=imdb_id"
    tmdb_response = requests.get(url)
    if tmdb_response.ok:
        poster_path = tmdb_response.json()["tv_results"][0]["poster_path"]
        poster_url = f"https://image.tmdb.org/t/p/w200/{poster_path}"
        poster_resonse = requests.get(poster_url)
        response = make_response(poster_resonse.content)
        response.headers.set("Content-Type", "image/jpeg")
        response.headers.set(
            "Content-Disposition", "attachment", filename=f"{tconst}.jpg"
        )
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    else:
        return ""


@app.route("/tconst/<tconst>", methods=["GET"])
def get_series(tconst: str) -> dict:
    with engine.connect() as connection:
        results = connection.execute(
            f"SELECT * FROM episodes WHERE parentTconst='{tconst}'"
        )
        rows = results.fetchall()
    episode_info = defaultdict(lambda: {})
    result = {}
    title = find_title[tconst]
    result["title"] = title
    result["episode_info"] = episode_info

    for row in rows:
        (
            tconst,
            _, # parentTconst
            seasonNumber,
            episodeNumber,
            averageRating,
            numVotes,
            primaryTitle
        ) = row
        seasonNumber = int(seasonNumber)
        episodeNumber = int(episodeNumber)
        result["episode_info"][seasonNumber][episodeNumber] = {
            "tconst": tconst,
            "episodeTitle": primaryTitle,
            "rating": averageRating,
            "votes": numVotes,
        }
    json = jsonify(result)
    json.headers.add("Access-Control-Allow-Origin", "*")
    return json


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
