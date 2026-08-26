from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base


class Empresa(Base):
    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    whatsapp_numero = Column(String(20), nullable=False)  # formato: 51987654321 (sin +)
    logo_url = Column(String(500), nullable=True)
    activo = Column(Boolean, default=True, nullable=False)

    buses = relationship("Bus", back_populates="empresa", cascade="all, delete-orphan")
    rutas = relationship("Ruta", back_populates="empresa", cascade="all, delete-orphan")
