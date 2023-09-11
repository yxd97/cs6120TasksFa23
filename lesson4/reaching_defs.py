import os, sys, copy
from typing import List, Dict, Tuple, Iterable
from dataclasses import dataclass

TASKS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(TASKS_ROOT)
import bril_utils as bu
import bril_dataflow as bdf

@dataclass
class Definition:
    var      : str
    count    : int      # global count
    instr_idx: int = -1 # points to func.instrs

    def __str__(self):
        return f'{self.var}_DEF{self.count}'

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other):
        if isinstance(other, Definition):
            return self.var == other.var and self.count == other.count
        raise ValueError(f"Object of {type(other)} cannot be compared with {type(self)}!")

@dataclass
class Use:
    count    : int # global count
    instr_idx: int # points to func.instrs

    def __str__(self):
        return f'USE{self.count}'

    def __repr__(self) -> str:
        return str(self)

def find_defs_uses_of_func(func:bu.Function):
    defs:Dict[str,List[Definition]] = {}
    def_count:Dict[str:int] = {}
    uses:Dict[str,List[Use]] = {}
    use_count = 0
    if hasattr(func, 'args'):
        defs[f'{func.name}_ENTRY'] = []
        for arg in func.args:
            def_count[arg.name] = 1
            defs[f'{func.name}_ENTRY'].append(Definition(f'{arg.name}', def_count[arg.name]))
    baisc_blks = bu.get_baisc_blks(func)
    for blk in baisc_blks:
        for i, instr in enumerate(blk.instrs):
            if isinstance(instr, bu.Instruction):
                if hasattr(instr, 'dest'):
                    if blk.name not in defs:
                        defs[blk.name] = []
                    if instr.dest in def_count:
                        def_count[instr.dest] += 1
                    else:
                        def_count[instr.dest] = 1
                    defs[blk.name].append(
                        Definition(instr.dest, def_count[instr.dest], i + blk.start)
                    )
            if hasattr(instr, 'args'):
                if blk.name not in uses:
                    uses[blk.name] = []
                use_count += 1
                uses[blk.name].append(Use(use_count, i + blk.start))
    return defs, uses

def build_cfg(funcname:str, blks:List[bu.BasicBlk]) -> bdf.CtrlFlowGraph:
    cfg = bdf.CtrlFlowGraph()
    entry_blk = bu.BasicBlk(name = f'{funcname}_ENTRY')
    # add blocks to cfg
    cfg.add_blk(entry_blk)
    for blk in blks:
        cfg.add_blk(blk)

    # add edges to cfg
    cfg.add_edge(entry_blk, blks[0])
    for i, blk in enumerate(blks):
        last_instr = blk.instrs[-1]
        if isinstance(last_instr, bu.Label):
            continue # skip empty blk
        if last_instr.op == 'jmp':
            target = last_instr.labels[0]
            for tblk in blks:
                if isinstance(tblk.instrs[0], bu.Label):
                    if tblk.instrs[0].label == target:
                        cfg.add_edge(blk, tblk)
                        break
        elif last_instr.op == 'br':
            target_true = last_instr.labels[0]
            target_flase = last_instr.labels[1]
            found_tt = False
            found_tf = False
            for tblk in blks:
                if isinstance(tblk.instrs[0], bu.Label):
                    if not found_tt and tblk.instrs[0].label == target_true:
                        cfg.add_edge(
                            blk, tblk,
                            cond = last_instr.args[0], val_if_taken=True
                        )
                        found_tt = True
                    if not found_tf and tblk.instrs[0].label == target_flase:
                        cfg.add_edge(
                            blk, tblk,
                            cond = last_instr.args[0], val_if_taken=False
                        )
                        found_tf = True
                    if found_tt and found_tf:
                        break
        elif i < len(blks) - 1:
            cfg.add_edge(blk, blks[i + 1])

    return cfg

def reaching_defs(func:bu.Function):
    defs, _ = find_defs_uses_of_func(func)
    blks = bu.get_baisc_blks(func)
    cfg = build_cfg(func.name, blks)

    # cfg.print()

    # # debugging
    # for k, v in defs.items():
    #     print(f'{k}: {v}')
    # print()

    def merge_func(inputs:Iterable[List[Definition]]) -> List[Definition]:
        result = []
        for idefs in inputs:
            for idef in idefs:
                if idef not in result:
                    result.append(copy.deepcopy(idef))
        return result

    def transfer_func(input:List[Definition], blk:bu.BasicBlk) -> List[Definition]:
        local_defs = defs.get(blk.name)
        if local_defs is None:
            return copy.deepcopy(input)

        # reduce local definitions into a kill list (only latest def is kept)
        local_defs.reverse() # let latest defs come first
        kill_list:List[Definition] = []
        for local_def in local_defs:
            if local_def.var not in [k.var for k in kill_list]:
                kill_list.append(local_def)
        local_defs.reverse() # restore to program order

        # add definitons from input that are not killed
        result:List[Definition] = list(
            filter(
                lambda d: d.var not in [k.var for k in kill_list],
                input
            )
        )

        # add new variable definitions
        result.extend(kill_list)
        return result

    # the worklist algorithm
    in_defs = {cfg.vertices[0].blk.name: []}
    out_defs = {v.blk.name:[] for v in cfg.vertices}
    worklist = [v for v in cfg.vertices]
    while len(worklist) > 0:
        work_vtx = worklist.pop(0)
        preds = [cfg.vertices[pid] for pid in work_vtx.pred_ids]
        in_defs[work_vtx.blk.name] = merge_func(
            [out_defs[p.blk.name] for p in preds]
        )
        new_out_def = transfer_func(
            in_defs[work_vtx.blk.name],
            work_vtx.blk
        )
        if out_defs[work_vtx.blk.name] != new_out_def:
            out_defs[work_vtx.blk.name] = new_out_def
            succs = [cfg.vertices[sid] for sid in work_vtx.succ_ids]
            worklist.extend(succs)

    # # debugging
    # for blk in blks:
    #     print(f'{blk.name}:')
    #     print(f'     {in_defs[blk.name]}')
    #     print(f'  -> {out_defs[blk.name]}')
    # print()

    # # debugging
    # for k, v in defs.items():
    #     print(f'{k}: {v}')
    # print()

    reached_defs:Dict[int:List[Definition]] = {}
    for blk in blks:
        remaining_defs:List[Definition] = in_defs[blk.name]
        def_idx = 0
        for i, instr in enumerate(blk.instrs):
            # print(f"{i + 1 + blk.start} | {instr}", end='')
            if isinstance(instr, bu.Instruction):
                # print(f"   remains: {remaining_defs}", end='')
                # if instr is a use, all remaining defs reaches here
                if hasattr(instr, 'args'):
                    reached_defs[i + blk.start] = copy.deepcopy(remaining_defs)
                # if instr is a def, add or kill remaining defs
                if hasattr(instr, 'dest'):
                    local_def = defs[blk.name][def_idx]
                    # print(f"; defining: {local_def}",end='')
                    # kill
                    killer = None
                    for remaining_def in remaining_defs:
                        if local_def.var == remaining_def.var:
                           killer = local_def
                           break
                    if killer is not None:
                        # print(f"; kill {local_def.var} with {local_def}", end='')
                        remaining_defs = list(
                            filter(
                                lambda p: p.var != killer.var, remaining_defs
                            )
                        )
                    # add
                    remaining_defs.append(copy.deepcopy(local_def))
                    def_idx += 1
            # print()
    # print()

    return reached_defs

