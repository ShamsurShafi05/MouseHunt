"""
tests/test_player.py
====================
Tests for player/player.py: name validation helpers and difficulty gold.
"""

import pytest
from unittest.mock import patch

# Import private helpers directly for unit testing
from player.player import (
    _is_valid_length,
    _is_valid_start,
    _is_one_word,
    _is_valid_name,
    setup_name,
    setup_difficulty,
)
from constants import START_GOLD


# ---------------------------------------------------------------------------
# Name validation helpers
# ---------------------------------------------------------------------------

class TestIsValidLength:
    def test_empty_string_invalid(self):
        assert not _is_valid_length("")

    def test_single_char_valid(self):
        assert _is_valid_length("A")

    def test_nine_chars_valid(self):
        assert _is_valid_length("Abcdefghi")

    def test_ten_chars_invalid(self):
        assert not _is_valid_length("Abcdefghij")


class TestIsValidStart:
    def test_letter_start_valid(self):
        assert _is_valid_start("Alice")

    def test_digit_start_invalid(self):
        assert not _is_valid_start("1Alice")

    def test_empty_string_invalid(self):
        assert not _is_valid_start("")

    def test_underscore_start_invalid(self):
        assert not _is_valid_start("_Alice")


class TestIsOneWord:
    def test_single_word_valid(self):
        assert _is_one_word("Hunter")

    def test_two_words_invalid(self):
        assert not _is_one_word("John Doe")

    def test_empty_invalid(self):
        assert not _is_one_word("")

    def test_trailing_space_invalid(self):
        assert not _is_one_word("Alice ")


class TestIsValidName:
    def test_valid_name_passes(self):
        assert _is_valid_name("Alice")

    def test_too_long_fails(self):
        assert not _is_valid_name("Abcdefghij")   # 10 chars

    def test_starts_with_digit_fails(self):
        assert not _is_valid_name("1Abc")

    def test_two_words_fails(self):
        assert not _is_valid_name("John Doe")

    def test_empty_fails(self):
        assert not _is_valid_name("")


# ---------------------------------------------------------------------------
# setup_name
# ---------------------------------------------------------------------------

class TestSetupName:
    def test_valid_name_stored(self, reset_state):
        with patch("builtins.input", return_value="Archer"):
            setup_name()
        assert reset_state.name == "Archer"

    def test_defaults_to_bob_after_max_attempts(self, reset_state):
        # All inputs are invalid (too long)
        with patch("builtins.input", return_value="Abcdefghij"):
            setup_name()
        assert reset_state.name == "Bob"

    def test_second_attempt_valid_name_accepted(self, reset_state):
        responses = iter(["1InvalidName", "ValidName"])
        with patch("builtins.input", side_effect=responses):
            setup_name()
        assert reset_state.name == "ValidName"


# ---------------------------------------------------------------------------
# setup_difficulty
# ---------------------------------------------------------------------------

class TestSetupDifficulty:
    def test_noob_sets_correct_gold(self, reset_state):
        reset_state.gold = 0
        with patch("builtins.input", return_value="1"):
            setup_difficulty()
        assert reset_state.gold == START_GOLD[0]

    def test_adventurer_sets_correct_gold(self, reset_state):
        reset_state.gold = 0
        with patch("builtins.input", return_value="2"):
            setup_difficulty()
        assert reset_state.gold == START_GOLD[1]

    def test_survivalist_sets_correct_gold(self, reset_state):
        reset_state.gold = 0
        with patch("builtins.input", return_value="3"):
            setup_difficulty()
        assert reset_state.gold == START_GOLD[2]

    def test_invalid_input_then_valid(self, reset_state):
        reset_state.gold = 0
        responses = iter(["x", "0", "4", "1"])
        with patch("builtins.input", side_effect=responses):
            setup_difficulty()
        assert reset_state.gold == START_GOLD[0]

    def test_gold_accumulates_on_existing_balance(self, reset_state):
        """Difficulty adds to existing gold, not resets it."""
        reset_state.gold = 50
        with patch("builtins.input", return_value="1"):
            setup_difficulty()
        assert reset_state.gold == 50 + START_GOLD[0]
