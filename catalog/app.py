
from flask import Flask, jsonify, request
from database import init_db, get_connection

app = Flask(__name__)

init_db()


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "service": "Catalog Service",
        "status": "running",
        "database": "initialized"
    })


@app.route("/books", methods=["GET"])
def get_books():
    with get_connection() as connection:
        books = connection.execute(
            "SELECT * FROM books"
        ).fetchall()

    return jsonify([dict(book) for book in books])


@app.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    with get_connection() as connection:
        book = connection.execute(
            "SELECT * FROM books WHERE id = ?",
            (book_id,)
        ).fetchone()

    if book is None:
        return jsonify({"error": "Book not found"}), 404

    return jsonify(dict(book))


@app.route("/books/search", methods=["GET"])
def search_books():
    subject = request.args.get("subject")

    if not subject:
        return jsonify({"error": "Subject is required"}), 400

    with get_connection() as connection:
        books = connection.execute(
            "SELECT * FROM books WHERE subject = ?",
            (subject,)
        ).fetchall()

    return jsonify([dict(book) for book in books])



@app.route("/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return jsonify({"error": "JSON data is required"}), 400

    updates = []

    if "price" in data:
        price = data["price"]

        if isinstance(price, bool) or not isinstance(price, (int, float)) or price < 0:
            return jsonify({"error": "Price must be a non-negative number"}), 400

        updates.append(("price", price))

    if "quantity" in data:
        quantity = data["quantity"]

        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 0:
            return jsonify({"error": "Quantity must be a non-negative integer"}), 400

        updates.append(("quantity", quantity))

    if not updates:
        return jsonify({"error": "No valid fields to update"}), 400

    columns = ", ".join(f"{column} = ?" for column, value in updates)
    values = [value for column, value in updates]
    values.append(book_id)

    with get_connection() as connection:
        cursor = connection.execute(
            f"UPDATE books SET {columns} WHERE id = ?",
            values
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "Book not found"}), 404

        book = connection.execute(
            "SELECT * FROM books WHERE id = ?",
            (book_id,)
        ).fetchone()

    return jsonify(dict(book))


@app.route("/books/<int:book_id>/purchase", methods=["POST"])
def purchase_book(book_id):
    with get_connection() as connection:
        cursor = connection.execute("""
            UPDATE books
            SET quantity = quantity - 1
            WHERE id = ? AND quantity > 0
        """, (book_id,))

        if cursor.rowcount == 0:
            book = connection.execute(
                "SELECT id FROM books WHERE id = ?",
                (book_id,)
            ).fetchone()

            if book is None:
                return jsonify({"error": "Book not found"}), 404

            return jsonify({
                "error": "Book is out of stock"
            }), 409

        book = connection.execute(
            "SELECT * FROM books WHERE id = ?",
            (book_id,)
        ).fetchone()

    return jsonify(dict(book)), 200


@app.route("/books/<int:book_id>/stock", methods=["PATCH"])
def adjust_stock(book_id):
    """
    Atomically increase or decrease book stock.
    Prevents the quantity from becoming negative.
    """

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "JSON data is required"
        }), 400

    delta = data.get("delta")

    if (
        isinstance(delta, bool)
        or not isinstance(delta, int)
        or delta == 0
    ):
        return jsonify({
            "error": "delta must be a non-zero integer"
        }), 400

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE books
            SET quantity = quantity + ?
            WHERE id = ?
              AND quantity + ? >= 0
            """,
            (delta, book_id, delta)
        )

        if cursor.rowcount == 0:
            book = connection.execute(
                "SELECT id FROM books WHERE id = ?",
                (book_id,)
            ).fetchone()

            if book is None:
                return jsonify({
                    "error": "Book not found"
                }), 404

            return jsonify({
                "error": "Insufficient stock"
            }), 409

        book = connection.execute(
            "SELECT * FROM books WHERE id = ?",
            (book_id,)
        ).fetchone()

    return jsonify(dict(book)), 200




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
