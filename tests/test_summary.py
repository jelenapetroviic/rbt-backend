def create_category(client, name):
    return client.post("/categories", json={"name": name, "color": "#000000"}).json()["id"]


def add_transaction(client, category_id, type, amount, date):
    data = {"type": type, "amount": amount, "date": date, "category_id": category_id}
    client.post("/transactions", json=data)


def test_month_without_data(client):
    assert client.get("/summary/2026-10").json() == {
        "month": "2026-10",
        "total_income": "0.00",
        "total_expense": "0.00",
        "balance": "0.00",
        "categories": [],
    }


def test_totals_and_balance(client):
    salary = create_category(client, "Salary")
    food = create_category(client, "Food")
    add_transaction(client, salary, "income", "100.00", "2026-10-01")
    add_transaction(client, food, "expense", "80.00", "2026-10-15")
    add_transaction(client, food, "expense", "70.00", "2026-10-31")
    add_transaction(client, food, "expense", "999.00", "2026-11-01")

    summary = client.get("/summary/2026-10").json()

    assert summary["total_income"] == "100.00"
    assert summary["total_expense"] == "150.00"
    assert summary["balance"] == "-50.00"


def test_categories(client):
    rent = create_category(client, "Rent")
    food = create_category(client, "Food")
    bus = create_category(client, "Bus")
    gym = create_category(client, "Gym")
    salary = create_category(client, "Salary")
    add_transaction(client, rent, "expense", "500.00", "2026-10-01")
    add_transaction(client, food, "expense", "30.00", "2026-10-02")
    add_transaction(client, bus, "expense", "30.00", "2026-10-03")
    add_transaction(client, salary, "income", "2000.00", "2026-10-01")
    client.put(f"/budgets/2026-10/{rent}", json={"amount": "400.00"})
    client.put(f"/budgets/2026-10/{food}", json={"amount": "100.00"})
    client.put(f"/budgets/2026-10/{gym}", json={"amount": "50.00"})

    categories = client.get("/summary/2026-10").json()["categories"]

    assert [(c["name"], c["spent"], c["budget"], c["remaining"]) for c in categories] == [
        ("Rent", "500.00", "400.00", "-100.00"),
        ("Bus", "30.00", None, None),
        ("Food", "30.00", "100.00", "70.00"),
        ("Gym", "0.00", "50.00", "50.00"),
    ]
