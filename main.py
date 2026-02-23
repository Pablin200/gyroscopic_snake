#!/usr/bin/env python3
import time
import random
from sense_hat import SenseHat

sense = SenseHat()
sense.clear()
sense.low_light = True

# ---- IMU Compatibility Fix ----
try:
    # Older versions use positional arguments
    sense.set_imu_config(False, True, True)
except TypeError:
    # Very old versions may not support set_imu_config
    pass
# --------------------------------

BLACK = (0, 0, 0)
SNAKE_HEAD = (0, 255, 0)
SNAKE_BODY = (0, 120, 0)
FOOD = (255, 0, 0)
TEXT = (80, 180, 255)

WIDTH = 8
HEIGHT = 8

BASE_DELAY = 0.35
SPEEDUP_EVERY = 4
MIN_DELAY = 0.10

TILT_THRESHOLD = 0.35
DIR_COOLDOWN = 0.12


def wrap_pos(x, y):
    return (x % WIDTH, y % HEIGHT)


def random_empty_cell(snake_cells):
    empty = [(x, y) for x in range(WIDTH) for y in range(HEIGHT)
             if (x, y) not in snake_cells]
    if not empty:
        return None
    return random.choice(empty)


def draw(snake, food):
    sense.clear()
    if food is not None:
        fx, fy = food
        sense.set_pixel(fx, fy, FOOD)

    if snake:
        hx, hy = snake[0]
        sense.set_pixel(hx, hy, SNAKE_HEAD)
        for x, y in snake[1:]:
            sense.set_pixel(x, y, SNAKE_BODY)


def show_game_over(score):
    sense.clear()
    sense.show_message("Score {}".format(score),
                       text_colour=TEXT,
                       back_colour=BLACK,
                       scroll_speed=0.06)
    sense.clear()


def read_tilt_direction():
    a = sense.get_accelerometer_raw()
    ax = a["x"]
    ay = a["y"]

    if abs(ax) < TILT_THRESHOLD and abs(ay) < TILT_THRESHOLD:
        return None

    if abs(ax) > abs(ay):
        return (1, 0) if ax > 0 else (-1, 0)
    else:
        return (0, -1) if ay > 0 else (0, 1)


def is_opposite(d1, d2):
    return (d1[0] == -d2[0]) and (d1[1] == -d2[1])


def main():
    snake = [(3, 4), (2, 4), (1, 4)]
    direction = (1, 0)

    food = random_empty_cell(set(snake))
    score = 0
    delay = BASE_DELAY
    last_dir_change = 0.0

    draw(snake, food)

    while True:
        now = time.time()

        new_dir = read_tilt_direction()
        if new_dir is not None and not is_opposite(new_dir, direction):
            if (now - last_dir_change) >= DIR_COOLDOWN:
                direction = new_dir
                last_dir_change = now

        hx, hy = snake[0]
        dx, dy = direction
        nx, ny = wrap_pos(hx + dx, hy + dy)
        new_head = (nx, ny)

        if new_head in snake:
            show_game_over(score)
            break

        snake.insert(0, new_head)

        if food is not None and new_head == food:
            score += 1

            if score % SPEEDUP_EVERY == 0:
                delay = max(MIN_DELAY, delay - 0.05)

            food = random_empty_cell(set(snake))
            if food is None:
                sense.show_message("YOU WIN!",
                                   text_colour=TEXT,
                                   back_colour=BLACK,
                                   scroll_speed=0.06)
                sense.clear()
                break
        else:
            snake.pop()

        draw(snake, food)
        time.sleep(delay)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sense.clear()
