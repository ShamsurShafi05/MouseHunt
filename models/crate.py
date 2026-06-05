"""
models/crate.py
===============
Crate model. Reads/writes state.gold and state.points directly
instead of taking them as parameters and returning new values.
"""

import time
from collections import deque
from state import state


class Crate:
    # (name, capacity, xp_req, gold_cost)
    TIERS = [
        ("Basic Crate",       5,   0,   0),
        ("Reinforced Crate", 10, 100,  80),
        ("Iron Crate",       20, 300, 200),
    ]

    def __init__(self):
        self._queue     = deque()
        self.tier_index = 0
        self.capacity   = self.TIERS[0][1]   # 5

    # -------------------------------------------------------------------
    # Core queue operations
    # -------------------------------------------------------------------

    def add(self, mouse) -> bool:
        """Enqueue a mouse. Returns False if crate is full."""
        if len(self._queue) >= self.capacity:
            return False
        self._queue.append(mouse)
        return True

    def remove(self):
        """Dequeue the oldest mouse (FIFO, for Trader). Returns None if empty."""
        if not self._queue:
            return None
        return self._queue.popleft()

    def is_full(self) -> bool:
        return len(self._queue) >= self.capacity

    def size(self) -> int:
        return len(self._queue)

    def contents(self) -> list:
        """Returns list of mouse names currently in the crate."""
        return [m.get_name() for m in self._queue]

    # -------------------------------------------------------------------
    # Events
    # -------------------------------------------------------------------

    def poison_wipe(self) -> None:
        """Poison mouse kills everything in the crate."""
        if not self._queue:
            print("Your crate is empty — nothing to poison.")
            return
        print("\nThe Poison Mouse's toxins seep through the crate...")
        time.sleep(1)
        while self._queue:
            victim = self._queue.popleft()
            print(f"  ...the {victim.get_name()} mouse convulses and goes still.")
            time.sleep(0.6)
        print("Your crate is now empty.\n")

    # -------------------------------------------------------------------
    # Upgrade  (reads/writes state directly — no parameter passing)
    # -------------------------------------------------------------------

    def upgrade(self) -> tuple[bool, str]:
        """
        Attempt to upgrade the crate to the next tier.
        Reads state.points and state.gold; deducts gold on success.
        Returns (success: bool, message: str).
        """
        if self.tier_index >= len(self.TIERS) - 1:
            return (False, "Old Carpenter: That crate's already as good as it gets, kid.")

        _, capacity, xp_req, gold_cost = self.TIERS[self.tier_index + 1]
        name = self.TIERS[self.tier_index + 1][0]

        if state.points < xp_req:
            return (False, f"Old Carpenter: You'll need at least {xp_req} XP before I upgrade that crate.")

        if state.gold < gold_cost:
            return (False, f"Old Carpenter: That'll cost {gold_cost} gold. You're a bit short, kid.")

        self.tier_index += 1
        self.capacity    = capacity
        state.gold      -= gold_cost
        return (True, f"Old Carpenter: There ye go — upgraded to a {name}! Holds {capacity} mice now.")

    # -------------------------------------------------------------------
    # Display
    # -------------------------------------------------------------------

    def display(self) -> None:
        tier_name = self.TIERS[self.tier_index][0]
        print(f"\n[ Crate: {tier_name} | {self.size()}/{self.capacity} mice ]")
        if self._queue:
            for i, m in enumerate(self._queue, 1):
                print(f"  {i}. {m.get_name()} mouse  |  Worth: {m.get_gold()} gold")
        else:
            print("  (empty)")
        print()