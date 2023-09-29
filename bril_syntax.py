import json, sys, copy
from typing import List, Union

class Type:
    def __init__(self, type) -> None:
        if isinstance(type, dict):
            self.name = list(type.keys())[0]
            self.param = list(type.values())[0]
        else:
            self.name = type

    def __str__(self) -> str:
        if hasattr(self, 'param'):
            return f'{self.name}<{self.param}>'
        return f'{self.name}'

    def __format__(self, __format_spec: str) -> str:
        return str(self)

class FunctionArg:
    def __init__(self, arg_dict) -> None:
        self.name:str = arg_dict['name']
        self.type:Type = Type(arg_dict['type'])

    def __str__(self) -> str:
        return f'{self.name}: {str(self.type)}'

    def __format__(self, __format_spec: str) -> str:
        return str(self)

class Label:
    def __init__(self, label_dict) -> None:
        self.label:str = label_dict['label']

    def __str__(self):
        return f'.{self.label}'

    def __repr__(self):
        return str(self)

    def __format__(self, __format_spec: str) -> str:
        return str(self)

class Instruction:
    def __init__(self, inst_dict) -> None:
        self.op:str = inst_dict['op']
        if 'dest' in inst_dict:
            self.dest:str = inst_dict['dest']
            if 'type' in inst_dict:
                self.type:Type = Type(inst_dict['type'])
        if 'args' in inst_dict:
            self.args:List[str] = inst_dict['args']
        if 'funcs' in inst_dict:
            self.funcs = inst_dict['funcs']
        if 'labels' in inst_dict:
            self.labels:List[str] = inst_dict['labels']
        if 'value' in inst_dict:
            self.value = inst_dict['value']

    def __str__(self):
        s = ''
        if 'dest' in self.__dict__:
            s += f'{self.dest}'
            if 'type' in self.__dict__:
                s += f': {str(self.type)}'
            s += " = "
        s += f'{self.op}'
        if self.op == 'const':
            # bool consts in bril are in lower case
            if self.value is True:
                return s + ' true;'
            if self.value is False:
                return s + ' false;'
            return s + f' {self.value};'
        if self.op == 'jmp':
            return s + f' .{self.labels[0]};'
        if self.op == 'br':
            return s + f' {self.args[0]} .{self.labels[0]} .{self.labels[1]};'
        if self.op == 'phi':
            for var, lbl in zip(self.args, self.labels):
                s += f' {var} .{lbl}'
            return s + ';'
        if self.op == 'call':
            s += f' @{self.funcs[0]}'
        if hasattr(self, 'args'):
            s += ' '
            for i, arg in enumerate(self.args):
                s += f'{arg}'
                if i < len(self.args) - 1:
                    s += ' '
        return s + ';'

    def __eq__(self, other):
        return str(self) == str(other)

    def __format__(self, __format_spec: str) -> str:
        return str(self)

    def __repr__(self):
        return str(self)

    def terminate_baisc_blk(self) -> bool:
        return self.op in ['jmp', 'br']

class Function:
    def __init__(self, func_dict = None) -> None:
        self.name:str = func_dict['name']
        if 'args' in func_dict:
            self.args = [FunctionArg(arg) for arg in func_dict['args']]
        if 'type' in func_dict:
            self.type = Type(func_dict['type'])
        self.instrs = []
        for instr_or_lbl in func_dict['instrs']:
            if 'op' in instr_or_lbl:
                self.instrs.append(Instruction(instr_or_lbl))
            elif 'label' in instr_or_lbl:
                self.instrs.append(Label(instr_or_lbl))

    def __str__(self):
        argstring = ''
        if hasattr(self, 'args'):
            argstring = '('
            for i, arg in enumerate(self.args):
                argstring += str(arg)
                if i != len(self.args) - 1:
                    argstring += ', '
            argstring += ')'
        retstring = f': {str(self.type)}' if hasattr(self, 'type') else ''
        return f'{self.name}{argstring}{retstring}'

    def __format__(self, __format_spec: str) -> str:
        return str(self)

    def to_lines(self):
        lines = ['@' + str(self) + ' {\n']
        for instr in self.instrs:
            if isinstance(instr, Label):
                lines.append(str(instr) + ':\n')
            else:
                lines.append('  ' + str(instr) + '\n')
        lines.append('}\n')
        return lines

