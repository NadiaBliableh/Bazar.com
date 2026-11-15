
import json
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor

FRONTEND = "http://frontend:5000"
CATALOG = "http://catalog:5001"
ORDER = "http://order:5002"

passed = 0
failed = 0


def api(method, url, data=None):
    body = json.dumps(data).encode() if data is not None else None

    request = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return response.status, json.load(response)

    except urllib.error.HTTPError as error:
        return error.code, json.load(error)


def check(name, condition):
    global passed, failed

    if condition:
        passed += 1
        print(f"PASS: {name}")
    else:
        failed += 1
        print(f"FAIL: {name}")


print("\n=== BAZAR.COM INTEGRATION TESTS ===\n")

# Test 1: Search
status, books = api(
    "GET",
    FRONTEND + "/search/Distributed%20Systems"
)
check(
    "Search books",
    status == 200 and len(books) == 2
)

# Test 2: Book information
status, book = api("GET", FRONTEND + "/info/1")
check(
    "Book information",
    status == 200 and book["id"] == 1
)

# Test 3: Invalid book
status, result = api("GET", FRONTEND + "/info/999")
check(
    "Book not found",
    status == 404
)

# Test 4: Invalid stock update
status, result = api(
    "PATCH",
    CATALOG + "/books/4/stock",
    {"delta": -1000}
)
check(
    "Prevent negative stock",
    status == 409
)

# Test 5: Invalid order
status, result = api(
    "POST",
    ORDER + "/orders",
    {"book_id": -1}
)
check(
    "Reject invalid order",
    status == 400
)

# Test 6: Concurrent purchases
# Save original stock and restore it after testing.
status, original = api("GET", CATALOG + "/books/4")
original_quantity = original["quantity"]

try:
    api(
        "PUT",
        CATALOG + "/books/4",
        {"quantity": 2}
    )

    status, orders_before = api("GET", ORDER + "/orders")
    before_count = len(orders_before)

    def purchase(_):
        return api(
            "POST",
            FRONTEND + "/purchase/4"
        )

    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(purchase, range(5)))

    successful = sum(
        1 for status, _ in results if status == 201
    )

    rejected = sum(
        1 for status, _ in results if status == 409
    )

    status, book_after = api(
        "GET",
        CATALOG + "/books/4"
    )

    status, orders_after = api(
        "GET",
        ORDER + "/orders"
    )

    check(
        "Concurrent purchases: 2 successes",
        successful == 2
    )

    check(
        "Concurrent purchases: 3 rejected",
        rejected == 3
    )

    check(
        "Stock does not become negative",
        book_after["quantity"] == 0
    )

    check(
        "Successful orders recorded",
        len(orders_after) - before_count == 2
    )

finally:
    status, restored = api(
        "PUT",
        CATALOG + "/books/4",
        {"quantity": original_quantity}
    )
    check(
        "Restore original test stock",
        status == 200
        and restored["quantity"] == original_quantity
    )

print("\n=== TEST SUMMARY ===")
print("Passed:", passed)
print("Failed:", failed)
print("Total:", passed + failed)

if failed:
    raise SystemExit(1)
