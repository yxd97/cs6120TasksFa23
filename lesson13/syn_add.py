import sys, lark, z3

from typing import List
from ex2 import GRAMMAR, BITWIDTH, pretty, synthesize


def make_and(lhs, rhs):
    return f"(({lhs}) ? ({rhs}) : 0)"

def make_or(lhs, rhs):
    return f"(({lhs}) ? 1 : ({rhs}))"

def make_not(expr):
    return f"(({expr}) ? 0 : 1)"

def gen_rca_sum_exprs() -> List[str]:
    sums:List[str] = []
    cin_expr = "0"
    cout_expr = ""
    sum_expr = ""
    for i in range(BITWIDTH):
        # sum = xi xor hi xor ci
        # => hi ? !xi xor ci : xi xor ci
        # => hi ? xi*ci + !xi*!ci : !xi*ci + xi*!ci
        sum_h1 = make_or(
            make_and(f"(x::{i})", f"({cin_expr})"),
            make_and(make_not(f"(x::{i})"), make_not(f"({cin_expr})"))
        )
        sum_h0 = make_or(
            make_and(make_not(f"(x::{i})"), f"({cin_expr})"),
            make_and(f"(x::{i})", make_not(f"({cin_expr})"))
        )
        sum_expr = f"((h::{i}) ? ({sum_h1}) : ({sum_h0}))"
        # cout = xi*hi + ci*hi + ci*xi
        # => hi ? xi + ci : ci*xi
        cout_h1 = make_or(f"(x::{i})", f"({cin_expr})")
        cout_h0 = make_and(f"(x::{i})", f"({cin_expr})")
        cout_expr = f"((h::{i}) ? ({cout_h1}) : ({cout_h0}))"
        cin_expr = cout_expr
        sums.append(sum_expr)
    return sums

def syn_rca(incr:int):
    parser = lark.Lark(GRAMMAR)
    baseline = parser.parse(f"x + {incr}")
    sums = gen_rca_sum_exprs()
    opt_eqn = ""
    for i in range(BITWIDTH):
        if i == BITWIDTH - 1:
            opt_eqn += f"(({sums[i]}) * {2**i})"
        else:
            opt_eqn += f"(({sums[i]}) * {2**i}) + "
    opt = parser.parse(opt_eqn)

    solution = synthesize(baseline, opt)
    print(solution.model)


def main():
    # input = sys.stdin.read()
    syn_rca(1)

if __name__ == '__main__':
    main()
