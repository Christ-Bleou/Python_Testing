def test_purchase_places_success(client):
    data = {"competition": "Spring Festival", "club": "Iron Temple", "places": "2"}
    response = client.post("/purchasePlaces", data=data, follow_redirects=True)
    assert b"Great - booking complete!" in response.data

def test_purchase_too_many_places(client):
    data = {"competition": "Spring Festival", "club": "Iron Temple", "places": "15"}
    response = client.post("/purchasePlaces", data=data, follow_redirects=True)
    assert b"You cannot book more than 12 places" in response.data

def test_purchase_not_enough_points(client):
    data = {"competition": "Spring Festival", "club": "Iron Temple", "places": "50"}
    response = client.post("/purchasePlaces", data=data, follow_redirects=True)
    assert b"Not enough points" in response.data
