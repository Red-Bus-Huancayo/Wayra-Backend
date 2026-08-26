from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine
from app.routers import empresas, rutas, buses, viajes, reservas, puntos_referencia, seguimientos

# Crea las tablas si no existen (en producción se recomienda usar Alembic para migraciones)
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(empresas.router)
app.include_router(rutas.router)
app.include_router(buses.router)
app.include_router(viajes.router)
app.include_router(reservas.router)
app.include_router(puntos_referencia.router)
app.include_router(seguimientos.router)


@app.get("/", tags=["Root"])
def root():
    return {"status": "ok", "app": settings.APP_NAME}
