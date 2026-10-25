---
id: py-fleet-mission-api
title: A Fleet Mission API with FastAPI
difficulty: Hard
order: 1
tags: FastAPI, Pydantic, status codes, dependency injection, API keys, app factory, TestClient
time_limit: 20
---
## Statement
Build the fleet manager's HTTP API with **FastAPI** and **Pydantic**. Implement `create_app(api_key: str) -> FastAPI`. Each call returns a fresh app with its own in-memory state. The judge drives it with `fastapi.testclient.TestClient`.

**Models**
- `RobotIn`: `name` is a string of 1–30 characters from `[a-z0-9-]`, and `max_speed` is a float with `0 < max_speed <= 3`.
- A robot in responses: `{"id": int, "name": str, "max_speed": float, "busy": bool}`. Ids start at 1.
- `MissionIn`: `goal` is a list of exactly 2 floats, and `speed` is a float `> 0`.

**Endpoints**

| Method & path | Success | Errors |
|---|---|---|
| `POST /robots` (body `RobotIn`) | **201**, the robot | 409 `"robot name taken"`, 422 invalid body |
| `GET /robots?busy=` | 200, list sorted by id, optionally filtered by `busy` (true/false) | 422 bad query |
| `GET /robots/{robot_id}` | 200 | 404 `"robot not found"`, 422 non-integer id |
| `POST /robots/{robot_id}/missions` (body `MissionIn`) | **201** `{"mission_id", "robot_id", "eta_s"}` | 401 `"invalid api key"`, 404 `"robot not found"`, 409 `"robot busy"`, 400 `"speed exceeds robot limit"`, 422 |
| `POST /missions/{mission_id}/complete` | 200 `{"mission_id", "status": "done"}` | 401, 404 `"mission not found"`, 409 `"mission already done"` |
| `GET /stats` | 200 `{"robots": n, "busy": k, "missions_done": d}` | |

Rules:
- Error bodies are FastAPI's standard `{"detail": "<message>"}`.
- The two `POST …/missions` and `…/complete` endpoints need the header `X-API-Key` equal to `api_key`. Implement this as a **dependency**.
- The API-key check happens before anything else (401 even for an unknown robot), but after request validation.
- Mission ids start at 1. `eta_s = round(hypot(goal_x, goal_y) / speed, 2)`.
- Creating a mission makes the robot busy, and completing it frees the robot.
- Two apps from two `create_app` calls must not share any state.

## Starter
```python
from fastapi import FastAPI
from pydantic import BaseModel


class RobotIn(BaseModel):
    name: str
    max_speed: float


def create_app(api_key: str) -> FastAPI:
    app = FastAPI()
    robots = []

    @app.post("/robots")
    def add_robot(r: RobotIn):
        robots.append(r)
        return {"id": len(robots), **r.model_dump(), "busy": False}

    @app.get("/robots")
    def list_robots():
        return robots

    return app
```

