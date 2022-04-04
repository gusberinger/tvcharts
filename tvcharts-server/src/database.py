from dotenv import dotenv_values
from mysql.connector import connect
from pathlib import Path

config = dotenv_values(".env")
print(config['PASSWORD'])


create_data_table_query = """
CREATE TABLE IF NOT EXISTS cache(
    id INT AUTO_INCREMENT PRIMARY KEY,
    imdbid INT,
    title VARCHAR(100),
    season INT,
    episode_number INT,
    rating FLOAT
);
"""

class Database:

    def __init__(self, path) -> None:
        with connect(host="localhost",
                    user=config['USERNAME'],
                    password=config['PASSWORD'],
                    database="series") as connection:

            with connection.cursor() as cursor:
                cursor.execute(create_data_table_query)
                connection.commit()

    def fetchItems



if __name__ == "__main__":
    db = Database()



