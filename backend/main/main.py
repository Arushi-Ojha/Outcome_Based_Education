from fastapi import FastAPI
from main.database import engine
from main import models
from main.routers import auth_router, router_hod, coordinator_router, faculty_router, analytics_router

# Initialize Database tables
# SQLAlchemy DeclarativeBase handles this safely with TiDB in sequential queries
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="OBE Tracking System API", version="1.0.0")

# Include domain routers
app.include_router(auth_router.router)
app.include_router(router_hod.router)
app.include_router(coordinator_router.router)
app.include_router(faculty_router.router)
app.include_router(analytics_router.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the OBE Tracking System API"}
