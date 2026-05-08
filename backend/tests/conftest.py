import warnings

import pytest


def pytest_configure(config):
    config.addinivalue_line("markers", "asyncio: mark test as an asyncio test.")


@pytest.fixture(scope="session")
def event_loop_policy():
    import asyncio

    return asyncio.DefaultEventLoopPolicy()


import sys

if not sys.warnoptions:
    warnings.simplefilter("ignore")
