import os, sys, copy
from tabulate import tabulate
from typing import List, Dict, Union, Set, Tuple
from dataclasses import dataclass

TASKS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(TASKS_ROOT)
import bril_utils as bu
import bril_dataflow as bdf
from lesson5.build_dominator_table import DominatorTable, find_dominators
from lesson5.check_dominance import check_dominance

def get_dominance_frontier(
    src_vid:int, cfg:bdf.CtrlFlowGraph, dom_tab:DominatorTable
) -> Set[int]:
    # get the list of vertices the specified block dominates
    dominating_vertices = list(
        filter(lambda vid: src_vid in dom_tab[vid], dom_tab.keys())
    )
    # check the successors of every dominated vertex
    dom_frontier = set()
    for vid in dominating_vertices:
        for succ in cfg.vertices[vid].succ_ids:
            if succ not in dominating_vertices:
                dom_frontier.add(succ)
    return dom_frontier

def print_dom_frontier(src_vid:int, dom_frontier:Set[int], cfg:bdf.CtrlFlowGraph):
    print(f"The dominance frontier of {cfg.vertices[src_vid].blk.name} is: ",end='')
    for i, df in enumerate(dom_frontier):
        print(cfg.vertices[df].blk.name, end='')
        if i < len(dom_frontier) - 1:
            print(', ', end='')
    print('')

def verify_dominance_frontier(src_vid:int, frontier:Set[int], cfg:bdf.CtrlFlowGraph) -> bool:
    passing = True
    for vid in frontier:
        # check if src dominates anyone in frontier
        if check_dominance(cfg, src_vid, vid):
            print(f"ERROR: {cfg.vertices[src_vid].blk.name} should not dominate"
                  f" {cfg.vertices[vid].blk.name} in its dominance frontier!")
            passing = False
        # check if src dominates any predecessor of everyone in frontier
        dominate_pred = [
            check_dominance(cfg, src_vid, pred)
            for pred in cfg.vertices[vid].pred_ids
        ]
        if not any(dominate_pred):
            print(f"ERROR: {cfg.vertices[src_vid].blk.name} should dominate"
                    f" one of the predcessors of {cfg.vertices[vid].blk.name}!")
    return passing

def main():
    prog = bu.Program()
    prog.read_json_stdin()
    for func in prog.functions:
        print(f"Dominance Frontier of {func}:")
        cfg = bdf.CtrlFlowGraph()
        cfg.build_from_blocks(bu.get_baisc_blks(func))
        dom_table = find_dominators(cfg)
        passing = True
        for v in cfg.vertices:
            dom_frontier = get_dominance_frontier(v.id, cfg, dom_table)
            print_dom_frontier(v.id, dom_frontier, cfg)
            passing = passing and verify_dominance_frontier(v.id, dom_frontier, cfg)
        if passing:
            print("Results are correct!")
        else:
            print("Results are WRONG!")

if __name__ == "__main__":
    main()
