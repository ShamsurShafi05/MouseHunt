"""
art/ascii_art.py
================
All ASCII art strings and print helpers.
No game logic, no state imports — pure display functions.
"""

import time


# ---------------------------------------------------------------------------
# Mouse coats  (returned as strings, not printed directly)
# ---------------------------------------------------------------------------

def tiny_mouse() -> str:
    return r"""
        (\_/)
        (o.o)  Tiny Mouse
        (")(")
        """

def brown_mouse() -> str:
    return r"""
        (\_/)
       ( o.o )  Brown Mouse
       (  :  )
       /     \
      /       \
    """

def white_mouse() -> str:
    return r"""
         (\__/)
        ( o . o )  White Mouse
         (  "  )
         /    \
        /      \
       (________)
    """

def grey_mouse() -> str:
    return r"""
         (\_/)
        ( o.o )  Grey Mouse
        (  :  )
       /       \
      (         )
       \_______/
    """

def field_mouse() -> str:
    return r"""
         (\__/)
        ( o.o )  Field Mouse
         (__:__)/

    """

def poison_mouse() -> str:          # kept bc previous test-cases use it 
    return r"""
         (\_/)
        ( x.x )  Poison Mouse
        (  :  )
       /  ~~~  \
      ( *dead* )
    """

def mouse_king() -> str:
    return r"""
          /\  /\
         ( crown )
       ╔═══════════╗
       ║ ◄ KING ►  ║
       ║  (x . x)  ║   <<< THE MOUSE KING >>>
       ║  ( ::: )  ║
       ║ /|     |\ ║
       ╚═══════════╝
         dark lord
    """


# ---------------------------------------------------------------------------
# Shop / world art  (these print directly)
# ---------------------------------------------------------------------------

def cheese_shop_art() -> None:
    print(r"""
      ________________________
     /                        \
    /    The  Cheese  Shop     \
   /____________________________\
        ||                ||
       _||________________||__
      |                      |
      |   PRICES (IN GOLD)   |
      |                      |
      |     Cheddar - 10     |
      |     Marble  - 50     |
      |     Swiss   - 100    |
      |______________________|
       (____________________)
    """)


def character_art(name: str) -> None:
    print(r"""
      O
     /|\
     / \
    """)
    print(f"~ {name} ~")


# ---------------------------------------------------------------------------
# Intro / narrative helpers
# ---------------------------------------------------------------------------

GAME_LOGO = r"""
      (\_/)
      (• .•)  < Mouse Hunt!
     \(  ><)
    ` ` ` ` `
"""

def show_description(message: str) -> None:
    """Print each line of a message with a short delay between lines."""
    for line in message.strip().split("\n"):
        print(line)
        time.sleep(2)


def game_intro(message: str) -> None:
    print(GAME_LOGO)
    print("Inspired by MouseHunt™, a release by ShafsterGames.")
    time.sleep(2)
    print("Programmer - Shamsur Shafi")
    time.sleep(2)
    print("Mice art - ChatGPT")
    time.sleep(2)
    print("Version launch - 1.2 (2026)")
    time.sleep(2)
    print()
    show_description(message)
    print()