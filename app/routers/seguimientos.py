from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from urllib.parse import quote

from app.core.database import get_db
from app.models.seguimiento import Seguimiento, EventoSeguimiento, EstadoSeguimiento, TipoEvento
from app.models.reserva import Reserva
from app.models.punto_referencia import PuntoReferencia
from app.schemas.seguimiento import (
    EventoSeguimientoCreate,
    EventoSeguimientoOut,
    EventoSeguimientoRespuesta,
    SeguimientoOut,
    SeguimientoPublicoOut,
)

router = APIRouter(prefix="/seguimientos", tags=["Angel Guardian"])


def _obtener_seguimiento_por_token(token: str, db: Session) -> Seguimiento:
    seguimiento = (
        db.query(Seguimiento)
        .options(joinedload(Seguimiento.reserva), joinedload(Seguimiento.eventos))
        .filter(Seguimiento.token == token)
        .first()
    )
    if not seguimiento:
        raise HTTPException(status_code=404, detail="Seguimiento no encontrado")
    return seguimiento


@router.get("/{token}", response_model=SeguimientoOut)
def obtener_seguimiento_privado(token: str, db: Session = Depends(get_db)):
    """
    Usado por la app del pasajero para descargar el mini-mapa offline
    (puntos de referencia de la ruta) apenas se confirma la reserva.
    """
    seguimiento = _obtener_seguimiento_por_token(token, db)
    ruta = seguimiento.reserva.viaje.horario.ruta
    puntos = (
        db.query(PuntoReferencia)
        .filter(PuntoReferencia.ruta_id == ruta.id)
        .order_by(PuntoReferencia.orden)
        .all()
    )
    return SeguimientoOut(
        id=seguimiento.id,
        token=seguimiento.token,
        estado=seguimiento.estado,
        puntos_ruta=puntos,
    )


@router.get("/{token}/publico", response_model=SeguimientoPublicoOut)
def obtener_estado_publico(token: str, db: Session = Depends(get_db)):
    """
    Endpoint PÚBLICO (sin autenticación) para el link que el pasajero comparte
    con su familiar/contacto. Muestra solo el último estado conocido del viaje.
    """
    seguimiento = _obtener_seguimiento_por_token(token, db)
    ultimo_evento = seguimiento.eventos[-1] if seguimiento.eventos else None
    ultimo_punto_nombre = None
    if ultimo_evento and ultimo_evento.punto_referencia_id:
        punto = db.query(PuntoReferencia).filter(
            PuntoReferencia.id == ultimo_evento.punto_referencia_id
        ).first()
        ultimo_punto_nombre = punto.nombre if punto else None
    elif ultimo_evento and ultimo_evento.tipo == TipoEvento.llegada:
        ultimo_punto_nombre = "Destino final"

    return SeguimientoPublicoOut(
        token=seguimiento.token,
        estado=seguimiento.estado,
        nombre_pasajero=seguimiento.reserva.nombre_pasajero,
        ultimo_evento=EventoSeguimientoOut.model_validate(ultimo_evento) if ultimo_evento else None,
        ultimo_punto_nombre=ultimo_punto_nombre,
    )


@router.post("/{token}/eventos", response_model=EventoSeguimientoRespuesta, status_code=201)
def registrar_evento(token: str, payload: EventoSeguimientoCreate, db: Session = Depends(get_db)):
    """
    El dispositivo del pasajero llama a este endpoint cuando el GPS local
    detecta que pasó cerca de un punto de referencia o que llegó a destino.
    `reportado_en` conserva el momento real del evento aunque la sincronización
    (esta llamada) ocurra después, cuando el celular recupere señal.
    """
    seguimiento = _obtener_seguimiento_por_token(token, db)

    if seguimiento.estado != EstadoSeguimiento.activo:
        raise HTTPException(status_code=400, detail="Este seguimiento ya no está activo")

    nombre_punto = "destino final"
    if payload.punto_referencia_id:
        punto = db.query(PuntoReferencia).filter(
            PuntoReferencia.id == payload.punto_referencia_id
        ).first()
        if not punto:
            raise HTTPException(status_code=404, detail="Punto de referencia no encontrado")
        nombre_punto = punto.nombre

    evento = EventoSeguimiento(
        seguimiento_id=seguimiento.id,
        punto_referencia_id=payload.punto_referencia_id,
        tipo=payload.tipo,
        latitud_reportada=payload.latitud_reportada,
        longitud_reportada=payload.longitud_reportada,
        reportado_en=payload.reportado_en,
    )
    db.add(evento)

    finalizado = payload.tipo == TipoEvento.llegada
    if finalizado:
        seguimiento.estado = EstadoSeguimiento.finalizado

    db.commit()
    db.refresh(evento)

    nombre_pasajero = seguimiento.reserva.nombre_pasajero
    if finalizado:
        mensaje = f"Hola {nombre_pasajero}, este es tu Angel Guardian: ¡llegaste a tu destino!"
    else:
        mensaje = f"Hola {nombre_pasajero}, este es tu Angel Guardian: estás cerca de {nombre_punto}."

    telefono_pasajero = seguimiento.reserva.telefono_pasajero
    whatsapp_url = f"https://wa.me/{telefono_pasajero}?text={quote(mensaje)}"

    return EventoSeguimientoRespuesta(
        evento=EventoSeguimientoOut.model_validate(evento),
        whatsapp_url_pasajero=whatsapp_url,
        mensaje=mensaje,
        seguimiento_finalizado=finalizado,
    )


@router.post("/{token}/cancelar", response_model=SeguimientoOut)
def cancelar_seguimiento(token: str, db: Session = Depends(get_db)):
    seguimiento = _obtener_seguimiento_por_token(token, db)
    seguimiento.estado = EstadoSeguimiento.cancelado
    db.commit()

    ruta = seguimiento.reserva.viaje.horario.ruta
    puntos = (
        db.query(PuntoReferencia)
        .filter(PuntoReferencia.ruta_id == ruta.id)
        .order_by(PuntoReferencia.orden)
        .all()
    )
    return SeguimientoOut(
        id=seguimiento.id,
        token=seguimiento.token,
        estado=seguimiento.estado,
        puntos_ruta=puntos,
    )
