def _register_user(client, email):
    resp = client.post("/auth/register", json={"email": email, "password": "password123"})
    assert resp.status_code == 201
    return resp.get_json()["id"]


def test_debts_crud(client):
    user_id = _register_user(client, "debts@example.com")

    create_resp = client.post(
        "/debts",
        json={"title": "Rent", "description": "January rent", "created_by": user_id},
    )
    assert create_resp.status_code == 201
    debt = create_resp.get_json()
    assert debt["title"] == "Rent"
    debt_id = debt["id"]

    list_resp = client.get(f"/debts?created_by={user_id}")
    assert list_resp.status_code == 200
    items = list_resp.get_json()["items"]
    assert len(items) == 1

    update_resp = client.put(
        f"/debts/{debt_id}",
        json={"status": "settled", "title": "Rent updated"},
    )
    assert update_resp.status_code == 200
    updated = update_resp.get_json()
    assert updated["status"] == "settled"
    assert updated["title"] == "Rent updated"

    delete_resp = client.delete(f"/debts/{debt_id}")
    assert delete_resp.status_code == 200
