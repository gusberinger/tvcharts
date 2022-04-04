from __future__ import annotations
from typing import Iterable, List, TYPE_CHECKING
from dotenv import dotenv_values
from mysql.connector import connect
import get_imdb

config = dotenv_values(".env")
print(config['PASSWORD'])


create_table_query = """
CREATE TABLE IF NOT EXISTS cache(
    id INT AUTO_INCREMENT PRIMARY KEY,
    imdb_id VARCHAR(100),
    title VARCHAR(100),
    season INT,
    episode_number INT,
    rating FLOAT
);
"""

insert_cache_query = """
INSERT INTO cache
(imdb_id, title, season, episode_number, rating)
VALUES ( %s, %s, %s, %s, %s )
"""

class Database:

    def __init__(self) -> None:
        self.db = connect(
            host="localhost",
            username=config['USERNAME'],
            password=config['PASSWORD'],
            database="series"
        )

    def insert_series(self, series : Iterable[get_imdb.Episode]) -> None:
        with self.db.cursor() as cursor:
            cursor.executemany(insert_cache_query, list(series))
            self.db.commit()


    def get_series(self, imdb_id : str) -> Iterable[get_imdb.Episode]:
        with self.db.cursor() as cursor:
            cursor.execute(f"SELECT * FROM cache WHERE imdb_id={imdb_id}")
            result = cursor.fetchall()
        # return (*row[1:] for row in result)
        return (get_imdb.Episode(*row[1:]) for row in result)


    def delete_series(self, imdb_id : str):
        with self.db.cursor() as cursor:
            cursor.execute(f"DELETE FROM cache WHERE imdb_id={imdb_id}")


    def clear_cache(self) -> None:
        with self.db.cursor() as cursor:
            cursor.execute("DROP TABLE cache")
            cursor.execute(create_table_query)
            self.db.commit()




if __name__ == "__main__":
    db = Database()
    # db.clear_cache()
    # series = get_imdb.get_show_data('0141842')
    # db.update_series(series)
    print(list(db.get_series('0141842')))

