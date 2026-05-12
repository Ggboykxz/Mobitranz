import asyncio
import threading
from kivy.clock import Clock


class KivyAPIClient:
    def __init__(self):
        self._client = None

    async def ensure_client(self):
        if self._client is None:
            from mobile.services.api_client import api_client
            self._client = api_client

    def call(self, method, *args, on_success=None, on_error=None, **kwargs):
        def run():
            try:
                result = asyncio.run(self._do_call(method, *args, **kwargs))
                if on_success:
                    Clock.schedule_once(lambda dt: on_success(result))
            except Exception as e:
                if on_error:
                    Clock.schedule_once(lambda dt: on_error(e))

        threading.Thread(target=run, daemon=True).start()

    async def _do_call(self, method, *args, **kwargs):
        await self.ensure_client()
        client_method = getattr(self._client, method)
        return await client_method(*args, **kwargs)


kivy_api_client = KivyAPIClient()
