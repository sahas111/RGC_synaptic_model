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

soma.nseg = 1
soma.diam = 18.8
soma.L = 18.8
soma.Ra = 123.0



#soma.insert('hh')
#soma.insert('CaT')
soma.insert('pas')
soma.insert('spike')
soma.insert('cad')
#soma.insert ('hd')
#soma.insert ('lva')


# excitatory synapse connection at soma
#ms

d={} #list for keeping excitatory and inhibitory synaptic parameters

d["excsyn1"]= h.ExpSyn(0.5, sec=soma) # position=0.5
d["excsyn1"].tau = 1 #ms decay time constant
d["excsyn1"].e = 0 #mV reversal potential
d["excsyn1"].i = 0.05 #nA synaptic current


d["inhsyn1"] = h.ExpSyn(0.8, sec=soma)
d["inhsyn1"].tau = 1
d["inhsyn1"].e = -70
d["inhsyn1"].i = 0.5




i = 0;

for x in range(1,exc['centers'].size):

    d["ppexc{0}".format(x)] = h.NetStim(0.5)
    # Creates a NetStim that will generate a stream of events that occur at times t0, t1, . . . ti, . . . such that the inter-event intervals are governed by the negative exponential distribution with mean interval equal to ISI.
    d["ppexc{0}".format(x)].interval = exc['counts'][0,i]
    # The maximum number of spikes that will be generated in any simulation is "number".
    d["ppexc{0}".format(x)].number = 1e9
    # earliest possible time of synaptic activation
    d["ppexc{0}".format(x)].start = 10
    # Noise=1 means that 100% of the total number of spikes follow a negexp distribution
    d["ppexc{0}".format(x)].noise = 1

    d["ncppexc{0}".format(x)] = h.NetCon( d["ppexc{0}".format(x)], d["excsyn1"]) #connecting the poisson stimulus and the synapse


    d["ncppexc{0}".format(x)].weight[0] = (-(exc['centers'][0,i]))/(-70-0) # i = G * (v - e)  G = weight * exp(-t/tau);
    d["ncppexc{0}".format(x)].delay = 1 #

    i = i+1


i =0
for x in range(1,2):

    d["ppinh{0}".format(x)] = h.NetStim(0.5)
    d["ppinh{0}".format(x)].interval = exc['counts'][0,i] # 1/f
    d["ppinh{0}".format(x)].number = 1e9
    d["ppinh{0}".format(x)].start = 10
    d["ppinh{0}".format(x)].noise = 1
    d["ncppinh{0}".format(x)] = h.NetCon( d["ppinh{0}".format(x)], d["inhsyn1"])
    d["ncppinh{0}".format(x)].weight[0] = (exc['centers'][0,i])/(0+70)
    d["ncppinh{0}".format(x)].delay = 20

    i = i+1


vecexc = {}
vecexc['i_excsyn']= h.Vector()
vecexc['i_excsyn'].record( d["excsyn1"]._ref_i)

vecinh = {}
vecinh['i_inhsyn']= h.Vector()
vecinh['i_inhsyn'].record( d["inhsyn1"]._ref_i)



v_vec = h.Vector()             # Membrane potential vector
t_vec = h.Vector()             # Time stamp vector
v_vec.record(soma(0.5)._ref_v) # References to variables are available as _ref_rangevariable.
t_vec.record(h._ref_t)
h.tstop = 500 #ms
h.run()


# pyplot.figure(figsize=(8,4)) # Default figsize is (8,6)

pylab.subplot(1,1,1)
pylab.plot(t_vec, v_vec)
pyplot.show()
pylab.subplot(2,1,1)
pylab.plot(t_vec, vecexc['i_excsyn'].div(5000)) # divided by membrane resistance (5,000 to 100,000 o/cm2), values obtained with intracellular sharp electrodes and wholecell recordings
pylab.subplot(2,1,2)
pylab.plot(t_vec, vecinh['i_inhsyn'].div(5000))

pyplot.show()

# pyplot.plot(t_vec, v_vec)
# pyplot.xlabel('time (ms)')
# pyplot.ylabel('mV')













