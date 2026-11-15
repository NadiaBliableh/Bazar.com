
# Bazar.com - Test Results

## 1. Test Environment

- Operating System: Windows 11
- Container Platform: Docker Desktop
- Docker Engine: 29.6.2
- Docker Compose: 5.3.1
- Backend Framework: Python Flask
- Database: SQLite
- Communication: HTTP REST APIs

## 2. Docker Deployment Test

Command:
`docker compose up --build -d`

Result: PASS

All three Docker images were successfully built and the following containers started:

- bazarcom-frontend-1 (Port 5000)
- bazarcom-catalog-1 (Port 5001)
- bazarcom-order-1 (Port 5002)

Verification command:
`docker compose ps`

Result: All three services were running.

## 3. Search Test

Request:
GET /search/Distributed%20Systems

Result: PASS

The system returned two books:

1. How to get a good grade in DOS in 40 minutes a day
2. RPCs for Noobs

Both books belong to the Distributed Systems category.

## 4. Book Information Test

Request:
GET /info/2

Result: PASS

Response:
{
  "id": 2,
  "title": "RPCs for Noobs",
  "price": 12.0,
  "quantity": 10,
  "subject": "Distributed Systems"
}

## 5. Purchase Test

Request:
POST /purchase/2

Result: PASS

Response:

- Book ID: 2
- Book Title: RPCs for Noobs
- Order ID: 1
- Price: 12.0
- Remaining Quantity: 9

The stock decreased from 10 to 9.

## 6. Data Persistence Test

Commands:
`docker compose down`
`docker compose up -d`

Result: PASS

Book 2 quantity before restarting: 9
Book 2 quantity after restarting: 9

SQLite data persisted using Docker named volumes.

## 7. Out-of-Stock Test

The quantity of book 4 was updated to 0.

Request:
POST /purchase/4

Result: PASS

HTTP Status: 409 Conflict

Response:
{"error": "Book is out of stock"}

The system correctly rejected the purchase.

## 8. Concurrent Requests Test

Initial stock for book 4: 2

Five purchase requests were submitted using
PowerShell background jobs.

Results:

- Successful purchases: 2
- Failed purchases: 3
- Final stock: 0

Result: PASS

No overselling was observed during this test.
The test does not guarantee that all requests
started at exactly the same instant.

## 9. Order History Test

Request:
GET /orders

Result: PASS

Three orders were returned:

- Order 1: RPCs for Noobs
- Order 2: Cooking for the Impatient Undergrad
- Order 3: Cooking for the Impatient Undergrad

All three successful purchases were recorded.

## 10. Test Summary

| Test | Status |
|---|---|
| Docker deployment | PASS |
| Service communication | PASS |
| Search | PASS |
| Book information | PASS |
| Purchase | PASS |
| Data persistence | PASS |
| Out-of-stock handling | PASS |
| Concurrent requests | PASS |
| Order history | PASS |

All documented test scenarios passed.

Additional stress testing and failure-recovery
testing are recommended for future improvements.
