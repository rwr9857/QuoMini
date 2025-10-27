from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder


class QuoMini:
    def __init__(self):
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.done = False
        self.winner = 0
        self.wall = -1
        self.playerspos = [[8, 4], [0, 4]]
        self.player1wallcount = 3
        self.player2wallcount = 3
        self.depth = 0
        self.record = []

    def clone(self):
        env = QuoMini()
        env.board = [row[:] for row in self.board]
        env.done = self.done
        env.winner = self.winner
        env.playerspos = [row[:] for row in self.playerspos]
        env.player1wallcount = self.player1wallcount
        env.player2wallcount = self.player2wallcount
        env.depth = self.depth
        env.record = self.record[:]
        return env

    def move(self, player, action):
        pos = self.playerspos[player - 1]

        # 방향 정수
        delta = (
            (-2, 0),  # 위
            (-2, 2),  # 위오른쪽
            (0, 2),  # 오른쪽
            (2, 2),  # 아래오른쪽
            (2, 0),  # 아래
            (2, -2),  # 아래왼쪽
            (0, -2),  # 왼쪽
            (-2, -2),  # 위왼쪽
            (-4, 0),  # 위 두 칸
            (0, 4),  # 오른쪽 두 칸
            (4, 0),  # 아래 두 칸
            (0, -4),  # 왼쪽 두 칸
        )

        # 보드에 플레이어의 선택을 표시
        if action >= 0 and action <= 11:
            self.playerspos[player - 1] = [
                pos[0] + delta[action][0],
                pos[1] + delta[action][1],
            ]
        elif action >= 12 and action <= 43:
            if player == 1:
                self.player1wallcount -= 1
            else:
                self.player2wallcount -= 1

            is_horizontal_wall = action > 27

            # H(가로)의 벽
            if is_horizontal_wall:
                row, col = self.wall_action_to_coord(action)
                self.board[row][col] = self.wall
                self.board[row][col + 1] = self.wall
                self.board[row][col + 2] = self.wall

            # V(세로)의 벽
            else:
                row, col = self.wall_action_to_coord(action)
                self.board[row][col] = self.wall
                self.board[row + 1][col] = self.wall
                self.board[row + 2][col] = self.wall
        self.depth += 1
        self.record.append(action)

    # 액션 번호를 벽 설치 위치로 변환한다.
    def wall_action_to_coord(self, action):
        is_horizontal_wall = action > 27
        action -= 27 if is_horizontal_wall else 11

        quotient = action // 4
        remainder = action % 4

        row = 2 * quotient + 1 if remainder != 0 else 2 * quotient - 1
        col = 2 * remainder - 2 if remainder != 0 else 6

        if is_horizontal_wall:
            return row, col
        else:
            row, col = col, row
            return row, col

    # 벽 설치 위치를 액션 번호로 변환한다.
    def coord_to_wall_action(self, w_row, w_col):
        # 세로
        if w_row % 2 == 0 and w_col % 2 == 1:
            action = (w_row // 2) + 1 + 4 * ((w_col - 1) // 2) + 11
        # 가로
        elif w_row % 2 == 1 and w_col % 2 == 0:
            action = (w_col // 2) + 1 + 4 * ((w_row - 1) // 2) + 11 + 16

        return action

    # 해당 플레이어가 이동 가능한 방향을 제공한다.
    def _valid_direction(self, player):
        def is_out_of_bounds(row, col):
            return not (0 <= row < 9 and 0 <= col < 9)

        def is_wall(row, col):
            return self.board[row][col] == self.wall

        def is_invalid_position(row, col):
            return is_out_of_bounds(row, col) or is_wall(row, col)

        p1_pos = self.playerspos[0]
        p2_pos = self.playerspos[1]

        curr_pos = p1_pos if player == 1 else p2_pos
        oppo_pos = p2_pos if player == 1 else p1_pos

        delta = [(0, 2), (0, -2), (-2, 0), (2, 0)]

        # 조건에 맞는 요소만 필터링
        delta = list(
            filter(
                lambda direction: not is_invalid_position(
                    curr_pos[0] + direction[0] // 2, curr_pos[1] + direction[1] // 2
                ),
                delta,
            )
        )

        d_row = oppo_pos[0] - curr_pos[0]
        d_col = oppo_pos[1] - curr_pos[1]

        if (d_row, d_col) not in delta:
            return delta
        else:
            delta.remove((d_row, d_col))

            check_row = oppo_pos[0] + d_row // 2
            check_col = oppo_pos[1] + d_col // 2

            # 조회한 위치가 보드 범위를 벗어나거나, 벽인지 확인
            if not is_invalid_position(check_row, check_col):
                delta.append((d_row * 2, d_col * 2))
                return delta
            else:
                d_x = -1 if d_row == 0 else 0
                d_y = -1 if d_col == 0 else 0

                for i in range(1, 3):
                    check_row = oppo_pos[0] + pow(d_x, i)
                    check_col = oppo_pos[1] + pow(d_y, i)
                    if not is_invalid_position(check_row, check_col):
                        delta.append((d_row + pow(d_x, i) * 2, d_col + pow(d_y, i) * 2))

                return delta

    # 벽 설치 후 플레이어들이 목표에 도달 가능한지 확인한다.
    def is_path_able(self, action):
        mat = [item[:] for item in self.board]

        # 벽 2개 나란히 세웠을 때 틈새 막기
        for row in range(1, len(mat), 2):
            for col in range(1, len(mat[len(mat) - 1]), 2):
                mat[row][col] = self.wall

        is_horizontal_wall = action > 27

        # H(가로)의 벽
        if is_horizontal_wall:
            row, col = self.wall_action_to_coord(action)
            mat[row][col] = self.wall
            mat[row][col + 1] = self.wall
            mat[row][col + 2] = self.wall

        # V(세로)의 벽
        else:
            row, col = self.wall_action_to_coord(action)
            mat[row][col] = self.wall
            mat[row + 1][col] = self.wall
            mat[row + 2][col] = self.wall

        p1_pos = self.playerspos[0]
        p2_pos = self.playerspos[1]

        # python List comprehension
        # pathfinding 패키지를 위해 0을 1로 변환
        mat = [[1 if element == 0 else element for element in row] for row in mat]

        p1_path, p2_path = False, False
        end_array = list(range(0, 9, 2))

        for i in range(len(end_array)):
            grid = Grid(matrix=mat)
            start = grid.node(p1_pos[1], p1_pos[0])
            end = grid.node(end_array[i], 0)
            path, _ = AStarFinder().find_path(start, end, grid)

            if len(path) != 0:
                p1_path = True
                break

        if not p1_path:
            return False

        for i in range(len(end_array)):
            grid = Grid(matrix=mat)
            start = grid.node(p2_pos[1], p2_pos[0])
            end = grid.node(end_array[i], 8)
            path, _ = AStarFinder().find_path(start, end, grid)

            if len(path) != 0:
                p2_path = True
                break

        # 길을 막지 않으면 True
        return p1_path and p2_path

    # 플레이어가 행동가능한 모든 액션을 고려한다.
    # path_check가 False면 is_path_able을 비활성화한다.
    def get_actions(self, player, path_check=True):
        actions = set()
        direction = self._valid_direction(player)

        delta = [
            (-2, 0),  # N (인덱스 0)
            (-2, 2),  # NE (인덱스 1)
            (0, 2),  # E (인덱스 2)
            (2, 2),  # SE (인덱스 3)
            (2, 0),  # S (인덱스 4)
            (2, -2),  # SW (인덱스 5)
            (0, -2),  # W (인덱스 6)
            (-2, -2),  # NW (인덱스 7)
            (-4, 0),  # NN (인덱스 8)
            (0, 4),  # EE (인덱스 9)
            (4, 0),  # SS (인덱스 10)
            (0, -4),  # WW (인덱스 11)
        ]

        for target in direction:
            actions.add(delta.index(target))

        if player == 1:
            wallcount = self.player1wallcount
        else:
            wallcount = self.player2wallcount

        if wallcount > 0:
            for row in range(1, 9, 2):
                for col in range(1, 9, 2):
                    # 벽 설치 가능한 부분 조사
                    if self.board[row][col] == 0:
                        # V(세로) 벽 가능 여부 조사
                        if (
                            self.board[row - 1][col] == 0
                            and self.board[row + 1][col] == 0
                        ):
                            act = self.coord_to_wall_action(row - 1, col)
                            if path_check:
                                if self.is_path_able(act):
                                    actions.add(act)
                            else:
                                actions.add(act)
                        # H(가로) 벽 가능 여부 조사
                        if (
                            self.board[row][col - 1] == 0
                            and self.board[row][col + 1] == 0
                        ):
                            act = self.coord_to_wall_action(row, col - 1)
                            if path_check:
                                if self.is_path_able(act):
                                    actions.add(act)
                            else:
                                actions.add(act)

        return sorted(list(actions))

    def get_state(self, player):
        p1_pos_ch = [[0 for _ in range(9)] for _ in range(9)]
        p2_pos_ch = [[0 for _ in range(9)] for _ in range(9)]
        walls_ch = [[0 for _ in range(9)] for _ in range(9)]
        p1_walls_ch = [[0 for _ in range(9)] for _ in range(9)]
        p2_walls_ch = [[0 for _ in range(9)] for _ in range(9)]
        current_turn_ch = [[0 for _ in range(9)] for _ in range(9)]

        # 플레이어의 위치 표시
        p1_pos_ch[self.playerspos[0][0]][self.playerspos[0][1]] = 1
        p2_pos_ch[self.playerspos[1][0]][self.playerspos[1][1]] = 1

        # 벽 위치 표시
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == self.wall:
                    walls_ch[i][j] = 1

        for i in range(self.player1wallcount):
            p1_walls_ch[0][i] = 1

        for i in range(self.player2wallcount):
            p2_walls_ch[0][i] = 1

        if player == 2:
            for i in range(9):
                for j in range(9):
                    current_turn_ch[i][j] = 1

        state = [
            p1_pos_ch,
            p2_pos_ch,
            walls_ch,
            p1_walls_ch,
            p2_walls_ch,
            current_turn_ch,
        ]

        return state

    # 최단 경로로 이동하는 액션을 반환한다. 상하좌우만 고려한다.
    def get_short_action(self, player):
        return

    # 게임이 끝났는지 확인하고 해당 플레이어를 winner로 설정한다.
    def end_check(self, player, for_ai=False):
        if for_ai and self.depth > 60:
            self.done = True
            self.winner = 0

        # 상단에 플레이어 1, 하단에 플레이어 2면 게임 종료
        if self.playerspos[0][0] == 0 or self.playerspos[1][0] == 8:
            self.done = True
            self.winner = player

    # 현재 상태에서 플레이어 보상 값을 계산한다.
    def reward(self, player):
        mat = [item[:] for item in self.board]

        # 벽 2개 나란히 세웠을 때 틈새 막기
        for row in range(1, len(mat), 2):
            for col in range(1, len(mat[len(mat) - 1]), 2):
                mat[row][col] = self.wall

        p1_pos = self.playerspos[0]
        p2_pos = self.playerspos[1]

        # python List comprehension
        # pathfinding 패키지를 위해 0을 1로 변환
        mat = [[1 if element == 0 else element for element in row] for row in mat]

        end_array = list(range(0, 9, 2))
        p1_path_lens = [0] * 5
        p2_path_lens = [0] * 5

        # 각 목표당 걸리는 거리 측정
        for i in range(len(end_array)):
            grid = Grid(matrix=mat)
            start = grid.node(p1_pos[1], p1_pos[0])
            end = grid.node(end_array[i], 0)
            path, _ = AStarFinder().find_path(start, end, grid)

            p1_path_lens[i] = (len(path) - 1) // 2

        # 각 목표당 걸리는 거리 측정
        for i in range(len(end_array)):
            grid = Grid(matrix=mat)
            start = grid.node(p2_pos[1], p2_pos[0])
            end = grid.node(end_array[i], 8)
            path, _ = AStarFinder().find_path(start, end, grid)

            p2_path_lens[i] = (len(path) - 1) // 2

        # 0 이하를 제외한 새로운 배열 생성
        p1_path_lens_filter = [num for num in p1_path_lens if num > 0]
        p2_path_lens_filter = [num for num in p2_path_lens if num > 0]

        # 가장 낮은 값의 인덱스 찾기
        p1_min_path_idx = p1_path_lens.index(min(p1_path_lens_filter))
        p2_min_path_idx = p2_path_lens.index(min(p2_path_lens_filter))

        if player == 1:
            curr_min_path_value = p1_path_lens[p1_min_path_idx]
            oppo_min_path_value = p2_path_lens[p2_min_path_idx]
        else:
            curr_min_path_value = p2_path_lens[p2_min_path_idx]
            oppo_min_path_value = p1_path_lens[p1_min_path_idx]

        return oppo_min_path_value - curr_min_path_value

    # 현재 보드 상태를 콘솔에 출력한다.
    def print_board(self):
        print()
        print([self.player2wallcount])

        # 열 레이블 (a, b, c, ...) 출력
        print("  ", end="")  # 왼쪽 여백 (행 번호와 맞추기 위해 2칸)
        for col in range(5):  # 5번 반복
            print(chr(97 + col), end="   ")  # 알파벳 + 공백 3칸
        print()  # 줄 바꿈

        # 보드와 행 레이블 출력
        for i in range(len(self.board)):
            if i % 2 == 0:
                # 행 번호 (아래에서 위로 1부터 시작하도록 뒤집기)
                row_num = 5 - (i // 2)
                print(row_num, end=" ")  # 행 레이블
            else:
                print(end="  ")

            for j in range(len(self.board[i])):
                # 플레이어 1 위치 확인
                if [i, j] == self.playerspos[0]:
                    print("\u265f", end=" ")  # 플레이어 1 (예: 백색 폰)
                # 플레이어 2 위치 확인
                elif [i, j] == self.playerspos[1]:
                    print("\u2659", end=" ")  # 플레이어 2 (예: 흑색 폰)
                # 기존 보드 값에 따른 출력
                elif self.board[i][j] == self.wall:
                    print("x", end=" ")
                elif self.board[i][j] == 0 and i % 2 == 0 and j % 2 == 0:
                    print("\u00b7", end=" ")  # 중간 점 (특정 패턴)
                else:
                    print(" ", end=" ")
            print()  # 줄 바꿈

        print([self.player1wallcount])
        print()
