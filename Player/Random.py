import random


class Random_player:

    def __init__(self):
        self.name = "Random player"

    def select_action(self, env, player):
        # 가능한 행동 조사
        available_action = env.get_actions(player)
        # 가능한 행동 중 하나를 무작위로 선택
        action = random.randint(0, len(available_action) - 1)

        return available_action[action]
