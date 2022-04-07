import sqlalchemy as db
from dotenv import dotenv_values
from cfuzzyset import cFuzzySet as FuzzySet
from collections import namedtuple
import time
import Levenshtein
from bisect import bisect_left
import math

config = dotenv_values(".env")
engine = db.create_engine(f"mysql+pymysql://{config['USERNAME']}:{config['PASSWORD']}@localhost/series")

# Show = namedtuple('Show', ['tconst', 'title', 'votes'])

shows = []
with engine.connect() as connection:
    request = connection.execute("SELECT * FROM titles").fetchall()
    for tconst, title, _, votes in request:
        shows.append((tconst, title.lower().strip(), votes))
shows = sorted(shows, key = lambda x: x[1]) # sort by title
tconst, title, votes = zip(*shows)

def search(text, limit=10):
    text = text.lower()
    first_char = text[0]
    start_index = bisect_left(title, first_char)
    print(f"{start_index=}", f"{title[start_index]}")
    distances = []
    for i in range(start_index, len(title)):
        if title[i].startswith(text[:1]):
            dist = Levenshtein.distance(text, title[i])
            if dist == 0:
                dist = 10 ** 8
            else:
                dist = 1 / dist
            dist *= votes[i]
            distances.append((i, dist))
        else:
            break
    distances = sorted(distances, key = lambda x: x[1], reverse=True)
    result = {}
    for i, row in enumerate(distances[:limit]):
        idx, dist = row
        result[i] = {"tconst": tconst[idx], "title": title[idx]}
    return result



t0 = time.perf_counter()
# print(len(shows))
print(search("rick and morty"))
t1 = time.perf_counter()

print(f"Found in {t1 - t0} seconds.")