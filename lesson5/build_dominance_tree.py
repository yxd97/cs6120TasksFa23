import os, sys, copy
from tabulate import tabulate
from typing import List, Dict, Union, Set, Tuple
from dataclasses import dataclass

TASKS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(TASKS_ROOT)
import bril_utils as bu
import bril_dataflow as bdf
from lesson5.check_dominance import check_dominance
from lesson5.build_dominator_table import DominatorTable, find_dominators

class DominanceTreeNode:
    def __init__(self, cfg_vid:int) -> None:
        self.cfg_vid = cfg_vid
        self.children_ids:List[int] = []

    def add_child(self, cfg_vid:int):
        if id not in self.children_ids:
            self.children_ids.append(cfg_vid)

DominanceTree = List[DominanceTreeNode]

def print_dom_tree(dom_tree:DominanceTree, cfg:bdf.CtrlFlowGraph):
    for node in dom_tree:
        print(f'({cfg.vertices[node.cfg_vid].blk.name}', end='')
        if len(node.children_ids) > 0:
            print(": ", end='')
            for i, child in enumerate(node.children_ids):
                print(f'{cfg.vertices[child].blk.name}', end='')
                if i < len(node.children_ids) - 1:
                    print(', ',end='')
        print(")")

class DominatingTableEntry:
    def __init__(self, cfg_vid:int, dominating_vertices:List[int]) -> None:
        self.cfg_vid:int = cfg_vid
        self.dominating_vertices:List[int] = dominating_vertices

def construct_dominance_tree(dom_tab:DominatorTable) -> DominanceTree:
    # 'transpose' the dominator table into dominating table for easier lookup
    dominating_table:Dict[int, Set[int]] = {
        vid: set() for vid in dom_tab.keys()
    }
    for vid, doms in dom_tab.items():
        for dom in doms:
            dominating_table[dom].add(vid)
    # sort the dominating table by the expanding order of zone of dominance
    ordered_doming_tab:List[DominatingTableEntry] = [
        DominatingTableEntry(*item) for item in dominating_table.items()
    ]
    ordered_doming_tab.sort(
        key = lambda x: len(x.dominating_vertices)
    )
    # construct the tree. keep a mapping from cfg vertex id to tree node for easier lookup
    dom_tree_dict = {
        entry.cfg_vid: DominanceTreeNode(entry.cfg_vid)
        for entry in ordered_doming_tab
    }
    # the parent of a node is the nearest entry
    # # whose dominating vertices are a super set of its own
    for i, entry in enumerate(ordered_doming_tab):
        for j in range(i + 1, len(ordered_doming_tab)):
            parent_candidate = ordered_doming_tab[j]
            found_in_candidate = [
                dv in parent_candidate.dominating_vertices
                for dv in entry.dominating_vertices
            ]
            if all(found_in_candidate):
                dom_tree_dict[parent_candidate.cfg_vid].add_child(entry.cfg_vid)
                break
    # retrive the actual tree in bfs order
    def bfs_tree(cfg_vid):
        if len(dom_tree_dict[cfg_vid].children_ids) == 0:
            return [dom_tree_dict[cfg_vid]]
        result = [dom_tree_dict[cfg_vid]]
        for child in dom_tree_dict[cfg_vid].children_ids:
            result.extend(bfs_tree(child))
        return result
    return bfs_tree(0)

def verify_dominance_tree(tree:DominanceTree, table:DominatorTable, cfg:bdf.CtrlFlowGraph) -> bool:
    passing = True
    for node in tree:
        node_dominating_vertices = set(
            filter(lambda vid: node.cfg_vid in table[vid], table.keys())
        )
        for child in node.children_ids:
            # see if parent immediately dominates child:
            # {child's dominators} -intersect- {parent's dominating vertices}
            # = {parent, child}
            child_dominators = table[child]
            test = node_dominating_vertices.intersection(child_dominators)
            if test != set([node.cfg_vid, child]):
                print(f"ERROR: {cfg.vertices[node.cfg_vid].blk.name}"
                      f" does not immediately dominate its child "
                      f" {cfg.vertices[child].blk.name}!")
                print("Intermediate blocks:")
                for b in test:
                    if b != node.cfg_vid:
                        print(f"{cfg.vertices[b].blk.name}", end=', ')
                print("")
                passing = False
    return passing

def main():
    prog = bu.Program()
    prog.read_json_stdin()
    for func in prog.functions:
        print(f"==== Dominance Tree of {func}:")
        cfg = bdf.CtrlFlowGraph()
        cfg.build_from_blocks(bu.get_baisc_blks(func))
        dom_table = find_dominators(cfg)
        dom_tree = construct_dominance_tree(dom_table)
        print_dom_tree(dom_tree, cfg)
        if verify_dominance_tree(dom_tree, dom_table, cfg):
            print("==== Results are correct!")
        else:
            cfg.print()
            print("==== Results are WRONG!")
        print("")


if __name__ == "__main__":
    main()
