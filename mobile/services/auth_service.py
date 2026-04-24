# ============================================================
# Service Auth Mobile
# Fichier : mobile/services/auth_service.py
# Description : Authentification avec stockage token sécurisé
# ============================================================

import asyncio
from kivy.storage.redisstore import RedisStore
from kivy.storage.jsonfile import JsonStore
import json


class AuthService:
    """Service d'authentification mobile.
    
    Gère la connexion, inscription et stockage des tokens.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._store = JsonStore("auth_store.json")
        self._access_token: str | None = None
        self._refresh_token: str | None = None
        self._user_id: str | None = None
        self._role: str | None = None
    
    def is_authenticated(self) -> bool:
        """Vérifie si l'utilisateur est connecté."""
        return self._access_token is not None or self._store.exists("access_token")
    
    def get_user_id(self) -> str | None:
        """Retourne l'ID de l'utilisateur."""
        if self._user_id:
            return self._user_id
        if self._store.exists("user_id"):
            return self._store.get("user_id")
        return None
    
    def get_role(self) -> str | None:
        """Retourne le rôle de l'utilisateur."""
        if self._role:
            return self._role
        if self._store.exists("role"):
            return self._store.get("role")
        return None
    
    def save_tokens(self, access_token: str, refresh_token: str, user_id: str, role: str):
        """Sauvegarde les tokens JWT."""
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._user_id = user_id
        self._role = role
        
        self._store.put("access_token", value=access_token)
        self._store.put("refresh_token", value=refresh_token)
        self._store.put("user_id", value=user_id)
        self._store.put("role", value=role)
    
    def clear_tokens(self):
        """Efface les tokens (déconnexion)."""
        self._access_token = None
        self._refresh_token = None
        self._user_id = None
        self._role = None
        
        if self._store.exists("access_token"):
            self._store.remove("access_token")
        if self._store.exists("refresh_token"):
            self._store.remove("refresh_token")
        if self._store.exists("user_id"):
            self._store.remove("user_id")
        if self._store.exists("role"):
            self._store.remove("role")
    
    def get_access_token(self) -> str | None:
        """Retourne le token d'accès."""
        if self._access_token:
            return self._access_token
        if self._store.exists("access_token"):
            return self._store.get("access_token")
        return None


auth_service = AuthService()