import os
os.environ["KIVY_NO_CONSOLELOG"] = "1"
os.environ["KIVY_UNITTEST"] = "1"

from kivy.config import Config
Config.set("kivy", "log_level", "error")
Config.set("kivy", "log_enable", "0")
Config.set("graphics", "width", 1)
Config.set("graphics", "height", 1)
Config.set("graphics", "borderless", "1")
Config.set("graphics", "window_state", "hidden")

import pytest
from kivy.base import EventLoop
from kivy.clock import Clock


@pytest.fixture(autouse=True)
def kivy_environment():
    if not EventLoop.started:
        EventLoop.init()
    yield
    while EventLoop.event_listeners:
        EventLoop.close()


@pytest.fixture
def event_loop():
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture
def sm():
    from kivy.uix.screenmanager import ScreenManager
    sm = ScreenManager()
    return sm


@pytest.fixture
def cache_service():
    from mobile.services.cache_service import cache_service
    cache_service.clear()
    return cache_service
