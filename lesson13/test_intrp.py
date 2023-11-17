import random, lark, z3
import pytest
from typing import Dict
from ex2 import GRAMMAR, BITWIDTH, pretty, run, z3_expr, solve

parser = lark.Lark(GRAMMAR)

def __test_harness(expr:str, env:Dict[str, int]):
    tree = parser.parse(expr)
    return run(tree, env)

GETBIT_TESTCASES = [
    (random.randint(0, 2**BITWIDTH-1), random.randint(0, BITWIDTH-1))
    for _ in range(10)
]

@pytest.mark.parametrize("x, y", GETBIT_TESTCASES)
def test_getbit(x, y):
    assert __test_harness("x::y", {'x': x, 'y': y}) == (x >> y) & 1
