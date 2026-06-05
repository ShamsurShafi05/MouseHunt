"""
models/animal.py
================
Animal model. Writes damage directly to state — no parameter passing needed.
"""

from state import state

ANIMAL_STATS = {
    "tiger":    {"damage": 60},
    "wild boar": {"damage": 20},
}


class Animal:
    def __init__(self, animal_type: str):
        if animal_type not in ANIMAL_STATS:
            raise ValueError(f"Unknown animal type: '{animal_type}'")
        self.type   = animal_type
        self.damage = ANIMAL_STATS[animal_type]["damage"]

    def attack(self) -> bool:
        """
        Apply damage to state.player_health.
        Returns True if player is still alive, False if dead.
        """
        state.player_health -= self.damage
        alive = True

        if state.player_health <= 0:
            state.player_health = 0
            alive = False

        print(f"A {self.type} just attacked you! You lost {self.damage} HP")
        return alive