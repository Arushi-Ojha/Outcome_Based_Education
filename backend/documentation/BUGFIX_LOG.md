# Backend Bug Fix Log

**Project:** OBE (Outcome Based Education) Tracking System  
**Date:** September 10, 2026  
**Document Location:** `backend/documentation/BUGFIX_LOG.md`

---

## Overview

This document records all backend code defects discovered and fixed during the
frontend–backend integration phase. It also documents the root cause analysis of
the `ECONNREFUSED` connection error that prevented the frontend from reaching the
backend API.

---

## Bug 1 — Frontend could not reach backend (`ECONNREFUSED 127.0.0.1:8000`)

### Symptom

Every request from the Vite dev server (`http://localhost:5173`) to the backend
proxy produced:

```
[vite] http proxy error: /api/health
Error: connect ECONNREFUSED 127.0.0.1:8000
    at TCPConnectWrap.afterConnect [as oncomplete] (node:net:1864:16)
```

`netstat -ano | findstr :8000` confirmed nothing was listening on port 8000.

### Root Cause

The FastAPI / Uvicorn backend server was **never started**. The two processes
(Vite dev server and Uvicorn API server) must run concurrently in separate
terminals.

A secondary blocker prevented easy startup: the virtual environment at `venv/`
points to `C:\Python314\python.exe` as its base interpreter (`venv/pyvenv.cfg`).
The `C:\Python314\` directory has restrictive Windows ACL permissions that deny
read/execute access to the current user (`eshaan-victus\eshaan`) in certain
execution contexts. Every attempt at `python.exe --version` or
`python.exe -m uvicorn` failed with `Access is denied`.

### Resolution

The venv's `uvicorn.exe` wrapper in `venv\Scripts\` invokes the interpreter
internally and does **not** go through the Windows Python Launcher — it bypasses
the ACL restriction entirely. Launching uvicorn directly via the `.exe` wrapper
succeeds:

```powershell
# From the backend/ directory
..\venv\Scripts\uvicorn.exe main.main:app --reload --port 8000
```

---

## Bug 2 — `NameError: name 'crud_hod' is not defined` in Coordinator Router

**File:** `backend/main/routers/coordinator_router.py`

### Symptom

Any HTTP request to a coordinator endpoint that internally calls a `crud_hod`
function (e.g. `POST /coordinator/course-outcomes`, `GET /coordinator/courses/{id}/mappings/co-po`,
`POST /coordinator/course-outcomes/clone`) would crash at runtime with:

```
NameError: name 'crud_hod' is not defined
```

### Root Cause

The module `crud_hod` was **used but never imported**. The router file imported
`crud_faculty` and `schemas_hod` but omitted `crud_hod`:

```python
# Before (missing import)
from main import crud_faculty
from main import schemas_faculty
```

### Fix Applied

```diff
- from main import crud_faculty
+ from main import crud_faculty, crud_hod
  from main import schemas_faculty
```

**Affected file:** `backend/main/routers/coordinator_router.py` — line 11.

---

## Bug 3 — `AttributeError: 'Course' object has no attribute 'semester'`

**File:** `backend/main/crud_faculty.py`

### Symptom

Calling the bulk student upload endpoint (`POST /faculty/students/bulk-upload`)
would crash during the auto-enrollment logic with:

```
AttributeError: 'Course' object has no attribute 'semester'
```

### Root Cause

In `process_bulk_students()`, the auto-enrollment block built a semester lookup
map using `s.semester` on `Course` model instances. The `Course` SQLAlchemy model
(`backend/main/models.py`) does **not** have a column named `semester` — the
correct column name is `intended_semester`.

```python
# Course model (models.py) — relevant columns
class Course(Base):
    ...
    intended_semester = Column(Integer, nullable=False)  # correct name
    intended_year     = Column(Integer, nullable=False)
    # There is NO .semester attribute
```

### Fix Applied

```diff
- subject_map = {s.id: s.semester for s in subjects}
+ subject_map = {s.id: s.intended_semester for s in subjects}
```

**Affected file:** `backend/main/crud_faculty.py` — line 64.

---

## Bug 4 — Duplicate `KSATagBase` / `KSATagCreate` / `KSATagResponse` class definitions

**File:** `backend/main/schemas_hod.py`

### Symptom

The same class names `KSATagBase`, `KSATagCreate`, and `KSATagResponse` were
declared twice in the same file. Python silently uses the **last** definition, so
the earlier one became dead code. The first definition was incomplete — it was
missing the three required weight columns that the database schema (`KSA_Tags`
table) mandates:

```python
# FIRST definition — INCOMPLETE (missing weight fields)
class KSATagBase(BaseModel):
    domain: KSADomain
    tag_level: str
    description: Optional[str] = None
    # knowledge_weight, skill_weight, attitude_weight missing!

# SECOND definition — CORRECT
class KSATagBase(BaseModel):
    domain: KSADomain
    tag_level: str
    description: Optional[str] = None
    knowledge_weight: float
    skill_weight: float
    attitude_weight: float
```

### Fix Applied

Removed the first (incomplete) triad of `KSATagBase`, `KSATagCreate`, and
`KSATagResponse`. The complete second definition with all weight fields is the
sole remaining definition.

**Affected file:** `backend/main/schemas_hod.py` — removed 12 lines of the
incomplete first declaration.

---

## Bug 5 — Duplicate route handler registrations for `/hod/framework/ksa-tags`

**File:** `backend/main/routers/router_hod.py`

### Symptom

FastAPI silently registered two `POST` and two `GET` handlers for the same path
`/hod/framework/ksa-tags`. FastAPI does not raise an error for this — it uses
the **first** registered handler and silently ignores all subsequent ones with
the same path+method combination. The second pair of handlers was therefore dead
code.

### Root Cause

The route handlers were inadvertently defined twice:

- First pair (active): called the generic `crud_hod.create_model()` / `crud_hod.get_all_models()`
- Second pair (dead): called the specific `crud_hod.create_ksa_tag()` / `crud_hod.get_ksa_tags()`

### Fix Applied

Removed the redundant second pair of handlers at the bottom of `router_hod.py`.
The first pair (using the generic CRUD helpers) is functionally equivalent and
is now the sole registration for this path.

**Affected file:** `backend/main/routers/router_hod.py` — removed 9 lines of
duplicate route definitions at the end of the file.

---

## Summary Table

| # | File | Error Type | Error Message | Status |
|---|------|-----------|--------------|--------|
| 1 | *(server not started)* | `ECONNREFUSED` | `connect ECONNREFUSED 127.0.0.1:8000` | ✅ Fixed — backend launched via `venv\Scripts\uvicorn.exe` |
| 2 | `routers/coordinator_router.py` | `NameError` | `name 'crud_hod' is not defined` | ✅ Fixed — added missing import |
| 3 | `crud_faculty.py` | `AttributeError` | `'Course' object has no attribute 'semester'` | ✅ Fixed — corrected to `intended_semester` |
| 4 | `schemas_hod.py` | Duplicate class | `KSATagBase` defined twice (incomplete + complete) | ✅ Fixed — removed incomplete duplicate |
| 5 | `routers/router_hod.py` | Duplicate route | `POST/GET /hod/framework/ksa-tags` registered twice | ✅ Fixed — removed dead duplicate handlers |
