"""
tests/test_state.py
===================
Tests for GameState vitals, energy/hunger/time helpers, and convenience reads.
"""

import pytest
from state import GameState


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def gs():
    """Fresh GameState for every test (independent of the singleton)."""
    return GameState()


# ---------------------------------------------------------------------------
# Initial values
# ---------------------------------------------------------------------------

class TestInitialValues:
    def test_health_starts_at_100(self, gs):
        assert gs.player_health == 100

    def test_energy_starts_at_100(self, gs):
        assert gs.player_energy == 100

    def test_hunger_starts_at_100(self, gs):
        assert gs.player_hunger == 100

    def test_gold_starts_at_zero(self, gs):
        assert gs.gold == 0

    def test_wood_starts_at_zero(self, gs):
        assert gs.wood == 0

    def test_points_starts_at_zero(self, gs):
        assert gs.points == 0

    def test_game_time_starts_at_0900(self, gs):
        assert gs.game_time == "09 00"

    def test_day_starts_at_1(self, gs):
        assert gs.day == 1

    def test_crate_is_none(self, gs):
        assert gs.crate is None

    def test_current_trap_is_none(self, gs):
        assert gs.current_trap is None

    def test_trap_cheese_is_none(self, gs):
        assert gs.trap_cheese is None

    def test_level_flags_all_false(self, gs):
        assert not any(gs.level_flags.values())

    def test_cheese_inventory_zeroed(self, gs):
        for _, qty in gs.cheese:
            assert qty == 0

    def test_food_inventory_zeroed(self, gs):
        for qty in gs.food.values():
            assert qty == 0


# ---------------------------------------------------------------------------
# Energy helpers
# ---------------------------------------------------------------------------

class TestEnergyHelpers:
    def test_drain_energy_normal(self, gs):
        gs.drain_energy(15)
        assert gs.player_energy == 85

    def test_drain_energy_clamps_at_zero(self, gs):
        gs.drain_energy(200)
        assert gs.player_energy == 0

    def test_drain_energy_exact_zero(self, gs):
        gs.drain_energy(100)
        assert gs.player_energy == 0

    def test_restore_energy_normal(self, gs):
        gs.player_energy = 50
        gs.restore_energy(30)
        assert gs.player_energy == 80

    def test_restore_energy_clamps_at_100(self, gs):
        gs.player_energy = 90
        gs.restore_energy(50)
        assert gs.player_energy == 100

    def test_restore_energy_from_zero(self, gs):
        gs.player_energy = 0
        gs.restore_energy(100)
        assert gs.player_energy == 100


# ---------------------------------------------------------------------------
# Hunger helper
# ---------------------------------------------------------------------------

class TestHungerHelper:
    def test_drain_hunger_normal(self, gs):
        gs.drain_hunger(10)
        assert gs.player_hunger == 90

    def test_drain_hunger_clamps_at_zero(self, gs):
        gs.drain_hunger(200)
        assert gs.player_hunger == 0

    def test_drain_hunger_exact_zero(self, gs):
        gs.drain_hunger(100)
        assert gs.player_hunger == 0


# ---------------------------------------------------------------------------
# Time helpers
# ---------------------------------------------------------------------------

class TestTimeHelpers:
    def test_increase_time_normal(self, gs):
        gs.game_time = "09 00"
        gs.increase_time(3)
        assert gs.game_time == "12 00"

    def test_increase_time_rolls_over_midnight(self, gs):
        gs.game_time = "22 00"
        gs.increase_time(3)
        assert gs.game_time == "01 00"
        assert gs.day == 2

    def test_increase_time_exact_midnight(self, gs):
        gs.game_time = "20 00"
        gs.increase_time(4)
        assert gs.game_time == "00 00"
        assert gs.day == 2

    def test_increase_time_multiple_days_rolled(self, gs):
        """Large increment that passes 24h still increments day."""
        gs.game_time = "10 00"
        gs.increase_time(20)
        assert gs.day == 2

    def test_day_counter_increments_once_per_rollover(self, gs):
        gs.game_time = "23 00"
        gs.increase_time(1)
        assert gs.day == 2
        gs.increase_time(1)
        assert gs.day == 2   # no second rollover this call

    def test_is_daytime_true_at_noon(self, gs):
        gs.game_time = "12 00"
        assert gs.is_daytime()

    def test_is_daytime_false_at_midnight(self, gs):
        gs.game_time = "00 00"
        assert not gs.is_daytime()

    def test_is_daytime_boundary_06(self, gs):
        gs.game_time = "06 00"
        assert gs.is_daytime()

    def test_is_daytime_boundary_18(self, gs):
        gs.game_time = "18 00"
        assert gs.is_daytime()

    def test_is_daytime_false_at_19(self, gs):
        gs.game_time = "19 00"
        assert not gs.is_daytime()


# ---------------------------------------------------------------------------
# Inventory counters
# ---------------------------------------------------------------------------

class TestInventoryCounters:
    def test_count_cheese_empty(self, gs):
        assert gs.count_cheese() == 0

    def test_count_cheese_nonzero(self, gs):
        gs.cheese[0][1] = 3
        gs.cheese[1][1] = 2
        assert gs.count_cheese() == 5

    def test_count_food_empty(self, gs):
        assert gs.count_food() == 0

    def test_count_food_nonzero(self, gs):
        gs.food["apple"] = 2
        gs.food["banana"] = 1
        assert gs.count_food() == 3
