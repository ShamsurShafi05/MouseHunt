"""
models/mouse.py
===============
Mouse model. Intentionally kept data-only — no game logic here.

NOTE: Mouse is NOT responsible for generating its own name/stats.
      The hunt module does the lookup and passes results in.
      This avoids a circular import (hunt.py spawns Mouse,
      Mouse used to import from hunt.py).

Construction example (from game/hunt.py):
    name  = generate_mouse(state.trap_cheese, state.enchant, state.points)
    gold, points = loot_lut(name)
    coat  = generate_coat(name)
    mouse = Mouse(name, gold, points, coat)
"""


class Mouse:
    def __init__(self, name: str | None, gold: int, points: int, coat: str):
        self.name   = name
        self.gold   = gold
        self.points = points
        self.coat   = coat

    def get_name(self) -> str | None:
        return self.name

    def get_gold(self) -> int:
        return self.gold

    def get_points(self) -> int:
        return self.points

    def get_coat(self) -> str:
        return self.coat

    def __str__(self) -> str:
        return self.name if self.name is not None else "None"