class Program:
    def __init__(self) -> None:
        self.functions = []

    def read_json_stdin(self):
        prog_dict = json.load(sys.stdin)
        self.functions = [
            Function(func) for func in prog_dict['functions']
        ]

    def load_json(self, path):
        with open(path, 'r') as f:
            prog_dict = json.load(f)
        self.functions = [
            Function(func) for func in prog_dict['functions']
        ]

    def store_txt(self, path):
        with open(path, 'w') as f:
            for func in self.functions:
                f.writelines(func.to_lines())
                f.write('\n')

class BasicBlk:
    def __init__(
        self,
        name:Union[str, None] = None,
        start:Union[int, None] = None,
        end:Union[int, None] = None,
    ) -> None:
        self.name = name
        self.instrs:List[Union[Instruction, Label]] = []
        self.start = start
        self.end = end

    def is_empty(self):
        return len(self.instrs) == 0

    def has_label(self):
        return (not self.is_empty()) and isinstance(self.instrs[0], Label)

    def get_label(self):
        if self.has_label():
            return self.instrs[0].label
        raise AttributeError(f"Block {self.name} does not have a label!")

    def __str__(self):
        return f'{self.name} ({self.start}:{self.end})'

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other) -> bool:
        if not isinstance(other, BasicBlk):
            return False
        return self.name == other.name

def __name_basic_blk(basic_blk, func_name, bblk_count):
    '''
        Generate a name for a basic block. If the block starts with
        a label, use the label as its name; otherwise, name is as the
        0, 1, 2... -th basic block of this function.
    '''
    if isinstance(basic_blk.instrs[0], Label):
        bblk_name = f'{func_name}_{basic_blk.instrs[0].label}'
    else:
        bblk_name = f'{func_name}_bb{bblk_count}'
    basic_blk.name = bblk_name

def get_baisc_blks(func:Function) -> List[BasicBlk]:
    '''
        Separate a function into a list of basic blocks
    '''
    basic_blks:List[BasicBlk] = [
        BasicBlk(name='ENTRY',start=0, end=1)
    ]
    basic_blks[0].instrs.append(
        Label({'label':'ENTRY'})
    )
    bblk_count = 0
    curr_blk = BasicBlk(start = 1)
    for i, instr in enumerate(func.instrs):
        # commit a basic block when it's the last instruction
        if i == len(func.instrs) - 1:
            curr_blk.instrs.append(instr)
            __name_basic_blk(curr_blk, func.name, bblk_count)
            bblk_count += 1
            curr_blk.end = i + 1 + 1
            basic_blks.append(copy.deepcopy(curr_blk))
        # add label if current block is empty, otherwise commit a block
        elif isinstance(instr, Label):
            if curr_blk.is_empty():
                curr_blk.instrs.append(instr)
            else:
                __name_basic_blk(curr_blk, func.name, bblk_count)
                bblk_count += 1
                curr_blk.end = i + 1
                basic_blks.append(copy.deepcopy(curr_blk))
                curr_blk = BasicBlk()
                curr_blk.start = i + 1
                curr_blk.instrs.append(instr)
        # for instructions, check if it terminates a block
        else:
            curr_blk.instrs.append(instr)
            if instr.terminate_baisc_blk():
                __name_basic_blk(curr_blk, func.name, bblk_count)
                bblk_count += 1
                curr_blk.end = i + 1 + 1
                basic_blks.append(copy.deepcopy(curr_blk))
                curr_blk = BasicBlk()
                curr_blk.start = i + 1 + 1
    return basic_blks

def line_no_to_blk(blocks:List[BasicBlk], line_no:int) -> BasicBlk:
    for blk in blocks:
        if line_no in range(blk.start, blk.end):
            return blk
    raise ValueError(f"Line {line_no} does not fall in any of the blocks!")

def concat_basic_blks(basic_blks:List[BasicBlk]) -> List[Union[Label, Instruction]]:
    '''
        Form a list of instructions|labels from a list of basic blocks.
    '''
    result = []
    for blk in basic_blks:
        result.extend(blk.instrs)
    return result

def instr_idx_to_blk(instr_idx:int, basic_blks:List[BasicBlk]) -> int:
    for i, blk in enumerate(basic_blks):
        if instr_idx in range(blk.start, blk.end):
            return i
    raise IndexError("Instruction not found in function!")
