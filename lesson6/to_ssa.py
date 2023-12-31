import os, sys, copy
from tabulate import tabulate
from typing import List, Dict, Union, Set, Tuple
from collections import namedtuple

TASKS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(TASKS_ROOT)
import bril_syntax as bst
import bril_dataflow as bdf
from lesson4.reaching_defs import find_defs_uses_of_func
from lesson5.build_dominator_table import find_dominators
from lesson5.build_dominance_tree import construct_dominance_tree
from lesson5.find_dominance_frontiers import get_dominance_frontier

def dummy(*args, **kwargs):
    pass

BLK_LEVEL_TRACING = False
INSTR_LEVEL_TRACING = False

blk_level_trace = print if BLK_LEVEL_TRACING else dummy
instr_level_trace = print if INSTR_LEVEL_TRACING else dummy

def __get_var_old_name(var_ssa:str) -> str:
    return var_ssa.split('.')[0]

def __has_phi(blk:bst.BasicBlk, var:str) -> bool:
    for instr in blk.instrs:
        if isinstance(instr, bst.Instruction):
            if instr.op == 'phi':
                if instr.dest == var:
                    return True
    return False

def __create_phi(target_blk:bst.BasicBlk, var:str, labels:List[bst.Label]):
    target_blk.instrs.insert(
        1,
        bst.Instruction(
            {
                'op': 'phi',
                'dest': var,
                'args': [var for _ in range(len(labels))],
                'labels':labels
            }
        )
    )

def __analyze_func(func:bst.Function):

    blocks = bst.get_baisc_blks(func)

    # make sure all blocks have a label
    for blk in blocks:
        if not blk.has_label():
            blk.instrs.insert(
                0, bst.Label({'label':blk.name})
            )

    defs_per_blk, _ = find_defs_uses_of_func(func)
    cfg = bdf.CtrlFlowGraph()
    cfg.build_from_blocks(blocks)

    # get dominance table
    dom_table = find_dominators(cfg)
    # get dominance tree
    dom_tree = construct_dominance_tree(dom_table)
    # turn it into a dict for easier lookup
    imm_dom_dict = {n.cfg_vid:n for n in dom_tree}

    # get all defined varialbes
    variables = set()
    for dlist in defs_per_blk.values():
        variables.update([d.var for d in dlist])
    variables:List[str] = list(variables)

    # build a global map: var -> [blks where its defined]
    defs:Dict[str, List[bst.BasicBlk]] = {
        var:[] for var in variables
    }
    for var in variables:
        for blk_name, dlist in defs_per_blk.items():
            if var in [d.var for d in dlist]:
                defs[var].extend(filter(lambda b : b.name == blk_name, blocks))

    # add function arguments to the mapping
    if hasattr(func, 'args'):
        for farg in func.args:
            defs[farg.name].append(blocks[0])

    return blocks, variables, defs, cfg, dom_table, imm_dom_dict

def to_ssa(func:bst.Function):
    blk_level_trace(f"===== Processing function {func}")
    # get some critical data structures
    blocks, variables, defs, cfg, dom_table, imm_dom_dict = __analyze_func(func)

    # insert phi nodes
    for var in variables:
        # loop until there is no change in defs and all phi nodes
        while True:
            changed_phi = False
            prev_defs = copy.deepcopy(defs[var])
            for def_blk in prev_defs:
                dom_frontier = get_dominance_frontier(cfg.index(def_blk), cfg, dom_table)
                phi_candidates = [cfg.vertices[i].blk for i in dom_frontier]
                # account for self-loops
                if cfg.index(def_blk) in cfg.vertices[cfg.index(def_blk)].succ_ids:
                    phi_candidates.append(cfg.vertices[cfg.index(def_blk)].blk)
                for blk in phi_candidates:
                    if blk.name == 'EXIT':
                        continue
                    if not __has_phi(blk, var):
                        pred_ids = cfg.vertices[cfg.index(blk)].pred_ids
                        labels:List[str] = []
                        for p in pred_ids:
                            if cfg.vertices[p].blk.has_label():
                                labels.append(cfg.vertices[p].blk.get_label())
                        __create_phi(blk, var, labels)
                        changed_phi = True
                        if blk not in defs[var]:
                            defs[var].append(blk)
            if prev_defs == defs[var] and not changed_phi:
                break

    blk_level_trace()

    # rename variables

    # initialize stack
    stack:Dict[str, List[str]] = {var:[] for var in variables}
    if hasattr(func, 'args'):
        for farg in func.args:
            stack[farg.name].append(farg.name)
    count:Dict[str, int] = {var:1 for var in variables}

    # recursive renaming function
    def rename(block:bst.BasicBlk):
        blk_level_trace(f"Processing block {block.name}")
        pushes:List[str] = []
        for instr in block.instrs:
            if isinstance(instr, bst.Instruction):
                instr_level_trace('**', instr)
                if hasattr(instr, 'args') and instr.op != 'phi':
                    for i in range(len(instr.args)):
                        new_name = f'{instr.args[i]}.NOT_DEFINED'
                        if len(stack[instr.args[i]]) > 0:
                            new_name = stack[instr.args[i]][-1]
                        instr_level_trace(f'    renaming arg {instr.args[i]} to {new_name}')
                        instr.args[i] = new_name
                if hasattr(instr, 'dest'):
                    instr_level_trace(f'    renaming def {instr.dest} to {instr.dest}.{count[instr.dest]}')
                    old_name = instr.dest
                    instr.dest = f'{instr.dest}.{count[instr.dest]}'
                    instr_level_trace(f'    adding def {old_name}.{count[old_name]} to stack')
                    stack[old_name].append(f'{old_name}.{count[old_name]}')
                    pushes.append(old_name)
                    count[old_name] += 1

        cfg_vid = cfg.index(block)
        for succ in cfg.vertices[cfg_vid].succ_ids:
            for instr in cfg.vertices[succ].blk.instrs:
                if isinstance(instr, bst.Instruction) and instr.op == 'phi':
                    this_label = block.get_label()
                    if this_label in instr.labels:
                        arg_idx = instr.labels.index(this_label)
                    else:
                        continue
                    instr_level_trace(f"    update subsequent PHI-Node "
                                        f"in block {cfg.vertices[succ].blk.name}: `{instr}' ")
                    old_name = __get_var_old_name(instr.dest)
                    new_name = f'{old_name}.NOT_DEFINED'
                    if len(stack[old_name]) > 0:
                        new_name = stack[old_name][-1]
                    instr_level_trace(f'    renaming arg {instr.args[arg_idx]} to {new_name}')
                    instr.args[arg_idx] = new_name
        instr_level_trace(f"cfg_vid = {cfg_vid}, "
                          f"immediate dominating blocks:", imm_dom_dict[cfg_vid].children_ids)
        instr_level_trace("-- Recursively renaming blocks "
                         f"{[cfg.vertices[idb].blk.name for idb in imm_dom_dict[cfg_vid].children_ids]}")
        for idb in imm_dom_dict[cfg_vid].children_ids:
            rename(cfg.vertices[idb].blk)

        for psh in pushes:
            stack[psh].pop()

        blk_level_trace()

    # call rename on the entry
    rename(blocks[0])

    func.instrs = bst.concat_basic_blks(blocks)
    return func


def main():
    prog = bst.Program()
    prog.read_json_stdin()
    for func in prog.functions:
        func_ssa = to_ssa(func)
        sys.stdout.writelines(func_ssa.to_lines())
        print()

if __name__ == "__main__":
    main()