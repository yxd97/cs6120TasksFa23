import os, sys, copy
from tabulate import tabulate
from typing import List, Dict, Union, Set, Tuple
from dataclasses import dataclass

TASKS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(TASKS_ROOT)
import bril_syntax as bst
import bril_dataflow as bdf
from lesson5.check_dominance import check_dominance, find_paths, print_paths

DominatorTable = Dict[int, Set[int]]

def find_dominators(cfg:bdf.CtrlFlowGraph) -> DominatorTable:
    # initialize to be the universe
    dom_tab = {
        vid: set([i for i in range(len(cfg.vertices))])
        for vid in range(len(cfg.vertices))
    }
    # set the dominator of ENTRY to be itself
    dom_tab[0] = set([0])
    exit = False
    while not exit:
        prev_dom_tab = copy.deepcopy(dom_tab)
        for v in cfg.vertices:
            for p in v.pred_ids:
                dom_tab[v.id].intersection_update(dom_tab[p])
            dom_tab[v.id].add(v.id)
        exit = prev_dom_tab == dom_tab
    return dom_tab

def print_dom_tab(dom_tab:DominatorTable, cfg:bdf.CtrlFlowGraph):
    text = []
    for vid, doms in dom_tab.items():
        row = [f"{cfg.vertices[vid].blk.name}", ""]
        for dom in doms:
            row[1] += f"{cfg.vertices[dom].blk.name}, "
        text.append(row)
    print(tabulate(text, headers=['Block Name', 'Dominators']))

def verify_dominator_table(dom_tab:DominatorTable, cfg:bdf.CtrlFlowGraph) -> bool:
    passing = True
    for vid, doms in dom_tab.items():
        for dom in doms:
            if not check_dominance(cfg, dom, vid):
                print(f"ERROR: {cfg.vertices[dom].blk.name} ({dom}) "
                      f" does not dominate "
                      f"{cfg.vertices[vid].blk.name} ({vid})!"
                      )
                print(f"Paths from ENTRY to {cfg.vertices[vid].blk.name} ({vid}) are:")
                print_paths(find_paths(cfg, 0, vid), cfg)
                passing = False
    return passing

def main():
    prog = bst.Program()
    prog.read_json_stdin()
    for func in prog.functions:
        print(f"==== Dominator Table of {func}:")
        cfg = bdf.CtrlFlowGraph()
        cfg.build_from_blocks(bst.get_baisc_blks(func))
        dom_table = find_dominators(cfg)
        print_dom_tab(dom_table, cfg)
        if verify_dominator_table(dom_table, cfg):
            print("==== Results are correct!")
        else:
            print("==== Results are WRONG!")
        print("")


if __name__ == "__main__":
    main()
