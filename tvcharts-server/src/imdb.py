from typing import Iterable
from imdb import Cinemagoer
from collections import namedtuple


Episode = namedtuple('Episode', ['season', 'episode_number', 'rating'])
ia = Cinemagoer()


def get_show_data(imdb_id) -> Iterable[Episode]:
    series = ia.get_movie(imdb_id)
    ia.update(series, 'episodes')
    for season in series['episodes']:
        for episode_number in series['episodes'][season]:
            rating = series['episodes'][season][episode_number]['rating']
            yield Episode(season, episode_number, rating)


if __name__ == "__main__":
    for episodes in get_show_data('0141842'):
        print(episodes)
