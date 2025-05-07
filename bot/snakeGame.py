import json
import os
import random

class SnakeGame:
    DIRECTIONS = ['UP', 'RIGHT', 'DOWN', 'LEFT']
    DIRECTION_VECTORS = {
        'UP': (-1, 0),
        'RIGHT': (0, 1),
        'DOWN': (1, 0),
        'LEFT': (0, -1)
    }
    DIRECTION_EMOJIS = {
        'UP': '⬆️',
        'RIGHT': '➡️',
        'DOWN': '⬇️',
        'LEFT': '⬅️'
    }
    
    EMOJI_EMPTY = '⬛'
    EMOJI_SNAKE_BODY = '🟩'
    EMOJI_FRUIT = '🍎'
    EMOJI_DEAD = '💥'
    
    def __init__(self, width=10, height=10, initial_length=3, modifiers=None, save_file="snake_game.json"):
        self.width = width
        self.height = height
        self.initial_length = initial_length
        self.modifiers = modifiers or {"wrap_edges": False}
        self.save_file = save_file
        self.fruits_eaten = 0

        if os.path.exists(save_file):
            self.load()
        else:
            self.snake = [(height // 2, width // 2 + i) for i in range(initial_length)][::-1]
            self.direction = 'LEFT'
            self.alive = True
            self.spawn_fruit()
            self.save()

    def spawn_fruit(self):
        empty_cells = [(r, c) for r in range(self.height) for c in range(self.width) if (r, c) not in self.snake]
        self.fruit = random.choice(empty_cells)

    def save(self):
        state = {
            "width": self.width,
            "height": self.height,
            "snake": self.snake,
            "direction": self.direction,
            "alive": self.alive,
            "fruit": self.fruit,
            "modifiers": self.modifiers,
            "fruits_eaten": self.fruits_eaten
        }
        with open(self.save_file, 'w') as f:
            json.dump(state, f)

    def load(self):
        with open(self.save_file, 'r') as f:
            state = json.load(f)
            self.width = state["width"]
            self.height = state["height"]
            self.snake = [tuple(pos) for pos in state["snake"]]
            self.direction = state["direction"]
            self.alive = state["alive"]
            self.fruit = tuple(state["fruit"])
            self.modifiers = state.get("modifiers", {"wrap_edges": False})
            self.fruits_eaten = state.get("fruits_eaten", 0)

    def display(self):
        board = [[self.EMOJI_EMPTY for _ in range(self.width)] for _ in range(self.height)]
        for y, x in self.snake[:-1]:
            board[y][x] = self.EMOJI_SNAKE_BODY
        head_y, head_x = self.snake[-1]
        if self.alive:
            board[head_y][head_x] = self.DIRECTION_EMOJIS[self.direction]
        else:
            board[head_y][head_x] = self.EMOJI_DEAD
        fruit_y, fruit_x = self.fruit
        board[fruit_y][fruit_x] = self.EMOJI_FRUIT
        return '\n'.join(''.join(row) for row in board)

    def turn(self, direction):  # 'LEFT', 'RIGHT', or 'FORWARD'
        if direction == 'LEFT':
            self.direction = self.DIRECTIONS[(self.DIRECTIONS.index(self.direction) - 1) % 4]
        elif direction == 'RIGHT':
            self.direction = self.DIRECTIONS[(self.DIRECTIONS.index(self.direction) + 1) % 4]
        # FORWARD just maintains current direction

        self.move()

    def move(self):
        if not self.alive:
            return

        dy, dx = self.DIRECTION_VECTORS[self.direction]
        head_y, head_x = self.snake[-1]
        new_y, new_x = head_y + dy, head_x + dx

        if self.modifiers.get("wrap_edges"):
            new_y %= self.height
            new_x %= self.width
        else:
            if not (0 <= new_y < self.height and 0 <= new_x < self.width):
                self.alive = False
                return

        new_head = (new_y, new_x)

        if new_head in self.snake:
            self.alive = False
            return

        self.snake.append(new_head)

        if new_head == self.fruit:
            self.fruits_eaten += 1
            self.spawn_fruit()
        else:
            self.snake.pop(0)

        self.save()

    def is_alive(self):
        return self.alive