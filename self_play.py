import os
import time
import pickle
import numpy as np
from datetime import datetime
from alpha_zero import AlphaZeroPlayer
from dual_network import DN_OUTPUT_SIZE
from QuoMini import QuoMini
from utils.loggerFactory import LoggerFactory


# 학습 데이터 저장
def write_data(history):
    now = datetime.now()
    os.makedirs("./data/", exist_ok=True)  # 폴더가 없는 경우에는 생성
    path = "./data/{:04}{:02}{:02}{:02}{:02}{:02}.pkl".format(
        now.year, now.month, now.day, now.hour, now.minute, now.second
    )
    with open(path, mode="wb") as f:
        pickle.dump(history, f)
        LoggerFactory._LOGGER.info("History File Saved! (" + path + ")")


# second를 [nn:nn:nn] 형식의 문자열로 변환
def convert_seconds_to_hms(sec):
    sec = int(sec)
    hours = sec // 3600
    minutes = (sec % 3600) // 60
    seconds = sec % 60

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def play():
    LoggerFactory._LOGGER.info("Game Started!")
    start_time = time.time()
    history = []

    env = QuoMini()
    agent = AlphaZeroPlayer(device="cpu", num_iterations=1000)

    for i in range(100):
        turn_start_time = time.time()
        if i % 2 == 0:
            player = 1
        else:
            player = 2

        scores = agent.select_action(env, player, training=True)

        policies = [0] * DN_OUTPUT_SIZE
        for action, policy in zip(env.get_actions(player), scores):
            policies[action] = policy

        action = np.random.choice(env.get_actions(player), p=scores)
        env.move(player, action)
        history.append([env.get_state(player), policies, None])

        turn_end_time = time.time()
        elapsed_time = turn_end_time - turn_start_time

        LoggerFactory._LOGGER.info(
            "Turn({}) Time: {}".format(i, convert_seconds_to_hms(elapsed_time))
        )

        if i % 2 == 0:
            wall_count = env.player1wallcount
            row = 5 - (env.playerspos[0][0] // 2)
            col = chr(97 + env.playerspos[0][1] // 2)
            pos = col + str(row)
        else:
            wall_count = env.player2wallcount
            row = 5 - (env.playerspos[1][0] // 2)
            col = chr(97 + env.playerspos[1][1] // 2)
            pos = col + str(row)

        if action > 12:
            row, col = env.wall_action_to_coord(action)
            if action > 27:
                action = "h" + chr(97 + col // 2) + str(4 - (row // 2))
            else:
                action = "v" + chr(97 + col // 2) + str(5 - (row + 2) // 2)
        else:
            action = pos
        LoggerFactory._LOGGER.info("Wall {} Action {}".format(wall_count, action))

        env.end_check(player, for_ai=True)
        if env.done == True:
            end_time = time.time()  # 함수 실행 후 시간 측정
            elapsed_time = end_time - start_time  # 실행 시간 계산
            elapsed_formatted = convert_seconds_to_hms(elapsed_time)
            LoggerFactory._LOGGER.info("Play Time : " + elapsed_formatted)
            LoggerFactory._LOGGER.info(
                "Game Terminated! (Turn " + str(len(history)) + ")"
            )
            if env.winner == 1:
                value = 1
            elif env.winner == 2:
                value = -1
            else:
                value = 0

            for i in range(len(history)):
                history[i][2] = value
                value = -value
            break
    return history


def self_play(num_games=10):
    training_data = []

    for i in range(num_games):
        h = play()
        training_data.extend(h)

        # 출력
        print("\rSelfPlay {}/{}".format(i + 1, num_games), end="")
    print("")

    # 학습 데이터 저장
    write_data(training_data)

if __name__ == "__main__":
    LoggerFactory.create_logger()
    self_play(num_games=10)