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

    # load title.basics in chunks into search table
    # the progress bars from tqdm are approximate
    chunksize = 10**6
    with gzip.open(dump_path.joinpath("title.basics.tsv.gz"), "rb") as fp:
        with pd.read_csv(
            fp,
            sep="\t",
            usecols=["tconst", "titleType", "primaryTitle", "startYear", "endYear"],
            na_values="\\N",
            chunksize=chunksize,
        ) as reader:
            for chunk in tqdm(reader, total=9087186 // chunksize):
                series_info = chunk[chunk["titleType"] == "tvSeries"]
                series_info = series_info.drop(["titleType"], axis=1)
                series_info.to_sql(
                    "search", con=engine, if_exists="append", index=False
                )

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
            for chunk in tqdm(reader, total=6838251 // chunksize):
                chunk = chunk.dropna(axis=0)
                chunk.to_sql(
                    "episodes_index", con=engine, if_exists="append", index=False
                )

    # load title.ratings into ratings table
    with gzip.open(dump_path.joinpath("title.ratings.tsv.gz"), "rb") as fp:
        ratings = pd.read_csv(
            fp,
            sep="\t",
            usecols=["tconst", "averageRating", "numVotes"],
            na_values="\\N",
        )
        ratings.to_sql("ratings", con=engine, index=False)


    print("Combining episode and rating tables...")
    with engine.connect() as connection:
        # combine episodes and ratings
        connection.execute(
            "CREATE TABLE episodes AS SELECT a.*, b.numVotes, b.averageRating FROM episodes_index a LEFT JOIN ratings b ON a.tconst=b.tconst;"
        )
        connection.execute("DROP TABLE episodes_index")
        connection.execute("DROP TABLE ratings")


    with engine.connect() as connection:
        # find all tconst of shows in both search and ratings
        episode_query = connection.execute("SELECT DISTINCT parentTconst FROM episodes").fetchall()
        episodes_tconst= {x[0] for x in episode_query}
        search_query = connection.execute("SELECT DISTINCT tconst FROM search").fetchall()
        search_tconst = {x[0] for x in search_query}
        
        search_remove = search_tconst.difference(episodes_tconst)
        episodes_remove = episodes_tconst.difference(search_tconst)
        print(f"Removing {len(search_remove) + len(episodes_remove):,} from database...")
        # query = f"SELECT * FROM episodes WHERE rowid in ({','.join(['?']*len(args))})"
        # cursor.execute(query, args)
 

        