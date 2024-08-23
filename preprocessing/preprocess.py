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
        self.buffer = np.zeros((16, 192))
        self.n = np.zeros(16)
        self.mean = np.zeros(16)
        self.M2 = np.zeros(16)

    def update_batch_stats(self, data):
        """
        Update the mean and variance of the data in the batch

        :param data: np.array, shape=(16, *), the data to update the stats with.
        """

        batch_mean = np.mean(data, axis=1)
        delta = batch_mean - self.mean
        batch_M2 = np.sum((data - batch_mean) ** 2, axis=1)
        n_new = self.n + data.shape[1]

        self.mean += delta * data.shape[1] / n_new
        self.M2 += batch_M2 + delta ** 2 * self.n * data.shape[1] / n_new
        self.n = n_new

        self.buffer = np.concatenate((self.buffer[:, data.shape[1]:], data), axis=1)

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

        return (data - self.mean) / np.sqrt(self.M2 / self.n)

    def preprocess(self, data):
        """
        Preprocess the data

        :param data: np.array, shape=(16, *), the data to preprocess
        :return: np.array, shape=(16, 192), the preprocessed data
        """

        self.update_batch_stats(data)
        data = self.buffer
        data = self.butter_bandpass_filter(data)
        data = self.zscore(data)

        return data
        
