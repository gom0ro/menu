from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.config import settings
from app.database import Base, engine
from app.routers import auth, categories, dishes, restaurants
from app.seed import seed_demo_data


def create_app() -> FastAPI:
    app = FastAPI(title="Restaurant Menu API", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    upload_path = Path(settings.upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(upload_path)), name="uploads")

    app.include_router(auth.router, prefix="/api")
    app.include_router(restaurants.router, prefix="/api")
    app.include_router(categories.router, prefix="/api")
    app.include_router(dishes.router, prefix="/api")

    @app.on_event("startup")
    async def startup():
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("Database tables created successfully!")
        except Exception as e:
            print(f"Warning: Could not create database tables: {e}")
            print("Make sure PostgreSQL is running and the database exists.")
        
        try:
            await seed_demo_data()
            print("Demo data seeded successfully!")
        except Exception as e:
            print(f"Warning: Could not seed demo data: {e}")

    @app.get("/api/health")
    async def health():
        return {"status": "ok"}

    return app


app = create_app()
