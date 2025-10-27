import re


class Human_player:
    def __init__(self):
        self.name = "Human player"

    def select_action(self, env, player):
        # 가능한 행동을 조사
        available_action = env.get_actions(player)
        env.print_board()
        while True:
            # 키보드로 방향 입력 받음
            action_input = input("Select action (human): ").lower()
            action = self.key_mapping(action_input)

            # 입력받은 행동이 가능한 행동이면 반복문을 탈출
            if action in available_action:
                return action
            # 아니면 행동 입력을 반복
            else:
                print("Invalid input.")

    def key_mapping(self, action_input):
        """입력된 문자열을 숫자로 매핑하는 함수"""
        action_input = action_input.lower()  # 대소문자 구분 없애기

        # 1. 한 글자 패턴 (u, r, d, l)
        single_key_map = {"u": 0, "r": 2, "d": 4, "l": 6}  # 상  # 우  # 하  # 좌

        # 2. 두 글자 패턴 (ur, rd, dl, lu)
        double_key_map = {
            "ur": 1,  # 우상
            "rd": 3,  # 우하
            "dl": 5,  # 좌하
            "lu": 7,  # 좌상
            "uu": 8,  # 상상
            "rr": 9,  # 우우
            "dd": 10,  # 하하
            "ll": 11,  # 좌좌
        }

        # 한 글자 입력 처리
        if len(action_input) == 1:
            return single_key_map.get(action_input, None)

        # 두 글자 입력 처리
        elif len(action_input) == 2:
            return double_key_map.get(action_input, None)

        # 세 글자 입력 처리 (ha3, vb2 등)
        elif len(action_input) == 3:
            pattern = r"^[hv][a-d][1-4]$"  # h/v로 시작, a~d, 1~4로 끝
            if re.match(pattern, action_input):
                prefix = action_input[0]
                mid = action_input[1]
                end = int(action_input[2])

                mid_map = {"a": 0, "b": 1, "c": 2, "d": 3}

                if prefix == "h":
                    return 28 + mid_map[mid] + 4 * (4 - end)
                else:
                    return 12 + mid_map[mid] * 4 + (4 - end)
            return None

        # 그 외는 유효하지 않음
        return None
