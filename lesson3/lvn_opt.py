import sys, copy, os
from typing import List, Tuple, Dict, Union

import unit_passes.dead_code_elimination as dce
import unit_passes.rename_old_defs as rod

TASKS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(TASKS_ROOT)
import bril_syntax as bst

COMMUTATIVE_INSTRS = ['add', 'mul']

class Value:
    def __init__(self, op:str, *ref_of_args:int, literal = None):
        '''
            ref_of_args should point to numbers in the Num2Var table
            value of const instructions are passed in as literal
        '''
        self.op = op
        self.args = [ar for ar in ref_of_args]
        if literal is not None:
            if op != 'const':
                raise ValueError(f"{op} instruction cannot have literals! (only const can)")
            self.literal = literal

    def __str__(self):
        if self.op == 'const':
            return f'(const, literal({self.literal}))'
        s = self.op
        argstr = ", ".join([str(arg) for arg in self.args])
        return f'{s}({argstr})'

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, Value):
            if self.op != other.op:
                return False
            same_args = self.args == other.args
            if self.op in COMMUTATIVE_INSTRS:
                same_args_swap = self.args[0] == other.args[1] and self.args[1] == other.args[0]
                return same_args or same_args_swap
            return same_args
        raise ValueError(f"Object of {type(other)} cannot be compared with {type(self)}!")

class LVNTables:
    def __init__(self) -> None:
        self.num2var:List[Tuple[Value, str, int]] = []
        self.var2num:Dict[str, int] = {}

    def add_instruction(self, instr:bst.Instruction, line_no:int):
        if not hasattr(instr, 'dest'):
            # skip if the instruction does not produce new values
            return
        if instr.op == 'id':
            # for id, just point it to the variable it is copying
            is_local = instr.args[0] in self.var2num
            if is_local:
                self.var2num[instr.dest] = self.var2num[instr.args[0]]
            return
        if instr.op in ['call', 'alloc']:
            # for calls, skip any analysis as there might be side effects
            # alloc will sure have side effects
            if hasattr(instr, 'arg'):
                is_local = (arg in self.var2num for arg in instr.args)
                if all(is_local):
                    args = (self.var2num[arg] for arg in instr.args)
                    val = Value(instr.op, *args)
                    self.var2num[instr.dest] = len(self.num2var)
                    self.num2var.append((val, instr.dest, line_no))
            else:
                val = Value(instr.op)
                self.var2num[instr.dest] = len(self.num2var)
                self.num2var.append((val, instr.dest, line_no))
            return
        if instr.op == 'const':
            # don't do constant propagation for now
            val = Value('const', literal = instr.value)
            self.var2num[instr.dest] = len(self.num2var)
            self.num2var.append((val, instr.dest, line_no))
            return
        else:
            # for other instructions, try to find a match in num2var table
            is_local = (arg in self.var2num for arg in instr.args)
            # only work if all arguments has local definition
            if all(is_local):
                args = (self.var2num[arg] for arg in instr.args)
                val = Value(instr.op, *args)
                for number, (registered_val, _, _) in enumerate(self.num2var):
                    if val == registered_val:
                        # if match, simply point to the record
                        # no need to worry about multiple definitions
                        # as the rename_old_defs pass will take care of them
                        self.var2num[instr.dest] = number
                        return
                # if no match, add a new entry
                self.var2num[instr.dest] = len(self.num2var)
                self.num2var.append((val, instr.dest, line_no))

def rewrite_basic_block(lvn_tables:LVNTables, input_blk:bst.BasicBlk) -> bst.BasicBlk:
    res_blk = bst.BasicBlk(name = input_blk.name)
    for line_no, instr in enumerate(input_blk.instrs):
        new_instr = copy.deepcopy(instr)
        if isinstance(instr, bst.Instruction):
            if hasattr(instr, 'args'):
                for i in range(len(instr.args)):
                    if instr.args[i] in lvn_tables.var2num:
                        val_number = lvn_tables.var2num[instr.args[i]]
                        if line_no > lvn_tables.num2var[val_number][2]:
                            # only rewrite variables defined earlier in the same block
                            src_arg = lvn_tables.num2var[val_number][1]
                            new_instr.args[i] = src_arg
        res_blk.instrs.append(new_instr)
    return res_blk

def reuse_common_subexpr(func:bst.Function) -> List[Union[bst.Label, bst.Instruction]]:
    blks = bst.get_baisc_blks(func)
    opt_blks = []
    for blk in blks:
        opt_blk = rod.rename_old_defs(blk)
        lvn_tables = LVNTables()
        for line_no, instr in enumerate(opt_blk.instrs):
            if isinstance(instr, bst.Instruction):
                lvn_tables.add_instruction(instr, line_no)
        opt_blks.append(rewrite_basic_block(lvn_tables, opt_blk))

        # print(opt_blks[-1].name)
        # for instr in opt_blks[-1].instrs:
        #     print(instr)
        # print("Num -> Var:")
        # for number, (val, var, _) in enumerate(lvn_tables.num2var):
        #     print(number, '|', val, '|', var)
        # print("Var -> Num:")
        # for var, number in lvn_tables.var2num.items():
        #     print(var, '|', number)
        # print()
    return bst.concat_basic_blks(opt_blks)

def lvn_opt_flow(func:bst.Function) -> bst.Function:
    opt_func = dce.delete_unused(func)
    opt_func.instrs = reuse_common_subexpr(opt_func)
    return dce.delete_unused(opt_func)

def main():
    prog = bst.Program()
    prog.read_json_stdin()
    for func in prog.functions:
        opt_func = lvn_opt_flow(func)
        sys.stdout.writelines(opt_func.to_lines())

if __name__ == '__main__':
    main()