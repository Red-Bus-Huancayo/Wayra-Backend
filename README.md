# RedBus Clone API (Backend)

Backend FastAPI para una PWA intermediaria de venta de boletos terrestres,
sin pagos en línea (se redirige a WhatsApp de la empresa), sin boletos
digitales ni reseñas.

## Instalación

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Editar .env con tu DATABASE_URL de PostgreSQL
```

## Ejecutar

```bash
uvicorn app.main:app --reload
```

Documentación interactiva en `http://localhost:8000/docs`.

## Flujo típico

1. `POST /empresas` — registrar empresa de transporte
2. `POST /buses` — registrar bus con su distribución de asientos (plantilla)
3. `POST /rutas` — registrar ruta (origen/destino) de una empresa
4. `POST /rutas/horarios` — registrar horario recurrente de una ruta
5. `POST /rutas/horarios/{id}/generar-viaje?fecha=YYYY-MM-DD` — abrir disponibilidad
   para una fecha concreta (llamar por adelantado, ej. vía cron diario)
6. `GET /viajes?origen=&destino=&fecha=` — búsqueda que hace el usuario final
7. `GET /viajes/{id}/asientos` — mapa de asientos para que el usuario elija
8. `POST /reservas` — crear una reserva (bloquea los asientos elegidos)
9. `POST /reservas/{id}/whatsapp` — genera el link `wa.me` con el mensaje
   prellenado, para redirigir al usuario a confirmar con la empresa
10. `POST /reservas/{id}/cancelar` — libera los asientos si el usuario desiste

## Panel de administración (para cargar empresas, sin usar /docs)

Se agregó un login simple (una sola contraseña, sin usuarios/roles) para
proteger la creación de datos. En el frontend, entra a `/admin/login` con la
contraseña que pongas en `ADMIN_PASSWORD`.

- `POST /admin/login` — recibe `{"password": "..."}`, devuelve un token JWT
  válido por `ADMIN_TOKEN_EXPIRA_HORAS` (12 por defecto).
- Los endpoints de escritura (crear empresa, bus, ruta, horario, generar
  viaje, punto de referencia) ahora requieren `Authorization: Bearer <token>`.
- Los endpoints de lectura (búsquedas, mapa de asientos, etc.) siguen siendo
  públicos — el frontend de pasajeros no necesita login.
- **Importante:** cambia `ADMIN_PASSWORD` y `ADMIN_SECRET_KEY` a valores
  reales en producción (Railway → Variables). Los valores por defecto en
  `.env.example` son solo de referencia, no los uses tal cual.

## Función "Ángel Guardián"

Al confirmar la reserva (`POST /reservas/{id}/whatsapp`) se crea automáticamente
un `Seguimiento` con un token público. La respuesta incluye:

- `seguimiento_token` — usado por la PWA del pasajero para descargar el
  mini-mapa offline (`GET /seguimientos/{token}`, trae los puntos de
  referencia de la ruta para guardarlos en el dispositivo, ej. IndexedDB).
- `seguimiento_link_familiar` — link que el pasajero comparte manualmente con
  un familiar; abre una vista de solo lectura (`GET /seguimientos/{token}/publico`)
  sin necesidad de que el contacto se registre.

Flujo esperado en el frontend (fuera de este backend):

1. Descargar los puntos de referencia (distritos/localidades) al confirmar.
2. Usar el GPS del dispositivo (funciona sin datos móviles) para detectar
   cercanía a cada punto.
3. Al detectar un paso o la llegada, intentar `POST /seguimientos/{token}/eventos`
   de inmediato. Si no hay señal, guardar el evento en cola local (IndexedDB)
   y reintentar con Background Sync API del service worker apenas el celular
   recupere señal — el campo `reportado_en` conserva el momento real del evento.
4. La respuesta de ese POST trae `whatsapp_url_pasajero` con el mensaje ya
   armado, para que la PWA lo abra (`wa.me`) y confirme el aviso al pasajero.
5. El familiar simplemente abre el link compartido para ver el último estado.

Puntos de referencia recomendados: solo distritos/localidades principales
(`POST /rutas/{ruta_id}/puntos`), no anexos pequeños, para no generar avisos
de más.

## Notas

- Las tablas se crean automáticamente al iniciar (`Base.metadata.create_all`).
  Para producción se recomienda migrar a Alembic más adelante.
- La reserva queda en estado `pendiente` → `enviada` (tras generar el link de
  WhatsApp). La confirmación final por parte de la empresa es manual, fuera
  del sistema, por ahora.
- No hay expiración automática de reservas todavía (asientos quedan en
  `reservado` hasta que se cancelen manualmente); es un candidato para una
  próxima iteración (ej. tarea en background o cron).
