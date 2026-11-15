
import os
import requests

from flask import Flask, jsonify

app = Flask(__name__)

CATALOG_URL = os.environ.get(
    "CATALOG_URL",
    "http://127.0.0.1:5001"
)

ORDER_URL = os.environ.get(
    "ORDER_URL",
    "http://127.0.0.1:5002"
)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "service": "Front-end Service",
        "status": "running"
    })


@app.route("/search/<string:topic>", methods=["GET"])
def search(topic):
    try:
        response = requests.get(
            f"{CATALOG_URL}/books/search",
            params={"subject": topic},
            timeout=5
        )
        
        books = response.json()

        print(f"\nSearch results for: {topic}", flush=True)

        if isinstance(books, list):
            for book in books:
                print(
                    f"ID: {book['id']} | "
                    f"Title: {book['title']} | "
                    f"Price: ${book['price']} | "
                    f"Quantity: {book['quantity']}",
                    flush=True
                )
        else:
            print(books, flush=True)

        return jsonify(books), response.status_code


    except requests.RequestException:
        return jsonify({
            "error": "Catalog Service is unavailable"
        }), 503


@app.route("/info/<int:item_number>", methods=["GET"])
def info(item_number):
    try:
        response = requests.get(
            f"{CATALOG_URL}/books/{item_number}",
            timeout=5
        )
        
        book = response.json()

        print(f"\nBook information for ID {item_number}:", flush=True)

        if response.status_code == 200:
            print(
                f"Title: {book['title']}\n"
                f"Subject: {book['subject']}\n"
                f"Price: ${book['price']}\n"
                f"Quantity: {book['quantity']}",
                flush=True
            )
        else:
            print(book, flush=True)

        return jsonify(book), response.status_code


    except requests.RequestException:
        return jsonify({
            "error": "Catalog Service is unavailable"
        }), 503


@app.route("/purchase/<int:item_number>", methods=["POST"])
def purchase(item_number):
    try:
        response = requests.post(
            f"{ORDER_URL}/orders",
            json={"book_id": item_number},
            timeout=10
        )
        return jsonify(response.json()), response.status_code

    except requests.RequestException:
        return jsonify({
            "error": "Order Service is unavailable"
        }), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
