from typing import List

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

    def add_edge(self,
        src_blk:bu.BasicBlk, dst_blk:bu.BasicBlk,
        cond:str = None, val_if_taken:bool = None
    ) -> None:
        src_id = self.vertices.index(src_blk)
        dst_id = self.vertices.index(dst_blk)
        name = f'{src_blk.name} -> {dst_blk.name}'
        self.vertices[src_id].add_successor(dst_id)
        self.vertices[dst_id].add_predesessor(src_id)
        e = CFGEdge(src_id, dst_id, cond, val_if_taken, name=name)
        self.edges.append(e)

    def print(self):
        print("Vertices:")
        for v in self.vertices:
            print(f'  {v.id}: {v.blk.name}')
        print("Edges:")
        for e in self.edges:
            print(f'  {e.name}')
