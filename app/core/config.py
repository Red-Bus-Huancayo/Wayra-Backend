import os


class Settings:
    APP_NAME: str = "RedBus Clone API"
    CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "*").split(",")
    # Vigencia en minutos de una reserva "pendiente" antes de expirar automáticamente
    RESERVA_EXPIRA_MINUTOS: int = int(os.getenv("RESERVA_EXPIRA_MINUTOS", "20"))
    # Dominio de la PWA, usado para armar el link público de "Ángel Guardián" que el pasajero comparte
    FRONTEND_BASE_URL: str = os.getenv("FRONTEND_BASE_URL", "https://tu-pwa.vercel.app")


settings = Settings()
