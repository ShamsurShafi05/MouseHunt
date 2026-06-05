"""
tests/test_models.py
====================
Unit tests for Mouse, Animal, and Crate models.
"""

import pytest
from unittest.mock import patch
from state import GameState
from models.mouse import Mouse
from models.animal import Animal
from models.crate import Crate


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def fresh_state(reset_state):
    """Delegate to the autouse conftest fixture; expose it for explicit use."""
    return reset_state


def _mouse(name="Brown", gold=70, pts=60, coat=""):
    return Mouse(name, gold, pts, coat)


# ===========================================================================
# Mouse
# ===========================================================================

class TestMouse:
    def test_getters_return_constructor_values(self):
        m = Mouse("Tiny", 100, 100, "~coat~")
        assert m.get_name() == "Tiny"
        assert m.get_gold() == 100
        assert m.get_points() == 100
        assert m.get_coat() == "~coat~"

    def test_str_returns_name(self):
        m = Mouse("Grey", 60, 50, "")
        assert str(m) == "Grey"

    def test_none_mouse_str(self):
        m = Mouse(None, 0, 0, "")
        assert str(m) == "None"
        assert m.get_name() is None

    def test_zero_gold_and_points(self):
        m = Mouse(None, 0, 0, "")
        assert m.get_gold() == 0
        assert m.get_points() == 0


# ===========================================================================
# Animal
# ===========================================================================

class TestAnimal:
    def test_tiger_damage(self, reset_state):
        reset_state.player_health = 100
        a = Animal("tiger")
        a.attack()
        assert reset_state.player_health == 40

    def test_wild_boar_damage(self, reset_state):
        reset_state.player_health = 100
        a = Animal("wild boar")
        a.attack()
        assert reset_state.player_health == 80

    def test_health_cannot_go_below_zero(self, reset_state):
        reset_state.player_health = 10
        a = Animal("tiger")
        alive = a.attack()
        assert reset_state.player_health == 0
        assert alive is False

    def test_attack_returns_true_when_alive(self, reset_state):
        reset_state.player_health = 100
        a = Animal("wild boar")
        assert a.attack() is True

    def test_unknown_animal_raises(self):
        with pytest.raises(ValueError):
            Animal("dragon")

    def test_multiple_attacks_accumulate(self, reset_state):
        reset_state.player_health = 100
        boar = Animal("wild boar")
        boar.attack()   # -20
        boar.attack()   # -20
        assert reset_state.player_health == 60


# ===========================================================================
# Crate
# ===========================================================================

class TestCrateBasic:
    @pytest.fixture
    def crate(self):
        return Crate()

    def test_initial_capacity_is_5(self, crate):
        assert crate.capacity == 5

    def test_initial_size_is_zero(self, crate):
        assert crate.size() == 0

    def test_is_not_full_when_empty(self, crate):
        assert not crate.is_full()

    def test_add_mouse_increases_size(self, crate):
        crate.add(_mouse())
        assert crate.size() == 1

    def test_add_returns_true_when_space(self, crate):
        assert crate.add(_mouse()) is True

    def test_add_returns_false_when_full(self, crate):
        for _ in range(5):
            crate.add(_mouse())
        assert crate.add(_mouse()) is False

    def test_is_full_after_capacity(self, crate):
        for _ in range(5):
            crate.add(_mouse())
        assert crate.is_full()

    def test_remove_returns_oldest_mouse_fifo(self, crate):
        m1 = _mouse("Brown")
        m2 = _mouse("Grey")
        crate.add(m1)
        crate.add(m2)
        assert crate.remove() is m1

    def test_remove_from_empty_returns_none(self, crate):
        assert crate.remove() is None

    def test_contents_lists_names(self, crate):
        crate.add(_mouse("Tiny"))
        crate.add(_mouse("White"))
        assert crate.contents() == ["Tiny", "White"]

    def test_contents_empty(self, crate):
        assert crate.contents() == []


