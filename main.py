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

_suit_stacks = [(suit,)*4 for suit in (('club',), ('diamond',), ('heart',), ('spade',))]
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

def make_valid_stacks():
    valid_stacks = set()
    for suit in (('club',), ('diamond',), ('heart',), ('spade',)):
        valid_stacks.add((suit, suit))
    for i in range(6, 10):
        valid_stacks.add((('black', i+1), ('red', i)))
        valid_stacks.add((('red', i+1), ('black', i)))
    return valid_stacks
valid_stacks = make_valid_stacks()

def maximal_stack(stack):
    m = len(stack)-1
    while m > 0:
        if (stack[m-1], stack[m]) in valid_stacks:
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
                if not target or (target[-1], chunk[0]) in valid_stacks:
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
                    # We can't have solved with a card in the free space, so don't check is_solved.

        # if the free cell is full, try to move it
        if cur.free:
            for j, target in enumerate(cur.stacks):
                if not target or (target[-1], cur.free) in valid_stacks:
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