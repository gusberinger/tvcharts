import chunk
import gzip
from numpy import full
import pandas as pd
from pathlib import Path
import requests
import sqlalchemy as db
from dotenv import dotenv_values

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
        response = requests.get(url)
        with open(filepath, "wb") as fp:
            fp.write(response.content)
        response = None
    else:
        print(f"{filename} Already exists, skipping")


if __name__ == "__main__":
    engine = db.create_engine(f"sqlite:///{db_path}")

    with engine.connect() as connection:
        connection.execute("DROP TABLE IF EXISTS data;")
        connection.execute("DROP TABLE IF EXISTS search;")

    if not dump_path.exists():
        dump_path.mkdir()

    download_file(title_ratings_url, "title.ratings.tsv.gz")
    download_file(title_basics_url, "title.basics.tsv.gz")
    download_file(title_episodes_url, "title.episodes.tsv.gz")

    
    # load title.basics in chunks into search table
    with gzip.open(dump_path.joinpath("title.basics.tsv.gz"), "rb") as fp:
        with pd.read_csv(
            fp,
            sep="\t",
            usecols=["tconst", "titleType", "primaryTitle", "startYear", "endYear"],
            na_values="\\N",
            chunksize=1000,
        ) as reader:
            for chunk in reader:
                series_info = chunk[chunk["titleType"] == "tvSeries"]
                series_info = series_info.drop(["titleType"], axis=1)
                series_info.to_sql(
                    "search", con=engine, if_exists="append", index=False
                )
    
    # load title.episodes into episodes table
    with gzip.open(dump_path.joinpath("title.episodes.tsv.gz"), "rb") as fp:
        with pd.read_csv(
            fp,
            sep="\t",
            usecols=["tconst", "parentTconst", "seasonNumber", "episodeNumber"],
            na_values="\\N",
            chunksize=1000
        ) as reader:
            for chunk in reader:
                

