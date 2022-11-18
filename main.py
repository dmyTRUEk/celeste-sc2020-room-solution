# Celeste Spring Collab 2020 room solution

from dataclasses import dataclass, field
from copy import deepcopy
import sys


FINISH_CELL_INDEX: int = 8


@dataclass
class RoomGraph:
    connected: list[list[bool]] = field(default_factory=list)

    def __post_init__(self):
        def b(*args: int):
            return list(map(bool, args))

        # initial room graph
        self.connected = [
            # s r c y o b g b f
            b(0,1,0,0,0,0,0,0,0), # spawn
            b(1,0,0,0,1,0,0,0,0), # red
            b(0,0,0,0,0,0,0,0,0), # cyan
            b(0,0,0,0,0,0,1,0,0), # yellow
            b(0,1,0,0,0,1,0,0,0), # orange
            b(0,0,0,0,1,0,0,0,1), # blue
            b(0,0,0,1,0,0,0,0,0), # green
            b(0,0,0,0,0,0,0,0,1), # bottom
            b(0,0,0,0,0,1,0,1,0), # finish
        ]

    def connect(self, i: int, j: int):
        self.connected[i][j] = True
        self.connected[j][i] = True

    def disconnect(self, i: int, j: int):
        self.connected[i][j] = False
        self.connected[j][i] = False

    def is_connected(self, starting_node: int, target_node: int) -> bool:
        visited = set()
        stack = [starting_node]
        while stack:
            node = stack.pop(-1)
            if node == target_node:
                return True
            if node not in visited:
                visited.add(node)
                # for neighbour in graph[node]:
                #     stack.append(neighbour)
                for i in range(9):
                    if self.connected[node][i]:
                        stack.append(i)
        return False
    
    def can_finish(self, madeline_position: int) -> bool:
        return self.is_connected(madeline_position, FINISH_CELL_INDEX)

    def get_possible_madeline_positions(self, madeline_position: int) -> list[int]:
        possible_madeline_positions: list[int] = []
        for i in range(FINISH_CELL_INDEX):
            if self.is_connected(madeline_position, i):
                possible_madeline_positions.append(i)
        return possible_madeline_positions




@dataclass
class RoomState:
    _red   : bool = False # 1 - number of cell where this key is located
    _cyan  : bool = False # 2
    _yellow: bool = False # 3
    _orange: bool = False # 4
    _blue  : bool = False # 5
    _green : bool = False # 6
    madeline_position: int = 0 # initial position

    def is_all_keys_enabled(self) -> bool:
        return self._red and self._cyan and self._yellow and self._orange and self._blue and self._green

    def enable_key(self, index: None | int):
        match index:
            case None: pass
            case 1: self._red    = True
            case 2: self._cyan   = True
            case 3: self._yellow = True
            case 4: self._orange = True
            case 5: self._blue   = True
            case 6: self._green  = True
            case _: raise ValueError("index must be in [1..=6]")

    def get_enableable_keys(self) -> list[int]:
        possible_madeline_positions: list[int] = (self
            .get_connections_graph()
            .get_possible_madeline_positions(self.madeline_position))
        enableable_keys: list[int] = []
        if (1 in possible_madeline_positions) and (not self._red   ): enableable_keys.append(1)
        if (2 in possible_madeline_positions) and (not self._cyan  ): enableable_keys.append(2)
        if (3 in possible_madeline_positions) and (not self._yellow): enableable_keys.append(3)
        if (4 in possible_madeline_positions) and (not self._orange): enableable_keys.append(4)
        if (5 in possible_madeline_positions) and (not self._blue  ): enableable_keys.append(5)
        if (6 in possible_madeline_positions) and (not self._green ): enableable_keys.append(6)
        return enableable_keys

    def get_connections_graph(self) -> RoomGraph:
        return self._get_connections_graph_after_block_movement()
        # return self._get_connections_graph_during_block_movement()

    def _get_connections_graph_after_block_movement(self) -> RoomGraph:
        rg = RoomGraph()
        if self._red:
            rg.connect(1, 2)
            rg.disconnect(0, 1)
        if self._cyan:
            rg.connect(3, 4)
            rg.disconnect(4, 5)
        if self._yellow:
            rg.connect(0, 3)
            rg.disconnect(3, 6)
        if self._orange:
            rg.connect(2, 5)
            rg.disconnect(5, 8)
        if self._blue:
            rg.connect(6, 7)
            rg.disconnect(7, 8)
        if self._green:
            rg.connect(4, 7)
            rg.disconnect(1, 4)
        return rg

    def _get_connections_graph_during_block_movement(self) -> RoomGraph:
        rg = RoomGraph()
        if self._red:
            rg.connect(1, 2)
        if self._cyan:
            rg.connect(3, 4)
        if self._yellow:
            rg.connect(0, 3)
        if self._orange:
            rg.connect(2, 5)
        if self._blue:
            rg.connect(6, 7)
        if self._green:
            rg.connect(4, 7)
        return rg




def find_solution(rs: RoomState, solution: list = list(), recursion_step: int=0):
    RECURSION_STEP_TO_PRINT: int = 2
    # if 0 < recursion_step <= 2:
    #     print(' '*2*(recursion_step-1) + "working...")

    def is_solved(rs_: RoomState) -> bool:
        # return rs_.is_all_keys_enabled() and rs.get_connections_graph().can_finish(rs.madeline_position)
        return rs_.is_all_keys_enabled() and rs.madeline_position == FINISH_CELL_INDEX
        # return rs_.is_all_keys_enabled() # to test if it works

    def check_is_solved(rs_: RoomState):
        if is_solved(rs_):
            print("SOLUTION FOUND!!! solution is:")
            for solution_step in solution:
                print("  - "+solution_step)
            sys.exit(0)

    check_is_solved(rs)

    enableable_keys: list[None | int] = ([None] if recursion_step==0 else []) + rs.get_enableable_keys() # here [None] on first step of recurstion actually means skipping block moving and moving madeline to some spot
    for enableable_key in enableable_keys:
        if recursion_step <= RECURSION_STEP_TO_PRINT:
            print('-'*(2*recursion_step) + f"thinking on key in cell #{enableable_key} / {enableable_keys}...")
        rsm: RoomState = deepcopy(rs)
        rsm.enable_key(enableable_key)
        solution.append(f"key in cell #{enableable_key}")
        check_is_solved(rsm)
        possible_madeline_positions: list[int] = (rsm
            .get_connections_graph()
            .get_possible_madeline_positions(rsm.madeline_position))
        for possible_madeline_position in possible_madeline_positions:
            if recursion_step <= RECURSION_STEP_TO_PRINT:
                print('-'*(2*recursion_step+1) + f"thinking on madeline position in cell #{possible_madeline_position} / {possible_madeline_positions}...")
            rsmm: RoomState = deepcopy(rsm)
            rsmm.madeline_position = possible_madeline_position
            solution.append(f"madeline in cell #{possible_madeline_position}")
            check_is_solved(rsmm)
            find_solution(rsmm, solution, recursion_step+1)
            solution.pop()
        solution.pop()



if __name__ == "__main__":
    # rg = RoomGraph()
    # for i in range(9):
    #     for j in range(9):
    #         is_connected = rg.is_connected(i, j)
    #         print(int(is_connected), end=' ')
    #     print()
    find_solution(RoomState())

