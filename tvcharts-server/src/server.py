import sqlalchemy as db
from typing import Iterable
from collections import namedtuple, defaultdict
from dotenv import dotenv_values
from flask import Flask
config = dotenv_values(".env")


engine = db.create_engine(f"mysql+pymysql://{config['USERNAME']}:{config['PASSWORD']}@localhost/series")
app = Flask(__name__)

@app.route("/tconst/<tconst>")
def get_series(tconst : str) -> dict:
    with engine.connect() as connection:
        results = connection.execute(f"SELECT * FROM data WHERE parentTconst='{tconst}'")
        rows = results.fetchall()

    # max_season = rows[-1][3]
    result = defaultdict(lambda: {})

    for row in rows:
        tconst, _, seasonNumber, episodeNumber, primaryTitle, averageRating, numVotes = row
        seasonNumber = int(seasonNumber)
        episodeNumber = int(episodeNumber)
        result[seasonNumber][episodeNumber] = {
            "title": primaryTitle,
            "tconst": tconst,
            "rating": averageRating,
            "votes": numVotes
        }
    return result

if __name__ == "__main__":
    app.run(debug=True)
