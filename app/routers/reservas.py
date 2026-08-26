from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.core.database import get_db
from app.models.viaje import Viaje, AsientoViaje, EstadoAsiento
from app.models.reserva import Reserva, EstadoReserva
from app.models.ruta import Horario, Ruta
from app.models.seguimiento import Seguimiento
from app.schemas.reserva import ReservaCreate, ReservaOut, ReservaWhatsAppOut

router = APIRouter(prefix="/reservas", tags=["Reservas"])


@router.post("", response_model=ReservaOut, status_code=201)
def crear_reserva(payload: ReservaCreate, db: Session = Depends(get_db)):
    viaje = db.query(Viaje).filter(Viaje.id == payload.viaje_id).first()
    if not viaje:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")

    asientos = (
        db.query(AsientoViaje)
        .filter(AsientoViaje.id.in_(payload.asiento_viaje_ids))
        .with_for_update()
        .all()
    )

    if len(asientos) != len(payload.asiento_viaje_ids):
        raise HTTPException(status_code=400, detail="Uno o más asientos no existen")

    for asiento in asientos:
        if asiento.viaje_id != viaje.id:
            raise HTTPException(status_code=400, detail="Un asiento no pertenece a este viaje")
        if asiento.estado != EstadoAsiento.disponible:
            raise HTTPException(
                status_code=409,
                detail=f"El asiento {asiento.id} ya no está disponible",
            )

    total = sum(
        float(asiento.precio) if asiento.precio is not None
        else float(viaje.horario.precio_base)
        for asiento in asientos
    )

    reserva = Reserva(
        viaje_id=viaje.id,
        nombre_pasajero=payload.nombre_pasajero,
        telefono_pasajero=payload.telefono_pasajero,
        total=total,
        estado=EstadoReserva.pendiente,
    )
    reserva.asientos = asientos

    for asiento in asientos:
        asiento.estado = EstadoAsiento.reservado

    db.add(reserva)
    db.commit()
    db.refresh(reserva)
    return reserva


@router.get("/{reserva_id}", response_model=ReservaOut)
def obtener_reserva(reserva_id: int, db: Session = Depends(get_db)):
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return reserva


@router.post("/{reserva_id}/whatsapp", response_model=ReservaWhatsAppOut)
def generar_link_whatsapp(reserva_id: int, db: Session = Depends(get_db)):
    reserva = (
        db.query(Reserva)
        .options(
            joinedload(Reserva.viaje)
            .joinedload(Viaje.horario)
            .joinedload(Horario.ruta)
            .joinedload(Ruta.empresa),
            joinedload(Reserva.asientos),
        )
        .filter(Reserva.id == reserva_id)
        .first()
    )
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    empresa = reserva.viaje.horario.ruta.empresa
    ruta = reserva.viaje.horario.ruta
    numeros_asiento = ", ".join(a.asiento_plantilla.numero for a in reserva.asientos)

    mensaje = (
        f"Hola {empresa.nombre}, quiero confirmar mi reserva:\n"
        f"Ruta: {ruta.origen} -> {ruta.destino}\n"
        f"Fecha: {reserva.viaje.fecha}\n"
        f"Hora: {reserva.viaje.horario.hora_salida}\n"
        f"Asiento(s): {numeros_asiento}\n"
        f"Pasajero: {reserva.nombre_pasajero}\n"
        f"Total: S/ {reserva.total}\n"
        f"Código de reserva: #{reserva.id}"
    )

    whatsapp_url = f"https://wa.me/{empresa.whatsapp_numero}?text={quote(mensaje)}"

    reserva.estado = EstadoReserva.enviada

    # Crear (o reutilizar) el Seguimiento "Ángel Guardián" para esta reserva
    seguimiento = db.query(Seguimiento).filter(Seguimiento.reserva_id == reserva.id).first()
    if not seguimiento:
        seguimiento = Seguimiento(reserva_id=reserva.id)
        db.add(seguimiento)

    db.commit()
    db.refresh(seguimiento)

    seguimiento_link_familiar = f"{settings.FRONTEND_BASE_URL}/seguimiento/{seguimiento.token}"

    return ReservaWhatsAppOut(
        reserva_id=reserva.id,
        whatsapp_url=whatsapp_url,
        mensaje=mensaje,
        seguimiento_token=seguimiento.token,
        seguimiento_link_familiar=seguimiento_link_familiar,
    )


@router.post("/{reserva_id}/cancelar", response_model=ReservaOut)
def cancelar_reserva(reserva_id: int, db: Session = Depends(get_db)):
    reserva = (
        db.query(Reserva)
        .options(joinedload(Reserva.asientos))
        .filter(Reserva.id == reserva_id)
        .first()
    )
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    if reserva.estado in (EstadoReserva.cancelada, EstadoReserva.confirmada):
        raise HTTPException(status_code=400, detail="La reserva no se puede cancelar en su estado actual")

    for asiento in reserva.asientos:
        asiento.estado = EstadoAsiento.disponible

    reserva.estado = EstadoReserva.cancelada
    db.commit()
    db.refresh(reserva)
    return reserva
