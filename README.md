
# Bazar.com - Distributed Online Bookstore

A multi-tier distributed bookstore developed for
the Distributed and Operating Systems (DOS) course.

## 1. Project Overview

Bazar.com is a small online bookstore containing
four books in two categories:

- Distributed Systems
- Undergraduate School

The system allows clients to search for books,
retrieve book information, and purchase books.

It follows a microservices architecture using
HTTP REST APIs.

## 2. System Architecture

The application consists of three independent
microservices:

### Frontend Service (Port 5000)

Receives client requests and forwards them to
the appropriate backend service.

### Catalog Service (Port 5001)

Manages book information, prices, categories,
and available stock.

### Order Service (Port 5002)

Processes purchases, communicates with the
Catalog Service, and records successful orders.

### Communication Flow

Search and information requests:

Client -> Frontend -> Catalog

Purchase requests:

Client -> Frontend -> Order -> Catalog

All services communicate using HTTP REST APIs
and exchange JSON responses.

## 3. Technologies

- Python 3.11
- Flask
- SQLite
- HTTP REST APIs
- Docker
- Docker Compose
- Git and GitHub

## 4. Project Structure

Bazar.com/
- catalog/
  - app.py
  - database.py
  - requirements.txt
  - Dockerfile
- order/
  - app.py
  - database.py
  - requirements.txt
  - Dockerfile
- frontend/
  - app.py
  - requirements.txt
  - Dockerfile
- docs/
  - test-results.md
- docker-compose.yml
- README.md

## 5. How to Run

### Prerequisites

Install:

- Git
- Docker Desktop with Docker Compose

No local Python installation is required.

### Step 1: Clone the Repository

```bash
git clone https://github.com/NadiaBliableh/Bazar.com.git
cd Bazar.com
```

### Step 2: Build and Start

Run the following command from the project root:

```bash
docker compose up --build -d
```

Docker Compose builds and starts all three
microservices in separate Linux containers.

### Step 3: Verify Containers

```bash
docker compose ps
```

All three containers should have an Up status.

### Step 4: Access Services

- Frontend: http://localhost:5000
- Catalog: http://localhost:5001
- Order: http://localhost:5002

## 6. REST API Endpoints

### Frontend API

| Method | Endpoint | Description |
|---|---|---|
| GET | /search/{topic} | Search books |
| GET | /info/{id} | Retrieve book details |
| POST | /purchase/{id} | Purchase a book |

### Catalog API

| Method | Endpoint | Description |
|---|---|---|
| GET | /books | Retrieve all books |
| GET | /books/{id} | Retrieve a book |
| GET | /books/search?subject=... | Search by subject |
| PUT | /books/{id} | Update book information |
| POST | /books/{id}/purchase | Decrease stock |

### Order API

| Method | Endpoint | Description |
|---|---|---|
| POST | /orders | Create an order |
| GET | /orders | Retrieve order history |

## 7. API Testing Examples

### Search Books

Open in a browser:

http://localhost:5000/search/Distributed%20Systems

### Get Book Details

http://localhost:5000/info/2

### Purchase a Book

Run in PowerShell:

```powershell
Invoke-RestMethod -Uri "http://localhost:5000/purchase/2" -Method POST
```

### Check Order History

http://localhost:5002/orders

### Update Book Stock

Run in PowerShell:

```powershell
Invoke-RestMethod -Uri "http://localhost:5001/books/4" -Method PUT -ContentType "application/json" -Body '{"quantity":10}'
```

## 8. Data Persistence

The Catalog and Order services use separate
SQLite databases.

Docker named volumes preserve the databases
when containers are stopped or recreated.

To restart the application:

```bash
docker compose down
docker compose up -d
```

Do not use `docker compose down -v` unless
you intentionally want to delete stored data.

## 9. Concurrency

The application supports multiple HTTP requests.

Catalog stock is decreased using a conditional
SQLite UPDATE operation that prevents quantity
from becoming negative.

A concurrency test with five purchase requests
and an initial stock of two resulted in:

- 2 successful purchases
- 3 rejected purchases
- Final stock: 0

This test demonstrated correct stock handling
for the tested scenario.

## 10. Testing

The application was tested for:

- Docker deployment
- Service communication
- Book searching
- Book information retrieval
- Successful purchases
- Data persistence
- Out-of-stock handling
- Concurrent purchase requests
- Order history

Detailed test results are available in:

`docs/test-results.md`


### Automated Integration Tests

The project includes automated integration tests
in `tests/integration_test.py`.

After starting all services, run the tests from
the project root:

```powershell
docker run --rm --network bazarcom_default -v "${PWD}/tests:/tests:ro" python:3.11-slim python /tests/integration_test.py
```

The test suite checks search, book information,
invalid requests, stock validation, concurrent
purchases, and order recording.

Latest test execution:

- Passed: 10
- Failed: 0

**Note:** The concurrency test creates two real
orders in the SQLite database. It restores the
original book quantity but does not delete the
newly recorded orders.


## 11. Stopping the Application

Stop and remove containers:

```bash
docker compose down
```

Persistent Docker volumes are retained.

## 12. Known Limitations

- The bookstore contains four predefined books.
- No graphical user interface is implemented.
- No authentication or payment system is included.
- Cross-service transactions are not fully atomic.
- A failure between stock decrement and order
  recording may lead to inconsistent data.
- Extensive load and failure-recovery testing
  has not been performed.
- If order recording fails after inventory is
  decremented, the Order Service attempts to
  restore stock through the Catalog Service.
  This is best-effort compensation, not a
  guaranteed distributed transaction.
- The compensation failure scenario has not
  been directly tested.

## 13. Future Improvements

Possible extensions include:

- Automated integration and concurrency tests
- Health checks and retry mechanisms
- Improved distributed transaction handling
- Authentication and authorization
- Inventory management endpoints
- Monitoring and centralized logging
- A graphical user interface

## 14. Documentation

Additional documentation and test results
are stored in the `docs/` directory.
