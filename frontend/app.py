
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
        return jsonify(response.json()), response.status_code

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
        return jsonify(response.json()), response.status_code

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
