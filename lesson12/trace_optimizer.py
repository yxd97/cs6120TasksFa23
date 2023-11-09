import sys, copy, os, json
from dataclasses import dataclass
from typing import List, Tuple, Dict, Union

TASKS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(TASKS_ROOT)
import bril_syntax as bst

OPTIMIZE_THRESHOLD = 5

def read_func_trace(func_trace:List[str]) -> List[bst.Line]:
    instrs:List[bst.Line] = []
    for tr in func_trace:
        obj = json.loads(tr)
        if "op" in obj:
            instrs.append(bst.Instruction(obj))
        elif "label" in obj:
            instrs.append(bst.Label(obj))
    return instrs

def clean_trace(traces:List[bst.Line], recover_label:str) -> List[bst.Instruction]:
    '''
        remove all jumps and labels,
        turn branches into guards,
        add speculate and commit
    '''
    output = [l for l in traces if isinstance(l, bst.Instruction)]
    output = [l for l in output if l.op != "jmp"]
    for l in output:
        if l.op == "br":
            l.op = "guard"
            l.labels = [recover_label]
    output.insert(
        0, bst.Instruction({"op": "speculate"})
    )
    output.append(
        bst.Instruction({"op": "commit"})
    )
    return output

class HotTrace:
    insert_point_label:str = ""
    instrs:List[bst.Instruction] = []

    def __init__(self, ipl, instrs) -> None:
        self.insert_point_label = ipl
        self.instrs = instrs

def find_hotspot(traces:List[bst.Line]) -> List[HotTrace]:
    label_history:List[bst.Label] = []
    label_index:List[int] = []
    results:List[HotTrace] = []
    for i, trace in enumerate(traces):
        # record the labels we hit
        if isinstance(trace, bst.Label):
            label_history.append(trace)
            label_index.append(i)

        # cases to abort tracing:
        # 1. hit the same label 5+ times, save the trace
        if isinstance(trace, bst.Label):
            occurances = [
                idx for idx in range(len(label_history))
                if label_history[idx] == trace
            ]
            if len(occurances) > OPTIMIZE_THRESHOLD:
                results.append(HotTrace (
                    trace.label,
                    clean_trace(
                        traces [
                            label_index[occurances[0]]:
                            label_index[occurances[-1]]
                        ],
                        trace.label
                    )
                ))
                label_history.clear()
                label_index.clear()
        # 2. meet a call instruction, clean history
        elif trace.op == "call":
            label_history.clear()
            label_index.clear()
    return results

def locate_label(instrs:List[bst.Line], label:str) -> int:
    for i, ln in enumerate(instrs):
        if isinstance(ln, bst.Label) and ln.label == label:
            return i
    raise ValueError(f"Cannot find label '{label}' in the given list of instructions")

def main():
    baseline_program = bst.Program()
    baseline_program.read_json_stdin()
    # find main
    main_fn_idx = -1
    for i, fn in enumerate(baseline_program.functions):
        if fn.name == "main":
            main_fn_idx = i
            break
    if main_fn_idx < 0:
        raise ValueError("Cannot find function main!")
    main_fn = baseline_program.functions[main_fn_idx]

    trace_file_path = sys.argv[1]
    with open(trace_file_path, 'r') as f:
        trace = f.readlines()
    traced_instrs = read_func_trace(trace[1:])
    hot_traces = find_hotspot(traced_instrs)
    if len(hot_traces) > 0:
        for hot_trace in hot_traces:
            insert_point = locate_label(main_fn.instrs, hot_trace.insert_point_label)
            main_fn.instrs = main_fn.instrs[:insert_point] + hot_trace.instrs + main_fn.instrs[insert_point:]
    for fn in baseline_program.functions:
        sys.stdout.writelines(fn.to_lines())

if __name__ == "__main__":
    main()