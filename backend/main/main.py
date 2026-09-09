from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from main.database import engine
from main import models
from main.routers import auth_router, router_hod, coordinator_router, faculty_router, analytics_router, admin_router, program_head_router

# Initialize Database tables
# SQLAlchemy DeclarativeBase handles this safely with TiDB in sequential queries
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="OBE Tracking System API", version="1.0.0")

# Setup CORS middleware
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include domain routers
app.include_router(auth_router.router)
app.include_router(router_hod.router)
app.include_router(coordinator_router.router)
app.include_router(faculty_router.router)
app.include_router(analytics_router.router)
app.include_router(admin_router.router)
app.include_router(program_head_router.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the OBE Tracking System API"}

@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "OBE Tracking System API is running"}

