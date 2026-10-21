# Code Reflection: `main.py` — Seller-Pin API

## 1. Project Overview

**Project:** Seller-Pin — Pincode Lookup API

**Technology:** Python, FastAPI, Pydantic, Uvicorn

**Application version:** `0.0.2`

**GitHub:** `https://github.com/anshumansharma-cse/backend-experiments.git`

Seller-Pin exposes a small, predefined collection of Indian pincode records through a FastAPI application. This iteration separates the data, Pydantic models, and custom exceptions into individual files. It supports looking up one pincode, looking up multiple pincodes in a single POST request, validating incoming data, and returning custom JSON errors for invalid or unknown pincodes.

The API currently uses static, in-memory data. It does not connect to a database or persist changes.

## 2. Current Implementation

### A. Project structure

The implementation is split across these files:

| File               | Responsibility                                                               |
| ------------------ | ---------------------------------------------------------------------------- |
| `main.py`          | Creates the FastAPI app, registers exception handlers, and defines endpoints |
| `data.py`          | Stores the predefined `pin_data` dictionary                                  |
| `models.py`        | Defines Pydantic request/response models and a field validator               |
| `exceptions.py`    | Defines custom exception classes and their JSON response handlers            |
| `requirements.txt` | Declares `fastapi[standard]`                                                 |

### B. FastAPI application configuration

- Creates the application with the title `Seller Pincode Dashboard` and version `0.0.2`.
- Exposes Swagger UI at `/docs`, ReDoc at `/redoc`, and the OpenAPI schema at `/openapi.json`.
- Runs locally with Uvicorn on `127.0.0.1:8080`, with reload enabled during development.

### C. Root endpoint — `GET /`

Returns a small JSON object describing the purpose of the API. It is a simple health/landing-style endpoint rather than a pincode lookup.

### D. Single-pincode lookup — `GET /pincode/{pin}`

The endpoint accepts a pincode as a path parameter.

Its logic is:

1. Check that the supplied value contains exactly six digits.
2. Raise `InvalidPinError` if the format is invalid.
3. Check whether the pincode exists in `pin_data`.
4. Raise `PinNotFoundError` if the format is valid but the pincode is not in the local dataset.
5. Return the matching record when it exists.

The endpoint declares `response_model=PinResponse`, whose fields are `pincode`, `city`, `state`, and `district`.

These cases are intentionally different: a malformed pincode is a format error, while a correctly formatted pincode that is absent from the local dataset is a not-found case.

### E. Bulk lookup — `POST /bulk`

The bulk endpoint accepts a JSON request body using `BulkRequest`, with a `pincodes` list.

Example request:

```json
{
  "pincodes": ["110001", "400001", "201301"]
}
```

The endpoint iterates through the submitted pincodes and separates them into:

- `results`: records found in `pin_data`
- `missing`: valid-format pincodes that are not present in `pin_data`

It returns a `BulkResponse` containing `found`, `not_found`, `results`, and `missing`. The model also defines a `status` field with a default value of `200`.

The request model validates that the list is not empty, contains no more than 20 entries, and that every entry has exactly six digits. As a result, a badly formatted pincode in the bulk request is rejected during request validation rather than being placed in `missing`.

### F. Pydantic models

`models.py` defines four models:

- `PinRequest`: contains a `pincode` field and a `@field_validator` that checks its six-digit format.
- `PinResponse`: defines the fields returned for a single location record.
- `BulkRequest`: defines and validates the list of pincodes supplied to `POST /bulk`.
- `BulkResponse`: defines the bulk lookup result, including counts, found records, and missing pincodes.

The `PinRequest` validator is defined with `@field_validator("pincode")` and `@classmethod`. The validator raises `ValueError` when the format is invalid and returns the original value otherwise. The current single-lookup path endpoint performs its own format check directly, so `PinRequest` is not the request model used by that endpoint.

### G. Custom exceptions and handlers

`exceptions.py` defines two custom exception classes:

