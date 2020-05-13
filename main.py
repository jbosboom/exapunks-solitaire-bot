from pathlib import Path
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

def main(args):
    recognizer = Recognizer(Path('data/'))

    upper_left_x, upper_left_y, _, _ = pyautogui.locateOnScreen('data/upper-left.png')
    screenshot = pyautogui.screenshot(region=(upper_left_x, upper_left_y, 1920, 1080))
    puzzle = parse_screenshot(screenshot, recognizer)
    for stack in puzzle.stacks:
        print(stack)
    solution = solver.solve(puzzle)
    print(len(solution))
    print(solution)

if __name__ == '__main__':
    main(None)