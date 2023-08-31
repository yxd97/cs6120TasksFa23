import json

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

class FuncionArg:
    def __init__(self, arg_dict) -> None:
        self.name:str = arg_dict['name']
        self.type:Type = Type(arg_dict['type'])

    def __str__(self) -> str:
        return f'{self.name}:{str(self.type)}'

class Label:
    def __init__(self, label_dict) -> None:
        self.label:str = label_dict['label']

    def __str__(self):
        return f'.{self.label}'

class Instruction:
    def __init__(self, inst_dict) -> None:
        self.op:str = inst_dict['op']
        if 'dest' in inst_dict:
            self.dest:str = inst_dict['dest']
            self.type:Type = Type(inst_dict['type'])
        if 'args' in inst_dict:
            self.args = inst_dict['args']
        if 'funcs' in inst_dict:
            self.funcs = inst_dict['funcs']
        if 'labels' in inst_dict:
            self.labels = inst_dict['labels']

    def __str__(self):
        return self.op

    def terminate_baisc_blk(self) -> bool:
        return self.op in ['jmp', 'br']

class Function:
    def __init__(self, func_dict) -> None:
        self.name:str = func_dict['name']
        if 'args' in func_dict:
            self.args = [FuncionArg(arg) for arg in func_dict['args']]
        if 'type' in func_dict:
            self.type = func_dict['type']
        self.instrs = []
        for instr_or_lbl in func_dict['instrs']:
            if 'op' in instr_or_lbl:
                self.instrs.append(Instruction(instr_or_lbl))
            elif 'label' in instr_or_lbl:
                self.instrs.append(Label(instr_or_lbl))

    def __str__(self):
        argstring = ''
        if hasattr(self, 'args'):
            for i, arg in enumerate(self.args):
                argstring += str(arg)
                if i != len(self.args) - 1:
                    argstring += ', '
        retstring = f' -> {str(self.type)}' if hasattr(self, 'type') else ''
        return f'{self.name}({argstring}){retstring}'

def load_bril_prog(path:str):
    with open(path, 'r') as f:
        prog = json.load(f)
    return prog

class Program:
    def __init__(self, path) -> None:
        prog_dict = load_bril_prog(path)
        self.functions = [
            Function(func) for func in prog_dict['functions']
        ]
