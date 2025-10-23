import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server import app, clubs, competitions

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def sample_club():
    return {"name": "ClubTest", "email": "club@test.com", "points": 10}

@pytest.fixture
def sample_competition():
    return {"name": "CompetitionTest", "date": "2025-12-01", "numberOfPlaces": 20}
