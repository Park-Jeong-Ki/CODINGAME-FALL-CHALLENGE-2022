from typing import Optional

import math
from collections import deque
from dataclasses import dataclass

# GLOBAL VARIABLE
# ME = me flag
# OPP = opp flag
# NONE = neutral flag
ME = 1
OPP = 0
NONE = -1
DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

# INITALIZE WIDTH & HEIGHT
W, H = [int(i) for i in input().split()]

# INITALIZE TILE CLASS


@dataclass
class Tile:
    x: int
    y: int
    scrap_amount: int
    owner: int
    units: int
    recycler: bool
    can_build: bool
    can_spawn: bool
    in_range_of_recycler: bool


# CUSTOM FUNCTION

# 내 유닛에서 절반을 내 빈땅, 절반은 상대유닛으로 간다.
# 나머지는 리사이클러 설치
# 35로 2개만 설치하고, 적을 만나서 리사이클러 설치한 이후에는 설치X


def is_grass(tile):
    return tile.scrap_amount == 0


def is_unmovable(tile):
    return is_grass(tile) or tile.recycler or (tile.in_range_of_recycler and tile.scrap_amount <= 1)


def get_nearest_opp_unit(tile: Tile) -> Optional[Tile]:
    visited = [[False] * W for _ in range(H)]
    visited[tile.y][tile.x] = True
    q = deque([(tile.x, tile.y)])
    while q:
        x, y = q.popleft()
        for dx, dy in DIRS:
            nx, ny = x + dx, y + dy
            # 바운더리 벗어남
            if not (0 <= nx < W and 0 <= ny < H):
                continue
            # 이미 다른데서 먼저 들어감 (중복 방지)
            if visited[ny][nx]:
                continue
            ntile = tiles[ny][nx]
            # 만약 넥스트 타일이 못가는 곳이면
            if is_unmovable(ntile):
                continue
            # 넥스트 타일에 갔으니까 visited로 해주고
            visited[ny][nx] = True
            # 넥스트타일이 상대방 땅 + 유닛이 있으면
            if ntile.owner == OPP and ntile.units:
                return ntile
            q.append((nx, ny))
    return None

def get_nearest_neutral_unit(tile: Tile) -> Optional[Tile]:
    visited = [[False] * W for _ in range(H)]
    visited[tile.y][tile.x] = True
    q = deque([(tile.x, tile.y)])
    while q:
        x, y = q.popleft()
        for dx, dy in DIRS:
            nx, ny = x + dx, y + dy
            # 바운더리 벗어남
            if not (0 <= nx < W and 0 <= ny < H):
                continue
            # 이미 다른데서 먼저 들어감 (중복 방지)
            if visited[ny][nx]:
                continue
            ntile = tiles[ny][nx]
            # 만약 넥스트 타일이 못가는 곳이면
            if is_unmovable(ntile):
                continue
            # 넥스트 타일에 갔으니까 visited로 해주고
            visited[ny][nx] = True
            # 넥스트타일이 상대방 땅 + 유닛이 있으면
            if ntile.owner == NONE:
                return ntile
            q.append((nx, ny))
    return None


# 사실상 못가는거리를 재는 함수이므로 필요 X...
def get_distance(Tile1: Tile, Tile2: Tile) -> float:
    a = Tile1.x - Tile2.x  # length of a
    b = Tile1.y - Tile2.y  # length of b

    c = math.sqrt((a * a) + (b * b))  # ROOT (a * a) + (b * b)
    return c


# game loop
while True:
    tiles = []
    my_units = []
    opp_units = []
    my_recyclers = []
    opp_recyclers = []
    opp_tiles = []
    my_tiles = []
    neutral_tiles = []

    my_matter, opp_matter = [int(i) for i in input().split()]
    for y in range(H):
        # [y][x]로 넣기 위한 row 선언
        row = []
        for x in range(W):
            # owner: 1 = me, 0 = foe, -1 = neutral
            # recycler, can_build, can_spawn, in_range_of_recycler: 1 = True, 0 = False
            scrap_amount, owner, units, recycler, can_build, can_spawn, in_range_of_recycler = [
                int(k) for k in input().split()
            ]
            tile = Tile(
                x,
                y,
                scrap_amount,
                owner,
                units,
                recycler == 1,
                can_build == 1,
                can_spawn == 1,
                in_range_of_recycler == 1,
            )

            row.append(tile)

            if tile.owner == ME:
                my_tiles.append(tile)
                if tile.units > 0:
                    my_units.append(tile)
                elif tile.recycler:
                    my_recyclers.append(tile)
            elif tile.owner == OPP:
                opp_tiles.append(tile)
                if tile.units > 0:
                    opp_units.append(tile)
                elif tile.recycler:
                    opp_recyclers.append(tile)
            else:
                neutral_tiles.append(tile)
        tiles.append(row)

    actions = []

    # tile이 [y][x]순으로 돌아오기 때문에
    for tile in my_tiles:
        if tile.can_spawn:
            amount = int((my_matter // 10) / 2) # TODO: pick amount of robots to spawn here
            if amount > 0:
                actions.append("SPAWN {} {} {}".format(amount, tile.x, tile.y))
        if tile.can_build:
            should_build = False  # TODO: pick whether to build recycler here
            if should_build:
                actions.append("BUILD {} {}".format(tile.x, tile.y))

    for idx, tile in enumerate(my_units):
        if idx % 3 == 0 or idx % 3 == 1:
            target = get_nearest_opp_unit(tile)
        elif idx % 2 == 2:
            target = get_nearest_neutral_unit(tile)
        if target:
            amount = 0  # TODO: pick amount of units to move
            actions.append("MOVE {} {} {} {} {}".format(amount, tile.x, tile.y, target.x, target.y))

    # To debug: print("Debug messages...", file=sys.stderr, flush=True)
    print(";".join(actions) if len(actions) > 0 else "WAIT")
