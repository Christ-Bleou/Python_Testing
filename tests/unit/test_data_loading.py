from server import loadClubs, loadCompetitions

def test_load_clubs_structure():
    clubs = loadClubs()
    assert isinstance(clubs, list)
    assert all("points" in c for c in clubs)
    assert isinstance(clubs[0]["points"], int)

def test_load_competitions_structure():
    comps = loadCompetitions()
    assert isinstance(comps, list)
    assert "numberOfPlaces" in comps[0]
