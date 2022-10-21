
import torch
import torch.nn as nn
import torch.nn.functional as F


class DoubleConv(nn.Module):
    """(convolution => [BN] => ReLU) * 2"""

    def __init__(self, in_channels, out_channels, mid_channels=None):
        super().__init__()
        if not mid_channels:
            mid_channels = out_channels
        self.double_conv = nn.Sequential(
            nn.Conv2d(in_channels, mid_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(mid_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(mid_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        return self.double_conv(x)


class Down(nn.Module):
    """Downscaling with maxpool then double conv"""

    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.maxpool_conv = nn.Sequential(
            nn.MaxPool2d(2),
            DoubleConv(in_channels, out_channels)
        )

    def forward(self, x):
        return self.maxpool_conv(x)


class Up(nn.Module):
    """Upscaling then double conv"""

    def __init__(self, in_channels, out_channels, bilinear=True):
        super().__init__()

        # if bilinear, use the normal convolutions to reduce the number of channels
        if bilinear:
            self.up = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)
            self.conv = DoubleConv(in_channels, out_channels, in_channels // 2)
        else:
            self.up = nn.ConvTranspose2d(in_channels, in_channels // 2, kernel_size=2, stride=2)
            self.conv = DoubleConv(in_channels, out_channels)

    def forward(self, x1, x2):
        x1 = self.up(x1)
        # input is CHW
        diffY = x2.size()[2] - x1.size()[2]
        diffX = x2.size()[3] - x1.size()[3]

        x1 = F.pad(x1, [diffX // 2, diffX - diffX // 2,
                        diffY // 2, diffY - diffY // 2])
        # if you have padding issues, see
        # https://github.com/HaiyongJiang/U-Net-Pytorch-Unstructured-Buggy/commit/0e854509c2cea854e247a9c615f175f76fbb2e3a
        # https://github.com/xiaopeng-liao/Pytorch-UNet/commit/8ebac70e633bac59fc22bb5195e513d5832fb3bd
        x = torch.cat([x2, x1], dim=1)
        return self.conv(x)


class OutConv(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(OutConv, self).__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size=1)

    def forward(self, x):
        return self.conv(x)


class UNet(nn.Module):
    def __init__(self, n_channels, n_classes, bilinear=False, scaling=1):
        super(UNet, self).__init__()
        self.n_channels = n_channels
        self.n_classes = n_classes
        self.bilinear = bilinear

        self.scaling = scaling
        self.encoder = nn.Sequential(
            DoubleConv(n_channels, int(64 / self.scaling)),
            Down(int(64 / self.scaling), int(128 / self.scaling)),
            Down(int(128 / self.scaling), int(256 / self.scaling)),
            Down(int(256 / self.scaling), int(512 / self.scaling)),
            Down(int(512 / self.scaling), int(1024 / self.scaling)),
        )
        '''self.inc = DoubleConv(n_channels, int(64/self.scaling))
        self.down1 = Down(int(64/self.scaling), int(128/self.scaling))
        self.down2 = Down(int(128/self.scaling), int(256/self.scaling))
        self.down3 = Down(int(256/self.scaling), int(512/self.scaling))
        self.down4 = Down(int(512/self.scaling), int(1024/self.scaling))'''

        self.up1 = Up(int(1024/self.scaling), int(512/self.scaling), bilinear)
        self.up2 = Up(int(512/self.scaling), int(256/self.scaling), bilinear)
        self.up3 = Up(int(256/self.scaling), int(128/self.scaling), bilinear)
        self.up4 = Up(int(128/self.scaling), int(64/self.scaling), bilinear)
        self.outc = OutConv(int(64/self.scaling), n_classes)

    def forward(self, x):
        x_encoder = []
        for layer_idx, layer in enumerate(self.encoder):
            x = layer(x)
            x_encoder.append(x)
        '''x1 = self.inc(x)
        x2 = self.down1(x1)
        x3 = self.down2(x2)
        x4 = self.down3(x3)
        x5 = self.down4(x4)'''
        x = self.up1(x_encoder[4], x_encoder[3])
        x = self.up2(x, x_encoder[2])
        x = self.up3(x, x_encoder[1])
        x = self.up4(x, x_encoder[0])
        logits = self.outc(x)
        return logits

    def forward_ssl(self, x):
        x = F.avg_pool2d(self.encoder(x), kernel_size=16, stride=16)
        return x.flatten().reshape(-1, 2048)