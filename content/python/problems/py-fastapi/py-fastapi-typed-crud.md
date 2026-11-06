---
id: py-fastapi-typed-crud
title: Typed CRUD with Request and Response Models
difficulty: Easy
order: 2
tags: FastAPI, Pydantic, response_model, Field constraints, PATCH exclude_unset, 204, OpenAPI
time_limit: 10
---
## Statement
Build a notes API in FastAPI where **types do the work**: request models validate input, and response models decide exactly what leaves the server.

```python
class NoteIn(BaseModel): ...        # title: str, 1..80 chars; body: str = ""; tags: list[str] = [] (max 5 tags,
                                    #   each matching ^[a-z0-9-]{1,20}$)
class NoteUpdate(BaseModel): ...    # same fields, all optional (None by default), same constraints
class NoteOut(BaseModel): ...       # id: int, title, body, tags, version: int
class NoteSummary(BaseModel): ...   # id: int, title: str

def create_app() -> FastAPI: ...
```

Internally each stored note also has an `owner_token: str` (set it to `f"secret-{id}"`). It must **never** appear in a response. Achieve that with `response_model`, not by deleting keys by hand.

| Endpoint | Response |
|---|---|
| `POST /notes` | **201**, `NoteOut` (`version` starts at 1, ids start at 1) |
| `GET /notes` | 200, `list[NoteSummary]` in id order |
| `GET /notes/{note_id}` | 200 `NoteOut`; 404 `{"detail": "note not found"}` |
| `PATCH /notes/{note_id}` | 200 `NoteOut`. Only the fields the client **sent** change (`model_dump(exclude_unset=True)`). Sending `null` for any field is a **422** with `loc` `["body", "<field>"]` (for example, a title can't be removed). `version` increases by 1 on every successful PATCH, even an empty one. |
| `DELETE /notes/{note_id}` | **204** with an empty body; 404 if missing |

Validation errors are FastAPI's automatic **422**. The driver prints the error locations (`loc`) only.

The driver also inspects `app.openapi()`: the component schemas must be named `NoteIn`, `NoteOut`, `NoteSummary` and `NoteUpdate`, and `GET /notes` must declare an array of `NoteSummary`.

## Starter
```python
from fastapi import FastAPI
from pydantic import BaseModel


class NoteIn(BaseModel):
    title: str
    body: str = ""
    tags: list[str] = []


def create_app():
    app = FastAPI()
    notes = {}

    @app.post("/notes")
    def create(note: NoteIn):
        nid = len(notes) + 1
        notes[nid] = {"id": nid, **note.model_dump(), "version": 1, "owner_token": f"secret-{nid}"}
        return notes[nid]

    @app.get("/notes")
    def list_notes():
        return list(notes.values())

    return app
```

## Driver
```python
import json
import sys
import warnings
warnings.simplefilter("ignore")
from fastapi.testclient import TestClient

def show(label, r):
    if r.status_code == 422:
        print(f"{label}: 422 locs={[e['loc'] for e in r.json()['detail']]}")
    elif not r.content:
        print(f"{label}: {r.status_code} <empty>")
    else:
        print(f"{label}: {r.status_code} {json.dumps(r.json(), sort_keys=True)}")

for g in sys.stdin.read().split():
    print("#", g)
    app = create_app()
    c = TestClient(app)
    if g == "crud":
        show("create", c.post("/notes", json={"title": "Groceries", "body": "milk", "tags": ["home", "todo-1"]}))
        show("create2", c.post("/notes", json={"title": "Ideas"}))
        show("list", c.get("/notes"))
        show("get1", c.get("/notes/1"))
        show("get5", c.get("/notes/5"))
        show("get abc", c.get("/notes/abc"))
        show("delete1", c.delete("/notes/1"))
        show("delete1 again", c.delete("/notes/1"))
        show("list", c.get("/notes"))
        show("create3", c.post("/notes", json={"title": "Third"}))
    elif g == "validate":
        for bad in [{}, {"title": ""}, {"title": "x" * 81}, {"title": 5}, {"title": "ok", "tags": ["UPPER"]},
                    {"title": "ok", "tags": ["a", "b", "c", "d", "e", "f"]}, {"title": "ok", "tags": ["x" * 21]},
                    {"title": "ok", "tags": "home"}, {"title": "ok", "body": None}]:
            show(f"bad {json.dumps(bad)[:40]}", c.post("/notes", json=bad))
        show("edge", c.post("/notes", json={"title": "y" * 80, "tags": ["a", "b", "c", "d", "z" * 20]}))
    elif g == "patch":
        c.post("/notes", json={"title": "Plan", "body": "v1", "tags": ["work"]})
        show("patch body", c.patch("/notes/1", json={"body": "v2"}))
        show("patch tags", c.patch("/notes/1", json={"tags": []}))
        show("patch empty", c.patch("/notes/1", json={}))
        show("patch null title", c.patch("/notes/1", json={"title": None}))
        show("patch bad tag", c.patch("/notes/1", json={"tags": ["Bad Tag"]}))
        show("patch title", c.patch("/notes/1", json={"title": "Plan B"}))
        show("patch 404", c.patch("/notes/9", json={"body": "x"}))
        show("get", c.get("/notes/1"))
    elif g == "schema":
        spec = app.openapi()
        print("schemas", sorted(k for k in spec["components"]["schemas"] if k.startswith("Note")))
        lr = spec["paths"]["/notes"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
        print("list response", lr.get("type"), lr.get("items"))
        print("post status", sorted(spec["paths"]["/notes"]["post"]["responses"]))
        print("delete status", sorted(spec["paths"]["/notes/{note_id}"]["delete"]["responses"]))
        out = spec["components"]["schemas"]["NoteOut"]["properties"]
        print("NoteOut fields", sorted(out), "leaks token:", "owner_token" in json.dumps(spec))
        title = spec["components"]["schemas"]["NoteIn"]["properties"]["title"]
        print("title limits", title.get("minLength"), title.get("maxLength"))
```

## Tests
=== sample
crud
---
# crud
create: 201 {"body": "milk", "id": 1, "tags": ["home", "todo-1"], "title": "Groceries", "version": 1}
create2: 201 {"body": "", "id": 2, "tags": [], "title": "Ideas", "version": 1}
list: 200 [{"id": 1, "title": "Groceries"}, {"id": 2, "title": "Ideas"}]
get1: 200 {"body": "milk", "id": 1, "tags": ["home", "todo-1"], "title": "Groceries", "version": 1}
get5: 404 {"detail": "note not found"}
get abc: 422 locs=[['path', 'note_id']]
delete1: 204 <empty>
delete1 again: 404 {"detail": "note not found"}
list: 200 [{"id": 2, "title": "Ideas"}]
create3: 201 {"body": "", "id": 3, "tags": [], "title": "Third", "version": 1}
=== hidden
validate
---
# validate
bad {}: 422 locs=[['body', 'title']]
bad {"title": ""}: 422 locs=[['body', 'title']]
bad {"title": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxx: 422 locs=[['body', 'title']]
bad {"title": 5}: 422 locs=[['body', 'title']]
bad {"title": "ok", "tags": ["UPPER"]}: 422 locs=[['body', 'tags', 0]]
bad {"title": "ok", "tags": ["a", "b", "c", : 422 locs=[['body', 'tags']]
bad {"title": "ok", "tags": ["xxxxxxxxxxxxxx: 422 locs=[['body', 'tags', 0]]
bad {"title": "ok", "tags": "home"}: 422 locs=[['body', 'tags']]
bad {"title": "ok", "body": null}: 422 locs=[['body', 'body']]
edge: 201 {"body": "", "id": 1, "tags": ["a", "b", "c", "d", "zzzzzzzzzzzzzzzzzzzz"], "title": "yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy", "version": 1}
=== hidden
patch
---
# patch
patch body: 200 {"body": "v2", "id": 1, "tags": ["work"], "title": "Plan", "version": 2}
patch tags: 200 {"body": "v2", "id": 1, "tags": [], "title": "Plan", "version": 3}
patch empty: 200 {"body": "v2", "id": 1, "tags": [], "title": "Plan", "version": 4}
patch null title: 422 locs=[['body', 'title']]
patch bad tag: 422 locs=[['body', 'tags', 0]]
patch title: 200 {"body": "v2", "id": 1, "tags": [], "title": "Plan B", "version": 5}
patch 404: 404 {"detail": "note not found"}
get: 200 {"body": "v2", "id": 1, "tags": [], "title": "Plan B", "version": 5}
=== hidden
schema
---
# schema
schemas ['NoteIn', 'NoteOut', 'NoteSummary', 'NoteUpdate']
list response array {'$ref': '#/components/schemas/NoteSummary'}
post status ['201', '422']
delete status ['204', '422']
NoteOut fields ['body', 'id', 'tags', 'title', 'version'] leaks token: False
title limits 1 80

## Hints
- Put the constraints in the models: `Field(min_length=1, max_length=80)`, `list[Annotated[str, Field(pattern=...)]]` with `Field(max_length=5)` on the list.
- `@app.post(..., status_code=201, response_model=NoteOut)`. Returning the internal dict is fine: the response model filters out `owner_token`.
- In PATCH, `changes.model_dump(exclude_unset=True)` gives only the fields that were sent. Reject an explicit `None` with a 422, then update and bump `version`.

## Solution
**Separate models for separate jobs.**
- `NoteIn` validates what clients may send.
- `NoteUpdate` has the same constraints, but every field is optional, for PATCH.
- `NoteOut` and `NoteSummary` define what clients receive.

Storing extra internal fields (`owner_token`) is then safe: `response_model` validates the returned dict against the output model and **drops** anything not declared. The secret can't leak even if a developer returns the raw record. The same declaration feeds the OpenAPI schema, so the docs list exactly the public fields.

**Constraints in types.** `Annotated[str, Field(pattern=...)]` on the list item type validates every tag, and `Field(max_length=5)` on the list bounds its size. Pydantic reports each failure with a precise `loc` such as `["body", "tags", 0]`.

**PATCH semantics.** `model_dump(exclude_unset=True)` contains only the keys the client actually sent. That's how you tell "not sent" (keep the old value) from "sent as null" (rejected here, since a note always has a title).

**204 No Content.** Declare `status_code=204` and return an empty `Response`. A 204 must not have a body.

Complexity: O(1) per single-note operation, O(n log n) to list.

```python
from typing import Annotated

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field

Tag = Annotated[str, Field(pattern=r"^[a-z0-9-]{1,20}$")]
Title = Annotated[str, Field(min_length=1, max_length=80)]


class NoteIn(BaseModel):
    title: Title
    body: str = ""
    tags: list[Tag] = Field(default_factory=list, max_length=5)


class NoteUpdate(BaseModel):
    title: Title | None = None
    body: str | None = None
    tags: list[Tag] | None = Field(default=None, max_length=5)


class NoteOut(BaseModel):
    id: int
    title: str
    body: str
    tags: list[str]
    version: int


class NoteSummary(BaseModel):
    id: int
    title: str


def create_app():
    app = FastAPI(title="Notes")
    notes: dict[int, dict] = {}
    counter = [0]

    def get_or_404(note_id: int) -> dict:
        if note_id not in notes:
            raise HTTPException(404, "note not found")
        return notes[note_id]

    @app.post("/notes", status_code=201, response_model=NoteOut)
    def create(note: NoteIn):
        counter[0] += 1
        nid = counter[0]
        notes[nid] = {"id": nid, **note.model_dump(), "version": 1, "owner_token": f"secret-{nid}"}
        return notes[nid]

    @app.get("/notes", response_model=list[NoteSummary])
    def list_notes():
        return [notes[k] for k in sorted(notes)]

    @app.get("/notes/{note_id}", response_model=NoteOut)
    def get_note(note_id: int):
        return get_or_404(note_id)

    @app.patch("/notes/{note_id}", response_model=NoteOut)
    def patch_note(note_id: int, changes: NoteUpdate):
        note = get_or_404(note_id)
        sent = changes.model_dump(exclude_unset=True)
        if "title" in sent and sent["title"] is None:
            raise HTTPException(422, [{"loc": ["body", "title"], "msg": "title cannot be null", "type": "value_error"}])
        if sent.get("body", "") is None:
            raise HTTPException(422, [{"loc": ["body", "body"], "msg": "body cannot be null", "type": "value_error"}])
        if "tags" in sent and sent["tags"] is None:
            raise HTTPException(422, [{"loc": ["body", "tags"], "msg": "tags cannot be null", "type": "value_error"}])
        note.update(sent)
        note["version"] += 1
        return note

    @app.delete("/notes/{note_id}", status_code=204)
    def delete_note(note_id: int):
        get_or_404(note_id)
        del notes[note_id]
        return Response(status_code=204)

    return app
```
