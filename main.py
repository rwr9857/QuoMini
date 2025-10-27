from QuoMini import QuoMini
from Player import *

p1 = HumanPlayer()
p2 = MCTSPlayer()

while True:
    env = QuoMini()

    for i in range(100):
        if i % 2 == 0:
            player = 1
            action = p1.select_action(env, player)
            env.move(player, action)
        else:
            player = 2
            action = p2.select_action(env, player)
            env.move(player, action)

        env.end_check(player)
        env.print_board()
        if env.done == True:
            if env.winner == 1:
                print("winner is p1")
            elif env.winner == 2:
                print("winner is p2")
            else:
                print("Draw")
            break

    # 한게임 더?최종 결과 출력
    answer = input("More Game? (y/n)")

    if answer == "n":
        break
