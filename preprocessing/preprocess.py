import numpy as np
from scipy.signal import butter, filtfilt

class PreProcess:
    def __init__(self, fs, lowcut, highcut, order):
        """
        Initialize the PreProcess object
        """
        
        self.fs = fs
        self.lowcut = lowcut
        self.highcut = highcut
        self.order = order
        self.nyquist = 0.5 * fs
        self.low = lowcut / self.nyquist
        self.high = highcut / self.nyquist
        self.b, self.a = butter(order, [self.low, self.high], btype='band')
        self.buffer = np.zeros((16, 5000))
        self.mean = np.zeros((16, 1))
        self.var = np.zeros((16, 1))
        self.n = 0

    def update_batch_stats(self, data):
        """
        Update the mean and variance of the data in the batch

        :param data: np.array, shape=(16, *), the data to update the stats with.
        """
        self.n += data.shape[1]
        if self.n > 5000:
            self.mean = np.mean(self.buffer, axis=1, keepdims=True)
            self.var = np.var(self.buffer, axis=1, keepdims=True)
            self.std = np.sqrt(self.var)
            self.n = 5000

        else:
            self.mean = np.mean(self.buffer[:, -self.n:], axis=1, keepdims=True)
            self.var = np.var(self.buffer[:, -self.n:], axis=1, keepdims=True)
            self.std = np.sqrt(self.var)
        

    def butter_bandpass_filter(self, data):
        """
        Apply a butter bandpass filter to the data

        :param data: np.array, shape=(16, 192), the data to filter
        :return: np.array, shape=(16, 192), the filtered data
        """

        return filtfilt(self.b, self.a, data, axis=1)
    
    def zscore(self, data):
        """
        Apply z-score normalization to the data

        :param data: np.array, shape=(16, 192), the data to normalize
        :return: np.array, shape=(16, 192), the normalized data
        """

        return (data - self.mean) / self.std

    def preprocess(self, data):
        """
        Preprocess the data

        :param data: np.array, shape=(16, *), the data to preprocess
        :return: np.array, shape=(16, 192), the preprocessed data
        """
        self.buffer = np.concatenate((self.buffer[:, data.shape[1]:], data), axis=1)
        self.update_batch_stats(data)
        data = self.buffer
        data = self.butter_bandpass_filter(data)
        data = self.zscore(data)
        if data.shape[1] > 192:
            return data[:, -192:]

        return data
        
