# this module will be imported in the into your flowgraph

import math


p1 = -math.pi
p2 = +math.pi

p = 0


def shift_phase(weighted_trigger):
    global p1, p2, p

    if weighted_trigger:
        p = p - weighted_trigger

    if p <= p1:
        p = p2

    return p
