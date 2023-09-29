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

def __get_var_old_name(var_ssa:str) -> str:
    return var_ssa.split('.')[0]

def from_ssa(func:bst.Function):
    blocks = bst.get_baisc_blks(func)
    cfg = bdf.CtrlFlowGraph()
    cfg.build_from_blocks(blocks)

    # add id instructions to predecessors of phi nodes
    for blk in blocks:
        for instr in blk.instrs:
            if isinstance(instr, bst.Instruction) and instr.op == 'phi':
                # skip phi nodes with only one argument
                # if we still insert an id, the rhs might be undefined
                if len(instr.args) == 1:
                    continue
                var = instr.dest
                for arg, label in zip(instr.args, instr.labels):
                    if arg.split('.')[-1] == "NOT_DEFINED":
                        continue
                    for pred_id in cfg.vertices[cfg.index(blk)].pred_ids:
                        if cfg.vertices[pred_id].blk.get_label() == label:
                            # print(f"Adding {var} = id {arg} to {cfg.vertices[pred_id].blk}")
                            insert_point = len(cfg.vertices[pred_id].blk.instrs)
                            last_instr = cfg.vertices[pred_id].blk.instrs[-1]
                            if isinstance(last_instr, bst.Instruction) and last_instr.op in ['jmp', 'br', 'ret']:
                                insert_point -= 1
                            cfg.vertices[pred_id].blk.instrs.insert(
                                insert_point,
                                bst.Instruction(
                                    {
                                        'op':'id',
                                        'args':[arg],
                                        'dest':var
                                    }
                                )
                            )


    # delete all phi nodes
    blocks_wo_phi:List[bst.BasicBlk] = []
    for blk in blocks:
        blocks_wo_phi.append(copy.deepcopy(blk))
        blocks_wo_phi[-1].instrs = []
        for instr in blk.instrs:
            if isinstance(instr, bst.Instruction) and instr.op == 'phi':
                continue
            blocks_wo_phi[-1].instrs.append(copy.deepcopy(instr))

    # refrech data structures
    func.instrs = bst.concat_basic_blks(blocks_wo_phi)

    blocks = bst.get_baisc_blks(func)
    cfg = bdf.CtrlFlowGraph()
    cfg.build_from_blocks(blocks)
    # get dominance table
    dom_table = find_dominators(cfg)
    # get definitions
    defines, _ = find_defs_uses_of_func(func)

    # some `id`s will access undefined variables due to loops
    # scenarios to keep them
    # 1. there is a definition in one of its dominators
    # 2. there is a definition in all the predecessors of one of its dominators
    # 3. it is a function argument
    instrs_wo_ill_id:List[Union[bst.Instruction, bst.Label]] = []
    for i, instr in enumerate(func.instrs):
        if isinstance(instr, bst.Instruction) and instr.op == 'id':
            blk = bst.line_no_to_blk(blocks, i)
            cfg_vid = cfg.index(blk)
            # check dominators
            keep = False
            dominator_ids = dom_table[cfg_vid]
            for dom_id in dominator_ids:
                dom_blk_name = cfg.vertices[dom_id].blk.name
                defined_by_dom = False
                all_pred_defines = False
                # see if defined by this dominator
                if dom_blk_name in defines:
                    defined_vars = [d.var for d in defines[dom_blk_name]]
                    if instr.args[0] in defined_vars:
                        defined_by_dom = True
                if defined_by_dom:
                    break
                # if not, see if defined by all the predcessors of this dominator
                all_pred_defines = True
                pred_ids = cfg.vertices[dom_id].pred_ids
                if len(pred_ids) == 0:
                    all_pred_defines = False
                else:
                    for pred_id in pred_ids:
                        pred_blk_name = cfg.vertices[pred_id].blk.name
                        if pred_blk_name in defines:
                            defined_vars = [d.var for d in defines[pred_blk_name]]
                            if instr.args[0] not in defined_vars:
                                all_pred_defines = False
                                break
                        else:
                            all_pred_defines = False
                            break
                if all_pred_defines:
                    break
            keep = defined_by_dom or all_pred_defines

            # check function arguments
            is_func_arg = hasattr(func, 'args') \
                          and instr.args[0] in [a.name for a in func.args]

            # omit copy if neither condition holds
            if not (keep or is_func_arg):
                # remove the dest from definitions
                defines[blk.name] = list(
                    filter(lambda d: d.var != instr.dest, defines[blk.name])
                )
                continue

        instrs_wo_ill_id.append(copy.deepcopy(instr))

    func.instrs = instrs_wo_ill_id
    return func

def main():
    prog = bst.Program()
    prog.read_json_stdin()
    for func_ssa in prog.functions:
        func = from_ssa(func_ssa)
        sys.stdout.writelines(func.to_lines())
        print()

if __name__ == "__main__":
    main()
