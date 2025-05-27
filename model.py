import torch
from torch import nn

class MultiLabelClassifier(nn.Module):
    def __init__(self, in_count: int, hidden_count: int, out_count: int) -> None:
        super().__init__()

        self.conv_block_1 = nn.Sequential(
                nn.Conv2d(in_count, hidden_count, kernel_size=3),
                nn.ReLU(),
                nn.Conv2d(hidden_count, hidden_count, kernel_size=3),
                nn.ReLU(),
                nn.MaxPool2d(kernel_size=3)
        )
        self.conv_block_2 = nn.Sequential(
                nn.Conv2d(hidden_count, hidden_count, kernel_size=3),
                nn.ReLU(),
                nn.Conv2d(hidden_count, hidden_count, kernel_size=3),
                nn.ReLU(),
                nn.MaxPool2d(kernel_size=2)
        ) 
        self.classifier = nn.Sequential(
                nn.Flatten(),
                nn.Linear(in_features=hidden_count * 18 * 18,
                          out_features=out_count)
        )
    

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.conv_block_1(x)
        x = self.conv_block_2(x)
        x = self.classifier(x)
        return x
