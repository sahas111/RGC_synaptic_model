__author__ = 'Susmita'


import sys
sys.path = ['/Applications/NEURON-7.4/nrn/lib/python'] + sys.path
import pylab
import numpy as np
import copy



import neuron
from neuron import h, gui
from matplotlib import pyplot


soma = h.Section()

soma.nseg = 1
soma.diam = 18.8
soma.L = 18.8
soma.Ra = 123.0




soma.insert('pas')
soma.insert('spike')



'''//Check 4 conditions for
//1.vrest (on the First block 0,500)
//2.spont activity  ON 0 Hz (First Block 0,500)
//3.no activity during 500 ms hyperpolarization -0.2 nA (Second Block 500,1000)
//4.At the termination of 500 ms stimulus of -0.2 nA (Third Block 1000,1150)
//subscript  1  corresponds to first block,  2  to the second block etc
// Better to give 100ms to stabilize before measuring Vrest. Therefore all blocks move to +100.'''



f = open('output', 'r+') #opens the file for both reading and writing
f.write( 'gbar_nap, gbar_lva,  ghdbar_hd ,  v1NoSpikeMean , FreqMean1 ,  FreqSize1 ,  meanisi1 ,  stdev1 ,  cvisi1 , FreqMean2 ,  FreqSize2 ,  meanisi2 ,  stdev2 ,  cvisi2 , FreqMean3 ,  FreqSize3 ,  meanisi3 ,  stdev3 ,  cvisi3 , v1NoSpikeMean01 , FreqMean1_T , FreqMean1_S , FreqMean2_01 ,  FreqMean3_01 ,  AllCondSatOFF' )


ghdbar_hd=1e-6


tsp = h.Vector()
vCopy = h.Vector()

h('objref nil')

nc = h.NetCon(soma(0.5)._ref_v,h.nil)
# nc = h.NetCon(soma(0.5)._ref_v,h.nil, -20.0, 0, 0)

vCopy.record(soma(0.5)._ref_v)
nc.record(tsp) # After a simulation run, the elements of tsp will be the times at which  the cell spiked # how to record it

t_vec = h.Vector()             # Time stamp vector
t_vec.record(h._ref_t)

# v1NoSpike = h.Vector()
# v1 = h.Vector()

# tsp1= h.Vector()
# tsp2= h.Vector()
# tsp3= h.Vector()
# tsp4= h.Vector()
h.tstop = 500
h.init()
h.run()

# StartTimeBlock1=0+100
# StartTimeBlock2=500+100
# StartTimeBlock3=1000+100
# StartTimeBlock4=1150+100
# FinishTimeBlock4=2000+100
#
sizetsp=tsp.size()
print sizetsp
#
pylab.plot(t_vec, vCopy)
pyplot.show()
#
#
#
# for i in (0,sizetsp-1): # divided the tsps into diffent blocks
#
#     if (tsp[i]<StartTimeBlock2):
#         tsp1.append(tsp.x[i])
#     if (tsp.x[i]>=StartTimeBlock2 and tsp.x[i]<=StartTimeBlock3):
#         tsp2.append(tsp.x[i])
#     if (tsp.x[i]>StartTimeBlock3 and tsp.x[i]<StartTimeBlock4):
#         tsp3.append(tsp.x[i])
#     if (tsp.x[i]>StartTimeBlock4 and tsp.x[i]<FinishTimeBlock4):
#         tsp4.append(tsp.x[i])
#
#
# dt = 1
#
# for k in (0,StartTimeBlock2/dt-1):
#     v1.append(vCopy.x[k]) # making the voltage vector for tsp1
#
#
# v1_slope = v1.deriv()
# length_of_block = 2/dt
# threshold=0.01 #10mV/1s = 10mV/1000ms
#
# for k in (0,v1.size()-1):
#     if (v1_slope.x[k] > threshold):
#         k=k+length_of_block
#     else:
#         v1NoSpike.append(vCopy.x[k])
#
# v1NoSpikeMean=v1NoSpike.mean() # calculating the resting voltage from block1
#
#
#
# isivec1 = copy.copy(tsp1)
# isivec2 = copy.copy(tsp1)
# isivec3 = copy.copy(tsp1)
# isivec4 = copy.copy(tsp1)
# freq1 = h.Vector(isivec1.size())
# freq2 = h.Vector(isivec2.size())
# freq3 = h.Vector(isivec3.size())
# freq4 = h.Vector(isivec4.size())
#
#
# if (freq1.size()==0):#if no spike
#     FreqSize1=0
#     FreqMean1=0
#     meanisi1=0
#
#
#
#
#
#
#

