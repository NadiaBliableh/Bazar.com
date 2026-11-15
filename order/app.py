
import os
import requests

from flask import Flask, jsonify, request
from database import init_db, get_connection

app = Flask(__name__)

CATALOG_URL = os.environ.get(
    "CATALOG_URL",
    "http://127.0.0.1:5001"
)

init_db()


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "service": "Order Service",
        "status": "running"
    })


@app.route("/orders", methods=["POST"])
def purchase_book():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "JSON data is required"}), 400

    book_id = data.get("book_id")

    if isinstance(book_id, bool) or not isinstance(book_id, int) or book_id <= 0:
        return jsonify({"error": "A valid book_id is required"}), 400

    try:
        response = requests.post(
            f"{CATALOG_URL}/books/{book_id}/purchase",
            timeout=5
        )
    except requests.RequestException:
        return jsonify({
            "error": "Catalog Service is unavailable"
        }), 503

    if response.status_code != 200:
        return jsonify(response.json()), response.status_code

    book = response.json()

    
    try:
        with get_connection() as connection:
            cursor = connection.execute("""
                INSERT INTO orders (book_id, book_title, price)
                VALUES (?, ?, ?)
            """, (
                book["id"],
                book["title"],
                book["price"]
            ))

            order_id = cursor.lastrowid

    except Exception:
        # Attempt to restore stock if saving the order fails.
        try:
            restore_response = requests.patch(
                f"{CATALOG_URL}/books/{book_id}/stock",
                json={"delta": 1},
                timeout=5
            )

            if restore_response.status_code != 200:
                app.logger.error(
                    "Stock restoration failed for book %s",
                    book_id
                )

        except requests.RequestException:
            app.logger.error(
                "Catalog unavailable during stock restoration "
                "for book %s",
                book_id
            )

        return jsonify({
            "error": "Order could not be saved",
            "message": "Stock restoration was attempted"
        }), 500


    print(f"bought book {book['title']}")

    return jsonify({
        "message": f"bought book {book['title']}",
        "order_id": order_id,
        "book_id": book["id"],
        "book_title": book["title"],
        "price": book["price"],
        "remaining_quantity": book["quantity"]
    }), 201


@app.route("/orders", methods=["GET"])
def get_orders():
    with get_connection() as connection:
        orders = connection.execute(
            "SELECT * FROM orders ORDER BY id DESC"
        ).fetchall()

    return jsonify([dict(order) for order in orders])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
