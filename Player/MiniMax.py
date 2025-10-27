class MiniMax_Player:
    def __init__(self):
        self.name = "MiniMax_player"

    def select_action(self, env, player):
        # 가능한 행동을 조사
        available_actions = env.get_actions(player)
        best_score = float("-inf")  # 최대 점수를 찾기 위해 초기값을 음의 무한대로 설정
        best_action = None

        # 모든 가능한 행동에 대해 평가
        for action in available_actions:
            temp_env = env.clone()  # 현재 상태 복사
            temp_env.move(player, action)  # 행동 시뮬레이션
            temp_env.end_check(player, for_ai=True)  # 게임 종료 여부 확인
            score = self.minimax(temp_env, player, False)  # Minimax 점수 계산
            if score > best_score:
                best_score = score
                best_action = action

        return best_action

    def minimax(self, env, player, is_maximizing):
        # 게임이 종료된 경우 점수 반환
        if env.done:
            if env.winner == player:
                return 1  # 내가 이기면 +1
            elif env.winner == 0:
                return 0  # 비기면 0
            else:
                return -1  # 상대가 이기면 -1

        next_player = 2 if player == 1 else 1  # 플레이어 교체

        if is_maximizing:  # 현재 플레이어가 최대화하려는 경우
            available_actions = env.get_actions(player)
            max_score = float("-inf")
            for action in available_actions:
                temp_env = env.clone()
                temp_env.move(player, action)
                temp_env.end_check(player, for_ai=True)
                score = self.minimax(temp_env, player, False)
                max_score = max(max_score, score)
            return max_score
        else:  # 상대 플레이어가 최소화하려는 경우
            available_actions = env.get_actions(next_player)
            min_score = float("inf")
            for action in available_actions:
                temp_env = env.clone()
                temp_env.move(next_player, action)
                temp_env.end_check(next_player, for_ai=True)
                score = self.minimax(temp_env, player, True)
                min_score = min(min_score, score)
            return min_score
