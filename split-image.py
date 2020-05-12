#!/usr/bin/env python3

import sys
from PIL import Image

left_stack_origin = (369, 464)
x_incr = 503 - left_stack_origin[0]
y_incr = 494 - left_stack_origin[1]
region_bounds = (19, 19)
num_stacks = 9
cards_per_stack = 4

ctr = 1
for filename in sys.argv[1:]:
    with Image.open(filename) as image:
        for s in range(num_stacks):
            for c in range(cards_per_stack):
                x, y = left_stack_origin[0] + x_incr * s, left_stack_origin[1] + y_incr * c
                region = image.crop((x, y, x+region_bounds[0], y+region_bounds[1]))
                region.save('/tmp/output/'+str(ctr)+'.png')
                ctr += 1