def print_func_def_use_reach(
    func:bu.Function,
    defs:Dict[str,List[Definition]], uses:Dict[str,List[Use]],
    reached_defs, *,
    show_line_no = False,
    use_instr_idx = False
):
    blks = bu.get_baisc_blks(func)
    lines = func.to_lines()

    #===========================================================================
    # append defs and uses to each instruction
    #===========================================================================
    max_line_len = max([len(line) for line in lines])

    # treat defs for arguments
    padding = max_line_len - len(lines[0])
    if f'{func.name}_ENTRY' in defs:
        lines[0] = lines[0].replace('\n', '')
        lines[0] += (' '*padding + ' # defs: ')
        for d in defs[f'{func.name}_ENTRY']:
            lines[0] += f'{str(d)}, '
        lines[0] += '\n'

    # treat other lines
    curr_blk = 0
    blk_defs = defs.get(blks[curr_blk].name)
    blk_uses = uses.get(blks[curr_blk].name)
    for line_no in range(1, len(lines) - 1):
        padding = max_line_len - len(lines[line_no])
        instr_idx = line_no - 1
        if blk_defs is not None:
            curr_defs = list(filter(lambda d: d.instr_idx == instr_idx , blk_defs))
            has_def = len(curr_defs) > 0
        else:
            has_def = False

        if blk_uses is not None:
            curr_uses = list(filter(lambda u: u.instr_idx == instr_idx, blk_uses))
            has_use = len(curr_uses) > 0
        else:
            has_use = False

        if has_def or has_use:
            lines[line_no] = lines[line_no].replace('\n', '')
            lines[line_no] += (' '*padding + ' # ')
            if has_def:
                lines[line_no] += 'defs: '
                for d in curr_defs:
                    lines[line_no] += f'{str(d)}, '
            if has_use:
                lines[line_no] += 'uses: '
                for u in curr_uses:
                    lines[line_no] += f'{str(u)}, '
            lines[line_no] += '\n'
        if instr_idx >= blks[curr_blk].end and instr_idx < (len(lines) - 1):
            # print(f"current line {instr_idx}, switching to bblk {curr_blk + 1}")
            curr_blk += 1
            blk_defs = defs.get(blks[curr_blk].name)
            blk_uses = uses.get(blks[curr_blk].name)

    #===========================================================================
    # append reached defs to each instruction
    #===========================================================================
    max_line_len = max([len(line) for line in lines])

    for line_no in range(1, len(lines) - 1):
        padding = max_line_len - len(lines[line_no])
        instr_idx = line_no - 1
        if instr_idx in reached_defs:
            lines[line_no] = lines[line_no].replace('\n', '')
            lines[line_no] += (' '*padding + ' # reaching defs: ')
            for d in reached_defs[instr_idx]:
                lines[line_no] += f'{str(d)}, '
            lines[line_no] += '\n'

    line_no_digits = len(str(len(lines))) + 1
    for line_no, line in enumerate(lines):
        if show_line_no:
            if use_instr_idx:
                instr_idx = line_no - 1
                instr_idx_str = ' ' * (line_no_digits - len(str(instr_idx)))
                instr_idx_str += str(instr_idx)
                print(f'{instr_idx_str} | {line}', end='')
            else:
                line_no_str = ' ' * (line_no_digits - len(str(line_no)))
                line_no_str += str(line_no)
                print(f'{line_no_str} | {line}', end='')
        else:
            print(line, end='')



def main():
    prog = bu.Program()
    prog.read_json_stdin()
    for func in prog.functions:
        # for blk in bu.get_baisc_blks(func):
        #     print(f"{blk.name}: [{blk.start}, {blk.end})")
        defs, uses = find_defs_uses_of_func(func)
        reached_defs = reaching_defs(func)
        print_func_def_use_reach(
            func, defs, uses, reached_defs,
            # show_line_no=True, use_instr_idx=True
        )

if __name__ == "__main__":
    main()


