import search

def test_rick_and_morty():
    assert(search.search("rick and morty")[0]['tconst'] == 'tt2861424')