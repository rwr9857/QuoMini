import random


class Monte_Carlo_player:
    def __init__(self):
        self.name = "MC_player"
        self.num_playout = 50
        self.max_depth = 3  # 최대 탐색 깊이 설정

    def select_action(self, env, player):
        # 가능한 행동을 조사한 후 표시
        available_action = env.get_actions(player)
        V = [0 for _ in range(len(available_action))]

        for i in range(len(available_action)):

            # 플레이아웃을 반복
            for _ in range(self.num_playout):
                # 현재 상태를 복사해서 플레이아웃에 사용
                temp_env = env.clone()

                # winner가 플레이어면 +1 아니면 -1
                score = self.playout(temp_env, available_action[i], player, depth=1)
                V[i] += score

        max_value = max(V)
        max_index = V.index(max_value)
        return available_action[max_index]

    # 플레이아웃 재귀 함수
    # 게임이 종료 상태가 될 때까지 행동을 임의로 선택하는 것을 반복
    def playout(self, temp_env, action, player, depth):
        temp_env.move(player, action)
        temp_env.end_check(player, for_ai=True)

        # 게임이 종료된 경우
        if temp_env.done:
            if temp_env.winner == player:
                return 100
            elif temp_env.winner == 0:
                return 0
            else:
                return -100

        # 지정 깊이에 도달한 경우
        if depth >= self.max_depth:
            return temp_env.reward(player)

        next_player = 2 if player == 1 else 1

        # 가능한 행동 조사
        available_action = temp_env.get_actions(next_player)

        # 무작위로 행동을 선택
        action = random.randint(0, len(available_action) - 1)
        return self.playout(temp_env, available_action[action], next_player, depth + 1)
