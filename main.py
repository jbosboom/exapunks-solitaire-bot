from collections import namedtuple, deque
from pathlib import Path
import pyautogui
from recognizer import Recognizer

_left_stack_origin = (369, 464)
_x_incr = 503 - _left_stack_origin[0]
_y_incr = 494 - _left_stack_origin[1]
_region_bounds = (19, 19)
_num_stacks = 9
_cards_per_stack = 4

Puzzle = namedtuple('Puzzle', ('stacks', 'free'))

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
    return Puzzle(stacks, None)

_suit_stacks = [(suit,)*4 for suit in ('club', 'diamond', 'heart', 'spade')]
_pip_stacks = [
    (('black', 10), ('red', 9), ('black', 8), ('red', 7), ('black', 6)),
    (('red', 10), ('black', 9), ('red', 8), ('black', 7), ('red', 6)),
]
def is_solved(puzzle: Puzzle):
    if puzzle.free: return False
    for suit_stack in _suit_stacks:
        try:
            puzzle.stacks.index(suit_stack)
        except ValueError:
            return False
    for pip_stack in _pip_stacks:
        try:
            i = puzzle.stacks.index(pip_stack)
            puzzle.stacks.index(pip_stack, i+1)
        except ValueError:
            return False
    return True

def stacks_onto(before, after):
    if isinstance(before, str) or isinstance(after, str):
        return before == after
    sb, nb = before
    sa, na = after
    return sb != sa and nb == (na + 1)

def maximal_stack(stack):
    m = len(stack)-1
    while m > 0:
        if stacks_onto(stack[m-1], stack[m]):
            m -= 1
        else:
            break
    return m

def solve(puzzle: Puzzle):
    parent = {} # maps puzzles to (puzzle, move descriptor) pairs
    pending = deque()
    solved = None
    pending.append(puzzle)
    while pending and not solved:
        cur = pending.popleft()
        for i, source in enumerate(cur.stacks):
            if not source: continue
            m = maximal_stack(source)
            chunk = source[m:]

            # move this chunk to another stack
            for j, target in enumerate(cur.stacks):
                if i == j: continue
                if not target or stacks_onto(target[-1], chunk[0]):
                    stacks = list(cur.stacks)
                    stacks[i] = stacks[i][:m]
                    stacks[j] = stacks[j] + chunk
                    next = Puzzle(tuple(stacks), cur.free)
                    if next not in parent:
                        pending.append(next)
                        move_desc = ((i, m), (j, len(cur.stacks[j])))
                        parent[next] = (cur, move_desc)
                        if is_solved(next):
                            solved = next

            # if the free cell is empty and this stack is a single card, move it there
            if not cur.free and len(chunk) == 1:
                stacks = list(cur.stacks)
                stacks[i] = stacks[i][:m]
                next = Puzzle(tuple(stacks), chunk[0])
                if next not in parent:
                    pending.append(next)
                    move_desc = ((i, m), 'free')
                    parent[next] = (cur, move_desc)
                    if is_solved(next):
                        solved = next

        # if the free cell is full, try to move it
        if cur.free:
            for j, target in enumerate(cur.stacks):
                if not target or stacks_onto(target[-1], cur.free):
                    stacks = list(cur.stacks)
                    stacks[j] = stacks[j] + (cur.free,)
                    next = Puzzle(tuple(stacks), None)
                    if next not in parent:
                        pending.append(next)
                        move_desc = ('free', (j, len(cur.stacks[j])))
                        parent[next] = (cur, move_desc)
                        if is_solved(next):
                            solved = next

    solution = []
    while backptr := parent.get(solved):
        prev, move_desc = backptr
        solution.append(move_desc)
        solved = prev
    solution.reverse()
    return solution

def main(args):
    recognizer = Recognizer(Path('data/'))

    upper_left_x, upper_left_y, _, _ = pyautogui.locateOnScreen('data/upper-left.png')
    screenshot = pyautogui.screenshot(region=(upper_left_x, upper_left_y, 1920, 1080))
    puzzle = parse_screenshot(screenshot, recognizer)
    for stack in puzzle.stacks:
        print(stack)
    solution = solve(puzzle)
    print(len(solution))
    print(solution)

if __name__ == '__main__':
    main(None)