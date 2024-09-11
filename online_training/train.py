import torch
import torch.optim as optim
import torch.nn.functional as F
from model.CapsNet import EEGCapsNet
from online_training.loss import TotalLoss
import os
import numpy as np
import h5py
from tqdm import tqdm
import re

class Train:
    def __init__(self, model_path="C:/Users/Nathan/Git/capsnet_49.pth", data_path="C:/Users/Nathan/Git/pong_data", num_epochs=2):
        self.model = EEGCapsNet()
        self.model_path = model_path
        self.num_epochs = num_epochs
        self.optimizer = optim.SGD(self.model.parameters(), lr=0.001, momentum=0.95, nesterov=True, weight_decay=0.0001)
        self.criterion = TotalLoss()
        self.data, self.labels = self.load_data(data_path)
        self.data, self.labels = self.balance_data(self.data, self.labels)
        print("balanced the data")
        self.dl = torch.utils.data.DataLoader(list(zip(self.data, self.labels)), batch_size=64, shuffle=True)
        self.model.load_state_dict(torch.load(model_path, weights_only=True))

    def extract_time(self, s):
        s = int(''.join(re.findall(r'\d+', s)))
        return s
    
    def balance_data(self, data, labels):
        # get min number of each label (either 0 or 1)
        label_count = {0: 0, 1: 0}
        for label in labels:
            idx = torch.argmax(label).item()
            label_count[idx] += 1
        min_num = min(label_count.values())
        # balance the data by using the min_num and applying random sampling (both labels will have the same number of samples (min_num))
        balanced_data = []
        balanced_labels = []
        shuffle = np.random.permutation(len(data))
        for i in range(2):
            count = 0
            for j in shuffle:
                if torch.argmax(labels[j]).item() == i:
                    # check for nan
                    if torch.isnan(data[j]).any():
                        print("nan found")
                        continue
                    balanced_data.append(data[j])
                    balanced_labels.append(labels[j])
                    count += 1
                    if count == min_num:
                        break
        return balanced_data, balanced_labels



    def load_data(self, data_path):
        files = sorted(os.listdir(data_path), key=lambda x: self.extract_time(x.split('_')[2]))

        data = []
        labels = []
        for file in files:
            with h5py.File(os.path.join(data_path, file), "r") as f:
                for index in f.keys():
                    grp = f[index]
                    data.append(torch.from_numpy(np.array(grp['data'])).float())
                    label = grp.attrs['correct']
                    if label == 'right':
                        labels.append(torch.tensor([1, 0]).float())
                    else:
                        labels.append(torch.tensor([0, 1]).float())

        return data, labels
    
    def train(self):
        deep_super_weights = [1/(1.5**i) for i in range(4)]
        deep_super_weights = deep_super_weights / np.sum(deep_super_weights)
        # compute accuracy before
        self.model.eval()
        self.model.cuda()
        test_loss = 0
        total_accuracy = 0
        with torch.no_grad():
            pbar = tqdm(total=len(self.dl))
            for j, (x, y) in enumerate(self.dl):
                x = x.float().cuda()
                y = y.cuda()
                x = x.unsqueeze(1)
                outs = self.model(x, mode='eval')
                pred = outs[0]
                # check for nan
                if torch.isnan(pred).any():
                    print("nan found")
                    quit()
                img = outs[1]
                y = y.squeeze(1)
                x_fft = torch.fft.fft(x, dim=-1)
                loss = self.criterion(x_fft, y, img, pred)
                test_loss += loss.item()
                predicted = torch.argmax(pred, -1)
                labels = torch.argmax(y, -1)
                accuracy = (predicted == labels).float().mean().item()
                total_accuracy += accuracy
                pbar.set_description(f"val loss={test_loss / (j + 1):0.4f}    val acc={total_accuracy / (j + 1):0.4f}")
                pbar.update(1)
        pbar.close()
        print(f"Initial accuracy: {total_accuracy / len(self.dl)}")
        for epoch in range(self.num_epochs):
            pbar = tqdm(enumerate(self.dl), total=len(self.dl))
            self.model.train()
            total_loss = 0
            for i, (data, label) in enumerate(self.dl):
                data = data.unsqueeze(1).cuda()
                label = label.cuda()
                self.optimizer.zero_grad()
                x_fft = torch.fft.fft(data, dim=-1)
                outs = self.model(data)
                full_loss = 0
                # check if tensors require grad
                
                for k in range(0, 8, 2):
                    loss = self.criterion(x_fft, label, outs[k+1], outs[k])
                    loss *= deep_super_weights[k // 2]
                    full_loss += loss
                # identify what parameters do not require grad
                full_loss.backward()
                self.optimizer.step()
                total_loss += full_loss.item()
                pbar.set_description(f"Epoch {epoch + 1}    loss={total_loss / (i + 1):0.4f}")
                pbar.update(1)
            pbar.close()
        
        # compute accuracy after
        self.model.eval()
        test_loss = 0
        total_accuracy = 0
        with torch.no_grad():
            pbar = tqdm(total=len(self.dl))
            for j, (x, y) in enumerate(self.dl):
                x = x.float().cuda()
                y = y.cuda()
                x = x.unsqueeze(1)
                outs = self.model(x, mode='eval')
                pred = outs[0]
                img = outs[1]
                y = y.squeeze(1)
                x_fft = torch.fft.fft(x, dim=-1)
                loss = self.criterion(x_fft, y, img, pred)
                test_loss += loss.item()
                predicted = torch.argmax(pred, -1)
                labels = torch.argmax(y, -1)
                accuracy = (predicted == labels).float().mean().item()
                total_accuracy += accuracy
                pbar.set_description(f"val loss={test_loss / (j + 1):0.4f}    val acc={total_accuracy / (j + 1):0.4f}")
                pbar.update(1)
        pbar.close()
        print(f"Final accuracy: {total_accuracy / len(self.dl)}")

        torch.save(self.model.state_dict(), self.model_path)
        print("Model saved.")


def main():
    model_path = "C:/Users/Nathan/Git/capsnet_49.pth"
    data_path = "C:/Users/Nathan/Git/pong_data"
    t = Train(model_path, data_path)
    t.train()
        
    



