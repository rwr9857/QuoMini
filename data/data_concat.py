# ====================
# 데이터 병합
# ====================

# 패키지 임포트
import pickle
from pathlib import Path
from datetime import datetime

history = []

file_names = sorted(Path("./").glob("*.pkl"))

for file_name in file_names:
    with open(file_name, "rb") as f:
        data = pickle.load(f)
        # 데이터 당 몇 개의 국면을 가지고 있는지 출력
        print(len(data))
        history.extend(data)

now = datetime.now()
path = f'./{now.strftime("%Y%m%d%H%M%S")}.pkl'
with open(path, mode="wb") as f:
    pickle.dump(history, f)