- `PinNotFoundError`: carries the pincode that was not found in the local dataset.
- `InvalidPinError`: carries the pincode and a reason describing the format error.

`main.py` registers handlers for both exception types.

| Exception          |  Handler response | Meaning                                         |
| ------------------ | ----------------: | ----------------------------------------------- |
| `InvalidPinError`  | `400 Bad Request` | The pincode format is invalid                   |
| `PinNotFoundError` |   `404 Not Found` | The pincode is not present in the local dataset |

The handlers return JSON bodies with an `error` identifier, a human-readable `message`, and the relevant `pin`. These custom handlers apply to the registered exception types; they do not automatically handle unrelated programming errors.

### H. HTTP methods and testing workflow

The single lookup uses `GET`, while bulk lookup uses `POST` because it accepts a JSON request body.

Opening a URL directly in a browser normally performs a `GET` request. Therefore, navigating to `/bulk` in the address bar does not invoke the `POST /bulk` route and can return `405 Method Not Allowed`.

For the bulk endpoint, use an API request client such as Postman or RequestKit, or use Swagger UI at `/docs`. Send a `POST` request with a JSON body and the appropriate `Content-Type: application/json` header.

## 3. What I Learned

1. How to divide a small FastAPI application into data, model, exception, and endpoint modules.
2. How `@app.get()` and `@app.post()` register path operations for different HTTP methods.
3. How path parameters work in a route such as `/pincode/{pin}`.
4. How a POST request can accept a JSON body through a Pydantic request model.
5. How `BulkRequest` and `BulkResponse` serve different purposes: one validates input and the other defines output.
6. How Pydantic's `@field_validator` can enforce custom rules on model fields.
7. How `@classmethod` provides the `cls` parameter in a class method used by the validator.
8. How to define custom exception classes and attach exception handlers to a FastAPI app.
9. How to distinguish a format error (`400`) from a lookup miss (`404`).
10. Why an invalid request body can produce a FastAPI/Pydantic validation response, commonly `422`, before the endpoint function runs.
11. Why a `405 Method Not Allowed` response can occur when the URL is correct but the HTTP method does not match the route.
12. Why a response model should describe the returned data rather than be reused as the request model.
13. How a bulk operation can separate found records from missing records and return counts for both groups.
14. How an API client and Swagger UI can send POST requests that cannot be reproduced simply by typing the endpoint URL into the browser address bar.

## 4. Technical Observations, Limitations and Shortcomings

### A. Static, in-memory dataset

The pincode records live in `data.py`. The application does not query an official or live postal database, and the records are not persisted in a database. A correctly formatted pincode absent from this dictionary is reported as not found by this application; that does not prove the pincode is invalid in the real world.

### B. Validation logic is duplicated

The six-digit format check exists in the `PinRequest` field validator and separately in the `fetch_pin` endpoint. This is acceptable for a learning iteration, but repeated validation logic can drift if one copy changes and the other does not. A future cleanup could reuse a shared validation function or use a request/model design that centralizes the rule.

### C. Bulk request validation rejects malformed entries

`BulkRequest` validates every pincode before `bulk_pin` executes. If even one item has the wrong format, the whole request is rejected. This is different from a valid-format pincode that simply does not exist in `pin_data`, which is collected in `missing`.

The current behaviour is an all-or-nothing validation policy for input format. A future design could deliberately choose per-item validation if partial processing of malformed entries is desired.

### D. Custom handlers are intentionally narrow

The custom handlers cover `InvalidPinError` and `PinNotFoundError`. They do not convert every possible exception into a custom client error. Unexpected errors such as an `AttributeError` should generally remain visible during development and be investigated rather than being mislabeled as a `400` or `404`.

### E. `PinRequest` is not currently used by the lookup route

The `GET /pincode/{pin}` route receives `pin: str` and checks the format directly. `PinRequest` exists as a model with a field validator, but it is not the request model for this path operation. Keeping both may be useful for learning, though the project should eventually make the intended validation path clear.

### F. `status` in `BulkResponse` is not the HTTP status code

