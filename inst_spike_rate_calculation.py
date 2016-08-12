__author__ = 'Susmita'

## instantaneous spike rate and spike duration calculation

import sys
from scipy import signal
import pylab as plt
sys.path = ['/Applications/NEURON-7.4/nrn/lib/python'] + sys.path
from scipy.signal import butter, filtfilt
from scipy.signal import freqz
from scipy.signal import lfilter
import numpy as np
import glob
import os.path

path = 'control_ON_spikerate/*.txt'
files=glob.glob(path)

def deriv(a):
    n=len(a)
    d=[]
    d.insert(0,voltage1[1]-voltage1[0])
    d.insert(n-1,voltage1[n-1]-voltage1[n-2])
    for j in range(1,n-2):
        d.insert(j,float(voltage1[j+1]-voltage1[j-1])/2)

    return d

def find_nearest(array,value):
    idx = (np.abs(array-value)).argmin()
    return array[idx]






spike_freq_array=[]
spike_duration=[]
spike_amplitude=[]


for file in files:
    f = open(file, 'r')
    lines=f.readlines()

    time =[]
    voltage = []
    for x in lines:
        time.append(x.split()[0])
        voltage.append(x.split()[1])

    f.close()

    voltage1 = np.asarray(voltage,dtype = 'float64')
    time1 = np.asarray(time,dtype = 'float64')

    plt.figure()
    plt.plot(time1,voltage1)
    plt.show()






# inter_spike_interval and spike rate calculation

    spike_interval=np.diff(PeakX)
    good_spike_intervals=[]
    bad_spike_intervals=[]

    for i in range(0,len(spike_interval)-1):
        if (spike_interval[i]>0.02):
            good_spike_intervals.append(spike_interval[i])
        else:
            bad_spike_intervals.append(spike_interval[i])

    spike_freq = [1/x for x in good_spike_intervals]


    mean_spike_freq=np.mean(spike_freq)
    spike_freq_array.append(mean_spike_freq)



# plt.plot(time1,voltage1)
# plt.show()





