## Driver
```python
import json
import sys
import warnings
warnings.simplefilter("ignore")
from fastapi.testclient import TestClient

def show(label, r, body=True):
    if body and r.status_code != 422:
        print(f"{label}: {r.status_code} {json.dumps(r.json(), sort_keys=True) if r.content else ''}")
    else:
        print(f"{label}: {r.status_code}")

K = {"X-API-Key": "s3cret"}
for cmd in sys.stdin.read().split():
    c = TestClient(create_app("s3cret"))
    if cmd == "robots":
        show("add rover", c.post("/robots", json={"name": "rover-1", "max_speed": 1.5}))
        show("add arm", c.post("/robots", json={"name": "arm", "max_speed": 0.5}))
        show("dup", c.post("/robots", json={"name": "arm", "max_speed": 1}))
        for bad in [{"name": "Rover", "max_speed": 1}, {"name": "", "max_speed": 1}, {"name": "x" * 31, "max_speed": 1},
                    {"name": "ok", "max_speed": 0}, {"name": "ok", "max_speed": 3.5}, {"name": "ok"}, {"name": "a b", "max_speed": 1}]:
            show(f"bad {bad}", c.post("/robots", json=bad))
        show("edge", c.post("/robots", json={"name": "x" * 30, "max_speed": 3}))
        show("list", c.get("/robots"))
        show("get 2", c.get("/robots/2"))
        show("get 9", c.get("/robots/9"))
        show("get abc", c.get("/robots/abc"))
    elif cmd == "missions":
        c.post("/robots", json={"name": "r1", "max_speed": 1.0}); c.post("/robots", json={"name": "r2", "max_speed": 2.0})
        show("no key", c.post("/robots/1/missions", json={"goal": [3, 4], "speed": 0.5}))
        show("wrong key", c.post("/robots/1/missions", json={"goal": [3, 4], "speed": 0.5}, headers={"X-API-Key": "nope"}))
        show("no key unknown robot", c.post("/robots/99/missions", json={"goal": [3, 4], "speed": 0.5}))
        show("create", c.post("/robots/1/missions", json={"goal": [3, 4], "speed": 0.5}, headers=K))
        show("busy", c.post("/robots/1/missions", json={"goal": [1, 1], "speed": 0.5}, headers=K))
        show("too fast", c.post("/robots/2/missions", json={"goal": [1, 1], "speed": 2.5}, headers=K))
        show("unknown robot", c.post("/robots/7/missions", json={"goal": [1, 1], "speed": 1}, headers=K))
        show("bad goal", c.post("/robots/2/missions", json={"goal": [1, 1, 1], "speed": 1}, headers=K))
        show("bad speed", c.post("/robots/2/missions", json={"goal": [1, 1], "speed": -1}, headers=K))
        show("create 2", c.post("/robots/2/missions", json={"goal": [-6, 2.5], "speed": 2}, headers=K))
        show("busy list", c.get("/robots", params={"busy": "true"}))
        show("idle list", c.get("/robots", params={"busy": "false"}))
        show("bad busy", c.get("/robots", params={"busy": "maybe"}))
        show("stats", c.get("/stats"))
        show("complete no key", c.post("/missions/1/complete"))
        show("complete", c.post("/missions/1/complete", headers=K))
        show("again", c.post("/missions/1/complete", headers=K))
        show("missing", c.post("/missions/42/complete", headers=K))
        show("reassign", c.post("/robots/1/missions", json={"goal": [0, 0.5], "speed": 1}, headers=K))
        show("stats", c.get("/stats"))
    elif cmd == "isolation":
        a, b = TestClient(create_app("a")), TestClient(create_app("b"))
        a.post("/robots", json={"name": "only-a", "max_speed": 1})
        show("a list", a.get("/robots")); show("b list", b.get("/robots"))
        show("b key a", b.post("/robots/1/missions", json={"goal": [1, 0], "speed": 1}, headers={"X-API-Key": "a"}))
        show("a key a", a.post("/robots/1/missions", json={"goal": [1, 0], "speed": 1}, headers={"X-API-Key": "a"}))
        show("b stats", b.get("/stats"))
    elif cmd == "load":
        for i in range(300):
            c.post("/robots", json={"name": f"bot-{i}", "max_speed": 0.5 + i % 5 * 0.5})
        codes = {}
        for i in range(1, 301):
            r = c.post(f"/robots/{i}/missions", json={"goal": [i % 17, i % 11], "speed": 0.5 + i % 3 * 0.5}, headers=K)
            codes[r.status_code] = codes.get(r.status_code, 0) + 1
        done = sum(c.post(f"/missions/{m}/complete", headers=K).status_code == 200 for m in range(1, 400, 3))
        print("codes", dict(sorted(codes.items())), "completed", done)
        show("stats", c.get("/stats"))
        print("busy", len(c.get("/robots", params={"busy": True}).json()))
```

