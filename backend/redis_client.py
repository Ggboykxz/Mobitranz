# ============================================================
# Client Redis MobiTranz
# Fichier : backend/redis_client.py
# Description : Gestion du cache et des sessions Redis
# ============================================================

import redis.asyncio as redis
from typing import Optional
import json
from backend.config import settings


class RedisClient:
    """Client Redis pour MobiTranz.
    
    Gère les sessions utilisateur, le cache et les événements temps réel.
    Connexion avec support async pour FastAPI.
    """
    
    def __init__(self):
        """Initialise le client Redis."""
        self._redis: Optional[redis.Redis] = None
    
    async def connect(self):
        """Établit la connexion à Redis."""
        self._redis = await redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
    
    async def disconnect(self):
        """Ferme la connexion à Redis."""
        if self._redis:
            await self._redis.close()
    
    async def get_client(self) -> redis.Redis:
        """Retourne le client Redis connecté.
        
        Returns:
            redis.Redis: Client Redis
            
        Raises:
            RuntimeError: Si la connexion n'est pas établie
        """
        if not self._redis:
            raise RuntimeError("Redis non connecté. Appeler connect()d'abord")
        return self._redis
    
    async def set_session(
        self,
        session_id: str,
        data: dict,
        expire_seconds: int = 3600
    ):
        """Enregistre une session utilisateur.
        
        Args:
            session_id: Identifiant unique de session
            data: Données de session à JSON-sérialiser
            expire_seconds: Durée de vie en secondes (défaut 1h)
        """
        client = await self.get_client()
        await client.setex(
            f"session:{session_id}",
            expire_seconds,
            json.dumps(data, ensure_ascii=False)
        )
    
    async def get_session(self, session_id: str) -> Optional[dict]:
        """Récupère une session utilisateur.
        
        Args:
            session_id: Identifiant unique de session
            
        Returns:
            dict: Données de session ou None si expirée
        """
        client = await self.get_client()
        data = await client.get(f"session:{session_id}")
        if data:
            return json.loads(data)
        return None
    
    async def delete_session(self, session_id: str):
        """Supprime une session utilisateur.
        
        Args:
            session_id: Identifiant unique de session
        """
        client = await self.get_client()
        await client.delete(f"session:{session_id}")
    
    async def set_cache(
        self,
        key: str,
        value: str,
        expire_seconds: int = 300
    ):
        """Enregistre une donnée en cache.
        
        Args:
            key: Clé de cache
            value: Valeur à stocker
            expire_seconds: Durée de vie en secondes (défaut 5min)
        """
        client = await self.get_client()
        await client.setex(f"cache:{key}", expire_seconds, value)
    
    async def get_cache(self, key: str) -> Optional[str]:
        """Récupère une donnée en cache.
        
        Args:
            key: Clé de cache
            
        Returns:
            str: Valeur stockée ou None
        """
        client = await self.get_client()
        return await client.get(f"cache:{key}")
    
    async def set_proposal_active(
        self,
        trip_id: str,
        driver_id: str,
        data: dict,
        window_seconds: int = 30
    ):
        """Enregistre une proposition active (détection klaxon).
        
        Args:
            trip_id: Identifiant du trajet
            driver_id: Identifiant du conducteur
            data: Données de la proposition
            window_seconds: Fenêtre de détection (défaut 30s)
        """
        client = await self.get_client()
        key = f"proposal:{trip_id}:{driver_id}"
        await client.setex(
            key,
            window_seconds,
            json.dumps(data, ensure_ascii=False)
        )
    
    async def is_proposal_active(
        self,
        trip_id: str,
        driver_id: str
    ) -> bool:
        """Vérifie si une proposition est active.
        
        Args:
            trip_id: Identifiant du trajet
            driver_id: Identifiant du conducteur
            
        Returns:
            bool: True si proposition active
        """
        client = await self.get_client()
        key = f"proposal:{trip_id}:{driver_id}"
        return await client.exists(key) > 0
    
    async def use_qr_code(self, qr_id: str) -> bool:
        """Marque un QR Code comme utilisé (usage unique).
        
        Args:
            qr_id: Identifiant unique du QR Code
            
        Returns:
            bool: True si c'était le premier usage
        """
        client = await self.get_client()
        key = f"qr_used:{qr_id}"
        return await client.set(key, "1", nx=True, ex=300)
    
    async def publish_event(self, channel: str, message: dict):
        """Publie un événement sur un canal Redis.
        
        Args:
            channel: Nom du canal
            message: Message à publier
        """
        client = await self.get_client()
        await client.publish(
            channel,
            json.dumps(message, ensure_ascii=False)
        )
    
    async def subscribe(self, channel: str):
        """Souscrit à un canal Redis.
        
        Args:
            channel: Nom du canal
            
        Returns:
            Subscriber: Abonnement PubSub
        """
        client = await self.get_client()
        pubsub = client.pubsub()
        await pubsub.subscribe(channel)
        return pubsub


redis_client = RedisClient()