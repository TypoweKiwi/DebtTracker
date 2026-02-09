def _register_user(client, email):
    resp = client.post("/auth/register", json={"email": email, "password": "password123"})
    assert resp.status_code == 201
    return resp.get_json()["id"]


def _create_debt(client, created_by):
    resp = client.post(
        "/debts",
        json={"title": "Shared bill", "description": "Utilities", "created_by": created_by},
    )
    assert resp.status_code == 201
    return resp.get_json()["id"]


def test_debt_participants_crud(client):
    from_user = _register_user(client, "from@example.com")
    to_user = _register_user(client, "to@example.com")
    debt_id = _create_debt(client, from_user)

    create_resp = client.post(
        "/debt-participants",
        json={
            "debt_id": debt_id,
            "from_user_id": from_user,
            "to_user_id": to_user,
            "amount": 120.5,
            "description": "Electricity split",
        },
    )
    assert create_resp.status_code == 201
    participant = create_resp.get_json()
    participant_id = participant["id"]

    list_resp = client.get(f"/debt-participants?debt_id={debt_id}")
    assert list_resp.status_code == 200
    items = list_resp.get_json()["items"]
    assert len(items) == 1

    update_resp = client.put(
        f"/debt-participants/{participant_id}",
        json={"status": "settled", "amount": 130.0},
    )
    assert update_resp.status_code == 200
    updated = update_resp.get_json()
    assert updated["status"] == "settled"
    assert updated["amount"] == 130.0

    delete_resp = client.delete(f"/debt-participants/{participant_id}")
    assert delete_resp.status_code == 200
