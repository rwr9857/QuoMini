import math
import torch
from dual_network import DualNetwork
import torch.nn.functional as F

def boltzmann(xs, temperature=1.0):
    if temperature <= 0:
        raise ValueError("temperature must be > 0")
    max_x = max(xs)
    exps = [math.exp((x - max_x) / temperature) for x in xs]
    s = sum(exps)
    return [e / s for e in exps]


class PredNetwork:
    def __init__(self, model_path="./model/best.pth", device="cpu"):
        self.device = torch.device(device)
        self.model = DualNetwork().to(self.device)  # 모델 초기화
        self.model.load_state_dict(
            torch.load(model_path, map_location=self.device)
        )  # 저장된 모델 로드
        self.model.eval()  # 추론 모드 설정

    def predict(self, env, player):
        """
        환경(env)과 플레이어 정보를 입력받아 정책(p)과 가치(v)를 반환
        - 정책: 가능한 행동에 대한 확률 분포
        - 가치: 현재 상태의 승리 확률 (-1 ~ 1)
        """
        actions = env.get_actions(player)  # 가능한 행동 가져오기

        state = env.get_state(player)
        state = torch.tensor(state, dtype=torch.float32, device=self.device).unsqueeze(
            0
        )

        # 신경망 예측
        with torch.no_grad():
            policy_logits, value = self.model(state)
            policy_probs = F.softmax(policy_logits, dim=1).cpu().numpy().flatten()
            value = value.item()

        # 가능한 행동만 필터링
        policy = {action: policy_probs[action] for action in actions}
        total_prob = sum(policy.values())
        if total_prob == 0:
            # 균등 확률 분배
            policy = {action: 1 / len(policy) for action in policy}
        else:
            policy = {action: prob / total_prob for action, prob in policy.items()}

        return policy, value


# 트리 노드를 위한 클래스
class Node:
    def __init__(self, action=None, parent=None, prior=0.0):
        self.action = action  # 이 노드로 오게 한 행동
        self.parent = parent  # 부모 노드
        self.children = []  # 자식 노드들
        self.visits = 0  # 방문 횟수
        self.value = 0.0  # 가치 합계
        self.untried_actions = []  # 아직 시도하지 않은 행동들
        self.prior = prior  # 신경망에서 받은 사전 확률

    def puct(self, c_puct=1.0):
        if self.visits == 0:
            return float("inf")
        parent_visits = self.parent.visits
        q_value = self.value / self.visits if self.visits > 0 else 0
        u_value = c_puct * self.prior * math.sqrt(parent_visits) / (1 + self.visits)
        return q_value + u_value

    def select_child(self):
        return max(self.children, key=lambda child: child.puct())

    def add_child(self, action, prior):
        child = Node(action=action, parent=self, prior=prior)
        self.children.append(child)
        return child

    def update(self, value):
        self.visits += 1
        self.value += value


class AlphaZeroPlayer:
    def __init__(
        self, model_path="./model/best.pth", device="cpu", num_iterations=1000
    ):
        self.name = "AlphaZeroPlayer"
        self.neural_network = PredNetwork(model_path, device)  # 신경망 인스턴스
        self.num_iterations = num_iterations  # MCTS 반복 횟수

    def select_action(self, env, player, training=False):
        root = Node()
        root.untried_actions = env.get_actions(player)
        policy, _ = self.neural_network.predict(env, player)  # 신경망 예측

        # 초기 자식 노드 생성 및 사전 확률 할당
        for action in root.untried_actions:
            root.add_child(action, prior=policy.get(action, 0.0))
        root.untried_actions = []  # 모든 행동이 자식으로 추가됨

        # MCTS 반복
        for _ in range(self.num_iterations):
            node = root
            temp_env = env.clone()
            current_player = player

            # 1. 선택(Selection)
            while node.children and not temp_env.done:
                node = node.select_child()
                temp_env.move(current_player, node.action)
                temp_env.end_check(current_player, for_ai=True)
                current_player = 2 if current_player == 1 else 1

            # 2. 확장(Expansion) 및 평가
            if not temp_env.done:
                policy, value = self.neural_network.predict(temp_env, current_player)
                available_actions = temp_env.get_actions(current_player)
                for action in available_actions:
                    node.add_child(action, prior=policy.get(action, 0.0))
                node.untried_actions = []  # 모든 행동이 자식으로 추가됨
            else:
                # 게임 종료 시 결과로 가치 설정
                if temp_env.winner == current_player:
                    value = -1
                elif temp_env.winner == 0:
                    value = 0
                else:
                    value = 1

            # 3. 역전파(Backpropagation)
            while node is not None:
                node.update(value)
                value = -value  # 플레이어 관점 전환
                node = node.parent

        if training:
            visits = [child.visits for child in root.children]
            probs = boltzmann(visits, temperature=1.0)
            return probs  # 또는 확률 기반 샘플링
        else:
            # 가장 많이 방문한 행동 선택
            best_child = max(root.children, key=lambda child: child.visits)
            return best_child.action
