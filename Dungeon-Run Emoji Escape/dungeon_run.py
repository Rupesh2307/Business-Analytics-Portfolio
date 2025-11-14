import random
import os
import time

# Clear screen function (works on all OS and Google Colab)
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# Game settings
GRID_SIZE = 5

PLAYER = "🧙‍♂️"
MONSTER = "👹"
TREASURE = "💎"
TRAP = "💀"
EXIT = "🚪"
EMPTY = "·"

# Player stats
health = 10
score = 0

# Generate dungeon grid
def generate_grid():
    grid = [[EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    # Random placements
    grid[random.randint(0,4)][random.randint(0,4)] = TREASURE
    grid[random.randint(0,4)][random.randint(0,4)] = TRAP
    grid[random.randint(0,4)][random.randint(0,4)] = MONSTER

    # Place exit at bottom right
    grid[4][4] = EXIT

    return grid

# Game init
grid = generate_grid()
player_x, player_y = 0, 0

def draw_grid():
    clear()
    print("\n🔥 ** Dungeon Run: Emoji Escape ** 🔥\n")
    print(f"Health: ❤️ {health}   Score: ⭐ {score}\n")
    
    for r in range(GRID_SIZE):
        row = ""
        for c in range(GRID_SIZE):
            if r == player_y and c == player_x:
                row += PLAYER + " "
            else:
                row += grid[r][c] + " "
        print(row)
    print("\nMove using W A S D. Type Q to quit.")

def fight_monster():
    global health, score
    print("\n⚔️ A wild monster appears! ⚔️")
    time.sleep(1)
    outcome = random.choice(["win", "lose"])

    if outcome == "win":
        print("🎉 You defeated the monster!")
        score += 5
    else:
        print("💥 The monster hit you!")
        health -= 3
    time.sleep(1)

def trigger_trap():
    global health
    print("\n💀 You stepped on a trap! -2 health")
    health -= 2
    time.sleep(1)

def collect_treasure():
    global score
    print("\n💎 You found a treasure! +5 score")
    score += 5
    time.sleep(1)

# GAME LOOP
while True:
    draw_grid()

    move = input("Your move: ").lower()

    if move == "q":
        print("\nThanks for playing!")
        break

    # Movement logic
    if move == "w" and player_y > 0:
        player_y -= 1
    elif move == "s" and player_y < GRID_SIZE - 1:
        player_y += 1
    elif move == "a" and player_x > 0:
        player_x -= 1
    elif move == "d" and player_x < GRID_SIZE - 1:
        player_x += 1
    else:
        print("\n❌ Invalid move!")
        time.sleep(1)
        continue

    # Check the tile
    tile = grid[player_y][player_x]

    if tile == TREASURE:
        collect_treasure()
        grid[player_y][player_x] = EMPTY

    elif tile == TRAP:
        trigger_trap()
        grid[player_y][player_x] = EMPTY

    elif tile == MONSTER:
        fight_monster()
        grid[player_y][player_x] = EMPTY

    elif tile == EXIT:
        print("\n🎉🎉 YOU ESCAPED THE DUNGEON! 🎉🎉")
        print(f"Final Score: ⭐ {score}   Health: ❤️ {health}")
        print("Thanks for playing Dungeon Run: Emoji Escape!")
        break

    # Check health
    if health <= 0:
        print("\n💀 You died in the dungeon... Game Over!")
        break
