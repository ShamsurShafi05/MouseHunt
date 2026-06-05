"""
game/hunt.py
============
Mouse generation logic and the main hunt loop.
All game state is read/written via the shared `state` object —
no parameters passed in, nothing returned.
"""

import random
import time

from state import state
from constants import (
    XP_UNLOCK_TIER_1, XP_UNLOCK_TIER_2, XP_UNLOCK_TIER_3,
    ENERGY_HUNT_COST, ENERGY_ANIMAL_COST,
    HUNGER_DRAIN_HUNT,
)
from models.mouse import Mouse
from models.animal import Animal
from art.ascii_art import (
    tiny_mouse, brown_mouse, white_mouse,
    grey_mouse, field_mouse, poison_mouse,
)


# ---------------------------------------------------------------------------
# Mouse generation helpers
# ---------------------------------------------------------------------------

# Order matches the probability tuple index:
# (miss, Brown, Field, Grey, White, Tiny, Poison)
_PROB_TABLE = {
    "cheddar": (0.47, 0.10, 0.15, 0.10, 0.10, 0.05, 0.03),
    "marble":  (0.57, 0.05, 0.20, 0.05, 0.02, 0.08, 0.03),
    "swiss":   (0.67, 0.01, 0.05, 0.05, 0.04, 0.15, 0.03),
    "swiss_enchanted": (0.42, 0.01, 0.05, 0.05, 0.04, 0.40, 0.03),
}

_LOOT_TABLE = {
    None:     (0,   1),
    "Brown":  (70,  60),
    "Field":  (15,  20),
    "Grey":   (60,  50),
    "White":  (80,  70),
    "Tiny":   (100, 100),
    "Poison": (0,   150),
}

_COAT_TABLE = {
    "Tiny":   tiny_mouse,
    "Brown":  brown_mouse,
    "White":  white_mouse,
    "Grey":   grey_mouse,
    "Field":  field_mouse,
    "Poison": poison_mouse,
}

_XP_ALLOWED = {
    "tier0": [None, "Field"],
    "tier1": [None, "Field", "Grey", "White", "Brown"],
    "tier2": [None, "Field", "Grey", "White", "Brown", "Tiny"],   # Poison still locked
    "tier3": [None, "Field", "Grey", "White", "Brown", "Tiny", "Poison"],
}


def generate_probabilities(cheese_type: str, enchant: bool = False) -> tuple:
    key = cheese_type.lower()
    if key == "swiss" and enchant:
        key = "swiss_enchanted"
    return _PROB_TABLE.get(key, _PROB_TABLE["cheddar"])


def generate_mouse(cheese: str, enchant: bool, points: int) -> str | None:
    """Roll a random mouse type, respecting XP unlock gates."""
    while True:
        p = generate_probabilities(cheese, enchant)
        num = random.random()

        cumulative = 1.0
        cumulative -= p[6]; spawn = "Poison" if num >= cumulative else None
        cumulative -= p[5]; spawn = "Tiny"   if num >= cumulative and spawn is None else spawn
        cumulative -= p[4]; spawn = "White"  if num >= cumulative and spawn is None else spawn
        cumulative -= p[3]; spawn = "Grey"   if num >= cumulative and spawn is None else spawn
        cumulative -= p[2]; spawn = "Field"  if num >= cumulative and spawn is None else spawn
        cumulative -= p[1]; spawn = "Brown"  if num >= cumulative and spawn is None else spawn

        # XP gates
        if points < XP_UNLOCK_TIER_1:
            allowed = _XP_ALLOWED["tier0"]
        elif points < XP_UNLOCK_TIER_2:
            allowed = _XP_ALLOWED["tier1"]
        elif points < XP_UNLOCK_TIER_3:
            allowed = _XP_ALLOWED["tier2"]
        else:
            allowed = _XP_ALLOWED["tier3"]

        if spawn in allowed:
            return spawn


def loot_lut(mouse_type: str | None) -> tuple[int, int]:
    """Return (gold, points) for a given mouse type."""
    return _LOOT_TABLE.get(mouse_type, (0, 0))


def generate_coat(mouse_type: str | None) -> str:
    """Return the ASCII art string for a mouse type."""
    fn = _COAT_TABLE.get(mouse_type)
    return fn() if fn else ""


def spawn_mouse(cheese: str, enchant: bool, points: int) -> Mouse:
    """Full pipeline: roll → loot → coat → Mouse instance."""
    name        = generate_mouse(cheese, enchant, points)
    gold, pts   = loot_lut(name)
    coat        = generate_coat(name)
    return Mouse(name, gold, pts, coat)


