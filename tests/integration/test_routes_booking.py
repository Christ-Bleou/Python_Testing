def test_book_route_valid(client):
    response = client.get("/book/Spring%20Festival/Iron%20Temple")
    assert response.status_code == 200
    assert b"booking" in response.data
