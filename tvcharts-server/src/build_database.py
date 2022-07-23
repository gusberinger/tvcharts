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
if not dump_path.exists():
    dump_path.mkdir()
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
        connection.execute("DROP TABLE IF EXISTS episode_titles;")
        connection.execute("DROP TABLE IF EXISTS ratings;")
        connection.execute("DROP TABLE IF EXISTS episodes;")
        connection.execute("DROP TABLE IF EXISTS search;")

        # cannot specify primary key using pd.Dataframe.to_sql
        # cannot add primary key after table created
        # so we manually create table schema with primary key
        connection.execute(
        """
        CREATE TABLE episode_titles (
            tconst TEXT PRIMARY KEY,
            "primaryTitle" TEXT,
            "startYear" INT,
            "endYear" INT
        );"""
        )

        connection.execute(
        """
        CREATE TABLE ratings (
            tconst TEXT PRIMARY KEY,
            "averageRating" FLOAT,
            "numVotes" BIGINT
        );"""
        )

        # connection.execute(
        # """
        # CREATE TABLE episodes (
        #     tconst TEXT PRIMARY KEY,
        #     "parentTconst" TEXT,
        #     "seasonNumber" INT,
        #     "episodeNumber" INT,
        #     "averageRating" FLOAT,
        #     "numVotes" INT
        # );"""
        # )

        connection.execute(
        """
        CREATE TABLE search (
            tconst TEXT PRIMARY KEY,
            "primaryTitle" TEXT,
            "startYear" INT,
            "endYear" INT,
            "averageRating" FLOAT,
            "numVotes" INT
        );"""
        )


    if not dump_path.is_dir():
        dump_path.mkdir()

    download_file(title_ratings_url, "title.ratings.tsv.gz")
    download_file(title_basics_url, "title.basics.tsv.gz")
    download_file(title_episodes_url, "title.episodes.tsv.gz")

    # load title.ratings into ratings table
    # table is small enough that we don't chunk
    print("Loading ratings.tsv")
    with gzip.open(dump_path.joinpath("title.ratings.tsv.gz"), "rb") as fp:
        ratings = pd.read_csv(
            fp,
            sep="\t",
            usecols=["tconst", "averageRating", "numVotes"],
            na_values="\\N",
        )
        # ratings.to_sql("ratings", con=engine, index=False, if_exists="append")

    # load title.episodes into episodes table
    chunksize = 10**6
    print("loading episodes.tsv")
    with gzip.open(dump_path.joinpath("title.episodes.tsv.gz"), "rb") as fp:
        with pd.read_csv(
            fp,
            sep="\t",
            usecols=["tconst", "parentTconst", "seasonNumber", "episodeNumber"],
            na_values="\\N",
            chunksize=chunksize,
        ) as reader:
            for episode_chunk in tqdm(reader, total=6838251 // chunksize):
                episode_chunk = episode_chunk.dropna(axis=0)
                episode_chunk = episode_chunk.merge(
                    ratings, how="left", on="tconst"
                )
                episode_chunk.fillna(0) # fill in tconsts with no rating
                episode_chunk.to_sql(
                    "episodes_rating", con=engine, if_exists="append", index=False
                )


    # find all tconst in episodes to avoid extra rows in search table
    with engine.connect() as connection:
        episode_query = connection.execute(
            "SELECT DISTINCT parentTconst FROM episodes_rating"
        ).fetchall()
        episodes_parentTconst = {x[0] for x in episode_query}

    # load title.basics in chunks into search table
    chunksize = 10**6
    print("L:oading basics.tsv")
    with gzip.open(dump_path.joinpath("title.basics.tsv.gz"), "rb") as fp:
        with pd.read_csv(
            fp,
            sep="\t",
            usecols=["tconst", "titleType", "primaryTitle", "startYear", "endYear"],
            na_values="\\N",
            chunksize=chunksize,
        ) as reader:
            for basics_chunk in tqdm(reader, total=9087186 // chunksize):
                episode_chunk = basics_chunk[basics_chunk["titleType"] == "tvEpisode"]
                episode_chunk = episode_chunk.drop(["titleType"], axis=1)
                episode_chunk.to_sql("episode_titles", con=engine, if_exists="append", index=False)
                del episode_chunk
                

                series_chunk = basics_chunk[basics_chunk["titleType"] == "tvSeries"]
                series_chunk = series_chunk.drop(["titleType"], axis=1)
                series_chunk = series_chunk[
                    series_chunk["tconst"].isin(episodes_parentTconst)
                ]
                series_chunk = series_chunk.merge(ratings, how="left", on="tconst")
                series_chunk.to_sql(
                    "search", con=engine, if_exists="append", index=False
                )
                del series_chunk

    print("Merging episodes with titles...")
    with engine.connect() as connection:
        connection.execute("""
        CREATE TABLE episodes AS SELECT 
        a.*, b.primaryTitle 
        FROM episodes_rating a LEFT JOIN episode_titles b
        ON a.tconst=b.tconst;"""
        )
        connection.execute("DROP TABLE episodes_rating;")