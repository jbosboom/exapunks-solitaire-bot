import argparse
from pathlib import Path
import ast
import pyautogui
import solver
from recognizer import Recognizer

_left_stack_origin = (369, 464)
_x_incr = 503 - _left_stack_origin[0]
_y_incr = 494 - _left_stack_origin[1]
_region_bounds = (19, 19)
_num_stacks = 9
_cards_per_stack = 4

def parse_screenshot(image, recognizer):
    stacks = []
    for s in range(_num_stacks):
        stack = []
        for c in range(_cards_per_stack):
            x, y = _left_stack_origin[0] + _x_incr * s, _left_stack_origin[1] + _y_incr * c
            region = image.crop((x, y, x + _region_bounds[0], y + _region_bounds[1]))
            stack.append(recognizer(region))
        stacks.append(tuple(stack))
    stacks = tuple(stacks)
    return solver.Puzzle(stacks, None)

def solve_via_server(puzzle: solver.Puzzle, server_url):
    # ast.literal_eval doesn't handle namedtuples, so convert to a regular tuple.
    puzzle = (puzzle.stacks, puzzle.free)
    puzzle = repr(puzzle)

    import requests
    r = requests.post(server_url, data=puzzle)
    r.raise_for_status()
    solution = r.text
    return ast.literal_eval(solution)

def main(args):
    recognizer = Recognizer(Path('data/'))

    upper_left_x, upper_left_y, _, _ = pyautogui.locateOnScreen('data/upper-left.png')
    screenshot = pyautogui.screenshot(region=(upper_left_x, upper_left_y, 1920, 1080))
    puzzle = parse_screenshot(screenshot, recognizer)
    for stack in puzzle.stacks:
        print(stack)
    if args.server_url:
        solution = solve_via_server(puzzle, args.server_url)
    else:
        solution = solver.solve(puzzle)
    print(len(solution))
    print(solution)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--server-url", type=str)
    main(parser.parse_args())