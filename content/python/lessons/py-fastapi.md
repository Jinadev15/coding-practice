# FastAPI

FastAPI is the dominant modern Python framework for **HTTP APIs**: ML model serving, robot fleet management back ends, internal tools. It builds on **Starlette** (ASGI web toolkit) and **Pydantic** (validation via type hints), so endpoint signatures double as validation rules and as automatically generated OpenAPI documentation. This lesson covers path and query parameters, request and response models, status codes and errors, dependency injection, lifespan state, async vs sync endpoints, testing with `TestClient`, and production concerns.

## 1. A first API

```python
from fastapi import FastAPI

app = FastAPI(title="Fleet API", version="1.0")

@app.get("/robots/{robot_id}")
def get_robot(robot_id: int, verbose: bool = False):
    return {"id": robot_id, "verbose": verbose}
```

Run it with `uvicorn fleet:app --reload`, then open `/docs` for interactive Swagger UI generated from the code.
- `robot_id: int` is a **path parameter**: `/robots/abc` gets an automatic **422** with a precise error.
- `verbose: bool = False` is a **query parameter** (`?verbose=true`).
- The return value is serialised to JSON.

## 2. Request and response models

```python
from pydantic import BaseModel, Field
from typing import Literal

class MissionIn(BaseModel):
    robot_id: int = Field(gt=0)
    goal: tuple[float, float]
    priority: Literal["low", "normal", "high"] = "normal"
    max_speed: float = Field(default=0.5, gt=0, le=2.0)       # m/s, validated

class MissionOut(BaseModel):
    id: int
    robot_id: int
    status: str

@app.post("/missions", response_model=MissionOut, status_code=201)
def create_mission(m: MissionIn) -> MissionOut:
    mid = store.add(m)
    return MissionOut(id=mid, robot_id=m.robot_id, status="queued")
```

- A Pydantic-model parameter is read from the **JSON body** and validated. Wrong types, missing fields and out-of-range values all give 422 with field-level details.
- `response_model` **filters** the output to the declared fields. That's a security feature: an internal `password_hash` attribute can't leak.

## 3. Errors and status codes

```python
from fastapi import HTTPException, status

@app.get("/robots/{robot_id}")
def get_robot(robot_id: int):
    robot = db.get(robot_id)
    if robot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"robot {robot_id} not found")
    return robot
```

Use the right codes:
- 201 for created, 204 for no content.
- 400 for a semantically bad request, 401 for not authenticated, 403 for not allowed.
- 404 for missing, 409 for a conflict (a duplicate, or a robot already on a mission), 422 for a validation failure.

Custom exception handlers (`@app.exception_handler(MyDomainError)`) map domain exceptions to responses in one place.

## 4. Dependency injection

`Depends` declares what an endpoint needs. FastAPI resolves it per request: authentication, database sessions, settings, pagination.

```python
from fastapi import Depends, Header
from typing import Annotated

def require_api_key(x_api_key: Annotated[str | None, Header()] = None) -> str:
    if x_api_key not in VALID_KEYS:
        raise HTTPException(401, "invalid or missing API key")
    return x_api_key

def get_db():
    db = SessionLocal()
    try:
        yield db                      # code after yield runs after the response (cleanup)
    finally:
        db.close()

@app.delete("/robots/{robot_id}", status_code=204)
def delete_robot(robot_id: int, key: Annotated[str, Depends(require_api_key)], db=Depends(get_db)):
    ...
```

- The `X-API-Key` header maps to the `x_api_key` parameter, with underscores converted.
- Dependencies can depend on other dependencies, are cached per request, and can be **overridden in tests**: `app.dependency_overrides[get_db] = lambda: fake_db`.

## 5. Application factory and state

Build the app in a function so each test gets a fresh, isolated instance:

```python
from contextlib import asynccontextmanager

def create_app(store=None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.store = store or InMemoryStore()      # startup: open pools, load ML models
        yield
        app.state.store.close()                         # shutdown

    app = FastAPI(lifespan=lifespan)
    app.include_router(robots_router, prefix="/robots", tags=["robots"])   # APIRouter modules
    return app
```

## 6. async vs sync endpoints

- `async def` endpoints run on the event loop. Use them for non-blocking I/O (`await httpx`, async database drivers). **Never** call blocking code (`time.sleep`, `requests`, heavy NumPy work) inside them: it freezes every request.
- Plain `def` endpoints run in a thread pool, which is safe for blocking libraries.
- CPU-heavy ML inference belongs in a process pool, a separate worker service, or a GPU server such as Triton or TorchServe.

## 7. Testing

```python
from fastapi.testclient import TestClient

def test_create_mission():
    with TestClient(create_app()) as client:          # `with` runs lifespan startup/shutdown
        r = client.post("/missions", json={"robot_id": 1, "goal": [3, 4]})
        assert r.status_code == 201 and r.json()["status"] == "queued"
        assert client.post("/missions", json={"robot_id": 0, "goal": [3, 4]}).status_code == 422
```

`TestClient` calls the ASGI app in-process (via httpx), with no server or network, so tests are fast and deterministic.

## 8. Production checklist

- Serve with `uvicorn` workers (or `gunicorn -k uvicorn.workers.UvicornWorker`) behind a reverse proxy (nginx, Traefik) that terminates TLS.
- Use OAuth2/JWT (`fastapi.security`) for user auth and API keys for machines. Configure CORS (`CORSMiddleware`) deliberately.
- Load settings from the environment with `pydantic-settings`. Never commit secrets.
- Add structured logging, request IDs, `/healthz` and `/readyz` endpoints, Prometheus metrics, and rate limiting.
- Version the API (`/v1/...`) and evolve it compatibly: add optional fields, never repurpose existing ones.

> [!EXAM]
> **How does FastAPI use type hints, and why is dependency injection valuable?**
> Each endpoint parameter's annotation and default decide where it comes from (path, query, header, or JSON body for Pydantic models) and how it's validated and converted. Invalid input automatically gets a 422 with field-level errors, and the same metadata generates the OpenAPI schema and docs. Dependency injection (`Depends`) declares an endpoint's requirements, such as authentication, database sessions and settings, as reusable functions resolved per request, with cleanup via `yield`. That removes duplicated boilerplate, keeps endpoints focused on logic, and makes testing easy, because dependencies can be swapped with `dependency_overrides`.
