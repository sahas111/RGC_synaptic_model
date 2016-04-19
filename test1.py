__author__ = 'Susmita'

import sys
import scipy.io
exc= scipy.io.loadmat('histdata.mat')
sys.path = ['/Applications/NEURON-7.4/nrn/lib/python'] + sys.path

# print sys.path
import pylab
import numpy as np



import neuron
from neuron import h, gui
from matplotlib import pyplot

soma = h.Section()

# soma.nseg = 1
# soma.diam = 18.8
# soma.L = 18.8
# soma.Ra = 123.0

soma.nseg = 1
soma.diam = 25
soma.L = 25
soma.Ra=110

soma.insert('pas')
soma.e_pas=-60
soma.g_pas=5e-5



soma.insert('spike')
soma.gnabar_spike = 0.04
soma.gkbar_spike = 0.012
soma.gabar_spike = 0.036
soma.gcabar_spike = 0.0022
soma.gkcbar_spike = 0.00005


h.celsius = 22
soma.ena=35
soma.ek=-75 #75

soma.insert ('cad')
soma.depth_cad = 0.1 #(micron)3
soma.taur_cad = 1.5 # (ms)10


soma.insert ('lva')
soma.insert ('hd')
soma.insert ('nap')

# h.ehd=0

#soma.ghdbar_hd = 2e-6 #S/cm2,OFF-T
# soma.gbar_lva = 5e-4 #4e-4 #S/cm2,
# soma.gbar_nap = 5e-8 #S/cm2

soma.ghdbar_hd = 2e-6 #S/cm2,OFF-S
soma.gbar_lva = 1.2e-3 #4e-4 #S/cm2,
soma.gbar_nap = 5e-8 #S/cm2



# stim = h.IClamp(soma(0.5))
#
# stim.amp = 0.4
# stim.dur = 1000




d={} #list for keeping excitatory and inhibitory synaptic parameters

d["excsyn1"]= h.ExpSyn(0.5, sec=soma) # position=0.5
d["excsyn1"].tau = 1 #ms decay time constant
d["excsyn1"].e = 0 #mV reversal potential

d["excsyn1"].i = 0 #nA synaptic current


d["inhsyn1"] = h.ExpSyn(0.8, sec=soma)
d["inhsyn1"].tau = 1
d["inhsyn1"].e = -70
d["inhsyn1"].i = 0




i = 0
inter =10
weigh = 1

for x in range(0,1): #(1,exc['centers'].size):


    d["ppexc{0}".format(x)] = h.NetStim(0.5)
    # Creates a NetStim that will generate a stream of events that occur at times t0, t1, . . . ti, . . . such that the inter-event intervals are governed by the negative exponential distribution with mean interval equal to ISI.
    d["ppexc{0}".format(x)].interval = inter #exc['counts'][0,i]
    # The maximum number of spikes that will be generated in any simulation is "number".
    d["ppexc{0}".format(x)].number = 1e9
    # earliest possible time of synaptic activation
    d["ppexc{0}".format(x)].start = 0
    # Noise=1 means that 100% of the total number of spikes follow a negexp distribution
    d["ppexc{0}".format(x)].noise = 1

    d["ncppexc{0}".format(x)] = h.NetCon( d["ppexc{0}".format(x)], d["excsyn1"]) #connecting the poisson stimulus and the synapse

    d["ncppexc{0}".format(x)].weight[0] = weigh#((exc['centers'][0,i]))/(-70-0) # i = G * (v - e)  G = weight * exp(-t/tau);
    d["ncppexc{0}".format(x)].delay = 0 #g

    i = i+1
    inter = inter +10
    weigh = weigh+0.5



interin =10
weighin = 0.5
j =0
for x in range(0,1):

    d["ppinh{0}".format(x)] = h.NetStim(0.5)
    d["ppinh{0}".format(x)].interval = inter #exc['counts'][0,i] # 1/f
    d["ppinh{0}".format(x)].number = 1e9
    d["ppinh{0}".format(x)].start = 0
    d["ppinh{0}".format(x)].noise = 1
    d["ncppinh{0}".format(x)] = h.NetCon( d["ppinh{0}".format(x)], d["inhsyn1"])
    d["ncppinh{0}".format(x)].weight[0] =weighin #(exc['centers'][0,i])/(0+70)
    d["ncppinh{0}".format(x)].delay = 0

    j = j+1
    inter = interin +10
    weigh = weighin+0.5


vecexc = {}
vecexc['i_excsyn']= h.Vector()
vecexc['i_excsyn'].record(d["excsyn1"]._ref_i)

vecinh = {}
vecinh['i_inhsyn']= h.Vector()
vecinh['i_inhsyn'].record( d["inhsyn1"]._ref_i)



v_vec = h.Vector()             # Membrane potential vector
t_vec = h.Vector()             # Time stamp vector
v_vec.record(soma(0.5)._ref_v) # References to variables are available as _ref_rangevariable.
t_vec.record(h._ref_t)


h.tstop = 100 #ms
h.run()
# pyplot.figure(figsize=(8,4)) # Default figsize is (8,6)


pylab.subplot(3,1,1)
pyplot.plot(t_vec, v_vec)
# pyplot.show()
# pylab.plot(t_vec, v_vec)
# pyplot.show()

pylab.subplot(3,1,2)
pyplot.plot(t_vec, vecexc['i_excsyn']) #div(5000)) # divided by membrane resistance (5,000 to 100,000 o/cm2), values obtained with intracellular sharp electrodes and wholecell recordings
pylab.subplot(3,1,3)
pylab.plot(t_vec, vecinh['i_inhsyn'])#.div(5000))
pyplot.show()

# pyplot.plot(t_vec, v_vec)
# pyplot.xlabel('time (ms)')
# pyplot.ylabel('mV')













