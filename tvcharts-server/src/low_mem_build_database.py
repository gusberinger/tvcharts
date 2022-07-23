import gzip
import pandas as pd
from pathlib import Path
import requests
import sqlalchemy as db
from dotenv import dotenv_values
from tqdm import tqdm

config = dotenv_values(".env")
root_path = Path(__file__).parent
dump_path = root_path.joinpath("dump/")
db_path = dump_path.joinpath("db.sqlite")
title_ratings_url = "https://datasets.imdbws.com/title.ratings.tsv.gz"
title_basics_url = "https://datasets.imdbws.com/title.basics.tsv.gz"
title_episodes_url = "https://datasets.imdbws.com/title.episode.tsv.gz"


def download_file(url, filename):
    filepath = dump_path.joinpath(filename)
    if not filepath.exists():
        print(f"Downloading {filename}...")
        response = requests.get(url)
        with open(filepath, "wb") as fp:
            fp.write(response.content)
        response = None
    else:
        print(f"{filename} Already exists, skipping")


if __name__ == "__main__":
    engine = db.create_engine(f"sqlite:///{db_path}")

    with engine.connect() as connection:
        connection.execute("DROP TABLE IF EXISTS episodes;")
        connection.execute("DROP TABLE IF EXISTS episodes_index;")
        connection.execute("DROP TABLE IF EXISTS search;")
        connection.execute("DROP TABLE IF EXISTS ratings;")

    if not dump_path.is_dir():
        dump_path.mkdir()

    download_file(title_ratings_url, "title.ratings.tsv.gz")
    download_file(title_basics_url, "title.basics.tsv.gz")
    download_file(title_episodes_url, "title.episodes.tsv.gz")

    # load title.ratings into ratings table
    with gzip.open(dump_path.joinpath("title.ratings.tsv.gz"), "rb") as fp:
        ratings = pd.read_csv(
            fp,
            sep="\t",
            usecols=["tconst", "averageRating", "numVotes"],
            na_values="\\N",
        )
        ratings = ratings.fillna(0)
        ratings.to_sql("ratings", con=engine, index=False)

    # load title.episodes into episodes table
    chunksize = 10**6
    with gzip.open(dump_path.joinpath("title.episodes.tsv.gz"), "rb") as fp:
        with pd.read_csv(
            fp,
            sep="\t",
            usecols=["tconst", "parentTconst", "seasonNumber", "episodeNumber"],
            na_values="\\N",
            chunksize=chunksize,
        ) as reader:
            for search_chunk in tqdm(reader, total=6838251 // chunksize):
                search_chunk = search_chunk.dropna(axis=0)
                search_chunk = search_chunk.merge(
                    ratings, how="left", left_on="parentTconst", right_on="tconst", suffixes=('', '_y')
                )
                search_chunk = search_chunk.drop("tconst_y", axis=1)
                search_chunk.to_sql(
                    "episodes", con=engine, if_exists="append", index=False
                )


    # find all tconst in episodes to avoid extra rows in search table
    with engine.connect() as connection:
        episode_query = connection.execute(
            "SELECT DISTINCT parentTconst FROM episodes"
        ).fetchall()
        episodes_tconst = {x[0] for x in episode_query}

    # load title.basics in chunks into search table
    chunksize = 10**6
    with gzip.open(dump_path.joinpath("title.basics.tsv.gz"), "rb") as fp:
        with pd.read_csv(
            fp,
            sep="\t",
            usecols=["tconst", "titleType", "primaryTitle", "startYear", "endYear"],
            na_values="\\N",
            chunksize=chunksize,
        ) as reader:
            for search_chunk in tqdm(reader, total=9087186 // chunksize):
                search_chunk = search_chunk[search_chunk["titleType"] == "tvSeries"]
                search_chunk = search_chunk.drop(["titleType"], axis=1)
                search_chunk = search_chunk[
                    search_chunk["tconst"].isin(episodes_tconst)
                ]
                search_chunk = search_chunk.merge(ratings, how="left", on="tconst")
                search_chunk.to_sql(
                    "search", con=engine, if_exists="append", index=False
                )
