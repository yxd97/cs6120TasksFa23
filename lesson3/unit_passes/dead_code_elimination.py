import sys, copy, os

TASKS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(TASKS_ROOT)
import bril_utils as bu

SIDE_EFFECT_INSTR = ['call']
def delete_unused(func:bu.Function) -> bu.Function:
    res_func = copy.deepcopy(func)
    while True:
        deletable_instrs = []
        all_uses = set()
        # build a set of all uses
        for instr in res_func.instrs:
            if isinstance(instr, bu.Instruction):
                if hasattr(instr, 'args'):
                    for arg in instr.args:
                        all_uses.add(arg)
        # check if the dest of every instruction is used
        # record its index if not
        for i, instr in enumerate(res_func.instrs):
            if isinstance(instr, bu.Instruction):
                if instr.op in SIDE_EFFECT_INSTR:
                    continue
                if not hasattr(instr, 'dest'):
                    continue
                if instr.dest not in all_uses:
                    deletable_instrs.append(i)
        # return if nothing can be deleted
        if len(deletable_instrs) == 0:
            return res_func
        # otherwise, remove redundant instructions
        deletable_instrs.sort(reverse=True)
        for idx in deletable_instrs:
            res_func.instrs.pop(idx)

def main():
    prog = bu.Program()
    prog.read_json_stdin()
    for func in prog.functions:
        opt_func = delete_unused(func)
        sys.stdout.writelines(opt_func.to_lines())

if __name__ == '__main__':
    main()