# 🐭 MouseHunt

> *Inspired by MouseHunt™ — a ShafsterGames release*

A terminal-based survival hunting game where you track, trap, and catch elusive mice across a dangerous wilderness. Manage your gold, energy, hunger, and health while upgrading your gear — and ultimately hunt down the legendary **Mouse King**.

---

## 🎮 Gameplay Overview

You are a hunter stranded in an unknown land with nothing but your wits and a broken wooden crate. Seek out the Old Carpenter, earn a trap, and begin your hunt.

Every decision matters:
- Wrong cheese = missed catches
- No food = starvation
- Wrong trap = the Mouse King escapes and **poisons your crate**

**Win condition:** Reach 500 XP, unlock Swiss cheese + the Multilayer Glued-Board Trap, and catch the Mouse King.

**Lose conditions:** Run out of HP, starve to death, or exhaust your gold and cheese supply.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🪤 **3 trap tiers** | Wood-and-Spring → Reinforced Wood-Cage → Multilayer Glued-Board |
| 🧀 **3 cheese types** | Cheddar → Marble → Swiss, each with different mouse attraction rates |
| ✨ **Enchantment system** | Swiss cheese enchants your trap, boosting Tiny mouse attraction |
| 🐭 **7 mouse types** | Brown, Field, Grey, White, Tiny, and the legendary Mouse King |
| 🌍 **World actions** | Hunt, scavenge the forest, sleep, eat, travel |
| 🏪 **4 NPCs** | Cheese Dealer, Old Carpenter, Trader, Witch Doctor — each with their own story |
| 📦 **Upgradeable crate** | Basic → Reinforced → Iron; sell mice to the Trader for gold |
| ⚔️ **Animal encounters** | Tigers and wild boars attack during hunts and scavenging |
| 🌙 **Day/night cycle** | Night hunting is riskier — animal encounter rates spike after dusk |
| 🎯 **2 difficulty modes** | Noob (200 gold start) and Survivalist (125 gold, harsher penalties) |
| 📖 **Narrative ending** | Full multi-scene story epilogue when the Mouse King falls |

---

## 🗂️ Project Structure

```
MouseHunt/
│
├── main.py                  # Entry point and main game loop
├── constants.py             # All fixed game data (traps, cheese, difficulty)
├── state.py                 # Shared GameState singleton
│
├── game/
│   ├── hunt.py              # Mouse generation, loot tables, hunt logic
│   ├── shops.py             # Carpenter, Trader, Witch Doctor, Cheese Shop
│   ├── ui.py                # Menus, status checks, pro tips
│   └── world.py             # Scavenge, sleep, eat, travel events
│
├── models/
│   ├── mouse.py             # Mouse data model
│   ├── animal.py            # Animal attack model
│   └── crate.py             # Crate inventory (FIFO queue, upgrades)
│
├── art/
│   └── ascii_art.py         # All ASCII art and print helpers
│
├── player/
│   └── player.py            # Name validation, difficulty setup
│
├── tutorial/
│   └── tutorial.py          # Larry's tutorial sequence
│
└── tests/
    ├── conftest.py
    ├── test_hunt.py
    ├── test_models.py
    ├── test_player.py
    ├── test_shops.py
    ├── test_state.py
    ├── test_ui.py
    └── test_world.py
```

---

## 🚀 Getting Started

**Requirements:** Python 3.12+

```bash
# Clone the repo
git clone https://github.com/your-username/MouseHunt.git
cd MouseHunt

# No external dependencies — just run it
python main.py
```

---

## 🧪 Running Tests

```bash
pip install pytest
pytest tests/ -v
```

**252 tests** across 8 test modules covering game state, hunt logic, shop mechanics, world actions, and all models.

---

## 🎯 How to Win

The game progression follows three XP tiers:

```
0 XP ──────────── 100 XP ──────────── 300 XP ──────────── 500 XP
  Start             Tier 1              Tier 2              Tier 3
  Cheddar only      Marble unlocked     Swiss unlocked      Mouse King appears
  Field/None        Brown/Grey/White    Tiny mouse          Catchable with:
                    Reinforced trap     Multilayer trap     • Swiss cheese
                                        Enchantment         • Multilayer trap
```

**Key tip:** The Trader's son left behind notes. Find the Trader early.

---

## 🏗️ Version History

| Branch | Description |
|---|---|
| `v1-legacy` | Original single-file implementation (`mousehunt.py`) |
| `refactor/project-structure` | Full modular refactor — separate packages, GameState singleton, difficulty scaling |
| `feature/mouse-king` | Mouse King boss fight, narrative ending, enchantment system, 252 tests |

---

## 👤 Credits

| Role | Credit |
|---|---|
| Game Design & Programming | Shamsur Shafi |
| Mice ASCII Art | ChatGPT |
| NPC Dialogue & Story | Claude (Anthropic) |
