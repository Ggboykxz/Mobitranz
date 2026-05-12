import time
from kivy.storage.jsonstore import JsonStore


class CacheService:
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
        self._store = JsonStore("mobitranz_cache.json")

    def set(self, key, data, ttl=300):
        self._store.put(key, value=data, expires_at=time.time() + ttl)

    def get(self, key):
        try:
            entry = self._store.get(key)
            if entry["expires_at"] >= time.time():
                return entry["value"]
            self._store.remove(key)
        except KeyError:
            pass
        return None

    def get_stale(self, key):
        try:
            return self._store.get(key)["value"]
        except KeyError:
            return None

    def clear(self):
        for key in list(self._store.keys()):
            try:
                self._store.remove(key)
            except KeyError:
                pass

    def clear_expired(self):
        now = time.time()
        for key in list(self._store.keys()):
            try:
                entry = self._store.get(key)
                if entry["expires_at"] < now:
                    self._store.remove(key)
            except KeyError:
                pass


cache_service = CacheService()
