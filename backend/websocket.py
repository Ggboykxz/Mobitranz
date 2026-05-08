# ============================================================
# WebSocket Manager MobiTranz
# Fichier : backend/websocket.py
# Description : Gestion des connexions WebSocket temps réel
# ============================================================

import json
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
import structlog

from backend.redis_client import redis_client

logger = structlog.get_logger()


class ConnectionManager:
    """Gestionnaire de connexions WebSocket.

    Gère les connexions temps réel pour :
    - Position GPS des véhicules
    - Statut des trajets
    - Alertes et incidents
    - Notifications push
    """

    def __init__(self):
        # Connexions actives par type
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "trips": set(),
            "drivers": set(),
            "incidents": set(),
            "notifications": set(),
            "admin": set(),
        }

        # Mapping user_id -> websocket
        self.user_connections: Dict[str, WebSocket] = {}

        # Rooms actives
        self.rooms: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel: str = "notifications"):
        """Ajoute une connexion WebSocket.

        Args:
            websocket: Connexion WebSocket
            channel: Type de channel (trips, drivers, incidents, notifications, admin)
        """
        await websocket.accept()

        if channel not in self.active_connections:
            channel = "notifications"

        self.active_connections[channel].add(websocket)

        logger.info(
            "WebSocket connecté",
            channel=channel,
            total=len(self.active_connections[channel]),
        )

    def disconnect(self, websocket: WebSocket, channel: str = "notifications"):
        """Supprime une connexion WebSocket.

        Args:
            websocket: Connexion WebSocket
            channel: Type de channel
        """
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)

        for user_id, ws in list(self.user_connections.items()):
            if ws == websocket:
                del self.user_connections[user_id]
                break

        logger.info("WebSocket déconnecté", channel=channel)

    def register_user(self, user_id: str, websocket: WebSocket):
        """Enregistre un utilisateur avec sa connexion.

        Args:
            user_id: ID de l'utilisateur
            websocket: Connexion WebSocket
        """
        self.user_connections[user_id] = websocket

    async def send_personal_message(self, message: dict, user_id: str):
        """Envoie un message à un utilisateur spécifique.

        Args:
            message: Message à envoyer
            user_id: ID du destinataire
        """
        if user_id in self.user_connections:
            websocket = self.user_connections[user_id]
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error("Erreur envoi message personnel", error=str(e))

    async def broadcast(self, message: dict, channel: str = "notifications"):
        """Diffuse un message à tous les clients d'un channel.

        Args:
            message: Message à diffuser
            channel: Channel cible
        """
        if channel not in self.active_connections:
            return

        disconnected = set()

        for websocket in self.active_connections[channel]:
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.add(websocket)

        for ws in disconnected:
            self.disconnect(ws, channel)

    async def send_to_room(self, message: dict, room: str):
        """Envoie un message à une room spécifique.

        Args:
            message: Message à envoyer
            room: Nom de la room
        """
        if room not in self.rooms:
            return

        for websocket in self.rooms[room]:
            try:
                await websocket.send_json(message)
            except Exception:
                pass

    def join_room(self, websocket: WebSocket, room: str):
        """Ajoute un client à une room.

        Args:
            websocket: Connexion WebSocket
            room: Nom de la room
        """
        if room not in self.rooms:
            self.rooms[room] = set()

        self.rooms[room].add(websocket)

        logger.info("Client ajouté à la room", room=room)

    def leave_room(self, websocket: WebSocket, room: str):
        """Retire un client d'une room.

        Args:
            websocket: Connexion WebSocket
            room: Nom de la room
        """
        if room in self.rooms:
            self.rooms[room].discard(websocket)

    async def broadcast_location_update(
        self, driver_id: str, latitude: float, longitude: float
    ):
        """Diffuse une mise à jour de position GPS.

        Args:
            driver_id: ID du conducteur
            latitude: Latitude
            longitude: Longitude
        """
        message = {
            "type": "location_update",
            "driver_id": driver_id,
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        await self.broadcast(message, channel="drivers")

    async def broadcast_trip_status(
        self, trip_id: str, status: str, client_id: str = None, driver_id: str = None
    ):
        """Diffuse un changement de statut de trajet.

        Args:
            trip_id: ID du trajet
            status: Nouveau statut
            client_id: ID du client
            driver_id: ID du conducteur
        """
        message = {
            "type": "trip_status",
            "trip_id": trip_id,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if client_id:
            await self.send_personal_message(message, client_id)

        if driver_id:
            await self.send_personal_message(message, driver_id)

        await self.broadcast(message, channel="trips")

    async def broadcast_incident(
        self,
        incident_id: str,
        incident_type: str,
        trip_id: str,
        latitude: float = None,
        longitude: float = None,
    ):
        """Diffuse une alerte d'incident.

        Args:
            incident_id: ID de l'incident
            incident_type: Type d'incident
            trip_id: ID du trajet
            latitude: Latitude (optionnel)
            longitude: Longitude (optionnel)
        """
        message = {
            "type": "incident",
            "incident_id": incident_id,
            "incident_type": incident_type,
            "trip_id": trip_id,
            "latitude": latitude,
            "longitude": longitude,
            "priority": "high" if incident_type == "sos" else "medium",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        await self.broadcast(message, channel="incidents")
        await self.broadcast(message, channel="admin")

    async def broadcast_notification(
        self, title: str, body: str, user_id: str = None, data: dict = None
    ):
        """Diffuse une notification.

        Args:
            title: Titre de la notification
            body: Corps de la notification
            user_id: ID du destinataire (optionnel)
            data: Données additionnelles
        """
        message = {
            "type": "notification",
            "title": title,
            "body": body,
            "data": data or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if user_id:
            await self.send_personal_message(message, user_id)
        else:
            await self.broadcast(message, channel="notifications")


from datetime import datetime, timezone

manager = ConnectionManager()

websocket_router = APIRouter()


@websocket_router.websocket("/ws/{channel}")
async def websocket_endpoint(websocket: WebSocket, channel: str):
    """Endpoint WebSocket principal.

    Args:
        websocket: Connexion WebSocket
        channel: Type de channel
    """
    await manager.connect(websocket, channel)

    try:
        while True:
            data = await websocket.receive_text()

            try:
                message = json.loads(data)

                action = message.get("action")

                if action == "ping":
                    await websocket.send_json({"type": "pong"})

                elif action == "subscribe_room":
                    room = message.get("room")
                    if room:
                        manager.join_room(websocket, room)

                elif action == "unsubscribe_room":
                    room = message.get("room")
                    if room:
                        manager.leave_room(websocket, room)

                elif action == "register":
                    user_id = message.get("user_id")
                    if user_id:
                        manager.register_user(user_id, websocket)

                else:
                    logger.warning("Action WebSocket inconnue", action=action)

            except json.JSONDecodeError:
                logger.warning("Message WebSocket invalide")

    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)

    except Exception as e:
        logger.error("Erreur WebSocket", error=str(e))
        manager.disconnect(websocket, channel)
