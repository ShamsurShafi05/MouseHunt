"""
tests/test_world.py
===================
Tests for game/world.py: sleep() stat recovery and eat_food() consumption.
"""

import pytest
from unittest.mock import patch
from game.world import sleep, eat_food


class TestSleep:
    def _sleep(self, hours):
        with patch("builtins.input", return_value=str(hours)):
            sleep()

    def test_sleep_restores_energy(self, reset_state):
        reset_state.player_energy = 10
        self._sleep(2)
        assert reset_state.player_energy == 70   # 10 + 2*30

    def test_sleep_restores_hp(self, reset_state):
        reset_state.player_health = 50
        self._sleep(2)
        assert reset_state.player_health == 56   # 50 + 2*3

    def test_sleep_energy_capped_at_100(self, reset_state):
        reset_state.player_energy = 90
        self._sleep(8)
        assert reset_state.player_energy == 100

    def test_sleep_hp_capped_at_100(self, reset_state):
        reset_state.player_health = 99
        self._sleep(8)
        assert reset_state.player_health == 100

    def test_sleep_advances_time(self, reset_state):
        reset_state.game_time = "09 00"
        self._sleep(3)
        assert reset_state.game_time == "12 00"

    def test_sleep_invalid_then_valid(self, reset_state):
        """First input is invalid, second is valid."""
        reset_state.player_energy = 0
        responses = iter(["abc", "3"])
        with patch("builtins.input", side_effect=responses):
            sleep()
        assert reset_state.player_energy == 90   # 0 + 3*30

    def test_sleep_out_of_range_then_valid(self, reset_state):
        reset_state.player_energy = 0
        responses = iter(["0", "9", "2"])
        with patch("builtins.input", side_effect=responses):
            sleep()
        assert reset_state.player_energy == 60


class TestEatFood:
    def test_eat_apple_increases_energy(self, reset_state):
        reset_state.player_energy = 50
        reset_state.food["apple"] = 1
        with patch("builtins.input", return_value="1"):
            eat_food()
        assert reset_state.player_energy == 60   # +10 from apple
        assert reset_state.food["apple"] == 0

    def test_eat_reduces_food_count(self, reset_state):
        reset_state.food["banana"] = 3
        reset_state.player_energy = 0
        with patch("builtins.input", return_value="1"):
            eat_food()
        assert reset_state.food["banana"] == 2

    def test_eat_updates_hunger(self, reset_state):
        reset_state.player_hunger = 50
        reset_state.food["mushrooms"] = 1
        with patch("builtins.input", return_value="1"):
            eat_food()
        assert reset_state.player_hunger == 80   # +30 from mushrooms

    def test_hunger_capped_at_100(self, reset_state):
        reset_state.player_hunger = 90
        reset_state.food["mushrooms"] = 1
        with patch("builtins.input", return_value="1"):
            eat_food()
        assert reset_state.player_hunger == 100

    def test_energy_capped_at_100(self, reset_state):
        reset_state.player_energy = 95
        reset_state.food["apple"] = 1   # +10 energy
        with patch("builtins.input", return_value="1"):
            eat_food()
        assert reset_state.player_energy == 100

    def test_eat_with_no_food_prints_message(self, reset_state, capsys):
        eat_food()
        out = capsys.readouterr().out
        assert "no food" in out.lower()

    def test_back_input_exits_without_eating(self, reset_state):
        reset_state.food["apple"] = 5
        reset_state.player_energy = 50
        with patch("builtins.input", return_value="back"):
            eat_food()
        assert reset_state.player_energy == 50
        assert reset_state.food["apple"] == 5

    def test_invalid_choice_prints_invalid(self, reset_state, capsys):
        reset_state.food["apple"] = 1
        with patch("builtins.input", return_value="99"):
            eat_food()
        out = capsys.readouterr().out
        assert "invalid" in out.lower()
