import torch
import torch.nn as nn
import torch.nn.functional as F
import os

# 파라미터 설정
DN_FILTERS = 128
DN_RESIDUAL_NUM = 16
DN_INPUT_SHAPE = (6, 9, 9)  # PyTorch는 (C, H, W)
DN_OUTPUT_SIZE = 44  # 행동 수


# 컨볼루션 + BatchNorm + ReLU 블록
def conv_block(in_channels, out_channels):
    return nn.Sequential(
        nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1, bias=False),
        nn.BatchNorm2d(out_channels),
        nn.ReLU(inplace=True),
    )


# 레지듀얼 블록
class ResidualBlock(nn.Module):
    def __init__(self, channels):
        super(ResidualBlock, self).__init__()
        self.conv1 = nn.Conv2d(channels, channels, kernel_size=3, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(channels)
        self.conv2 = nn.Conv2d(channels, channels, kernel_size=3, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(channels)

    def forward(self, x):
        residual = x
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += residual
        out = F.relu(out)
        return out


# 듀얼 네트워크
class DualNetwork(nn.Module):
    def __init__(self):
        super(DualNetwork, self).__init__()
        self.input_conv = conv_block(DN_INPUT_SHAPE[0], DN_FILTERS)
        self.residual_blocks = nn.Sequential(
            *[ResidualBlock(DN_FILTERS) for _ in range(DN_RESIDUAL_NUM)]
        )
        self.global_pool = nn.AdaptiveAvgPool2d((1, 1))  # Global Average Pooling
        self.policy_head = nn.Linear(DN_FILTERS, DN_OUTPUT_SIZE)
        self.value_head = nn.Linear(DN_FILTERS, 1)

    def forward(self, x):
        x = self.input_conv(x)
        x = self.residual_blocks(x)
        x = self.global_pool(x)
        x = torch.flatten(x, 1)
        policy = self.policy_head(x)  # softmax 없이 raw logits
        value = torch.tanh(self.value_head(x))
        return policy, value


# 모델 저장 함수
def save_model(model, path="./model/best.pth"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    torch.save(model.state_dict(), path)


# 테스트 실행
if __name__ == "__main__":
    model = DualNetwork()
    dummy_input = torch.randn(1, *DN_INPUT_SHAPE)  # Batch size = 1
    policy, value = model(dummy_input)
    print(f"Policy Output: {policy.shape}, Value Output: {value.shape}")

    # 모델 저장
    save_model(model)
