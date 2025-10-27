# ====================
# 신규 파라미터 평가 파트
# ====================

# 패키지 임포트
import numpy as np
from QuoMini import QuoMini
from alpha_zero import AlphaZeroPlayer, boltzmann
from shutil import copy

# 파라미터 준비
EN_GAME_COUNT = 10  # 평가 1회 당 게임 수(오리지널: 400)
EN_TEMPERATURE = 1.0  # 볼츠만 분포 온도


# 게임 실행
def play(p1, p2):
    env = QuoMini()

    for i in range(100):
        if i % 2 == 0:
            player = 1
            scores = p1.select_action(env, player, training=True)
            scores = boltzmann(scores)
        else:
            player = 2
            scores = p2.select_action(env, player, training=True)
            scores = boltzmann(scores)
        action = np.random.choice(env.get_actions(player), p=scores)

        env.move(player, action)
        env.end_check(player, for_ai=True)

        if env.done == True:
            if env.winner == 1:
                point = 1
            elif env.winner == 2:
                point = 0
            else:
                point = 0.5
            break

    return point


# 베스트 플레이어 교대
def update_best_player():
    copy("./model/latest.pth", "./model/best.pth")
    print("Change BestPlayer")


# 네트워크 평가
def evaluate_network():
    # 최신 플레이어 모델 로드
    model_path = "./model/latest.pth"
    model0 = AlphaZeroPlayer(model_path=model_path, device="mps", num_iterations=100)

    # 베스트 플레이어 모델 로드
    model_path = "./model/best.pth"
    model1 = AlphaZeroPlayer(model_path=model_path, device="mps", num_iterations=100)

    # # 여러 차례 대전을 반복
    total_point = 0
    for i in range(EN_GAME_COUNT):
        # 1 게임 실행
        if i % 2 == 0:
            total_point += play(model0, model1)
        else:
            total_point += 1 - play(model1, model0)

        # 출력
        print("\rEvaluate {}/{}".format(i + 1, EN_GAME_COUNT), end="")
    print("")

    # 평균 포인트 계산
    average_point = total_point / EN_GAME_COUNT
    print("AveragePoint", average_point)

    # 베스트 플레이어 교대
    if average_point > 0.5:
        update_best_player()
        return True
    else:
        return False


# 동작 확인
if __name__ == "__main__":
    evaluate_network()
