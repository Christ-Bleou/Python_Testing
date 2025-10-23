def test_login_valid_email(client):
    response = client.post("/welcomeSummary", data={"email": "admin@irontemple.com"}, follow_redirects=True)
    assert b"competitions" in response.data or b"Great" in response.data

def test_login_invalid_email(client):
    response = client.post("/welcomeSummary", data={"email": "wrong@email.com"}, follow_redirects=True)
    assert b"Email not found" in response.data
