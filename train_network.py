from pathlib import Path
import pickle
import random
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.optim.lr_scheduler import LambdaLR
from dual_network import DualNetwork


# 학습 데이터 로드
def load_data():
    history_path = sorted(Path("./data").glob("*.pkl"))[-1]
    with history_path.open(mode="rb") as f:
        return pickle.load(f)


# 학습률 스케줄러
def step_decay(epoch):
    if epoch >= 80:
        return 0.25  # 0.001 * 0.25 = 0.00025
    elif epoch >= 50:
        return 0.5   # 0.001 * 0.5 = 0.0005
    else:
        return 1.0   # 기본 lr

# 듀얼 네트워크 학습
def train_network(dual_network, device, epochs=5):
    training_data = load_data()

    dual_network.to(device)
    optimizer = optim.Adam(dual_network.parameters(), lr=0.001)
    policy_loss_fn = nn.KLDivLoss(reduction="batchmean")  # 분포 학습용 손실 함수
    value_loss_fn = nn.MSELoss()

    # 학습률 스케줄러 적용
    scheduler = LambdaLR(optimizer, lr_lambda=step_decay)

    dual_network.train()

    for epoch in range(epochs):
        random.shuffle(training_data)
        total_loss = 0

        for state, policy_target, value_target in training_data:
            state_tensor = torch.tensor(
                state, dtype=torch.float32, device=device
            ).unsqueeze(0)
            policy_target_tensor = torch.tensor(
                [policy_target], dtype=torch.float32, device=device
            )
            value_target_tensor = torch.tensor(
                [[value_target]], dtype=torch.float32, device=device
            )

            policy, value = dual_network(state_tensor)

            # Policy에 log_softmax 적용
            policy_loss = policy_loss_fn(
                F.log_softmax(policy, dim=1), policy_target_tensor
            )
            value_loss = value_loss_fn(value, value_target_tensor)
            loss = policy_loss + value_loss

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        avg_loss = total_loss / len(training_data)
        scheduler.step()
        print(f"Train {epoch + 1}/{epochs} - Loss: {avg_loss:.6f}")

    torch.save(dual_network.state_dict(), "./model/latest.pth")

if __name__ == "__main__":
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")

    model_path = "./model/best.pth"
    model = DualNetwork().to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))

    train_network(model, device)
