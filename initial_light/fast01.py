from fastapi import FastAPI
import uvicorn

from fastapi import Request # THE WHAT & WHY?
# --- What: ---
#  `Request` is a Pydantic model that represents an incoming HTTP request.
# It gives you access to request metadata like headers, cookies, path params,
# query params, body (bytes), and more — all via Python attributes.
#
# --- Why use it: ---
# FastAPI auto-parses query params, path params, etc. by type hinting —
# so `Request` is needed only when you want explicit control over something
# that isn't covered by those shortcuts: reading raw headers, checking the
# origin/CORS info, reading a non-JSON body directly as bytes, peeking at
# the ASGI scope, etc.
#
# --- Common patterns: ---
#   @app.get("/x")
#   def x(req: Request):           # injected automatically by DI
#       origin = req.headers.get("origin")
#       return {"origin": origin}

app = FastAPI(
    title="FastAPI Experiments",
    description=(
        "Just playing with FastAPI"
        "OpenAPI?"
        "RESTAPI?"
    ), # why the ','?
    # Python joins adjacent string literals at compile time into ONE string before passing it to the function.
    # Without that comma Python would raise a SyntaxError on the next line (`version="0.0.1"`).
    version="0.0.1",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"

    # docs_url="...something...", WHAT
    # Path where Swagger UI lives. Defaults to "/docs". Set to None to hide it.
    # Example: docs_url="/swagger"  → browser goes to http://localhost:8000/swagger
    #
    # redoc_url="...something...", WHAT
    # Path where ReDoc (alternative docs view) lives. Defaults to "/redoc". Set to None to hide it.
    #
    # openapi_url="/openapi.json"
    # URL that serves the raw OpenAPI schema JSON. FastAPI generates it automatically at runtime.
    # Defaults to "/openapi.json". Set to None to disable schema generation entirely
    #  (useful when behind a reverse proxy that already exposes the schema separately).
    #
    # WHY does all this matter?
    # Every FastAPI app ships with a built-in OpenAPI 3.0 spec at runtime.
    # The "url" settings are just routes where users (and machines) can fetch
    # that spec / interactive docs without the code touching them explicitly.
)

@app.get("/")
def read_root():
    """Root endpoint — Statement of Purpose"""
    # --- Root endpoint means: ---
    # The route mounted at path "/" — the very first thing a visitor sees when they hit the base address.
    # In web architecture "/" is analogous to a home page or front door.
    #
    # In REST terms: it's the top-level resource of the API, often used to
    # expose health / readiness / introduction data.
    return {
        "Puroose": "Learning",
        "Day": "Sun",
        "Status": "Good"
    }

@app.get("/about")
# --- info to be displayed on 'http://127.0.0.1:8080/about' ---
#  When a client sends a GET request to 'http://127.0.0.1:8080/about' ,
# the routing table matches "/about", calls `about()`, and returns whatever
# that function returns (dict → JSON response) inside the HTTP body with
# status 200 and Content-Type: application/json.
#
# If the client navigates there in a browser you'll see a pretty-printed
# JSON payload. If they call the OpenAPI docs endpoint instead, the tool
# will render a full interactive spec for this route.
def about():
    """More Info"""
    return {
        "Location": "Ghaziabad",
        "Time": "IST",
        "version": "0.0.1"
    }


# Study This: Using Request class
#
# WHAT: FastAPI exposes an ASGI `Request` object that wraps the incoming
#       HTTP request. You get direct attribute access to method, URL,
#       headers, cookies, path/query params, and raw body — anything the
#       framework doesn't auto-parse via type hints.
#
# HOW: Add `request: Request` as a typed parameter in your endpoint
#      signature. FastAPI's DI system injects it automatically — no extra
#      boilerplate needed. Access fields like `request.method`,
#      `request.headers["x-custom"]`, `request.query_params`, etc.
#
# WHY: FastAPI's automatic parameter injection (path, query, body) covers
#      the common cases. Use `Request` when you need something those
#      shortcuts don't expose — arbitrary headers, raw body bytes, the
#      full ASGI scope, or when you want to inspect the request before
#      FastAPI processes it.

@app.get("/bug/info")
async def request_info(request: Request):
    """Bug Info"""
    return{
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
        "path_params": request.path_params,
        "query_params": request.query_params
    }


# --- Tags explained ---
#
# WHAT: Tags are string labels you attach to an endpoint's decorator.
#       They have zero effect on routing or request handling — they only
#       shape the auto-generated OpenAPI/Swagger docs.
#
# WHY: Without tags every route appears in one flat list in /docs.
#      With tags FastAPI groups routes by name so Swagger UI renders
#      collapsible sections (e.g. "Restaurant", "User", "Auth").
#      An endpoint can belong to multiple tags by passing a list.
#
# HOW: Pass a list of strings as the `tags` kwarg on any decorator
#      (@app.get, @app.post, etc.):
#
#   @app.get("/restaurant/delhi", tags=["Restaurant"])
#   @app.get("/user/profile",     tags=["User", "Auth"])   # multi-tag
#
# Tagged routes show up under their tag group in the interactive docs.