# ---------------------------------------------------------------------------
# Cheese helpers  (operate on state.cheese directly)
# ---------------------------------------------------------------------------

def has_cheese(cheese_name: str) -> int:
    """Return quantity of cheese_name in inventory, or 0 if none."""
    for entry in state.cheese:
        if entry[0] == cheese_name.capitalize():
            return entry[1]
    return 0


def consume_cheese(cheese_name: str) -> bool:
    """
    Deduct one unit of cheese_name from state.cheese.
    Returns True on success, False if out of stock.
    """
    if has_cheese(cheese_name) == 0:
        return False
    for entry in state.cheese:
        if entry[0] == cheese_name.capitalize():
            entry[1] -= 1
    return True


# ---------------------------------------------------------------------------
# Level-up announcements
# ---------------------------------------------------------------------------

def _level_check_1() -> None:
    print("=========================================================")
    print("Congrats you have unlocked new items:\n")
    print("NEW CHEESE: MARBLE")
    print("NEW TRAP: REINFORCED WOOD-CAGE")
    print(white_mouse())
    print(grey_mouse())
    print(brown_mouse())
    print("=========================================================")


def _level_check_2() -> None:
    print("=========================================================")
    print("Congrats you have unlocked new items:\n")
    print("NEW CHEESE: SWISS")
    print("NEW TRAP: MULTILAYER GLUED-BOARD")
    print("ENCHANTMENT UNLOCKED")
    print(tiny_mouse())
    print("=========================================================")


def _level_check_3() -> None:
    print("=========================================================")
    print("Congrats you have unlocked new content:\n")
    print("WARNING: Something has changed in these lands...")
    print("Rumour has it a deadly Poison Mouse has been spotted nearby.")
    print("Keep your crate close — and your wits closer.")
    print("=========================================================")


def _check_level_flags() -> None:
    """Fire level-up messages once each when XP thresholds are crossed."""
    if state.points >= XP_UNLOCK_TIER_1 and not state.level_flags["level_check_1"]:
        _level_check_1()
        state.level_flags["level_check_1"] = True

    if state.points >= XP_UNLOCK_TIER_2 and not state.level_flags["level_check_2"]:
        _level_check_2()
        state.level_flags["level_check_2"] = True

    if state.points >= XP_UNLOCK_TIER_3 and not state.level_flags["level_check_3"]:
        _level_check_3()
        state.level_flags["level_check_3"] = True


# ---------------------------------------------------------------------------
# Trap durability
# ---------------------------------------------------------------------------

def _decrement_trap(trap_name: str) -> None:
    """Reduce durability of the active trap by 1; mark broken at 0."""
    for t in state.trap_option:
        if t[0] == trap_name and t[2] > 0:
            t[2] -= 1
            if t[2] == 0:
                t[1] = 0
                print(f"\n*** Your {trap_name} has broken! Visit the Old Carpenter to get a new one. ***\n")
            break


# ---------------------------------------------------------------------------
# Hunt outcome handlers
# ---------------------------------------------------------------------------

def _handle_poison_mouse(mouse: Mouse) -> None:
    print("``````````````````````````````````````````")
    print("You caught a Poison Mouse!")
    print(mouse.get_coat())
    print("``````````````````````````````````````````")
    state.points += mouse.get_points()
    state.attempts["Successful hunt"] += 1
    state.caught_mouse_dictionary["Poison"] = (
        state.caught_mouse_dictionary.get("Poison", 0) + 1
    )
    print(f"You earned {mouse.get_points()} XP!")
    time.sleep(1)
    if state.crate is not None and state.crate.size() > 0:
        state.crate.poison_wipe()
    else:
        print("Lucky — your crate was empty. Nothing lost.\n")
    state.increase_time(3)


def _handle_caught_mouse(mouse: Mouse) -> None:
    state.points += mouse.get_points()
    state.gold   += mouse.get_gold()
    print("``````````````````````````````````````````")
    print(f"You caught a {mouse.name} mouse!")
    print(mouse.get_coat())
    print("``````````````````````````````````````````")
    state.caught_mouse_dictionary[mouse.name] = (
        state.caught_mouse_dictionary.get(mouse.name, 0) + 1
    )
    state.attempts["Successful hunt"] += 1
    print(f"You earned {mouse.get_gold()} gold and {mouse.get_points()} XP!")
    state.increase_time(3)

    # Crate prompt
    if state.crate is not None:
        if state.crate.is_full():
            print(f"Your crate is full. You watch the {mouse.name} mouse scurry away...")
        else:
            crate_input = input(
                "What do you want to do with it?\n1. Let Go\n2. Put in Crate\n"
            ).strip()
            if crate_input == "2":
                state.crate.add(mouse)
                print(f"{mouse.name} mouse added to crate. [{state.crate.size()}/{state.crate.capacity}]")
            else:
                print(f"You let the {mouse.name} mouse go.")


