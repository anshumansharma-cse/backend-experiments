# Code Reflection: `menu01.py`

## 1. Project Overview

**Project:** Read-Only Static Menu API

**Technology:** Python, FastAPI, Pydantic, Uvicorn

**Application version:** `0.0.2`

**GitHub:** `https://github.com/anshumansharma-cse/backend-experiments.git`

`menu01.py` exposes a predefined food and drinks menu through HTTP GET endpoints. This iteration builds on the original static API by separating menu data into `data_file.py`, defining response schemas in `data_models.py`, and adding query- and path-parameter-based filtering and item lookup.

The application is still a static, in-memory menu service: it does not use a database and does not implement create, update, or delete operations.

## 2. Current Implementation (As per *Commit: 091f208*)

### A. FastAPI application configuration

- Initializes the application with the title `Read-Only-Menu`, description, and version `0.0.2`.
- Exposes Swagger UI at `/docs`, ReDoc at `/redoc`, and the OpenAPI schema at `/openapi.json`.
- Runs locally with Uvicorn on `127.0.0.1:8080`, with reload enabled during development.

### B. Root endpoint — `GET /`

Returns a small JSON response describing the purpose of the application and placeholder instructions.

### C. Menu collection endpoint — `GET /menu`

The collection endpoint returns menu records wrapped in `MenuResponse`. It supports optional query parameters:

| Query parameter | Purpose | Example |
|---|---|---|
| `category` | Filter by category | `/menu?category=Indian` |
| `name` | Filter by item name | `/menu?name=Doodh` |
| `type` | Filter by item type | `/menu?type=Food` |
| `source` | Filter by source | `/menu?source=Veg` |
| `available` | Filter by availability | `/menu?available=false` |
| `id` | Filter by item ID | `/menu?id=3` |

Multiple filters can be combined. The filtering logic applies each supplied filter to the current result set, so combined filters use **AND** semantics. For example, `/menu?type=Food&available=true` returns records that match both conditions.

The Python parameter is named `item_type`, while `Query(..., alias="type")` exposes it publicly as `?type=`. The alias is the external API name; it does not rename the Python variable, dictionary key, or Pydantic model field.

Text filters for category, name, type, and source use `.lower()` to compare values without case sensitivity. Availability is checked with `available is not None`, which is important because `False` is a valid filter value and must not cause the filter to be skipped.

The endpoint raises `HTTPException` with status `404` when no records match. The `name` query parameter uses `min_length=1`, so an explicitly empty value such as `/menu?name=` is rejected by FastAPI validation rather than silently behaving like an omitted filter.

### D. Individual item and additional path endpoints

The code also retains path-parameter endpoints:

- `GET /menu/{item_id}` — returns one item by numeric ID, or `404` if no item exists.
- `GET /menu/name/{item_name}` — finds one item by name, case-insensitively.
- `GET /menu/type/{item_type}` — returns a list matching the requested type.
- `GET /menu/source/{item_src}` — returns a list matching the requested source.
- `GET /menu/availability/{item_available}` — returns a list matching the Boolean availability value.

The path-based filters and query-based filters overlap in functionality. They are both present in this learning iteration so that path parameters and query parameters can be practised and compared.

### E. Pydantic response models

The routes use `MenuList`, `MenuResponse`, or `list[MenuList]` as response models. FastAPI uses these response models to validate and shape returned data before serialization. `MenuResponse` wraps the collection with a `count` and an `items` list.

A field such as `status` inside a response model, if included, is part of the JSON response body; it is not automatically the same thing as the actual HTTP status code.

## 3. What I Learned

1. How to configure a FastAPI application and expose its interactive API documentation.
2. How `@app.get()` maps a URL path to a Python endpoint function.
3. The distinction between path parameters (for example, `/menu/1`) and query parameters (for example, `/menu?id=1`).
4. How to declare optional query parameters using `str | None`, `int | None`, and `bool | None`.
5. How `Query(default=None, alias="type")` maps the public query parameter `type` to the internal Python variable `item_type`.
6. How to combine multiple filters by progressively filtering a result list.
7. Why `if available:` is incorrect when `False` is a meaningful filter value, and why `if available is not None:` is needed.
8. Why `.lower()` must be called as `.lower()` rather than referenced as `.lower`.
9. How `min_length=1` can reject an explicitly empty query value such as `?name=`.
10. How FastAPI's automatic validation can return `422 Unprocessable Entity` for invalid parameter types, such as a non-integer ID or an invalid Boolean value.
11. How `HTTPException(status_code=404, ...)` represents a request for which no matching menu record was found.
12. How Pydantic response models define the expected shape of returned data.
13. How a query parameter and a path parameter can perform similar operations while remaining separate endpoint contracts.
14. How manual testing through the browser and `/docs` can verify valid inputs, combined filters, no-match cases, and invalid values.

