import gzip
import pandas as pd
from pathlib import Path
import requests
import sqlalchemy as db 
from dotenv import dotenv_values
config = dotenv_values(".env")
print(config['PASSWORD'])

root_path = Path(__file__).parent
dump_path = root_path.joinpath("dump/")
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

    if not dump_path.exists():
        dump_path.mkdir()

    download_file(title_ratings_url, "title.ratings.tsv.gz")
    download_file(title_basics_url, "title.basics.tsv.gz")
    download_file(title_episodes_url, "title.episodes.tsv.gz")

    with gzip.open(dump_path.joinpath("title.basics.tsv.gz"), "rb") as fp:
        basics_df = pd.read_csv(
            fp,
            sep="\t",
            usecols=["tconst", "titleType", "primaryTitle"],
            na_values="\\N"
        )

    with gzip.open(dump_path.joinpath("title.episodes.tsv.gz"), "rb") as fp:
        episodes_df = pd.read_csv(fp, sep="\t")

    print("Merging data...")
    episodes_df = episodes_df.merge(basics_df, on="tconst")
    basics_df = None

    with gzip.open(dump_path.joinpath("title.ratings.tsv.gz"), "rb") as fp:
        ratings_df = pd.read_csv(fp, sep="\t")

    print("Merging data...")
    full_df = episodes_df.merge(ratings_df, on="tconst").drop(["titleType"], axis=1)
    ratings_df = None
    engine = db.create_engine(f"mysql+pymysql://{config['USERNAME']}:{config['PASSWORD']}@localhost/series")
    with engine.connect() as connection:
        connection.execute("DROP TABLE IF EXISTS data;")
        full_df.to_sql('data', con=engine, index=False, chunksize=1000)


