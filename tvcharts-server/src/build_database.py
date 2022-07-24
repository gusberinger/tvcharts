import gzip
import sqlite3
import pandas as pd
from pathlib import Path
import requests

root_path = Path(__file__).parent
dump_path = root_path.joinpath("dump/")
if not dump_path.exists():
    dump_path.mkdir()
db_path = dump_path.joinpath("db.sqlite")
if db_path.exists():
    db_path.unlink()
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

    if not dump_path.is_dir():
        dump_path.mkdir()

    download_file(title_ratings_url, "title.ratings.tsv.gz")
    download_file(title_basics_url, "title.basics.tsv.gz")
    download_file(title_episodes_url, "title.episodes.tsv.gz")

    print("Loading ratings.tsv")
    with gzip.open(dump_path.joinpath("title.ratings.tsv.gz"), "rb") as fp:
        ratings = pd.read_csv(
            fp,
            sep="\t",
            usecols=["tconst", "averageRating", "numVotes"],
            na_values="\\N",
        )

    print("Loading episodes.tsv")
    with gzip.open(dump_path.joinpath("title.episodes.tsv.gz"), "rb") as fp:
        episodes = pd.read_csv(
            fp,
            sep="\t",
            usecols=["tconst", "parentTconst", "seasonNumber", "episodeNumber"],
            na_values="\\N",
        )
    episodes = episodes.merge(ratings, how="left", on="tconst")
    episodes = episodes.sort_values(
        by=["parentTconst", "seasonNumber", "episodeNumber"]
    )
    episodes["cumEpisodeNumber"] = episodes.groupby(["parentTconst"]).cumcount() + 1
    episodes = episodes.dropna(subset=["averageRating", "numVotes"])
    episodes_parentTconst = set(episodes["parentTconst"])

    print("Loading basics.tsv ...")
    with gzip.open(dump_path.joinpath("title.basics.tsv.gz"), "rb") as fp:
        basics = pd.read_csv(
            fp,
            sep="\t",
            usecols=["tconst", "titleType", "primaryTitle", "startYear", "endYear"],
            na_values="\\N",
        )

    print("Merging episodes dataframe with basics...")
    basic_episodes = basics[basics["titleType"] == "tvEpisode"]
    basic_episodes = basic_episodes.drop(["titleType"], axis=1)
    episodes = episodes.merge(basic_episodes, how="left", on="tconst")
    print("Creating episodes table...")
    with sqlite3.connect(db_path) as con:
        episodes.to_sql(
            "episodes",
            con=con,
            index=False,
            chunksize=10**6,
            # to_sql can't specify dtype automatically
            dtype={
                "tconst": "VARCHAR(10) PRIMARY KEY",
                "parentTcont": "VARCHAR(10)",
                "seasonNumber": "INTEGER",
                "episodeNumber": "INTEGER",
                "averageRating": "FLOAT",
                "numVotes": "INTEGER",
                "startYear": "INTEGER",
                "endYear": "INTEGER",
            },
        )

    print("Creating search table...")
    basic_series = basics[basics["titleType"] == "tvSeries"]
    basic_series = basic_series.drop(["titleType"], axis=1)
    basic_series = basic_series[basic_series["tconst"].isin(episodes_parentTconst)]
    basic_series = basic_series.merge(ratings, how="left", on="tconst")
    with sqlite3.connect(db_path) as con:
        basic_series.to_sql(
            "search",
            con=con,
            index=False,
            chunksize=10**6,
            dtype={
                "tconst": "VARCHAR(10) PRIMARY KEY",
                "primaryTitle": "TEXT",
                "startYear": "INTEGER",
                "endYear": "INTEGER",
                "averageRating": "FLOAT",
                "numVotes": "INTEGER",
            },
        )