## 4. Technical Observations, Limitations and Shortcomings

### A. Static, in-memory data

The menu records are imported from `data_file.py`, but they remain predefined Python data. Changes are not persisted to a database, and the API does not implement data-management operations such as create, update, or delete.

### B. Repeated filtering logic and overlapping endpoints

The query-based `/menu` endpoint supports filtering by category, name, type, source, availability, and ID. Separate path-based endpoints repeat some of the same filtering functionality. This is useful for learning both parameter styles, but a production API should choose and document a consistent interface to avoid unnecessary duplication.

### C. Response schema and data contracts

Pydantic response models provide explicit response contracts. The model definitions in `data_models.py` must stay consistent with the keys and types in `data_file.py`. If a dictionary key or schema field is renamed, the filtering code and/or response model may need to be updated too.

### D. Validation is not yet uniform

The `name` query parameter has `min_length=1`, but other text filters currently do not have equivalent constraints. Some conditions use truth value based checks (`if category:`, `if name:`, `if source:`, and `if id:`), while `item_type` and `available` use explicit `is not None` checks. A consistent style such as `is not None` can make the intended handling of omitted and supplied values clearer. In particular, `if id:` skips filtering for `id=0`; using `if id is not None:` would make the intent explicit.

### E. Query parameter alias can be confusing

The external URL parameter is `type`, but the internal Python variable is `item_type`. Consequently, `/menu?type=Food` activates this filter, while `/menu?item_type=Food` does not activate it unless the alias is changed or removed. This is intentional and documented in the code.

### F. Error responses

The collection endpoint returns `404` when the combined filters produce no records. FastAPI can return `422` when a supplied parameter fails type or constraint validation. These are different cases: `404` is produced by the application's no-match logic, while `422` is generated by request validation.

### G. No automated tests yet

The current verification has been performed manually using URLs and the interactive documentation. Automated tests with FastAPI's `TestClient` and pytest would make the behaviour repeatable and guard against regressions.

### H. Code cleanup

The current file contains some commented-out exploratory notes. These can be removed or consolidated once the learning notes are no longer needed. The comments about response models and aliases are useful learning notes, but should be corrected for spelling and kept concise.

## 5. Manual Validation Performed / Suggested

The following cases are useful for checking the current API:

| Request | Expected behaviour |
|---|---|
| `/menu` | Return all menu records |
| `/menu?category=Indian` | Return records in the Indian category |
| `/menu?name=Doodh` | Return the matching item |
| `/menu?name=` | Return `422` due to `min_length=1` |
| `/menu?type=Food` | Return Food records |
| `/menu?source=Veg` | Return records whose source is Veg |
| `/menu?available=true` | Return only available records |
| `/menu?available=false` | Return only unavailable records |
| `/menu?id=3` | Return the collection wrapper containing the matching record |
| `/menu?type=Food&available=true` | Return records satisfying both filters |
| `/menu?id=abc` | Return `422` because `id` must be an integer |
| `/menu?available=maybe` | Return `422` because the Boolean value is invalid |
| `/menu?category=Atlantis` | Return `404` if no records match |
| `/menu/1` | Return one item by path ID |
| `/menu/999` | Return `404` if that ID does not exist |
| `/menu/abc` | Return `422` because the path ID must be an integer |
| `/menu/availability/false` | Return the unavailable items through the separate path endpoint |

The exact number and identity of matching records depend on the current contents of `data_file.py`.

## 6. Proposed Future Improvements

**Phase 1 — Cleanup and consistency**

- Remove obsolete comments.
- Use consistent checks where explicit 'parameter presence' matters.
- Consider whether to retain both query-based and path-based filters or standardize on one approach.

**Phase 2 — Stronger validation**

- Add appropriate constraints.
- Decide how empty strings and whitespace-only strings should be handled.
- Consider whether invalid filter values should return an empty-result `404` or be rejected through explicit validation.

**Phase 3 — Automated tests**

- Add tests using FastAPI's `TestClient` and pytest.
- Test each filter independently and in combinations.
- Test `available=true` and `available=false` explicitly.
- Test empty input, invalid types, no-match cases, response structure, and HTTP status codes.


## 7. Conclusion and Learning Outcome

This iteration moves the Read-Only Static Menu API beyond hardcoded category routes into a more reusable filtering API. The main learning milestone is understanding how FastAPI extracts and validates path and query parameters, how aliases map public parameter names to Python variables, how multiple filters combine, and how response models and HTTP exceptions shape API behaviour.

The application is still intentionally small and static. The next practical step is to clean up the implementation and add automated tests for the behaviour already verified manually.