@app.get("/restaurant/delhi", tags=["Restaurant"])
def list_restro_delhi():
    """another docstring for another endpoint"""
    return {
        "restaurant": [
            {"Bk": "Aloo Tikki"}
        ]
    }



@app.get("/restaurant/up", tags=["Restaurant"])
def list_restro_up():
    """another docstring for another endpoint"""
    return {
        "restaurant": [
            {"M'D": "Aloo Tikki"}
        ]
    }


if __name__ == "__main__":
    # --- Why didn't `__name__ == "__01_fast__"` check work? ---
    # The dunder `__name__` is ALWAYS set to one of two values:
    #   • "__main__"  — when the script is executed directly (python fast01.py)
    #   • "<module>"  — when the script is imported (import fast01)
    #
    # Python does NOT let one invent their own name for the direct-execution case;
    # there is no such thing as "__01_fast__". The string is literally
    # the two characters __ name __ = "__main__".
    # Writing == "__01_fast__" therefore NEVER matched, so uvicorn never started.
    #
    # --- Why did `uvicorn` from the terminal work but `python fast01.py` not? ---
    # Terminal command:
    #     uvicorn fast01:app --host 127.0.0.1 --port 8080 --reload
    #
    # uvicorn is a SERVER. It imports your module, finds the `app` object,
    # and starts listening. It does this regardless of `__name__`. So even
    # when `if __name__` block was broken, uvicorn ran the server fine
    # because it never entered that guard — uvicorn starts directly.
    #
    # Running via python:
    #     python fast01.py
    #
    # In this case uvicorn MUST be started from inside the script itself
    # (inside the `if __name__` block). Since the guard was broken, the
    # process exited immediately after defining `app` — no server started,
    # so nothing was listening on port 8080.
    #
    # Fix: change `__01_fast__` to `__main__`. Then both invocation styles work.
    uvicorn.run("fast01:app", host="127.0.0.1", port=8080, reload=True)


# ============================================================================
# HEADS-UP — FastAPI Pitfalls & Mental Models
# ============================================================================
#
# 1. async def vs def — which one should one use and when?
#    • `async def` runs on the main event loop. Great for I/O-bound work
#      (HTTP calls, DB queries via async drivers). BUT if you call blocking
#      sync code inside it (requests.get, time.sleep, synchronous DB drivers),
#      you BLOCK the entire event loop — every other request stalls.
#    • `def` runs in FastAPI's thread pool automatically. Safe for CPU-bound
#      or blocking sync code; the framework delegates it off the event loop.
#
#     • Rule of thumb: use `def` unless you have a good async library available.
#
# 2. Python's return value → HTTP response
#    Returning a dict/list/str is auto-converted:
#      dict  → 200 + application/json
#      str   → 200 + text/plain
#      None  → 204 No Content
#    For control over status code / headers, return Response objects from
#    fastapi.responses.
#
# 3. Path params vs query params — don't mix!
#    Path: /items/{item_id}  →  captured by path parameter
#    Query: /items?name=abc&age=10  →  captured by function kwargs (keyword argument, eg: name=value)
#    FastAPI reads them from the URL structure, not from arbitrary places.
#
# 4. Type hints are NOT optional — they DO something
#    FastAPI uses type hints for: validation, serialization, and docs.
#    `item_id: int` means "this must be an integer; otherwise return 422".
#    Drop the hint and you drop validation + auto-docs for that parameter.
#
# 5. The app object is another Python object
#    It's possible to mount sub-apps, add middleware, register events — it's all standard Python.
#    `app = FastAPI(...)` is the entry point; everything else hangs off it.
#
# 6. Startup / shutdown events
#    Use @app.on_event("startup") and @app.on_event("shutdown") for
#    one-time setup (DB connections, cache warm-up) and teardown.
#    Modern FastAPI prefers lifespan context managers.
#
# 7. Middleware runs on EVERY request
#    Added via `app.add_middleware(...)`. Order matters — the first one
#    added wraps the outermost layer. Common uses: CORS, auth, logging.
#
# Cross-Origin Resource Sharing(CORS): Cross-Origin Resource Sharing (CORS) is an HTTP-header based security
# mechanism that allows a server to permit a web browser to load resources from a 
# domain, scheme, or port different from the one that served the original page.
#
# 8. /docs and /redoc are FREE
#    They exist because FastAPI generates an OpenAPI schema at runtime.
#    Set docs_url=None / redoc_url=None to disable them in production.
#
# 9. Exceptions → automatic JSON error responses
#    Raise HTTPException(status_code=404, detail="Not found") and FastAPI
#    turns it into a 404 JSON response. Don't return error dicts manually.
#
# 10. reload=True is for development only
#     Uvicorn's --reload watches files and restarts on change. Never use
#     it in production — it adds overhead and can cause state loss.
#
# ============================================================================

