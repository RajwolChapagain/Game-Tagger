import torch
from torch import nn

class MultiLabelClassifier(nn.Module):
    def __init__(self, in_count: int, hidden_count: int, out_count: int) -> None:
        super().__init__()

        self.conv_block_1 = nn.Sequential(
                nn.Conv2d(in_count, hidden_count, kernel_size=3, padding=1),
                nn.BatchNorm2d(hidden_count),
                nn.ReLU(),
                nn.Dropout(p=0.4),
                nn.Conv2d(hidden_count, hidden_count, kernel_size=3, padding=1),
                nn.BatchNorm2d(hidden_count),
                nn.ReLU(),
                nn.MaxPool2d(kernel_size=2, stride=2)
        )
        self.conv_block_2 = nn.Sequential(
                nn.Conv2d(hidden_count, hidden_count, kernel_size=3, padding=1),
                nn.BatchNorm2d(hidden_count),
                nn.ReLU(),
                nn.Dropout(p=0.3),
                nn.Conv2d(hidden_count, hidden_count, kernel_size=3, padding=1),
                nn.BatchNorm2d(hidden_count),
                nn.ReLU(),
                nn.MaxPool2d(kernel_size=2, stride=2)
        ) 
        self.conv_block_3 = nn.Sequential(
                nn.Conv2d(hidden_count, hidden_count, kernel_size=3, padding=1),
                nn.BatchNorm2d(hidden_count),
                nn.ReLU(),
                nn.Conv2d(hidden_count, hidden_count, kernel_size=3, padding=1),
                nn.BatchNorm2d(hidden_count),
                nn.ReLU(),
                nn.Dropout(p=0.2),
                nn.MaxPool2d(kernel_size=2, stride=2)
        ) 
        self.classifier = nn.Sequential(
                nn.AdaptiveAvgPool2d((1,1)),
                nn.Flatten(),
                nn.Dropout(p=0.2),
                nn.Linear(in_features=hidden_count, 
                          out_features=256),
                nn.ReLU(),
                nn.Dropout(p=0.2),
                nn.Linear(in_features=256,
                          out_features=out_count)
        )
    

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.classifier(self.conv_block_3(self.conv_block_2(self.conv_block_1(x))))
