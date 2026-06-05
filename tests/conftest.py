"""
tests/conftest.py
=================
Shared fixtures. The single `state` singleton is reset before every test
so that mutations in one test never bleed into another.
"""

import sys
import os
import importlib
import pytest

# Make the project root importable without installing a package.
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


@pytest.fixture(autouse=True)
def reset_state():
    """
    Re-import state and replace the singleton in every module that holds a
    reference to it, giving each test a clean GameState.
    """
    import state as state_mod
    import constants

    # Build a fresh GameState
    fresh = state_mod.GameState()
    state_mod.state.__dict__.update(fresh.__dict__)

    # Patch references held by sub-modules that were already imported
    for mod_name in [
        "models.animal",
        "models.crate",
        "game.hunt",
        "game.ui",
        "game.world",
        "game.shops",
        "player.player",
    ]:
        mod = sys.modules.get(mod_name)
        if mod and hasattr(mod, "state"):
            mod.state = state_mod.state

    yield state_mod.state


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    """Prevent any time.sleep call from actually waiting during tests."""
    import time
    monkeypatch.setattr(time, "sleep", lambda _: None)
