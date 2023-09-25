import os, sys, copy
from tabulate import tabulate
from typing import List, Dict, Union, Set, Tuple
from dataclasses import dataclass

TASKS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(TASKS_ROOT)
import bril_syntax as bst
import bril_dataflow as bdf

@dataclass
class Fork:
    vid:int
    from_start:int
    other_way:int

def find_paths(
    cfg:bdf.CtrlFlowGraph,
    src_blk:Union[bst.BasicBlk, int], dst_blk:Union[bst.BasicBlk, int],
) -> List[List[int]]:
    if isinstance(src_blk, int):
        src_id = src_blk
    else:
        src_id = cfg.vertices.index(src_blk)
    if isinstance(dst_blk, int):
        dst_id = dst_blk
    else:
        dst_id = cfg.vertices.index(dst_blk)
    paths:List[List[int]] = []
    branches:List[Fork] = []
    curr_path:List[int] = []
    curr_vid = src_id
    while True:
        # stop and commit if we reached the destination
        if curr_vid == dst_id:
            curr_path.append(dst_id)
            paths.append(copy.deepcopy(curr_path))
            if len(branches) == 0:
                break
            else:
                fork = branches.pop()
                curr_vid = fork.other_way
                curr_path = curr_path[:(fork.from_start + 1)]
                continue
        # if we visited a vertex again
        if curr_vid in curr_path:
            # see if there is another way out of the loop
            is_way_out = False
            for fork in branches:
                if curr_vid == fork.vid:
                    curr_path.append(curr_vid)
                    curr_vid = fork.other_way
                    is_way_out = True
                    break
            # if so, get out of the loop
            if is_way_out:
                continue
            # otherwise, backtrack
            else:
                if len(branches) == 0:
                    break
                else:
                    fork = branches.pop()
                    curr_vid = fork.other_way
                    curr_path = curr_path[:(fork.from_start + 1)]
                    continue

        next_vids = cfg.vertices[curr_vid].succ_ids
        # backtrack if we reached an end
        if len(next_vids) == 0:
            if len(branches) == 0:
                break
            else:
                fork = branches.pop()
                curr_vid = fork.other_way
                curr_path = curr_path[:(fork.from_start + 1)]
                continue
        # continue if there is only 1 successor
        if len(next_vids) == 1:
            curr_path.append(curr_vid)
            curr_vid = next_vids[0]
            continue
        # pick one way and record the other if there are 2 successors
        if len(next_vids) == 2:
            branches.append(Fork(curr_vid, len(curr_path), next_vids[1]))
            curr_path.append(curr_vid)
            curr_vid = next_vids[0]
            continue
        # there cannot be three successors in an CFG
    return paths

def print_paths(paths, cfg:bdf.CtrlFlowGraph):
    for i, p in enumerate(paths):
        print(f'Path {i+1}: ',end='')
        name_list = [cfg.vertices[vid].blk.name for vid in p]
        for j, n in enumerate(name_list):
            print(f'{n}', end='')
            if j < len(name_list) - 1:
                print(' -> ', end='')
        print("")

def check_dominance(cfg:bdf.CtrlFlowGraph, dom:int, target:int) -> bool:
    paths = find_paths(cfg, 0, target)
    for p in paths:
        if dom not in p:
            return False
    return True