def _handle_miss(miss_streak: int) -> int:
    miss_streak += 1
    state.attempts["Unsuccessful hunt"] += 1
    print("The wilderness can sometimes be cruel. Hunt unsuccessful")
    state.increase_time(3)
    return miss_streak


# ---------------------------------------------------------------------------
# Main hunt loop
# ---------------------------------------------------------------------------

def hunt() -> None:
    """
    Main hunting session. Runs until the player types 'stop',
    game-over conditions are met, or energy runs out.
    Reads and writes state directly — no parameters, no return value.
    """
    from game.ui import check_game_over, check_health, check_energy

    miss_streak = 0

    while True:
        if check_game_over():
            break

        check_health()

        day_night = "Day" if state.is_daytime() else "Night"
        print(
            f"Day {state.day} [{day_night}]  Time: {state.game_time}  "
            f"Gold: {state.gold}  XP: {state.points}  Energy: {state.player_energy}/100\n"
        )

        if not check_energy():
            break

        # Night warning
        if not state.is_daytime():
            print("ProTip: The elders say it's best to avoid what lurks in the shadows of these unknown realms once dusk falls.")
            if input("Do you want to still continue to hunt? ['yes' or 'no'] ").lower() == "no":
                break
            risk1, risk2 = 0.5, 0.6
        else:
            risk1, risk2 = 0.1, 0.2

        # Guard: no trap selected
        if state.current_trap is None:
            print("You have no trap set. Head to the Old Carpenter first.")
            if input('Type "stop" to leave, or anything else to stay: ').lower() == "stop":
                break
            continue

        # Guard: trap is broken
        trap_broken = all(
            t[1] == 0 for t in state.trap_option if t[0] == state.current_trap
        )
        if trap_broken:
            print(f"Your {state.current_trap} is broken. Visit the Old Carpenter to get a new one.")
            if input('Type "stop" to leave, or anything else to stay: ').lower() == "stop":
                break
            continue

        # Sound the horn
        sound_input = input(
            '\nSound the horn by typing "yes". Type "stop" to end hunting session: '
        )
        if sound_input.isdigit():
            print("Invalid input.\n")
            continue
        if sound_input.lower() == "stop":
            break

        state.drain_energy(ENERGY_HUNT_COST)
        state.drain_hunger(HUNGER_DRAIN_HUNT)

        # Animal encounter
        roll = random.random()
        if roll < risk1:
            animal = Animal("tiger")
        elif roll < risk2:
            animal = Animal("wild boar")
        else:
            animal = None

        if animal:
            animal.attack()
            state.drain_energy(ENERGY_ANIMAL_COST)
            continue

        # Bad horn input
        if sound_input == "" or sound_input.lower() != "yes":
            print("You did not properly sound the horn. Hunt wasted.")
            miss_streak += 1
            state.increase_time(3)
            continue

        # No cheese on trap
        print("\n~~ ~ ~~~~ ~~~ ~~ ~~ ~ ~~~~\n")
        if state.trap_cheese is None:
            miss_streak += 1
            state.increase_time(1)
            print("Nothing happens. You are out of cheese!")
            continue

        # Try to consume cheese
        if not consume_cheese(state.trap_cheese):
            miss_streak += 1
            state.increase_time(1)
            print("Nothing happens. You are out of cheese!")
            continue

        # Spawn and resolve mouse
        mouse = spawn_mouse(state.trap_cheese, state.enchant, state.points)

        if mouse.name == "Poison":
            _handle_poison_mouse(mouse)
            miss_streak = 0
        elif mouse.name is not None:
            _handle_caught_mouse(mouse)
            miss_streak = 0
        else:
            miss_streak = _handle_miss(miss_streak)

        # Trap durability
        if state.trap_cheese is not None:
            _decrement_trap(state.current_trap)

        # Level-up checks
        _check_level_flags()

        # Miss streak warning
        if miss_streak > 0 and miss_streak % 5 == 0:
            print("Looks like you're not having a great hunting session today.")
            if input("Do you want to still continue to hunt? ['yes' or 'no'] ").lower() == "no":
                break

        print()