class TestCratePoison:
    @pytest.fixture
    def loaded_crate(self):
        c = Crate()
        c.add(_mouse("Brown"))
        c.add(_mouse("Grey"))
        return c

    def test_poison_wipe_clears_crate(self, loaded_crate):
        loaded_crate.poison_wipe()
        assert loaded_crate.size() == 0

    def test_poison_wipe_empty_crate_is_safe(self):
        c = Crate()
        c.poison_wipe()   # should not raise
        assert c.size() == 0


class TestCrateUpgrade:
    @pytest.fixture
    def crate(self):
        return Crate()

    def test_upgrade_requires_xp(self, crate, reset_state):
        reset_state.points = 0
        reset_state.gold   = 1000
        success, msg = crate.upgrade()
        assert not success
        assert "XP" in msg

    def test_upgrade_requires_gold(self, crate, reset_state):
        reset_state.points = 200
        reset_state.gold   = 0
        success, msg = crate.upgrade()
        assert not success
        assert "gold" in msg.lower()

    def test_upgrade_succeeds_with_enough_resources(self, crate, reset_state):
        reset_state.points = 200
        reset_state.gold   = 200
        success, msg = crate.upgrade()
        assert success
        assert crate.capacity == 10
        assert reset_state.gold == 120   # 200 - 80

    def test_upgrade_deducts_gold(self, crate, reset_state):
        reset_state.points = 200
        reset_state.gold   = 200
        crate.upgrade()
        assert reset_state.gold == 120

    def test_upgrade_cap_at_max_tier(self, crate, reset_state):
        # Upgrade twice to reach Iron Crate
        reset_state.points = 9999
        reset_state.gold   = 9999
        crate.upgrade()   # tier 1 → 2
        crate.upgrade()   # tier 2 → 3
        success, msg = crate.upgrade()   # already at max
        assert not success

    def test_tier_index_increments(self, crate, reset_state):
        reset_state.points = 200
        reset_state.gold   = 200
        crate.upgrade()
        assert crate.tier_index == 1


class TestCrateDisplay:
    def test_display_prints_tier_name(self, capsys):
        c = Crate()
        c.display()
        out = capsys.readouterr().out
        assert "Basic Crate" in out

    def test_display_shows_size_and_capacity(self, capsys):
        c = Crate()
        c.add(_mouse("Brown"))
        c.display()
        out = capsys.readouterr().out
        assert "1/5" in out

    def test_display_empty_crate_says_empty(self, capsys):
        c = Crate()
        c.display()
        out = capsys.readouterr().out
        assert "empty" in out.lower()

    def test_display_lists_mouse_names(self, capsys):
        c = Crate()
        c.add(_mouse("Tiny"))
        c.display()
        out = capsys.readouterr().out
        assert "Tiny" in out


class TestCrateQueueIntegrity:
    def test_add_then_remove_restores_empty(self):
        c = Crate()
        c.add(_mouse("Grey"))
        c.remove()
        assert c.size() == 0
        assert not c.is_full()

    def test_fifo_order_three_mice(self):
        c = Crate()
        m1, m2, m3 = _mouse("Brown"), _mouse("Grey"), _mouse("White")
        c.add(m1); c.add(m2); c.add(m3)
        assert c.remove() is m1
        assert c.remove() is m2
        assert c.remove() is m3

    def test_contents_reflects_remaining_after_remove(self):
        c = Crate()
        c.add(_mouse("Tiny"))
        c.add(_mouse("White"))
        c.remove()
        assert c.contents() == ["White"]


class TestAnimalMessages:
    def test_tiger_attack_prints_message(self, reset_state, capsys):
        reset_state.player_health = 100
        Animal("tiger").attack()
        out = capsys.readouterr().out
        assert "tiger" in out.lower()

    def test_boar_attack_prints_message(self, reset_state, capsys):
        reset_state.player_health = 100
        Animal("wild boar").attack()
        out = capsys.readouterr().out
        assert "boar" in out.lower() or "wild" in out.lower()