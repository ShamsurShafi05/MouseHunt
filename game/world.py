"""
game/world.py
=============
World actions the player takes outside of shops:
scavenging, sleeping, eating.

All functions read/write state directly — no parameters, no return values.
"""

import random
import time

from state import state
from constants import (
    FOOD_ENERGY, FOOD_HUNGER,
    ENERGY_SCAVENGE_COST, ENERGY_ANIMAL_COST,
    HUNGER_DRAIN_SCAVENGE, MAX_ENERGY,
)
from models.animal import Animal
from art.ascii_art import show_description
from constants import TRAVEL_EVENTS


# ---------------------------------------------------------------------------
# Message pools for scavenging (module-level — they never change)
# ---------------------------------------------------------------------------

_SUCCESS_MESSAGES = [
    "You carefully search the forest floor and find some dry twigs..\nThey can be handy!",
    "You dig through the leaves and discover a few sturdy branches..\nDefinitely some good loot for the day!",
    "You stumble upon a fallen tree branch, perfect for crafting..\nThe carpenter will be delighted!",
    "You gather some scattered sticks from the ground..\nGod's mercy, indeed!",
    "You rummage through the underbrush and find a pile of firewood..\nCan definitely chop it up and put to good use!",
]

_FAIL_MESSAGES = [
    "You carefully search the forest floor and find some dry twigs..\nOh no — they are too brittle!",
    "You dig through the leaves and discover a few sturdy branches..\nNvm — they are too easily snappable!",
    "You stumble upon a fallen tree branch, perfect for crafting..\nWelp — it's too heavy to carry back!",
    "You gather some scattered sticks from the ground..\nDrop and run — Termites!",
    "You rummage through the underbrush and find a pile of firewood..\nHard luck — it's soaking wet!",
]

_FOOD_OPTIONS = ["apple", "banana", "berries", "mushrooms", "frog"]


# ---------------------------------------------------------------------------
# Scavenge
# ---------------------------------------------------------------------------

def travel_event_damage() -> None:
    if random.random() > 0.40:
        return
    msg, _ = random.choice(TRAVEL_EVENTS)   # base damage ignored — difficulty range used
    lo, hi = state.diff("travel_damage_range")
    damage = random.randint(lo, hi)
    state.player_health = max(0, state.player_health - damage)
    print(f"\n{msg} (-{damage} HP)\n")
    time.sleep(1)

def scavenge() -> None:
    from game.ui import check_energy, check_game_over

    day_night = "Day" if state.is_daytime() else "Night"
    print(
        f"Day {state.day} [{day_night}]  Time: {state.game_time}  "
        f"Gold: {state.gold}  XP: {state.points}  Energy: {state.player_energy}/100\n"
    )

    if not check_energy():
        return

    # state.drain_energy(ENERGY_SCAVENGE_COST)
    # state.drain_hunger(HUNGER_DRAIN_SCAVENGE)

    state.drain_energy(ENERGY_SCAVENGE_COST + state.diff("energy_drain_bonus"))
    state.drain_hunger(HUNGER_DRAIN_SCAVENGE + state.diff("hunger_drain_bonus"))

    # Animal risk scales with time of day
    if state.is_daytime():
        risk1, risk2 = state.diff("animal_risk_day")
    else:
        risk1, risk2 = state.diff("animal_risk_night")

    # Scavenge outcome — success rate scales with difficulty
    success_rate = state.diff("scavenge_success_rate")
    half_rate    = success_rate / 2
    event_roll   = random.random()
    random_index = random.randint(0, len(_SUCCESS_MESSAGES) - 1)   # ← add this line

    if event_roll < half_rate:
        wood_found = random_index + 1
        state.wood += wood_found
        msg = _SUCCESS_MESSAGES[random_index]
    elif event_roll < success_rate:
        food_found = random.choice(_FOOD_OPTIONS)
        state.food[food_found] += 1
        msg = f"You scavenge the forest and discover a {food_found}. Might come in handy!"
    elif event_roll < success_rate + 0.15:
        msg = _FAIL_MESSAGES[random_index]
    else:
        msg = "Despite your efforts, the forest floor yields nothing today."

    print(f"Wood collected: {state.wood}")
    show_description(msg)

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
        check_game_over()


# ---------------------------------------------------------------------------
# Sleep
# ---------------------------------------------------------------------------

def sleep() -> None:
    """Prompt the player for hours to sleep, then apply stat recovery."""
    while True:
        try:
            hours = int(input("How many hours do you want to sleep? (1-8): ").strip())
        except ValueError:
            print("Please enter a number.")
            continue
        if 1 <= hours <= 8:
            break
        print("Enter a number between 1 and 8.")

    energy_gain      = min(MAX_ENERGY, hours * 30)
    hp_gain          = hours * 3
    state.restore_energy(energy_gain)
    state.player_health = min(100, state.player_health + hp_gain)
    state.increase_time(hours)

    print(f"\nYou rest for {hours} hour(s).")
    print(f"  +{energy_gain} energy  →  {state.player_energy}/100")
    print(f"  +{hp_gain} HP       →  {state.player_health}/100\n")


# ---------------------------------------------------------------------------
# Eat food
# ---------------------------------------------------------------------------

def eat_food() -> None:
    """Let the player choose a food item from their inventory and consume it."""
    available = {k: v for k, v in state.food.items() if v > 0}

    if not available:
        print("You have no food to eat.")
        return

    print("What do you want to eat?")
    for i, (item, qty) in enumerate(available.items(), 1):
        print(f"  {i}. {item.capitalize()} (x{qty}) → +{FOOD_ENERGY[item]} energy, +{FOOD_HUNGER[item]} hunger")

    choice = input("Enter number (or 'back'): ").strip()

    if choice == "back":
        return

    if choice.isdigit() and 1 <= int(choice) <= len(available):
        item = list(available.keys())[int(choice) - 1]
        state.food[item] -= 1
        state.restore_energy(FOOD_ENERGY[item])
        state.player_hunger = min(100, state.player_hunger + FOOD_HUNGER[item])
        print(
            f"You ate a {item}. "
            f"+{FOOD_ENERGY[item]} energy → {state.player_energy}/100 | "
            f"Hunger: {state.player_hunger}/100"
        )
    else:
        print("Invalid choice.")