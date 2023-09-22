from typing import List, Union

import bril_utils as bu

class CFGVertex:
    def __init__(self, blk:bu.BasicBlk, id:int) -> None:
        self.id = id
        self.blk = blk
        self.pred_ids:List[int] = []
        self.succ_ids:List[int] = []

    def add_predesessor(self, id:int):
        self.pred_ids.append(id)

    def add_successor(self, id:int):
        self.succ_ids.append(id)

    def __eq__(self, other) -> bool:
        if isinstance(other, bu.BasicBlk):
            return self.blk.name == other.name # used to index blk in vertex list
        if isinstance(other, CFGVertex):
            return self.blk.name == other.blk.name and self.id == other.id
        return False

class CFGEdge:
    def __init__(
        self,
        src_blk_id:int, dst_blk_id:int,
        cond:str = None, val_if_taken:bool = None,
        *, name = None
    ) -> None:
        self.src = src_blk_id
        self.dst = dst_blk_id
        if name is None:
            self.name = f'{src_blk_id} -> {dst_blk_id}'
        else:
            self.name = name
        if cond is not None and val_if_taken is not None:
            self.add_contition(cond, val_if_taken)

    def add_contition(self, cond:str, val_if_taken:bool):
        self.cond = cond
        self.val_if_taken = val_if_taken

class CtrlFlowGraph:
    def __init__(self) -> None:
        self.vertices:List[CFGVertex] = []
        self.edges:List[CFGEdge] = []

    def add_blk(self, blk:bu.BasicBlk):
        v = CFGVertex(blk, len(self.vertices))
        self.vertices.append(v)

    def add_edge(
        self,
        src_blk:Union[bu.BasicBlk, int], dst_blk:Union[bu.BasicBlk, int],
        cond:str = None, val_if_taken:bool = None
    ) -> None:
        if isinstance(src_blk, int):
            src_id = src_blk
            src_name = self.vertices[src_blk].blk.name
        else:
            src_id = self.vertices.index(src_blk)
            src_name = src_blk.name
        if isinstance(dst_blk, int):
            dst_id = dst_blk
            dst_name = self.vertices[dst_blk].blk.name
        else:
            dst_id = self.vertices.index(dst_blk)
            dst_name = dst_blk.name
        name = f'{src_name} -> {dst_name}'
        self.vertices[src_id].add_successor(dst_id)
        self.vertices[dst_id].add_predesessor(src_id)
        e = CFGEdge(src_id, dst_id, cond, val_if_taken, name=name)
        self.edges.append(e)

    def build_from_blocks(self, blocks:List[bu.BasicBlk]) -> None:
        # add entry block
        self.add_blk(bu.BasicBlk(name='ENTRY'))
        # add other blocks
        for blk in blocks:
            self.add_blk(blk)
        # add exit block
        self.add_blk(bu.BasicBlk(name='EXIT'))
        # add edges
        self.add_edge(0, blocks[0]) # from entry to the first block
        for i, blk in enumerate(blocks):
            last_instr = blk.instrs[-1]
            if isinstance(last_instr, bu.Label): # this block only serves as target
                continue
            if last_instr.op == 'jmp': # has 1 target
                target_label = last_instr.labels[0]
                for b in blocks:
                    label = getattr(b.instrs[0], 'label', None)
                    if label == target_label:
                        self.add_edge(blk, b)
                        break
            elif last_instr.op == 'br': # has 2 targets
                target_label_t = last_instr.labels[0]
                target_label_f = last_instr.labels[1]
                found_blk_t = False
                found_blk_f = False
                for b in blocks:
                    label = getattr(b.instrs[0], 'label', None)
                    if not found_blk_t and label == target_label_t:
                        self.add_edge(blk, b, cond=last_instr.args[0], val_if_taken=True)
                        found_blk_t = True
                    if not found_blk_f and label == target_label_f:
                        self.add_edge(blk, b, cond=last_instr.args[0], val_if_taken=False)
                        found_blk_f = True
                    if found_blk_f and found_blk_t:
                        break
            elif last_instr.op == 'ret': # exit in the middle
                self.add_edge(blk, blocks[-1])
            elif i < len(blocks) - 1: # no targets and not the last
                self.add_edge(blk, blocks[i + 1])
            else: # if is the last, go to EXIT
                self.add_edge(blk, blocks[-1])

    def print(self):
        print("Vertices:")
        for v in self.vertices:
            print(f'  {v.id}: {v.blk.name}')
        print("Edges:")
        for e in self.edges:
            print(f'  {e.name}')
