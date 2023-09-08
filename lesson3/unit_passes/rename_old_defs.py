import sys, copy, os
from typing import List, Dict

TASKS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(TASKS_ROOT)
import bril_utils as bu

def floor_in_list(n:int, l:List[int]) -> int:
    '''
        find the cloest value that is smaller than n
        within a increasingly sorted list.
        n and number in list must be non-negative
    '''
    for i in range(len(l) - 1):
        if l[i] < n and l[i+1] >= n:
            return l[i]
    return l[-1]

def rename_old_defs(blk:bu.BasicBlk) -> bu.BasicBlk:
    '''
        Rename all odl definitions of a variable with the
        block name and relative line number as the suffix. E.g.,
        ```
        4| x:int = const 3; => x_bb1_ln4:int = const 3;
        5| y:int = add x x; => y:int = add x_bb1_ln4 x_bb1_ln4;
        6| x:int = const 6; => x:int = const 6;
        7| z:int = add x x; => z:int = add x x;
        ```
        The last definition is left as is, because it may reach other
        basic blocks.
    '''
    res_blk = copy.deepcopy(blk)
    clean_blk_name = res_blk.name.replace('.', '_') # avoid . in variable names
    # scan the basic block to find the defs and uses of all variables
    # use list of relative line numbers
    defs:Dict[str,List[int]] = {}
    uses:Dict[str,List[int]] = {}
    for i, instr in enumerate(res_blk.instrs):
        if hasattr(instr, 'dest'):
            if instr.dest in defs:
                defs[instr.dest].append(i)
            else:
                defs[instr.dest] = [i]
        if hasattr(instr, 'args'):
            for arg in instr.args:
                if arg in uses:
                    uses[arg].append(i)
                else:
                    uses[arg] = [i]

    # for each use, replace variable name
    for var, use in uses.items():
        for use_ln in use:
            if var not in defs:
                continue # skip variables whose def is not in this baisc block
            if len(defs[var]) == 1:
                continue # skip single definitions
            def_ln = floor_in_list(use_ln, defs[var])
            if def_ln == defs[var][-1]:
                continue # skip if is the last definition
            use_instr = res_blk.instrs[use_ln]
            for i in range(len(use_instr.args)):
                if use_instr.args[i] == var:
                    use_instr.args[i] = f'{var}_{clean_blk_name}_ln{def_ln}'

    # for each definitions other than the last one, rename them
    for var, definition in defs.items():
        if len(definition) > 1:
            for def_ln in definition[:-1]:
                def_instr = res_blk.instrs[def_ln]
                def_instr.dest = f'{var}_{clean_blk_name}_ln{def_ln}'

    return res_blk


def main():
    prog = bu.Program()
    prog.read_json_stdin()
    for func in prog.functions:
        blks = bu.get_baisc_blks(func)
        opt_blks = []
        for blk in blks:
            opt_blk = rename_old_defs(blk)
            opt_blks.append(opt_blk)
        func.instrs = bu.concat_basic_blks(opt_blks)
        sys.stdout.writelines(func.to_lines())

if __name__ == "__main__":
    main()