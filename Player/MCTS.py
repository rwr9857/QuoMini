import random
import math


# 트리 노드를 위한 클래스
class Node:
    def __init__(self, action=None, parent=None):
        self.action = action  # 이 노드로 오게 한 행동
        self.parent = parent  # 부모 노드
        self.children = []  # 자식 노드들
        self.visits = 0  # 방문 횟수
        self.value = 0.0  # 승리 값(승리 누적)
        self.untried_actions = []  # 아직 시도하지 않은 행동들

    def uct(self):
        if self.visits == 0:
            return float("inf")  # 방문하지 않은 노드는 우선 탐색
        parent_visits = self.parent.visits
        return (self.value / self.visits) + math.sqrt(2) * math.sqrt(
            math.log(parent_visits) / self.visits
        )

    def select_child(self):
        return max(self.children, key=lambda child: child.uct())

    def add_child(self, action):
        child = Node(action=action, parent=self)
        self.children.append(child)
        return child

    def update(self, result):
        self.visits += 1
        self.value += result


class MCTS_player:
    def __init__(self):
        self.name = "MCTS_player"
        self.num_iterations = 1000  # MCTS 반복 횟수

    def select_action(self, env, player):
        # 루트 노드 초기화
        root = Node()
        root.untried_actions = env.get_actions(player)

        # 주어진 반복 횟수만큼 MCTS 실행
        for _ in range(self.num_iterations):
            node = root
            temp_env = env.clone()
            current_player = player  # 현재 플레이어 추적

            # 1. 선택(Selection)
            # 자식이 있고 시도하지 않은 행동이 없을 때 실행된다.
            while (
                node.untried_actions == [] and node.children != [] and not temp_env.done
            ):
                node = node.select_child()
                temp_env.move(current_player, node.action)
                temp_env.end_check(current_player, for_ai=True)
                current_player = 2 if current_player == 1 else 1  # 플레이어 교체

            # 2. 확장(Expansion)
            if node.untried_actions != [] and not temp_env.done:
                action_index = random.randint(0, len(node.untried_actions) - 1)
                action = node.untried_actions.pop(action_index)
                temp_env.move(current_player, action)
                temp_env.end_check(current_player, for_ai=True)
                node = node.add_child(action)
                current_player = 2 if current_player == 1 else 1  # 플레이어 교체

            # 3. 시뮬레이션(Simulation)
            winner = self.simulate(temp_env, current_player)

            if winner == current_player:
                result = -1
            elif winner == 0:
                result = 0
            else:
                result = 1

            # 4. 역전파(Backpropagation)
            while node is not None:
                node.update(result)
                result = -result
                node = node.parent

        # 가장 많이 방문한 자식 노드의 행동 반환
        best_child = max(root.children, key=lambda child: child.visits)
        return best_child.action

    def simulate(self, temp_env, current_player):
        # 게임이 끝날 때까지 무작위 플레이아웃
        while not temp_env.done:
            available_actions = temp_env.get_actions(current_player)
            action = available_actions[random.randint(0, len(available_actions) - 1)]
            temp_env.move(current_player, action)
            temp_env.end_check(current_player, for_ai=True)
            current_player = 2 if current_player == 1 else 1  # 플레이어 교체
        # 결과 반환
        return temp_env.winner
