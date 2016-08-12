__author__ = 'Susmita'

import sys
import copy

sys.path = ['/Applications/NEURON-7.4/nrn/lib/python'] + sys.path

# print sys.path
import pylab
import numpy as np

import time



import neuron
from neuron import h, gui
from matplotlib import pyplot

soma = h.Section()

# soma.nseg = 1
# soma.diam = 18.8
# soma.L = 18.8
# soma.Ra = 123.0

soma.nseg = 1
soma.diam =25.0
soma.L =25.0
soma.Ra=110.0

soma.insert('pas')
soma.e_pas=-60
soma.g_pas=5e-5





soma.insert('spike')
soma.gnabar_spike = 0.04
soma.gkbar_spike = 0.012
soma.gabar_spike = 0.036
soma.gcabar_spike = 0.002
soma.gkcbar_spike = 0.00005


h.celsius = 22
soma.ena=35
soma.ek=-75 #-75

# h.ehd_hd= 0



soma.insert ('cad')
soma.depth_cad = 0.1 #0.1 #(micron)3
soma.taur_cad = 1.5 #1.5 # (ms)10


soma.insert ('lva')
soma.insert ('hd')
soma.insert ('nap')



'''//Check 4 conditions for
//1.vrest (on the First block 0,500)
//2.spont activity  ON 0 Hz (First Block 0,500)
//3.no activity during 500 ms hyperpolarization -0.02 nA (Second Block 500,1000)
//4.At the termination of 500 ms stimulus of -0.02 nA (Third Block 1000,1150)
//subscript  1  corresponds to first block,  2  to the second block etc
// Better to give 100ms to stabilize before measuring Vrest. Therefore all blocks move to +100.'''



# f = open('outputt', 'r+') #opens the file for both reading and writing
# f.write( 'gbar_nap, gbar_lva,  ghdbar_hd ,  v1NoSpikeMean , FreqMean1 ,  FreqSize1 ,  meanisi1 ,  stdev1 ,  cvisi1 , FreqMean2 ,  FreqSize2 ,  meanisi2 ,  stdev2 ,  cvisi2 , FreqMean3 ,  FreqSize3 ,  meanisi3 ,  stdev3 ,  cvisi3 , v1NoSpikeMean01 , FreqMean1_T , FreqMean1_S , FreqMean2_01 ,  FreqMean3_01 ,  AllCondSatOFF' )





soma.ghdbar_hd =4e-6#2e-6 #S/cm2,OFF-S
soma.gbar_lva = 12e-4#1.2e-3  #S/cm2,
soma.gbar_nap = 5e-8 #S/cm2

# dt=1

tsp = h.Vector()
vCopy = h.Vector()


stim = h.IClamp(soma(0.5))

stim.amp = -0.020
stim.dur = 500
stim.delay = 600


def find_nearest(array,value):
    idx = (np.abs(array-value)).argmin()
    return array[idx]



h("objref nil")
nc = h.NetCon(soma(0.5)._ref_v,h.nil)

nc.record(tsp)
vCopy.record(soma(0.5)._ref_v)
 # After a simulation run, the elements of tsp will be the times at which  the cell spiked # how to record it


t_vec = h.Vector()             # Time stamp vector
t_vec.record(h._ref_t)



tsp1= h.Vector()
tsp2= h.Vector()
tsp3= h.Vector()
tsp4= h.Vector()

h.v_init = -65
h.dt=0.025

h.tstop = 2100
h.init()
h.run()
sizetsp=tsp.size()

StartTimeBlock1=0+100
StartTimeBlock2=500+100
StartTimeBlock3=1000+100
StartTimeBlock4=1150+150#1150+100
FinishTimeBlock4=2000+100



pylab.plot(t_vec, vCopy)
pyplot.show()



def deriv_sus(a):
    n=len(a)
    d=[]
    d.insert(0,vCopy[1]-vCopy[0])
    d.insert(n-1,vCopy[n-1]-vCopy[n-2])
    for j in range(1,n-2):
        d.insert(j,float(vCopy[j+1]-vCopy[j-1])/2)

    return d

d1=deriv_sus(vCopy)


#first block

v1 = h.Vector()
t1 = h.Vector()

k=0
for k in range(0,np.int(StartTimeBlock2/h.dt*1)):
    v1.append(vCopy.x[k])
    t1.append(t_vec.x[k])# making the voltage vector for tsp1

final_count_firstblock=(len(v1)-1)
PeakX=[]
PeakY=[]
peak_index=[]
j=0
for j in range(0,final_count_firstblock-1):  # 0/StartTimeBlock1*40, StartTimeBlock2*40
    if (np.sign(d1[j])>np.sign(d1[j+1])):
        if vCopy[j]>0:
           PeakX.append(t_vec[j])
           PeakY.append(vCopy[j])
           peak_index.append(j)

PeakX_array = np.asarray(PeakX,dtype = 'float64')
PeakY_array = np.asarray(PeakY,dtype = 'float64')
peak_index_array = np.asarray(peak_index,dtype = 'float64')

t1_array = np.asarray(t1,dtype = 'float64')
v1_array = np.asarray(v1,dtype = 'float64')


index_Peak_ends=[]
v1_Peak_ends=[]
j=0

for j in (range(0,final_count_firstblock-1)):
   if (np.sign(d1[j])<np.sign(d1[j+1])):
       index_Peak_ends.append(j)
       v1_Peak_ends.append(v1[j])

index_Peak_ends_array = np.asarray(index_Peak_ends,dtype = 'float64')
v1_Peak_ends_array = np.asarray(v1_Peak_ends,dtype = 'float64')

i=0
j=0
v1_nospike=[]
count=[]
j_range=range(0,final_count_firstblock)


# resting mean membrane potential and spike duration calculation

spike_duration = []

import itertools
for j,k in itertools.izip(j_range,index_Peak_ends ): # 0/StartTimeBlock1*40, StartTimeBlock2*40

        if d1[j]>0.01:
            diff = k-j
            count.append(j)
            spike_duration.append(t1[j]-t1[index_Peak_ends])
            j= j+diff



        else:
            v1_nospike.append(v1[j])



if np.size(v1_nospike)== 0:
    v1_nospike_mean = np.mean(v1_Peak_ends_array)

#  mean_spike_amplitude calculation

spike_amplitude=[]
j=0
k=0
j_range=range(0,final_count_firstblock)

for j,k in itertools.izip(j_range,PeakY): # 0/StartTimeBlock1*40, StartTimeBlock2*40

        if d1[j]>0.01:
            diff = k-v1[j]
            count.append(j)
            spike_amplitude.append(diff)
            j= j+diff


mean_spike_amplitude= np.mean(spike_amplitude)
mean_spike_duration= np.mean(spike_duration)





