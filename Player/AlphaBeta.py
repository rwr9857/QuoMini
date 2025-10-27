class AlphaBeta_Player:
    def __init__(self):
        self.name = "AlphaBeta_player"
        self.max_depth = 3  # 최대 탐색 깊이 설정

    def select_action(self, env, player):
        available_actions = env.get_actions(player)
        best_score = float("-inf")
        best_action = None
        alpha = float("-inf")  # 알파: 최대값 하한
        beta = float("inf")  # 베타: 최소값 상한

        for action in available_actions:
            temp_env = env.clone()
            temp_env.move(player, action)
            temp_env.end_check(player, for_ai=True)
            score = self.alpha_beta(temp_env, player, False, alpha, beta, depth=1)
            if score > best_score:
                best_score = score
                best_action = action
            alpha = max(alpha, best_score)  # 알파 값 갱신
        return best_action

    def alpha_beta(self, env, player, is_maximizing, alpha, beta, depth):
        if env.done:
            if env.winner == player:
                return 100
            elif env.winner == 0:
                return 0
            else:
                return -100

        # 최대 깊이에 도달한 경우
        if depth >= self.max_depth:
            return env.reward(player)

        next_player = 2 if player == 1 else 1

        if is_maximizing:
            available_actions = env.get_actions(player)
            max_score = float("-inf")
            for action in available_actions:
                temp_env = env.clone()
                temp_env.move(player, action)
                temp_env.end_check(player, for_ai=True)
                score = self.alpha_beta(temp_env, player, False, alpha, beta, depth + 1)
                max_score = max(max_score, score)
                alpha = max(alpha, max_score)
                if beta <= alpha:  # 가지치기
                    break
            return max_score
        else:
            available_actions = env.get_actions(next_player)
            min_score = float("inf")
            for action in available_actions:
                temp_env = env.clone()
                temp_env.move(next_player, action)
                temp_env.end_check(next_player, for_ai=True)
                score = self.alpha_beta(temp_env, player, True, alpha, beta, depth + 1)
                min_score = min(min_score, score)
                beta = min(beta, min_score)
                if beta <= alpha:  # 가지치기
                    break
            return min_score
