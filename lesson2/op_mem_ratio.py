import sys, copy
from typing import List

sys.path.append('..')
import bril_syntax as bst

class BasicBlk:
    def __init__(self, name = None) -> None:
        self.name = name
        self.instrs = []

    def is_empty(self):
        return len(self.instrs) == 0

def name_basic_blk(basic_blk, func_name, bblk_count):
    '''
        Generate a name for a basic block. If the block starts with
        a label, use the label as its name; otherwise, name is as the
        0, 1, 2... -th basic block of this function.
    '''
    if isinstance(basic_blk.instrs[0], bst.Label):
        bblk_name = f'{func_name}.{basic_blk.instrs[0].label}'
    else:
        bblk_name = f'{func_name}.bb_{bblk_count}'
    basic_blk.name = bblk_name

def get_baisc_blks(func:bst.Function) -> List[BasicBlk]:
    basic_blks:List[BasicBlk] = []
    bblk_count = 0
    curr_blk = BasicBlk()
    for i, instr in enumerate(func.instrs):
        # commit a basic block when it's the last instruction
        if i == len(func.instrs) - 1:
            curr_blk.instrs.append(instr)
            name_basic_blk(curr_blk, func.name, bblk_count)
            bblk_count += 1
            basic_blks.append(copy.deepcopy(curr_blk))
        # add label if current block is empty, otherwise commit a block
        elif isinstance(instr, bst.Label):
            if curr_blk.is_empty():
                curr_blk.instrs.append(instr)
            else:
                name_basic_blk(curr_blk, func.name, bblk_count)
                bblk_count += 1
                basic_blks.append(copy.deepcopy(curr_blk))
                curr_blk = BasicBlk()
                curr_blk.instrs.append(instr)
        # for instructions, check if it terminates a block
        else:
            curr_blk.instrs.append(instr)
            if instr.terminate_baisc_blk():
                name_basic_blk(curr_blk, func.name, bblk_count)
                bblk_count += 1
                basic_blks.append(copy.deepcopy(curr_blk))
                curr_blk = BasicBlk()
    return basic_blks

ARITH_OPS = [
    'add', 'mul', 'sub', 'div'
]

CMP_OPS = [
    'eq', 'lt', 'gt', 'le', 'ge'
]

LOGIC_OPS = [
    'not', 'and', 'or'
]

MEM_ACCESS = [
    'load', 'store'
]

def count_operations(blk:BasicBlk) -> int:
    opcount = 0
    for instr in blk.instrs:
        if isinstance(instr, bst.Instruction):
            if instr.op in (ARITH_OPS + CMP_OPS + LOGIC_OPS):
                opcount += 1
    return opcount

def count_memory_access(blk:BasicBlk) -> int:
    accesses = 0
    for instr in blk.instrs:
        if isinstance(instr, bst.Instruction):
            if instr.op in MEM_ACCESS:
                accesses += 1
    return accesses

def print_help():
    print("Usage: python3 op_mem_ratio.py <json file>")
    print("  Ananlyzes the ratio of opeartions to memory accesses of each basic block in the program.")
    print("  Pointer arithmetics and function calls are ignored.")
    print("  Arguments:")
    print("    <json file>: A file contains the Bril program.")

def main():
    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)

    file_path = sys.argv[1]
    prog = bst.Program(file_path)
    for func in prog.functions:
        basic_blks = get_baisc_blks(func)
        for blk in basic_blks:
            ops = count_operations(blk)
            mems = count_memory_access(blk)
            if ops == 0:
                result_str = 'no operation'
            elif mems == 0:
                result_str = 'no memory access'
            else:
                result_str = f'{ops}/{mems} = {ops/mems}'
            print(f'{blk.name}: {result_str}')


if __name__ == '__main__':
    main()