## Tests
=== sample
robots
---
add rover: 201 {"busy": false, "id": 1, "max_speed": 1.5, "name": "rover-1"}
add arm: 201 {"busy": false, "id": 2, "max_speed": 0.5, "name": "arm"}
dup: 409 {"detail": "robot name taken"}
bad {'name': 'Rover', 'max_speed': 1}: 422
bad {'name': '', 'max_speed': 1}: 422
bad {'name': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', 'max_speed': 1}: 422
bad {'name': 'ok', 'max_speed': 0}: 422
bad {'name': 'ok', 'max_speed': 3.5}: 422
bad {'name': 'ok'}: 422
bad {'name': 'a b', 'max_speed': 1}: 422
edge: 201 {"busy": false, "id": 3, "max_speed": 3.0, "name": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"}
list: 200 [{"busy": false, "id": 1, "max_speed": 1.5, "name": "rover-1"}, {"busy": false, "id": 2, "max_speed": 0.5, "name": "arm"}, {"busy": false, "id": 3, "max_speed": 3.0, "name": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"}]
get 2: 200 {"busy": false, "id": 2, "max_speed": 0.5, "name": "arm"}
get 9: 404 {"detail": "robot not found"}
get abc: 422
=== hidden
missions
---
no key: 401 {"detail": "invalid api key"}
wrong key: 401 {"detail": "invalid api key"}
no key unknown robot: 401 {"detail": "invalid api key"}
create: 201 {"eta_s": 10.0, "mission_id": 1, "robot_id": 1}
busy: 409 {"detail": "robot busy"}
too fast: 400 {"detail": "speed exceeds robot limit"}
unknown robot: 404 {"detail": "robot not found"}
bad goal: 422
bad speed: 422
create 2: 201 {"eta_s": 3.25, "mission_id": 2, "robot_id": 2}
busy list: 200 [{"busy": true, "id": 1, "max_speed": 1.0, "name": "r1"}, {"busy": true, "id": 2, "max_speed": 2.0, "name": "r2"}]
idle list: 200 []
bad busy: 422
stats: 200 {"busy": 2, "missions_done": 0, "robots": 2}
complete no key: 401 {"detail": "invalid api key"}
complete: 200 {"mission_id": 1, "status": "done"}
again: 409 {"detail": "mission already done"}
missing: 404 {"detail": "mission not found"}
reassign: 201 {"eta_s": 0.5, "mission_id": 3, "robot_id": 1}
stats: 200 {"busy": 2, "missions_done": 1, "robots": 2}
=== hidden
isolation
---
a list: 200 [{"busy": false, "id": 1, "max_speed": 1.0, "name": "only-a"}]
b list: 200 []
b key a: 401 {"detail": "invalid api key"}
a key a: 201 {"eta_s": 1.0, "mission_id": 1, "robot_id": 1}
b stats: 200 {"busy": 0, "missions_done": 0, "robots": 0}
=== hidden
load
---
codes {201: 240, 400: 60} completed 80
stats: 200 {"busy": 160, "missions_done": 80, "robots": 300}
busy 160

## Hints
- Field constraints: `name: str = Field(min_length=1, max_length=30, pattern=r"^[a-z0-9-]+$")`, `max_speed: float = Field(gt=0, le=3)`, `goal: list[float] = Field(min_length=2, max_length=2)`.
- Status codes: `@app.post("/robots", status_code=201)` and `raise HTTPException(409, "robot name taken")`.
- API key dependency: `def require_key(x_api_key: Annotated[str | None, Header()] = None)`. Add it as a parameter, `_: Annotated[None, Depends(require_key)]`, listed **first**.
- Keep the state (dicts and counters) inside `create_app`, so every app gets its own.

## Solution
```python
import math
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field


class RobotIn(BaseModel):
    name: str = Field(min_length=1, max_length=30, pattern=r"^[a-z0-9-]+$")
    max_speed: float = Field(gt=0, le=3)


class Robot(BaseModel):
    id: int
    name: str
    max_speed: float
    busy: bool = False


class MissionIn(BaseModel):
    goal: list[float] = Field(min_length=2, max_length=2)
    speed: float = Field(gt=0)


def create_app(api_key: str) -> FastAPI:
    app = FastAPI(title="Fleet API")
    robots: dict[int, Robot] = {}
    missions: dict[int, dict] = {}
    counters = {"robot": 0, "mission": 0, "done": 0}

    def require_key(x_api_key: Annotated[str | None, Header()] = None) -> None:
        if x_api_key != api_key:
            raise HTTPException(401, "invalid api key")

    def get_robot_or_404(robot_id: int) -> Robot:
        robot = robots.get(robot_id)
        if robot is None:
            raise HTTPException(404, "robot not found")
        return robot

    @app.post("/robots", status_code=201, response_model=Robot)
    def add_robot(body: RobotIn) -> Robot:
        if any(r.name == body.name for r in robots.values()):
            raise HTTPException(409, "robot name taken")
        counters["robot"] += 1
        robot = Robot(id=counters["robot"], **body.model_dump())
        robots[robot.id] = robot
        return robot

    @app.get("/robots", response_model=list[Robot])
    def list_robots(busy: bool | None = None) -> list[Robot]:
        return [r for _, r in sorted(robots.items()) if busy is None or r.busy == busy]

    @app.get("/robots/{robot_id}", response_model=Robot)
    def get_robot(robot_id: int) -> Robot:
        return get_robot_or_404(robot_id)

    @app.post("/robots/{robot_id}/missions", status_code=201)
    def create_mission(_: Annotated[None, Depends(require_key)], robot_id: int, body: MissionIn) -> dict:
        robot = get_robot_or_404(robot_id)
        if robot.busy:
            raise HTTPException(409, "robot busy")
        if body.speed > robot.max_speed:
            raise HTTPException(400, "speed exceeds robot limit")
        counters["mission"] += 1
        mid = counters["mission"]
        missions[mid] = {"robot_id": robot_id, "done": False}
        robot.busy = True
        return {"mission_id": mid, "robot_id": robot_id,
                "eta_s": round(math.hypot(*body.goal) / body.speed, 2)}

    @app.post("/missions/{mission_id}/complete")
    def complete_mission(_: Annotated[None, Depends(require_key)], mission_id: int) -> dict:
        m = missions.get(mission_id)
        if m is None:
            raise HTTPException(404, "mission not found")
        if m["done"]:
            raise HTTPException(409, "mission already done")
        m["done"] = True
        robots[m["robot_id"]].busy = False
        counters["done"] += 1
        return {"mission_id": mission_id, "status": "done"}

    @app.get("/stats")
    def stats() -> dict:
        return {"robots": len(robots), "busy": sum(r.busy for r in robots.values()),
                "missions_done": counters["done"]}

    return app
```

- **Validation lives in the models**: length, character set, numeric bounds and list size are declared once with `Field`, enforced automatically (422), and published in the OpenAPI schema.
- **Precise status codes**: 201 for creation, 404 for unknown resources, 409 for state conflicts (busy robot, duplicate name, double completion), 400 for a valid-but-unacceptable request, 401 for authentication. Clients can react correctly to each.
- **Authentication as a dependency**: declared once and reused, it runs before the endpoint body. In tests or a different deployment it could be swapped with `dependency_overrides`.
- **The app factory** captures state in a closure, so every `create_app` call is isolated. That's exactly what makes the API testable, and it's how you'd inject a real database later.
- **`response_model`** guarantees the response shape and filters out anything internal.
