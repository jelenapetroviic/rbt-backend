import pytest

CATEGORY = {"name": "Food", "color": "#4CAF50"}
TRANSACTION = {"type": "expense", "amount": "12.50", "date": "2026-10-08", "category_id": 1}


def test_category_name_is_trimmed_and_unique_ignoring_case(client):
    response = client.post("/categories", json={"name": "  Food  ", "color": "#4CAF50"})
    assert response.status_code == 201
    assert response.json()["name"] == "Food"

    response = client.post("/categories", json={"name": "FOOD", "color": "#4CAF50"})
    assert response.status_code == 409


@pytest.mark.parametrize(
    "data",
    [
        {"name": "", "color": "#4CAF50"},
        {"name": "x" * 31, "color": "#4CAF50"},
        {"name": "Food", "color": "red"},
        {"name": "Food", "color": "#12345"},
    ],
)
def test_invalid_category(client, data):
    assert client.post("/categories", json=data).status_code == 400


def test_valid_transaction(client):
    client.post("/categories", json=CATEGORY)

    response = client.post(
        "/transactions", json={**TRANSACTION, "amount": "1000000.00", "description": ""}
    )

    assert response.status_code == 201
    assert response.json()["amount"] == "1000000.00"
    assert response.json()["description"] is None


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("type", "transfer"),
        ("amount", None),
        ("amount", "0"),
        ("amount", "12.345"),
        ("amount", "1000000.01"),
        ("date", "2026-02-30"),
        ("description", "x" * 201),
        ("category_id", 99),
    ],
)
def test_invalid_transaction(client, field, value):
    client.post("/categories", json=CATEGORY)

    response = client.post("/transactions", json={**TRANSACTION, field: value})

    assert response.status_code == 400


def test_budget_rules(client):
    client.post("/categories", json=CATEGORY)

    assert client.put("/budgets/2026-10/1", json={"amount": "0"}).status_code == 400
    assert client.put("/budgets/2026-10/99", json={"amount": "100.00"}).status_code == 404

    client.put("/budgets/2026-10/1", json={"amount": "100.00"})
    client.put("/budgets/2026-10/1", json={"amount": "200.00"})
    assert client.get("/budgets", params={"month": "2026-10"}).json() == [
        {"month": "2026-10", "category_id": 1, "amount": "200.00"}
    ]
