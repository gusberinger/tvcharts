from collections import namedtuple
from this import d
from typing import Iterable
import sqlalchemy as db
from dotenv import dotenv_values
config = dotenv_values(".env")


Episode = namedtuple('Episode', ['tconst', 'title', 'season', 'episode_number', 'rating', 'votes'])
engine = db.create_engine(f"mysql+pymysql://{config['USERNAME']}:{config['PASSWORD']}@localhost/series")

def get_series(tconst : str) -> Iterable[Episode]:
    with engine.connect() as connection:
        results = connection.execute(f"SELECT * FROM data WHERE parentTconst='{tconst}'")
        rows = results.fetchall()
    for row in rows:
        tconst, _, seasonNumber, episodeNumber, primaryTitle, averageRating, numVotes = row
        yield Episode(tconst, primaryTitle, seasonNumber,
                      episodeNumber, averageRating, numVotes)


if __name__ == "__main__":
    for episodes in get_series('tt0141842'):
        print(episodes)
