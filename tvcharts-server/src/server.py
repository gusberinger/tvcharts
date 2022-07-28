from pathlib import Path
from dotenv import load_dotenv
import requests
import sqlalchemy as db
import os
from flask import Flask, jsonify, make_response
from flask_cors import CORS

load_dotenv()
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
    search_jsonify.headers.add("Access-Control-Allow-Origin", "*")
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
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
    else:
        return ""


@app.route("/episodes/<tconst>", methods=["GET"])
def get_episodes(tconst: str) -> dict:
    with engine.connect() as connection:
        episode_query = connection.execute(
            f"SELECT tconst, parentTconst, seasonNumber, episodeNumber, cumEpisodeNumber, averageRating, numVotes, primaryTitle FROM episodes WHERE parentTconst='{tconst}'"
        ).fetchall()
    title = find_title[tconst]
    colors = [
        "#8dd3c7",
        "#bebada",
        "#fb8072",
        "#80b1d3",
        "#fdb462",
        "#b3de69",
        "#fccde5",
        "#d9d9d9",
    ]
    rating_rows = []
    vote_rows = []
    for (
        tconst,
        _,
        seasonNumber,
        episodeNumber,
        cumEpisodeNumber,
        averageRating,
        numVotes,
        primaryTitle,
    ) in episode_query:
        annotation = f"""<b>Season {seasonNumber} Epsiode {episodeNumber}</b><br/><a href={f'https://www.imdb.com/title/{tconst}'}>{primaryTitle}<a/><br/>{numVotes:,} Votes<br/>{averageRating:.1f} Average Rating<br/>"""


        rating_row = [cumEpisodeNumber, averageRating, annotation, colors[(seasonNumber - 1) % len(colors)]]
        vote_row = rating_row.copy()
        vote_row[1] = numVotes
        rating_rows.append(rating_row)
        vote_rows.append(vote_row)

        json = {
            "numVotes": vote_rows,
            "averageRating": rating_rows,
            "title": title
        }
        json = jsonify(json)
        json.headers.add("Access-Control-Allow-Origin", "*")
    return json

@app.route("/season/<tconst>", methods=["GET"])
def get_season(tconst: str):
    with engine.connect() as connection:
        season_query = connection.execute(
            f"SELECT seasonNumber, averageRating, numVotes FROM seasons WHERE parentTconst='{tconst}'"
        ).fetchall()
    data = [[season_number, rating, vote] for season_number, rating, vote in season_query]
    json = {"data": data}
    json = jsonify(data)
    json.headers.add("Access-Control-Allow-Origin", "*")
    return json

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
