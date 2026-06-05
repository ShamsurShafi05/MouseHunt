"""
tests/test_ui.py
================
Tests for game/ui.py: status-check booleans and show_pro_tips output.
"""

import pytest
from game.ui import check_health, check_energy, check_game_over, show_pro_tips


class TestCheckHealth:
    def test_healthy_returns_true(self, reset_state):
        reset_state.player_health = 100
        assert check_health() is True

    def test_zero_health_returns_false(self, reset_state):
        reset_state.player_health = 0
        assert check_health() is False

    def test_low_health_still_returns_true(self, reset_state, capsys):
        reset_state.player_health = 5
        result = check_health()
        assert result is True
        out = capsys.readouterr().out
        assert "attention" in out.lower()

    def test_negative_health_returns_false(self, reset_state):
        reset_state.player_health = -10
        assert check_health() is False


class TestCheckEnergy:
    def test_full_energy_returns_true(self, reset_state):
        reset_state.player_energy = 100
        assert check_energy() is True

    def test_zero_energy_returns_false(self, reset_state):
        reset_state.player_energy = 0
        assert check_energy() is False

    def test_low_energy_prints_warning(self, reset_state, capsys):
        reset_state.player_energy = 10
        check_energy()
        out = capsys.readouterr().out
        assert "critically low" in out.lower() or "energy" in out.lower()

    def test_low_energy_still_returns_true(self, reset_state):
        reset_state.player_energy = 15
        assert check_energy() is True


class TestCheckGameOver:
    def test_healthy_player_returns_false(self, reset_state):
        reset_state.player_health = 100
        reset_state.player_hunger = 100
        reset_state.gold = 100
        reset_state.cheese[0][1] = 5
        assert check_game_over() is False

    def test_dead_player_returns_true(self, reset_state):
        reset_state.player_health = 0
        assert check_game_over() is True

    def test_zero_hunger_returns_true(self, reset_state):
        reset_state.player_hunger = 0
        reset_state.player_health = 100
        assert check_game_over() is True

    def test_broke_and_no_cheese_returns_true(self, reset_state):
        reset_state.gold = 5
        reset_state.player_health = 100
        reset_state.player_hunger = 100
        # All cheese at 0
        assert check_game_over() is True

    def test_broke_but_one_cheese_returns_false(self, reset_state):
        reset_state.gold = 5
        reset_state.player_health = 100
        reset_state.player_hunger = 100
        reset_state.cheese[0][1] = 1
        result = check_game_over()
        assert result is False

    def test_hunger_warning_printed_at_20(self, reset_state, capsys):
        reset_state.player_health = 100
        reset_state.player_hunger = 20
        reset_state.gold = 100
        reset_state.cheese[0][1] = 5
        check_game_over()
        out = capsys.readouterr().out
        assert "starving" in out.lower()


class TestShowProTips:
    def test_no_food_warns_about_food(self, reset_state, capsys):
        # All food 0, give cheese+trap so only the food tip fires
        reset_state.cheese[0][1] = 5
        reset_state.trap_option[0] = ["Wood-and-Spring Trap", 1, 5]
        reset_state.current_trap = "Wood-and-Spring Trap"
        reset_state.trap_cheese = "Cheddar"
        show_pro_tips()
        out = capsys.readouterr().out
        assert "food" in out.lower() or "scavenge" in out.lower()

    def test_no_trap_warns_about_trap(self, reset_state, capsys):
        reset_state.food["apple"] = 1
        reset_state.current_trap = None
        # Make all traps non-functional
        for t in reset_state.trap_option:
            t[1] = 0
            t[2] = 0
        show_pro_tips()
        out = capsys.readouterr().out
        assert "trap" in out.lower()

    def test_no_cheese_warns_about_cheese(self, reset_state, capsys):
        reset_state.food["apple"] = 1
        reset_state.trap_option[0] = ["Wood-and-Spring Trap", 1, 5]
        reset_state.current_trap = "Wood-and-Spring Trap"
        reset_state.trap_cheese = None
        # All cheese qty = 0
        show_pro_tips()
        out = capsys.readouterr().out
        assert "cheese" in out.lower()

    def test_ready_to_hunt_message(self, reset_state, capsys):
        reset_state.food["apple"] = 1
        reset_state.trap_option[0] = ["Wood-and-Spring Trap", 1, 5]
        reset_state.current_trap = "Wood-and-Spring Trap"
        reset_state.trap_cheese = "Cheddar"
        reset_state.cheese[0][1] = 3   # Cheddar in stock
        show_pro_tips()
        out = capsys.readouterr().out
        assert "pro" in out.lower()   # "Looking like a pro…"
