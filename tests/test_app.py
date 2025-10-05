# tests/test_app.py
import copy
from typing import cast
import pytest
from flask.wrappers import Response
import server

@pytest.fixture
def client(monkeypatch):
    # sauvegarde état original
    orig_clubs = copy.deepcopy(server.clubs)
    orig_comps = copy.deepcopy(server.competitions)

    # empêcher l'écriture sur disque pendant les tests
    monkeypatch.setattr(server, "saveClubs", lambda *_: None, raising=False)
    monkeypatch.setattr(server, "saveCompetitions", lambda *_: None, raising=False)

    # travailler sur des copies isolées
    server.clubs = copy.deepcopy(orig_clubs)
    server.competitions = copy.deepcopy(orig_comps)

    server.app.config["TESTING"] = True
    client = server.app.test_client()

    yield client

    # restauration
    server.clubs = orig_clubs
    server.competitions = orig_comps

def test_home_route(client):
    res = cast(Response, client.get("/"))
    assert res.status_code == 200
    assert b"GUDLFT Registration" in res.data

def test_show_summary_invalid_email_redirects_to_index(client):
    res = cast(Response, client.post("/showSummary", data={"email": "unknown@example.com"}, follow_redirects=True))
    assert res.status_code == 200
    assert b"Welcome to the GUDLFT Registration Portal" in res.data

def test_purchase_not_enough_places(client):
    comp = server.competitions[0]
    club = server.clubs[0]
    too_many = int(comp["numberOfPlaces"]) + 10
    data = {"club": club["name"], "competition": comp["name"], "places": str(too_many)}
    res = cast(Response, client.post("/purchasePlaces", data=data, follow_redirects=True))
    assert res.status_code == 200
    assert b"Not enough places available" in res.data or b"Not enough places" in res.data

def test_purchase_more_than_12_rejected(client):
    comp = server.competitions[0]
    club = server.clubs[0]
    data = {"club": club["name"], "competition": comp["name"], "places": "13"}
    res = cast(Response, client.post("/purchasePlaces", data=data, follow_redirects=True))
    assert res.status_code == 200
    assert b"You cannot book more than 12 places" in res.data or b"more than 12" in res.data

def test_purchase_not_enough_points(client):
    comp = server.competitions[0]
    club = server.clubs[0]
    club["points"] = 0
    data = {"club": club["name"], "competition": comp["name"], "places": "1"}
    res = cast(Response, client.post("/purchasePlaces", data=data, follow_redirects=True))
    assert res.status_code == 200
    assert b"Not enough points" in res.data or b"Not enough points to book" in res.data

def test_purchase_success_updates_state(client):
    comp = server.competitions[0]
    club = server.clubs[0]
    initial_places = int(comp["numberOfPlaces"])
    initial_points = int(club["points"])

    places_to_book = 1
    data = {"club": club["name"], "competition": comp["name"], "places": str(places_to_book)}
    res = cast(Response, client.post("/purchasePlaces", data=data, follow_redirects=True))
    assert res.status_code == 200
    assert int(comp["numberOfPlaces"]) == initial_places - places_to_book
    assert int(club["points"]) == initial_points - places_to_book
    assert b"Great" in res.data or b"booking complete" in res.data