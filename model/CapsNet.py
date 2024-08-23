import torch
import torch.nn as nn
from BCIPong.model.utils import Routing, CapsMask, CapsLen, ReconstructionNet


class EEGCapsNet(nn.Module):
    def __init__(self, input_size=(1, 16, 192), num_classes=2):
        super(EEGCapsNet, self).__init__()
        self.channelCapsTemporal_1 = nn.Sequential(
            nn.Conv2d(in_channels=16, out_channels=128, kernel_size=(1,64), groups=16, padding=0),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.Conv2d(in_channels=128, out_channels=256, kernel_size=(1,input_size[2]-63), groups=128) # collapse to 1 point
        )
        self.channelCapsTemporal_2 = nn.Sequential(
            nn.Conv2d(in_channels=16, out_channels=128, kernel_size=(1, 24), groups=16, padding=0),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.Conv2d(in_channels=128, out_channels=256, kernel_size=(1,input_size[2]-23), groups=128) # collapse to 1 point
        )
        # channel caps will eventually be transformed from 8x4 capsules to 4x8 higher level capsules

        self.channelRouting = Routing(16, (8, 4), (4, 8))
        self.channelShrink = Routing(8, (8, 8), (4, 8))
        self.channelDeepSuper = Routing(1, (64, 8), (2, 32))

        self.localCapsSpatial_1 = nn.Sequential(
            nn.Conv2d(in_channels=8, out_channels=64, kernel_size=(2, 36), groups=8, padding=0),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Conv2d(in_channels=64, out_channels=128, kernel_size=(1, input_size[2]-35), groups=64) # collapse to 1 point
        )
        
        self.localCapsSpatial_2 = nn.Sequential(
            nn.Conv2d(in_channels=8, out_channels=64, kernel_size=(2, 16), groups=8),
            nn.BatchNorm2d(64),
            nn.ELU(),
            nn.Conv2d(in_channels=64, out_channels=128, kernel_size=(1, input_size[2]-15), groups=64) # collapse to 1 point
        )

        self.localRouting = Routing(8, (8, 4), (4, 8))
        self.localShrink = Routing(8, (8, 8), (4, 16))
        self.localRegion = Routing(4, (8, 16), (4, 16))
        self.localDeepSuper = Routing(1, (32, 8), (2, 64))

        # local spatial caps will be transformed from 8x4 capsules to 8x8 higher level capsules
        # local caps will be 16x8 (with addition from channel caps) this will be reduced to 8x8


        self.regionCapsSpatial_1 = nn.Sequential(
            nn.Conv2d(in_channels=4, out_channels=32, kernel_size=(4, 24), groups=4),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.Conv2d(in_channels=32, out_channels=64, kernel_size=(1, input_size[2]-23), groups=32) # collapse to 1 point
        )

        self.regionCapsSpatial_2 = nn.Sequential(
            nn.Conv2d(in_channels=4, out_channels=32, kernel_size=(4, 32), groups=4),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.Conv2d(in_channels=32, out_channels=64, kernel_size=(1, input_size[2]-31), groups=32) # collapse to 1 point
        )

        # region caps will be transformed from 8x4 capsules to 16x8 higher level capsules
        # region caps will be 32x8 (with addition from local caps) this will be reduced to 16x8

        self.regionRouting = Routing(4, (8, 4), (4, 16))
        self.regionShrink = Routing(4, (8, 16), (4, 16))
        self.regionHemi = Routing(2, (8, 16), (4, 16))
        self.regionDeepSuper = Routing(1, (16, 16), (2, 64))


        self.hemiCapsSpatial_1 = nn.Sequential(
            nn.Conv2d(in_channels=2, out_channels=16, kernel_size=(8, 30), groups=2),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.Conv2d(in_channels=16, out_channels=32, kernel_size=(1, input_size[2]-29), groups=16) # collapse to 1 point
        )

        self.hemiCapsSpatial_2 = nn.Sequential(
            nn.Conv2d(in_channels=2, out_channels=16, kernel_size=(8, 60), groups=2),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.Conv2d(in_channels=16, out_channels=32, kernel_size=(1, input_size[2]-59), groups=16) # collapse to 1 point
        )

        # hemi caps will be transformed from 8x4 capsules to 32x8 higher level capsules
        # hemi caps will be 64x8 (with addition from region caps) this will be reduced to 32x8

        self.hemiRouting = Routing(2, (8, 4), (4, 16))
        self.hemiShrink = Routing(2, (8, 16), (4, 16))

        self.out = Routing(1, (8, 16), (num_classes, 64))
        self.generator = ReconstructionNet(input_size, num_classes)
        self.channel_generator = ReconstructionNet(input_size, num_classes, num_capsules=32)
        self.local_generator = ReconstructionNet(input_size, num_classes, num_capsules=64)
        self.region_generator = ReconstructionNet(input_size, num_classes, num_capsules=64)
        self.mask = CapsMask()
        self.capsLen = CapsLen()


    def forward(self, x, y_true=None, mode='train'):
        x = x.permute(0, 2, 1, 3)
        data = x
        x1 = self.channelCapsTemporal_1(data).view(data.size(0), 16, 16)
        x2 = self.channelCapsTemporal_2(data).view(data.size(0), 16, 16)
        channels = torch.cat((x1, x2), dim=2).view(data.size(0), 16, 8, 4)
        channels = self.channelRouting(channels)
        deep_channels = self.channelDeepSuper(channels.view(data.size(0), 1, 64, 8))
        new_locals = self.channelShrink(channels.view(data.size(0), 8, 8, 8))

        x1 = self.localCapsSpatial_1(data.view(data.size(0), 8, 2, 192)).view(data.size(0), 8, 16)
        x2 = self.localCapsSpatial_2(data.view(data.size(0), 8, 2, 192)).view(data.size(0), 8, 16)
        local = torch.cat((x1, x2), dim=2).view(data.size(0), 8, 8, 4)
        local = self.localRouting(local)
        deep_locals = self.localDeepSuper(local.view(data.size(0), 1, 32, 8))

        local = torch.cat((local, new_locals), dim=2)
        local = self.localShrink(local)
        new_regions = self.localRegion(local.view(data.size(0), 4, 8, 16))

        x1 = self.regionCapsSpatial_1(data.view(data.size(0), 4, 4, 192)).view(data.size(0), 4, 16)
        x2 = self.regionCapsSpatial_2(data.view(data.size(0), 4, 4, 192)).view(data.size(0), 4, 16)
        regions = torch.cat((x1, x2), dim=2).view(data.size(0), 4, 8, 4)
        regions = self.regionRouting(regions)
        deep_regions = self.regionDeepSuper(regions.view(data.size(0), 1, 16, 16))
        regions = torch.cat((regions, new_regions), dim=2)
        regions = self.regionShrink(regions)
        new_hemis = self.regionHemi(regions.view(data.size(0), 2, 8, 16))

        x1 = self.hemiCapsSpatial_1(data.view(data.size(0), 2, 8, 192)).view(data.size(0), 2, 16)
        x2 = self.hemiCapsSpatial_2(data.view(data.size(0), 2, 8, 192)).view(data.size(0), 2, 16)
        hemis = torch.cat((x1, x2), dim=2).view(data.size(0), 2, 8, 4)
        hemis = self.hemiRouting(hemis)
        hemis = torch.cat((hemis, new_hemis), dim=2)
        hemis = self.hemiShrink(hemis).view(data.size(0), 1, 8, 16)

        out = self.out(hemis)
        out = out.squeeze(1)

        pred = self.capsLen(out)

        if mode == "train":
            masked = self.mask(out, y_true)
            deep_channels = deep_channels.squeeze(1)
            deep_locals = deep_locals.squeeze(1)
            deep_regions = deep_regions.squeeze(1)
            masked_channels = self.mask(deep_channels, y_true)
            masked_locals = self.mask(deep_locals, y_true)
            masked_regions = self.mask(deep_regions, y_true)
        elif mode == "eval":
            masked = self.mask(out)
            x = self.generator(masked)
            return pred, x
        elif mode == "test":
            return pred
        x = self.generator(masked)
        x_channels = self.channel_generator(masked_channels)
        x_locals = self.local_generator(masked_locals)
        x_regions = self.region_generator(masked_regions)
        pred_channels = self.capsLen(deep_channels)
        pred_locals = self.capsLen(deep_locals)
        pred_regions = self.capsLen(deep_regions)

   
        return pred, x, pred_regions, x_regions, pred_locals, x_locals, pred_channels, x_channels