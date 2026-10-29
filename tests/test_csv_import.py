from app.services import csv_import

HEADER = "type,amount,date,description,category\n"


def upload(client, content):
    return client.post("/transactions/import", files={"file": ("data.csv", content.encode())})


def test_example_from_the_task(client):
    client.post("/categories", json={"name": "Eating out", "color": "#FF9800"})
    client.post("/categories", json={"name": "Other", "color": "#9E9E9E"})

    response = upload(
        client,
        HEADER
        + "expense,12.50,2026-10-08,Lunch,Eating out\n"
        + "income,300.00,2026-10-09,,Other\n",
    )

    assert response.json() == {"imported": 2, "failed": 0, "errors": []}
    income, expense = client.get("/transactions").json()["items"]
    assert expense["description"] == "Lunch"
    assert income["description"] is None


def test_invalid_rows_are_reported(client):
    client.post("/categories", json={"name": "Other", "color": "#9E9E9E"})

    response = upload(
        client,
        HEADER
        + "expense,10.00,2026-10-01,Category in lower case,other\n"
        + "expense,0,2026-10-01,Zero amount,Other\n"
        + "expense,10.00,2026-10-01,Unknown category,Travel\n",
    )

    assert response.json() == {
        "imported": 1,
        "failed": 2,
        "errors": [
            {"row": 3, "errors": ["amount: Input should be greater than 0"]},
            {"row": 4, "errors": ["category: Category 'Travel' does not exist"]},
        ],
    }


def test_too_many_rows(client, monkeypatch):
    client.post("/categories", json={"name": "Other", "color": "#9E9E9E"})
    monkeypatch.setattr(csv_import, "MAX_ROWS", 2) 

    response = upload(client, HEADER + "expense,1.00,2026-10-01,,Other\n" * 3)

    assert response.status_code == 400
    assert client.get("/transactions").json()["total"] == 0