`BulkResponse.status` is a field in the returned JSON body and defaults to `200`. It does not itself set the HTTP response status. The actual HTTP status is controlled by FastAPI/the response object and route behaviour. Keeping a body-level status field is a design choice, but it can duplicate information already available in the HTTP response.

### G. No automated tests yet

The current checks have been explored manually through API requests and Swagger UI. Automated tests using FastAPI's `TestClient` and pytest would make the expected results repeatable and help prevent regressions.

### H. Exploratory comments and naming cleanup

`main.py` and `models.py` contain spelling mistakes and commented-out exploratory code. These are normal during learning, but can be removed or consolidated before treating the repository as a polished project. Names and comments should consistently distinguish request models, response models, path operations, and exception handlers.

## 5. Manual Validation Performed / Suggested

Use an API request client for `POST /bulk`. The table below records expected behaviour based on the current code; cases marked as suggested should be run to verify the implementation.

| Request                                              | Expected behaviour                                                |
| ---------------------------------------------------- | ----------------------------------------------------------------- |
| `GET /`                                              | `200` with the root JSON response                                 |
| `GET /pincode/110001`                                | `200` with the New Delhi record                                   |
| `GET /pincode/201301`                                | `200` with the Noida record                                       |
| `GET /pincode/123`                                   | `400` via `InvalidPinError` handler                               |
| `GET /pincode/999999`                                | `404` via `PinNotFoundError` handler                              |
| `POST /bulk` with `{"pincodes":["110001","400001"]}` | `200` with two found records                                      |
| `POST /bulk` with `{"pincodes":["110001","999999"]}` | `200` with one found record and `999999` in `missing`             |
| `POST /bulk` with `{"pincodes":[]}`                  | `422` because the list must not be empty                          |
| `POST /bulk` with more than 20 pincodes              | `422` because the list exceeds the limit                          |
| `POST /bulk` with `{"pincodes":["123"]}`             | `422` because the request model rejects the format                |
| `GET /bulk`                                          | `405 Method Not Allowed` because the route is registered for POST |
| `POST /bulk` with malformed JSON                     | `422` for request-body parsing/validation failure                 |

The response for a bulk request depends on the current contents of `data.py`. The status expectations above assume the exception handlers and request validators are registered as shown in the current source.

## 6. Proposed Future Improvements

**Phase 1 — Cleanup and consistency**

- Correct spelling mistakes in comments and exception messages.
- Remove obsolete commented-out validator experiments once their lessons have been captured.
- Decide whether to centralize the six-digit validation rule.
- Decide whether the `status` field belongs in `BulkResponse`.

**Phase 2 — Clearer API contracts**

- Keep request and response models distinct.
- Document that the bulk request is all-or-nothing for malformed input.
- Keep the distinction between an invalid format and a pincode missing from the local dataset.
- Continue using an API request client for POST requests and Swagger UI for schema exploration.

**Phase 3 — Automated tests**

- Add tests using FastAPI's `TestClient` and pytest.
- Test known, unknown, and malformed single pincodes.
- Test bulk requests with all-found, partially missing, empty, oversized, and malformed lists.
- Verify response JSON structure and HTTP status codes.
- Test that `GET /bulk` returns `405` while `POST /bulk` is accepted.

**Phase 4 — More realistic data and operations**

- Consider replacing the in-memory dictionary with a database or a maintained data source.
- Add structured logging for unexpected errors.
- Add deployment configuration once the API behaviour is stable.

## 7. Conclusion and Learning Outcome

Seller-Pin is a small backend experiment that moves beyond basic GET routes by introducing request-body handling, Pydantic validation, bulk processing, and custom exception handlers. The main learning milestone is understanding how FastAPI routes requests by HTTP method, how request and response models serve different contracts, and how validation failures differ from application-level lookup errors.

The project remains intentionally small and uses a local dictionary rather than a database. The next useful step is to clean up the validation and exception definitions, then add automated tests for the status codes and response shapes already explored manually.
