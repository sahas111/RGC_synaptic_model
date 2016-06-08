
# coding: utf-8

# In[1]:

import plotly_plotting as pp
import plotly.plotly as py
import plotly.graph_objs as go


# In[2]:

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
soma.gcabar_spike = 0.002
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
# soma.gbar_nap = 5e-8 #S/cm2

h.ehd_hd =0

# soma.ghdbar_hd = 4e-6 #S/cm2,OFF-S
# soma.gbar_lva = 10e-4  #S/cm2,
# soma.gbar_nap = 5e-8 #S/cm2

'''//Check 4 conditions for
//1.vrest (on the First block 0,500)
//2.spont activity  ON 0 Hz/OFF-S: [34, 54] Hz/OFF-T: [9 29] Hz (First Block 0,500)
//3.no activity during 500 ms hyperpolarization -0.2 nA (Second Block 500,1000)
//4.At the termination of 500 ms stimulus of -0.2 nA (Third Block 1000,1150)
//subscript  1  corresponds to first block,  2  to the second block etc
// Better to give 100ms to stabilize before measuring Vrest. Therefore all blocks move to +100.'''



# f = open('outputt', 'r+') #opens the file for both reading and writing
# f.write( 'gbar_nap, gbar_lva,  ghdbar_hd ,  v1NoSpikeMean , FreqMean1 ,  FreqSize1 ,  meanisi1 ,  stdev1 ,  cvisi1 , FreqMean2 ,  FreqSize2 ,  meanisi2 ,  stdev2 ,  cvisi2 , FreqMean3 ,  FreqSize3 ,  meanisi3 ,  stdev3 ,  cvisi3 , v1NoSpikeMean01 , FreqMean1_T , FreqMean1_S , FreqMean2_01 ,  FreqMean3_01 ,  AllCondSatOFF' )





tsp = h.Vector()
vCopy = h.Vector()
ghdbar_hd =h.Vector()
gbar_lva = h.Vector()
gbar_nap=h.Vector()



stim = h.IClamp(soma(0.5))

stim.amp = -0.020
stim.dur = 500
stim.delay = 600


soma.gbar_nap=5e-8
for zz in range(0,1):#(0,13)
    soma.gbar_lva=2e-4

    for jj in range(0,17):#13 or 20

        soma.ghdbar_hd=2e-6
        for ii in range(0,15): #2,13 or 20

            start_time = time.time()

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

            h.dt=0.025
            h.v_init =-65
            h.tstop = 5000
            h.init()
            h.run()
            sizetsp=tsp.size()

            StartTimeBlock1=0+100
            StartTimeBlock2=500+100
            StartTimeBlock3=1000+100
            StartTimeBlock4=1150+150#1150+100
            FinishTimeBlock4=2000+100



            # pylab.plot(t_vec, vCopy)
            # pyplot.show()

            for i in range(0,np.int(sizetsp)): # divided the tsps into diffent blocks
                if sizetsp == 0:
                    break;
                if (tsp.x[i]<StartTimeBlock2):#  if (tsp.x[i]>StartTimeBlock1 and tsp.x[i]<StartTimeBlock2)
                    tsp1.append(tsp.x[i])
                if (tsp.x[i]>=StartTimeBlock2 and tsp.x[i]<=StartTimeBlock3):
                    tsp2.append(tsp.x[i])
                if (tsp.x[i]>=StartTimeBlock3 and tsp.x[i]<=StartTimeBlock4):
                    tsp3.append(tsp.x[i])
                if (tsp.x[i]>StartTimeBlock4 and tsp.x[i]<FinishTimeBlock4):
                    tsp4.append(tsp.x[i])
                i = i+1

            v1 = h.Vector()
            v1NoSpike = h.Vector()



            for k in range(0,np.int((StartTimeBlock2/h.dt)*1)):
                v1.append(vCopy.x[k]) # making the voltage vector for tsp1


            v1_slope = copy.copy(v1)
            v1_slope.deriv(1) #dx=1
            length_of_block = 2
            threshold=0.01 #unit will be 10 mv/ms

            # for k in range(0,np.int((v1_slope.size())-1)):
            #     if (v1_slope.x[k] < threshold):
                    # v1NoSpike.append(vCopy.x[k])/

            k = 0
            while (k < np.int((v1_slope.size()))):
                if (v1_slope.x[k] > threshold):
                    k=k+length_of_block
                else:
                    v1NoSpike.append(vCopy.x[k])
                    k += 1

            if (v1NoSpike.size() == 0):
                v1NoSpikeMean=0.0 # no NaN maybe?
            else:
                v1NoSpikeMean=v1NoSpike.mean() # calculating the resting voltage from block1



            isivec1 = copy.copy(tsp1)
            isivec2 =copy.copy(tsp2)
            isivec3 = copy.copy(tsp3)
            isivec4 = copy.copy(tsp4)

            freq1 = h.Vector(isivec1.size())
            freq2 = h.Vector(isivec2.size())
            freq3 = h.Vector(isivec3.size())
            freq4 = h.Vector(isivec4.size())

                 ###### First time block ######
            if (freq1.size()==0):
                FreqSize1=0; FreqMean1=0; meanisi1=0

            if (freq1.size()==1):
                FreqSize1=1;FreqMean1=0;meanisi1=0

            if (freq1.size()>=2):
               isivec1.deriv(1) #isivec contains the interspike intervals//Vector class's deriv method using Euler method and "dx" parameter == 1 transforms recorded spike times to interspike intervals at machine language speeds.//
               for i in range(0,np.int(isivec1.size())): # change it to np.int(freq1.size()-1)
                   freq1.x[i] = 1000.0/isivec1.x[i]#instanteneous frequency

               FreqSize1=freq1.size()
               FreqMean1=freq1.mean()
               meanisi1=isivec1.mean()
               stdev1=9999 #to control if FreqMean1=0 then cannot calculate stdev and cvisi
               cvisi1=9999
               if (FreqMean1 > 0):
                  stdev1=isivec1.stdev()
                  cvisi1= stdev1/(isivec1.mean())




                              ###### Second time block######

            if (freq2.size()==0):
                FreqSize2=0; FreqMean2=0; meanisi2=0

            if (freq2.size()==1):
                FreqSize2=1;FreqMean2=0;meanisi2=0

            if (freq2.size()>=2):
                isivec2.deriv(1) #isivec contains the interspike intervals//Vector class's deriv method using Euler method and "dx" parameter == 1 transforms recorded spike times to interspike intervals at machine language speeds.//
                for i in range(0,np.int(isivec2.size())):
                    freq2.x[i] = 1000.0/isivec2.x[i] #instanteneous frequency
                FreqSize2=freq2.size()
                FreqMean2=freq2.mean()
                meanisi2=isivec2.mean()
                stdev2=9999 #to control if FreqMean1=0 then cannot calculate stdev and cvisi
                cvisi2=9999
                if (FreqMean2 > 0):
                    stdev2=isivec2.stdev()
                    cvisi2= stdev2/(isivec2.mean())



                          ###### Third time block######

            if (freq3.size()==0):
                FreqSize3=0; FreqMean3=0; meanisi3=0

            if (freq3.size()==1):
                FreqSize3=1;FreqMean3=0;meanisi3=0

            if (freq3.size()>=2):
                isivec3.deriv(1) #isivec contains the interspike intervals//Vector class's deriv method using Euler method and "dx" parameter == 1 transforms recorded spike times to interspike intervals at machine language speeds.//
                for i in range(0,np.int(isivec3.size())):
                    freq3.x[i] = 1000/isivec3.x[i] #instanteneous frequency
                FreqSize3=freq3.size()
                FreqMean3=freq3.mean()
                meanisi3=isivec3.mean()
                stdev1=9999 #to control if FreqMean1=0 then cannot calculate stdev and cvisi
                cvisi1=9999
                if (FreqMean3 > 0):
                    stdev3=isivec3.stdev()
                    cvisi3= stdev3/(isivec3.mean())



                           ###### Fourth time block######

            if (freq4.size()==0):
                FreqSize4=0; FreqMean4=0; meanisi4=0

            if (freq4.size()==1):
                FreqSize4=1;FreqMean4=0;meanisi4=0

            if (freq4.size()>=2):
                isivec4.deriv() #isivec contains the interspike intervals//Vector class's deriv method using Euler method and "dx" parameter == 1 transforms recorded spike times to interspike intervals at machine language speeds.//
                for i in range(0,np.int(isivec4.size())):
                    freq4.x[i] = 1000/isivec4.x[i] #instanteneous frequency
                FreqSize4=freq4.size()
                FreqMean4=freq4.mean()
                meanisi4=isivec4.mean()

                stdev4=9999 #to control if FreqMean1=0 then cannot calculate stdev and cvisi
                cvisi4=9999

                if (FreqMean4 > 0):
                    stdev4=isivec4.stdev()
                    cvisi4= stdev4/(isivec4.mean())



                               #########--------OFF-S-------#########
            if (v1NoSpikeMean>-60 and v1NoSpikeMean<=-50):
                v1NoSpikeMean01=1

            else:
                v1NoSpikeMean01=0

            if (FreqMean1>=9 and FreqMean1<=54): #change the S values 34-54
                FreqMean1_S=1

            else:
                FreqMean1_S=0

            if (FreqMean2==0):
                FreqMean2_01=1

            else:
                FreqMean2_01=0 #no activity during hyperpolarization -0.2 nA

            if (FreqMean3>=60):#60
                FreqMean3_01=1
            else:
                FreqMean3_01=0 #burst after hyperpolarization


            # if (FreqMean3>=2*FreqMean1):
            #      FreqMean3_01=1
            # else:
            #      FreqMean3_01=0} #burst after hyperpolarization


            AllCondSatOFF=0

            if (v1NoSpikeMean01==1 and FreqMean1_S==1 and  FreqMean2_01==1 and FreqMean3_01==1):
                AllCondSatOFF=1
                # f.write( "%g %g %g" %soma.gbar_nap %soma.gbar_lva %soma.ghdbar_hd)
                ghdbar_hd.append(soma.ghdbar_hd)
                gbar_lva.append(soma.gbar_lva)
                gbar_nap.append(soma.gbar_nap)


            else:
                m=0


            soma.ghdbar_hd=soma.ghdbar_hd+1e-6 #1e-6

            # print "elapsed_time = "  + str(time.time() - start_time)

        soma.gbar_lva=soma.gbar_lva+1e-4 #2e-4

    # soma.gbar_nap=soma.gbar_nap*10




'''import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(ghdbar_hd, gbar_lva, gbar_nap)
ax.scatter(ghdbar_hd_syn, gbar_lva_syn, gbar_nap_syn,c='g')

ax.set_xlabel('ghdbar_hd')
ax.set_ylabel('gbar_lva')
ax.set_zlabel('gbar_nap')

ax.plot_wireframe(ghdbar_hd, gbar_lva, gbar_nap)


ax.plot_trisurf(ghdbar_hd, gbar_lva, gbar_nap)

ax.plot_trisurf(ghdbar_hd_syn, gbar_lva_syn, gbar_nap_syn)

import numpy
import numpy.random as nprnd
import matplotlib.pyplot as plt

plt.axis([1e-4,16e-4,1e-6,18e-6])
plt.plot(gbar_lva,ghdbar_hd,linestyle='', marker='o',markersize=15,markerfacecolor='none')

plt.plot(gbar_lva, ghdbar_hd,linestyle='', marker='^',markersize=10,markerfacecolor='blue')
plt.xlabel('ghdbar_lva')
plt.ylabel('ghdbar_hd')
'''

# import matplotlib.pyplot as plt
#
# plt.axis([1e-4,16e-4,1e-6,18e-6])
# plt.plot(gbar_lva,ghdbar_hd,linestyle='', marker='o',markersize=15,markerfacecolor='none')
# plt.plot(gbar_lva_syn_rd, ghdbar_hd_syn_rd,linestyle='', marker='^',markersize=10,markerfacecolor='blue')
# plt.show()


# In[3]:

ghdbar_hd=np.array(ghdbar_hd)
gbar_lva=np.array(gbar_lva)

no_syn = go.Scatter(
    x = gbar_lva,
    y = ghdbar_hd,
    mode = 'markers',
    marker=dict(size=14,color = 'rgba(0, 0, 0)'),
    name='no_syn'      
)
data = [no_syn]


# In[5]:

import plotly.plotly as py
layout = pp.Layout(
    autosize=False,
    width=500,
    height=500,
    showlegend=True,
    xaxis=dict(
        title='gbar_lva[S/cm2]',
        
    ),
    yaxis=dict(
        title='gbar_hd[S/cm2]',
    )       

fig = pp.Figure(data = data, layout=layout)
pp.iplot(fig)


# In[2]:

__author__ = 'Susmita'

import sys
import copy

sys.path = ['/Applications/NEURON-7.4/nrn/lib/python'] + sys.path

import scipy.io
exc= scipy.io.loadmat('wt-OFF-exc-output/wt_OFF_exc_output.mat')
inh = scipy.io.loadmat('wt-OFF-inh-output/wt_OFF_inh_output.mat')

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

# soma.ghdbar_hd = 4e-6 #S/cm2,OFF-S
# soma.gbar_lva = 10e-4  #S/cm2,
# soma.gbar_nap = 5e-8 #S/cm2

'''//Check  conditions with the presence of synaptic activity:

//2.spont activity  wt-ON [6, 9] Hz/wt-OFF: [1, 28]Hz  (First Block 0,500)'''




# f = open('outputt', 'r+') #opens the file for both reading and writing
# f.write( 'gbar_nap, gbar_lva,  ghdbar_hd ,  v1NoSpikeMean , FreqMean1 ,  FreqSize1 ,  meanisi1 ,  stdev1 ,  cvisi1 , FreqMean2 ,  FreqSize2 ,  meanisi2 ,  stdev2 ,  cvisi2 , FreqMean3 ,  FreqSize3 ,  meanisi3 ,  stdev3 ,  cvisi3 , v1NoSpikeMean01 , FreqMean1_T , FreqMean1_S , FreqMean2_01 ,  FreqMean3_01 ,  AllCondSatOFF' )


tsp = h.Vector()
vCopy = h.Vector()
ghdbar_hd_syn_wt =h.Vector()
gbar_lva_syn_wt = h.Vector()
gbar_nap_syn_wt=h.Vector()



# stim = h.IClamp(soma(0))
#
# stim.amp = -0.2
# stim.dur = 500
# stim.delay = 600

d={} #list for keeping excitatory and inhibitory synaptic parameters

d["excsyn1"]= h.ExpSyn(0.5, sec=soma) # position=0.5
d["excsyn1"].tau = 5 #ms decay time constant:from Tian et al.1998
d["excsyn1"].e = 0 #mV reversal potential
d["excsyn1"].i = 0 #nA synaptic current


d["inhsyn1"] = h.ExpSyn(0.8, sec=soma)
d["inhsyn1"].tau = 10 #from Tian et al.1998
d["inhsyn1"].e = -70
d["inhsyn1"].i = 0





i = exc['centers'].size

for x in range(0,i):


    d["ppexc{0}".format(x)] = h.NetStim(0.5)
    # Creates a NetStim that will generate a stream of events that occur at times t0, t1, . . . ti, . . . such that the inter-event intervals are governed by the negative exponential distribution with mean interval equal to ISI.
    if (exc['freq'][0,x]==0):
        d["ppexc{0}".format(x)].interval = 1e100
        d["ppexc{0}".format(x)].number = 0
    else:
        d["ppexc{0}".format(x)].interval = (1.0/exc['freq'][0,x])*1000

    # The maximum number of spikes that will be generated in any simulation is "number".
    d["ppexc{0}".format(x)].number = 1e9
    # earliest possible time of synaptic activation
    d["ppexc{0}".format(x)].start = 0
    # Noise=1 means that 100% of the total number of spikes follow a negexp distribution
    d["ppexc{0}".format(x)].noise = 1

    d["ncppexc{0}".format(x)] = h.NetCon( d["ppexc{0}".format(x)], d["excsyn1"]) #connecting the poisson stimulus and the synapse

    d["ncppexc{0}".format(x)].weight[0] = -((exc['centers'][0,x])*1e-3)/(-70-0) # i = G * (v - e)  G = weight * exp(-t/tau);
    d["ncppexc{0}".format(x)].delay = 0 #g







j= inh['centers'].size

for x in range(0,j):

    d["ppinh{0}".format(x)] = h.NetStim(0.8)
    if (inh['freq'][0,x]==0):
        d["ppexc{0}".format(x)].interval = 1e1000
        d["ppinh{0}".format(x)].number = 0
    else:
        d["ppinh{0}".format(x)].interval = (1.0/inh['freq'][0,x])*1000

    d["ppinh{0}".format(x)].number = 1e9
    d["ppinh{0}".format(x)].start = 0
    d["ppinh{0}".format(x)].noise = 1
    d["ncppinh{0}".format(x)] = h.NetCon( d["ppinh{0}".format(x)], d["inhsyn1"])
    d["ncppinh{0}".format(x)].weight[0] =((inh['centers'][0,x])*1e-3)/(0+70)
    d["ncppinh{0}".format(x)].delay = 0







soma.gbar_nap=5e-8
for zz in range(0,1):
    soma.gbar_lva=2e-4 #2e-4

    for jj in range(0,17):#13 or 20

        soma.ghdbar_hd=2e-6
        for ii in range(0,15): #13 or 20

            #start_time = time.time()

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

            # h.v_init = -65
            h.dt=0.025
            h.v_init =-65
            h.tstop = 5000
            h.init()
            h.run()
            sizetsp=tsp.size()

            StartTimeBlock1=0+100
            StartTimeBlock2=500+100
            StartTimeBlock3=1000+100
            StartTimeBlock4=1150+150#1150+100
            FinishTimeBlock4=2000+100



            # pylab.plot(t_vec, vCopy)
            # pyplot.show()



            for i in range(0,np.int(sizetsp)): # divided the tsps into diffent blocks
                if sizetsp == 0:
                    break;
                if (tsp.x[i]<StartTimeBlock2):#  if (tsp.x[i]>StartTimeBlock1 and tsp.x[i]<StartTimeBlock2)
                    tsp1.append(tsp.x[i])
                # if (tsp.x[i]>StartTimeBlock2 and tsp.x[i]<=StartTimeBlock3):
                #     tsp2.append(tsp.x[i])
                # if (tsp.x[i]>StartTimeBlock3 and tsp.x[i]<StartTimeBlock4):
                #     tsp3.append(tsp.x[i])
                # if (tsp.x[i]>StartTimeBlock4 and tsp.x[i]<FinishTimeBlock4):
                #     tsp4.append(tsp.x[i])
                i = i+1

            v1 = h.Vector()
            v1NoSpike = h.Vector()



            for k in range(0,np.int((StartTimeBlock2/h.dt)*1)):
                v1.append(vCopy.x[k]) # making the voltage vector for tsp1


            v1_slope = copy.copy(v1)
            v1_slope.deriv(1) #dx=1
            length_of_block = 2
            threshold=0.01 #unit will be 10 mv/ms

            # for k in range(0,np.int((v1_slope.size())-1)):
            #     if (v1_slope.x[k] < threshold):
                    # v1NoSpike.append(vCopy.x[k])/

            k = 0
            while (k < np.int((v1_slope.size()))):
                if (v1_slope.x[k] > threshold):
                    k=k+length_of_block
                else:
                    v1NoSpike.append(vCopy.x[k])
                    k += 1

            if (v1NoSpike.size() == 0):
                v1NoSpikeMean=0.0 # no NaN maybe?
            else:
                v1NoSpikeMean=v1NoSpike.mean() # calculating the resting voltage from block1



            isivec1 = copy.copy(tsp1)
            isivec2 =copy.copy(tsp2)
            isivec3 = copy.copy(tsp3)
            isivec4 = copy.copy(tsp4)

            freq1 = h.Vector(isivec1.size())
            freq2 = h.Vector(isivec2.size())
            freq3 = h.Vector(isivec3.size())
            freq4 = h.Vector(isivec4.size())

                 ###### First time block ######
            if (freq1.size()==0):
                FreqSize1=0; FreqMean1=0; meanisi1=0

            if (freq1.size()==1):
                FreqSize1=1;FreqMean1=0;meanisi1=0

            if (freq1.size()>=2):
               isivec1.deriv(1) #isivec contains the interspike intervals//Vector class's deriv method using Euler method and "dx" parameter == 1 transforms recorded spike times to interspike intervals at machine language speeds.//
               for i in range(0,np.int(isivec1.size())): # change it to np.int(freq1.size()-1)
                   freq1.x[i] = 1000.0/isivec1.x[i]#instanteneous frequency

               FreqSize1=freq1.size()
               FreqMean1=freq1.mean()
               meanisi1=isivec1.mean()
               stdev1=9999 #to control if FreqMean1=0 then cannot calculate stdev and cvisi
               cvisi1=9999
               if (FreqMean1 > 0):
                  stdev1=isivec1.stdev()
                  cvisi1= stdev1/(isivec1.mean())



            #
            #                   ###### Second time block######
            #
            # if (freq2.size()==0):
            #     FreqSize2=0; FreqMean2=0; meanisi2=0
            #
            # if (freq2.size()==1):
            #     FreqSize2=1;FreqMean2=0;meanisi2=0
            #
            # if (freq2.size()>=2):
            #     isivec2.deriv(1) #isivec contains the interspike intervals//Vector class's deriv method using Euler method and "dx" parameter == 1 transforms recorded spike times to interspike intervals at machine language speeds.//
            #     for i in range(0,np.int(isivec2.size())):
            #         freq2.x[i] = 1000/isivec2.x[i] #instanteneous frequency
            #     FreqSize2=freq2.size()
            #     FreqMean2=freq2.mean()
            #     meanisi2=isivec2.mean()
            #     stdev2=9999 #to control if FreqMean1=0 then cannot calculate stdev and cvisi
            #     cvisi2=9999
            #     if (FreqMean2 > 0):
            #         stdev2=isivec2.stdev()
            #         cvisi2= stdev2/(isivec2.mean())
            #
            #
            #
            #               ###### Third time block######
            #
            # if (freq3.size()==0):
            #     FreqSize3=0; FreqMean3=0; meanisi3=0
            #
            # if (freq3.size()==1):
            #     FreqSize3=1;FreqMean3=0;meanisi3=0
            #
            # if (freq3.size()>=2):
            #     isivec3.deriv() #isivec contains the interspike intervals//Vector class's deriv method using Euler method and "dx" parameter == 1 transforms recorded spike times to interspike intervals at machine language speeds.//
            #     for i in range(0,np.int(isivec3.size())):
            #         freq3.x[i] = 1000/isivec3.x[i] #instanteneous frequency
            #     FreqSize3=freq3.size()
            #     FreqMean3=freq3.mean()
            #     meanisi3=isivec3.mean()
            #     stdev1=9999 #to control if FreqMean1=0 then cannot calculate stdev and cvisi
            #     cvisi1=9999
            #     if (FreqMean3 > 0):
            #         stdev3=isivec3.stdev()
            #         cvisi3= stdev3/(isivec3.mean())
            #
            #
            #
            #                ###### Fourth time block######
            #
            # if (freq4.size()==0):
            #     FreqSize4=0; FreqMean4=0; meanisi4=0
            #
            # if (freq4.size()==1):
            #     FreqSize4=1;FreqMean4=0;meanisi4=0
            #
            # if (freq4.size()>=2):
            #     isivec4.deriv() #isivec contains the interspike intervals//Vector class's deriv method using Euler method and "dx" parameter == 1 transforms recorded spike times to interspike intervals at machine language speeds.//
            #     for i in range(0,np.int(isivec4.size())):
            #         freq4.x[i] = 1000/isivec4.x[i] #instanteneous frequency
            #     FreqSize4=freq4.size()
            #     FreqMean4=freq4.mean()
            #     meanisi4=isivec4.mean()
            #
            #     stdev4=9999 #to control if FreqMean1=0 then cannot calculate stdev and cvisi
            #     cvisi4=9999
            #
            #     if (FreqMean4 > 0):
            #         stdev4=isivec4.stdev()
            #         cvisi4= stdev4/(isivec4.mean())



                               #########--------OFF-S-------#########
            # if (v1NoSpikeMean>-60 and v1NoSpikeMean<=-50):
            #     v1NoSpikeMean01=1
            #
            # else:
            #     v1NoSpikeMean01=0

            if (FreqMean1>=1 and FreqMean1<=28):
                FreqMean1_S=1

            else:
                FreqMean1_S=0

            # if (FreqMean2==0):
            #     FreqMean2_01=1
            #
            # else:
            #     FreqMean2_01=0 #no activity during hyperpolarization -0.2 nA
            #
            # if (FreqMean3>=60):
            #     FreqMean3_01=1
            # else:
            #     FreqMean3_01=0 #burst after hyperpolarization


            # if (FreqMean3>=2*FreqMean1):
            #      FreqMean3_01=1
            # else:
            #      FreqMean3_01=0} #burst after hyperpolarization


            AllCondSatOFF=0

            # if (v1NoSpikeMean01==1 and FreqMean1_S==1 and  FreqMean2_01==1 and FreqMean3_01==1):
            if (FreqMean1_S==1 ):

                AllCondSatOFF=1
                # f.write( "%g %g %g" %soma.gbar_nap %soma.gbar_lva %soma.ghdbar_hd)

                # f.write( "%g %g %g" %soma.gbar_nap %soma.gbar_lva %soma.ghdbar_hd)
                ghdbar_hd_syn_wt.append(soma.ghdbar_hd)
                gbar_lva_syn_wt.append(soma.gbar_lva)
                gbar_nap_syn_wt.append(soma.gbar_nap)


            else:
                m=0


            soma.ghdbar_hd=soma.ghdbar_hd+1e-6

            # print "elapsed_time = "  + str(time.time() - start_time)

        soma.gbar_lva=soma.gbar_lva+1e-4

    soma.gbar_nap=soma.gbar_nap*10




# In[7]:

ghdbar_hd_syn_wt=np.array(ghdbar_hd_syn_wt)
gbar_lva_syn_wt=np.array(gbar_lva_syn_wt)

wt_with_syn = go.Scatter(
    x = gbar_lva_syn_wt,
    y = ghdbar_hd_syn_wt,
    mode = 'markers',
    marker=dict(size=10,color = 'rgba(100, 150, 150)'),
    name='wt_with_syn'
           
)


# In[8]:

data = [no_syn, wt_with_syn]


# In[9]:

layout = pp.Layout(
    autosize=False,
    width=500,
    height=500,
    showlegend=True,
    xaxis=dict(
        title='gbar_lva[S/cm2]',
        
    ),
    yaxis=dict(
        title='gbar_hd[S/cm2]',
    )       
)

fig = pp.Figure(data = data, layout=layout)
pp.iplot(fig)


# In[10]:

__author__ = 'Susmita'

import sys
import copy

sys.path = ['/Applications/NEURON-7.4/nrn/lib/python'] + sys.path

import scipy.io
exc= scipy.io.loadmat('rd-OFF-exc-output/rd_OFF_exc_output.mat')
inh = scipy.io.loadmat('rd-OFF-inh-output/rd_OFF_inh_output.mat')

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
soma.gcabar_spike = 0.002
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



'''//Check  conditions with the presence of synaptic activity:

//2.spont activity  wt-ON [6, 9] Hz/wt-OFF: [1, 28]Hz  (First Block 0,500)'''




# f = open('outputt', 'r+') #opens the file for both reading and writing
# f.write( 'gbar_nap, gbar_lva,  ghdbar_hd ,  v1NoSpikeMean , FreqMean1 ,  FreqSize1 ,  meanisi1 ,  stdev1 ,  cvisi1 , FreqMean2 ,  FreqSize2 ,  meanisi2 ,  stdev2 ,  cvisi2 , FreqMean3 ,  FreqSize3 ,  meanisi3 ,  stdev3 ,  cvisi3 , v1NoSpikeMean01 , FreqMean1_T , FreqMean1_S , FreqMean2_01 ,  FreqMean3_01 ,  AllCondSatOFF' )


tsp = h.Vector()
vCopy = h.Vector()
ghdbar_hd_syn_rd =h.Vector()
gbar_lva_syn_rd = h.Vector()
gbar_nap_syn_rd=h.Vector()

# soma.ghdbar_hd = 4e-6 #S/cm2,OFF-S
# soma.gbar_lva = 10e-4  #S/cm2,
# soma.gbar_nap = 5e-8 #S/cm2

# stim = h.IClamp(soma(0))
#
# stim.amp = -0.2
# stim.dur = 500
# stim.delay = 600

d={} #list for keeping excitatory and inhibitory synaptic parameters

d["excsyn1"]= h.ExpSyn(0.5, sec=soma) # position=0.5
d["excsyn1"].tau = 5 #ms decay time constant:from Tian et al.1998
d["excsyn1"].e = 0 #mV reversal potential
d["excsyn1"].i = 0 #nA synaptic current


d["inhsyn1"] = h.ExpSyn(0.8, sec=soma)
d["inhsyn1"].tau = 10 #from Tian et al.1998
d["inhsyn1"].e = -70
d["inhsyn1"].i = 0





i = exc['centers'].size

for x in range(0,i):


    d["ppexc{0}".format(x)] = h.NetStim(0.5)
    # Creates a NetStim that will generate a stream of events that occur at times t0, t1, . . . ti, . . . such that the inter-event intervals are governed by the negative exponential distribution with mean interval equal to ISI.
    if (exc['freq'][0,x]==0):
        d["ppexc{0}".format(x)].interval = 1e100
        d["ppexc{0}".format(x)].number = 0
    else:
        d["ppexc{0}".format(x)].interval = (1.0/exc['freq'][0,x])*1000

    # The maximum number of spikes that will be generated in any simulation is "number".
    d["ppexc{0}".format(x)].number = 1e9
    # earliest possible time of synaptic activation
    d["ppexc{0}".format(x)].start = 0
    # Noise=1 means that 100% of the total number of spikes follow a negexp distribution
    d["ppexc{0}".format(x)].noise = 1

    d["ncppexc{0}".format(x)] = h.NetCon( d["ppexc{0}".format(x)], d["excsyn1"]) #connecting the poisson stimulus and the synapse

    d["ncppexc{0}".format(x)].weight[0] = -((exc['centers'][0,x])*1e-3)/(-70-0) # i = G * (v - e)  G = weight * exp(-t/tau);
    d["ncppexc{0}".format(x)].delay = 0 #g







j= inh['centers'].size

for x in range(0,j):

    d["ppinh{0}".format(x)] = h.NetStim(0.8)
    if (inh['freq'][0,x]==0):
        d["ppexc{0}".format(x)].interval = 1e1000
        d["ppinh{0}".format(x)].number = 0
    else:
        d["ppinh{0}".format(x)].interval = (1.0/inh['freq'][0,x])*1000

    d["ppinh{0}".format(x)].number = 1e9
    d["ppinh{0}".format(x)].start = 0
    d["ppinh{0}".format(x)].noise = 1
    d["ncppinh{0}".format(x)] = h.NetCon( d["ppinh{0}".format(x)], d["inhsyn1"])
    d["ncppinh{0}".format(x)].weight[0] =((inh['centers'][0,x])*1e-3)/(0+70)
    d["ncppinh{0}".format(x)].delay = 0








soma.gbar_nap=5e-8
for zz in range(0,1):
    soma.gbar_lva=2e-4 #2e-4

    for jj in range(0,17):#13 or 20

        soma.ghdbar_hd=2e-6
        for ii in range(0,15): #13 or 20

            #start_time = time.time()

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

            # h.v_init = -65
            # h.v_init = -65
            h.dt=0.025
            h.v_init =-65
            h.tstop = 5000
            h.init()
            h.run()
            sizetsp=tsp.size()

            StartTimeBlock1=0+100
            StartTimeBlock2=500+100
            StartTimeBlock3=1000+100
            StartTimeBlock4=1150+150#1150+100
            FinishTimeBlock4=2000+100



            # pylab.plot(t_vec, vCopy)
            # pyplot.show()



            for i in range(0,np.int(sizetsp)): # divided the tsps into diffent blocks
                if sizetsp == 0:
                    break;
                if (tsp.x[i]<StartTimeBlock2):#  if (tsp.x[i]>StartTimeBlock1 and tsp.x[i]<StartTimeBlock2)
                    tsp1.append(tsp.x[i])
                # if (tsp.x[i]>StartTimeBlock2 and tsp.x[i]<=StartTimeBlock3):
                #     tsp2.append(tsp.x[i])
                # if (tsp.x[i]>StartTimeBlock3 and tsp.x[i]<StartTimeBlock4):
                #     tsp3.append(tsp.x[i])
                # if (tsp.x[i]>StartTimeBlock4 and tsp.x[i]<FinishTimeBlock4):
                #     tsp4.append(tsp.x[i])
                i = i+1

            v1 = h.Vector()
            v1NoSpike = h.Vector()



            for k in range(0,np.int((StartTimeBlock2/h.dt)*1)):
                v1.append(vCopy.x[k]) # making the voltage vector for tsp1


            v1_slope = copy.copy(v1)
            v1_slope.deriv(1) #dx=1
            length_of_block = 2
            threshold=0.01 #unit will be 10 mv/ms

            # for k in range(0,np.int((v1_slope.size())-1)):
            #     if (v1_slope.x[k] < threshold):
                    # v1NoSpike.append(vCopy.x[k])/

            k = 0
            while (k < np.int((v1_slope.size()))):
                if (v1_slope.x[k] > threshold):
                    k=k+length_of_block
                else:
                    v1NoSpike.append(vCopy.x[k])
                    k += 1

            if (v1NoSpike.size() == 0):
                v1NoSpikeMean=0.0 # no NaN maybe?
            else:
                v1NoSpikeMean=v1NoSpike.mean() # calculating the resting voltage from block1



            isivec1 = copy.copy(tsp1)
            isivec2 =copy.copy(tsp2)
            isivec3 = copy.copy(tsp3)
            isivec4 = copy.copy(tsp4)

            freq1 = h.Vector(isivec1.size())
            freq2 = h.Vector(isivec2.size())
            freq3 = h.Vector(isivec3.size())
            freq4 = h.Vector(isivec4.size())

                 ###### First time block ######
            if (freq1.size()==0):
                FreqSize1=0; FreqMean1=0; meanisi1=0

            if (freq1.size()==1):
                FreqSize1=1;FreqMean1=0;meanisi1=0

            if (freq1.size()>=2):
               isivec1.deriv(1) #isivec contains the interspike intervals//Vector class's deriv method using Euler method and "dx" parameter == 1 transforms recorded spike times to interspike intervals at machine language speeds.//
               for i in range(0,np.int(isivec1.size())): # change it to np.int(freq1.size()-1)
                   freq1.x[i] = 1000.0/isivec1.x[i]#instanteneous frequency

               FreqSize1=freq1.size()
               FreqMean1=freq1.mean()
               meanisi1=isivec1.mean()
               stdev1=9999 #to control if FreqMean1=0 then cannot calculate stdev and cvisi
               cvisi1=9999
               if (FreqMean1 > 0):
                  stdev1=isivec1.stdev()
                  cvisi1= stdev1/(isivec1.mean())



            #
            #                   ###### Second time block######
            #
            # if (freq2.size()==0):
            #     FreqSize2=0; FreqMean2=0; meanisi2=0
            #
            # if (freq2.size()==1):
            #     FreqSize2=1;FreqMean2=0;meanisi2=0
            #
            # if (freq2.size()>=2):
            #     isivec2.deriv(1) #isivec contains the interspike intervals//Vector class's deriv method using Euler method and "dx" parameter == 1 transforms recorded spike times to interspike intervals at machine language speeds.//
            #     for i in range(0,np.int(isivec2.size())):
            #         freq2.x[i] = 1000/isivec2.x[i] #instanteneous frequency
            #     FreqSize2=freq2.size()
            #     FreqMean2=freq2.mean()
            #     meanisi2=isivec2.mean()
            #     stdev2=9999 #to control if FreqMean1=0 then cannot calculate stdev and cvisi
            #     cvisi2=9999
            #     if (FreqMean2 > 0):
            #         stdev2=isivec2.stdev()
            #         cvisi2= stdev2/(isivec2.mean())
            #
            #
            #
            #               ###### Third time block######
            #
            # if (freq3.size()==0):
            #     FreqSize3=0; FreqMean3=0; meanisi3=0
            #
            # if (freq3.size()==1):
            #     FreqSize3=1;FreqMean3=0;meanisi3=0
            #
            # if (freq3.size()>=2):
            #     isivec3.deriv() #isivec contains the interspike intervals//Vector class's deriv method using Euler method and "dx" parameter == 1 transforms recorded spike times to interspike intervals at machine language speeds.//
            #     for i in range(0,np.int(isivec3.size())):
            #         freq3.x[i] = 1000/isivec3.x[i] #instanteneous frequency
            #     FreqSize3=freq3.size()
            #     FreqMean3=freq3.mean()
            #     meanisi3=isivec3.mean()
            #     stdev1=9999 #to control if FreqMean1=0 then cannot calculate stdev and cvisi
            #     cvisi1=9999
            #     if (FreqMean3 > 0):
            #         stdev3=isivec3.stdev()
            #         cvisi3= stdev3/(isivec3.mean())
            #
            #
            #
            #                ###### Fourth time block######
            #
            # if (freq4.size()==0):
            #     FreqSize4=0; FreqMean4=0; meanisi4=0
            #
            # if (freq4.size()==1):
            #     FreqSize4=1;FreqMean4=0;meanisi4=0
            #
            # if (freq4.size()>=2):
            #     isivec4.deriv() #isivec contains the interspike intervals//Vector class's deriv method using Euler method and "dx" parameter == 1 transforms recorded spike times to interspike intervals at machine language speeds.//
            #     for i in range(0,np.int(isivec4.size())):
            #         freq4.x[i] = 1000/isivec4.x[i] #instanteneous frequency
            #     FreqSize4=freq4.size()
            #     FreqMean4=freq4.mean()
            #     meanisi4=isivec4.mean()
            #
            #     stdev4=9999 #to control if FreqMean1=0 then cannot calculate stdev and cvisi
            #     cvisi4=9999
            #
            #     if (FreqMean4 > 0):
            #         stdev4=isivec4.stdev()
            #         cvisi4= stdev4/(isivec4.mean())



                               #########--------OFF-S-------#########
            # if (v1NoSpikeMean>-60 and v1NoSpikeMean<=-50):
            #     v1NoSpikeMean01=1
            #
            # else:
            #     v1NoSpikeMean01=0

            if (FreqMean1>=3 and FreqMean1<=16):
                FreqMean1_S=1

            else:
                FreqMean1_S=0

            # if (FreqMean2==0):
            #     FreqMean2_01=1
            #
            # else:
            #     FreqMean2_01=0 #no activity during hyperpolarization -0.2 nA
            #
            # if (FreqMean3>=60):
            #     FreqMean3_01=1
            # else:
            #     FreqMean3_01=0 #burst after hyperpolarization


            # if (FreqMean3>=2*FreqMean1):
            #      FreqMean3_01=1
            # else:
            #      FreqMean3_01=0} #burst after hyperpolarization


            AllCondSatOFF=0

            # if (v1NoSpikeMean01==1 and FreqMean1_S==1 and  FreqMean2_01==1 and FreqMean3_01==1):
            if (FreqMean1_S==1 ):

                AllCondSatOFF=1
                # f.write( "%g %g %g" %soma.gbar_nap %soma.gbar_lva %soma.ghdbar_hd)

                # f.write( "%g %g %g" %soma.gbar_nap %soma.gbar_lva %soma.ghdbar_hd)
                ghdbar_hd_syn_rd.append(soma.ghdbar_hd)
                gbar_lva_syn_rd.append(soma.gbar_lva)
                gbar_nap_syn_rd.append(soma.gbar_nap)


            else:
                m=0


            soma.ghdbar_hd=soma.ghdbar_hd+1e-6

            # print "elapsed_time = "  + str(time.time() - start_time)

        soma.gbar_lva=soma.gbar_lva+1e-4

    soma.gbar_nap=soma.gbar_nap*10



# In[80]:

ghdbar_hd_syn_rd=np.array(ghdbar_hd_syn_rd)
gbar_lva_syn_rd=np.array(gbar_lva_syn_rd)

rd_with_syn = go.Scatter(
    x = gbar_lva_syn_rd,
    y = ghdbar_hd_syn_rd,
    mode = 'markers',
    marker=dict(size=10,color = 'rgba(200, 300, 0,100)'),
    name='rd_with_syn')


# In[81]:

data1 = [no_syn, rd_with_syn]


# In[82]:

data2 = [wt_with_syn, rd_with_syn]


# In[83]:

layout = pp.Layout(
    autosize=False,
    width=500,
    height=500,
    showlegend=True,
    xaxis=dict(
        title='gbar_lva[S/cm2]',
        
    ),
    yaxis=dict(
        title='gbar_hd[S/cm2]',
    )       
)

fig = pp.Figure(data = data1, layout=layout)
pp.iplot(fig)


# In[2]:

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
soma.gcabar_spike = 0.002
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
# soma.gbar_nap = 5e-8 #S/cm2



# soma.ghdbar_hd = 4e-6 #S/cm2,OFF-S
# soma.gbar_lva = 10e-4  #S/cm2,
# soma.gbar_nap = 5e-8 #S/cm2

'''//Check 4 conditions for
//1.vrest (on the First block 0,500)
//2.spont activity  ON 0 Hz/OFF-S: [34, 54] Hz/OFF-T: [9 29] Hz (First Block 0,500)
//3.no activity during 500 ms hyperpolarization -0.2 nA (Second Block 500,1000)
//4.At the termination of 500 ms stimulus of -0.2 nA (Third Block 1000,1150)
//subscript  1  corresponds to first block,  2  to the second block etc
// Better to give 100ms to stabilize before measuring Vrest. Therefore all blocks move to +100.'''



# f = open('outputt', 'r+') #opens the file for both reading and writing
# f.write( 'gbar_nap, gbar_lva,  ghdbar_hd ,  v1NoSpikeMean , FreqMean1 ,  FreqSize1 ,  meanisi1 ,  stdev1 ,  cvisi1 , FreqMean2 ,  FreqSize2 ,  meanisi2 ,  stdev2 ,  cvisi2 , FreqMean3 ,  FreqSize3 ,  meanisi3 ,  stdev3 ,  cvisi3 , v1NoSpikeMean01 , FreqMean1_T , FreqMean1_S , FreqMean2_01 ,  FreqMean3_01 ,  AllCondSatOFF' )





tsp = h.Vector()
vCopy = h.Vector()
ghdbar_hd_ON =h.Vector()
gbar_lva_ON = h.Vector()
gbar_nap_ON=h.Vector()



stim = h.IClamp(soma(0.5))

stim.amp = -0.050
stim.dur = 500
stim.delay = 600


soma.gbar_nap=5e-8
for zz in range(0,1):#(0,13)
    soma.gbar_lva=1

    # print 'zz=' + str(zz)

    for jj in range(0,16):#13 or 20

        # print 'jj=' + str(jj)

        soma.ghdbar_hd=1
        for ii in range(0,16): #2,13 or 20

            # start_time = time.time()

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

            h.dt=0.025
            h.v_init =-65
            h.tstop = 5000
            h.init()
            h.run()
            sizetsp=tsp.size()

            StartTimeBlock1=0+100
            StartTimeBlock2=500+100
            StartTimeBlock3=1000+100
            StartTimeBlock4=1150+150#1150+100
            FinishTimeBlock4=2000+100



            # pylab.plot(t_vec, vCopy)
            # pyplot.show()

            for i in range(0,np.int(sizetsp)): # divided the tsps into diffent blocks
                if sizetsp == 0:
                    break;
                if (tsp.x[i]<StartTimeBlock2):#  if (tsp.x[i]>StartTimeBlock1 and tsp.x[i]<StartTimeBlock2)
                    tsp1.append(tsp.x[i])
                if (tsp.x[i]>=StartTimeBlock2 and tsp.x[i]<=StartTimeBlock3):
                    tsp2.append(tsp.x[i])
                if (tsp.x[i]>=StartTimeBlock3 and tsp.x[i]<=StartTimeBlock4):
                    tsp3.append(tsp.x[i])
                if (tsp.x[i]>StartTimeBlock4 and tsp.x[i]<FinishTimeBlock4):
                    tsp4.append(tsp.x[i])
                i = i+1

            v1 = h.Vector()
            v1NoSpike = h.Vector()



            for k in range(0,np.int((StartTimeBlock2/h.dt)*1)):
                v1.append(vCopy.x[k]) # making the voltage vector for tsp1


            v1_slope = copy.copy(v1)
            v1_slope.deriv(1) #dx=1
            length_of_block = 2
            threshold=0.01 #unit will be 10 mv/s

            # for k in range(0,np.int((v1_slope.size())-1)):
            #     if (v1_slope.x[k] < threshold):
                    # v1NoSpike.append(vCopy.x[k])/

            k = 0
            while (k < np.int((v1_slope.size()))):
                if (v1_slope.x[k] > threshold):
                    k=k+length_of_block
                else:
                    v1NoSpike.append(vCopy.x[k])
                    k += 1

            if (v1NoSpike.size() == 0):
                v1NoSpikeMean=0.0 # no NaN maybe?
            else:
                v1NoSpikeMean=v1NoSpike.mean() # calculating the resting voltage from block1



            isivec1 = copy.copy(tsp1)
            isivec2 =copy.copy(tsp2)
            isivec3 = copy.copy(tsp3)
            isivec4 = copy.copy(tsp4)

            freq1 = h.Vector(isivec1.size())
            freq2 = h.Vector(isivec2.size())
            freq3 = h.Vector(isivec3.size())
            freq4 = h.Vector(isivec4.size())

                 ###### First time block ######
            if (freq1.size()==0):
                FreqSize1=0; FreqMean1=0; meanisi1=0

            if (freq1.size()==1):
                FreqSize1=1;FreqMean1=0;meanisi1=0

            if (freq1.size()>=2):
               isivec1.deriv(1) #isivec contains the interspike intervals//Vector class's deriv method using Euler method and "dx" parameter == 1 transforms recorded spike times to interspike intervals at machine language speeds.//
               for i in range(0,np.int(isivec1.size())): # change it to np.int(freq1.size()-1)
                   freq1.x[i] = 1000.0/isivec1.x[i]#instanteneous frequency

               FreqSize1=freq1.size()
               FreqMean1=freq1.mean()
               meanisi1=isivec1.mean()
               stdev1=9999 #to control if FreqMean1=0 then cannot calculate stdev and cvisi
               cvisi1=9999
               if (FreqMean1 > 0):
                  stdev1=isivec1.stdev()
                  cvisi1= stdev1/(isivec1.mean())




                              ###### Second time block######

            if (freq2.size()==0):
                FreqSize2=0; FreqMean2=0; meanisi2=0

            if (freq2.size()==1):
                FreqSize2=1;FreqMean2=0;meanisi2=0

            if (freq2.size()>=2):
                isivec2.deriv(1) #isivec contains the interspike intervals//Vector class's deriv method using Euler method and "dx" parameter == 1 transforms recorded spike times to interspike intervals at machine language speeds.//
                for i in range(0,np.int(isivec2.size())):
                    freq2.x[i] = 1000.0/isivec2.x[i] #instanteneous frequency
                FreqSize2=freq2.size()
                FreqMean2=freq2.mean()
                meanisi2=isivec2.mean()
                stdev2=9999 #to control if FreqMean1=0 then cannot calculate stdev and cvisi
                cvisi2=9999
                if (FreqMean2 > 0):
                    stdev2=isivec2.stdev()
                    cvisi2= stdev2/(isivec2.mean())



                          ###### Third time block######

            if (freq3.size()==0):
                FreqSize3=0; FreqMean3=0; meanisi3=0

            if (freq3.size()==1):
                FreqSize3=1;FreqMean3=0;meanisi3=0

            if (freq3.size()>=2):
                isivec3.deriv(1) #isivec contains the interspike intervals//Vector class's deriv method using Euler method and "dx" parameter == 1 transforms recorded spike times to interspike intervals at machine language speeds.//
                for i in range(0,np.int(isivec3.size())):
                    freq3.x[i] = 1000/isivec3.x[i] #instanteneous frequency
                FreqSize3=freq3.size()
                FreqMean3=freq3.mean()
                meanisi3=isivec3.mean()
                stdev1=9999 #to control if FreqMean1=0 then cannot calculate stdev and cvisi
                cvisi1=9999
                if (FreqMean3 > 0):
                    stdev3=isivec3.stdev()
                    cvisi3= stdev3/(isivec3.mean())



                           ###### Fourth time block######

            if (freq4.size()==0):
                FreqSize4=0; FreqMean4=0; meanisi4=0

            if (freq4.size()==1):
                FreqSize4=1;FreqMean4=0;meanisi4=0

            if (freq4.size()>=2):
                isivec4.deriv() #isivec contains the interspike intervals//Vector class's deriv method using Euler method and "dx" parameter == 1 transforms recorded spike times to interspike intervals at machine language speeds.//
                for i in range(0,np.int(isivec4.size())):
                    freq4.x[i] = 1000/isivec4.x[i] #instanteneous frequency
                FreqSize4=freq4.size()
                FreqMean4=freq4.mean()
                meanisi4=isivec4.mean()

                stdev4=9999 #to control if FreqMean1=0 then cannot calculate stdev and cvisi
                cvisi4=9999

                if (FreqMean4 > 0):
                    stdev4=isivec4.stdev()
                    cvisi4= stdev4/(isivec4.mean())



                               #########--------OFF-S-------#########
            if (v1NoSpikeMean>-70 and v1NoSpikeMean<=-60):
                v1NoSpikeMean01=1

            else:
                v1NoSpikeMean01=0

            if (FreqMean1==0): #change the S values 34-54
                FreqMean1_S=1

            else:
                FreqMean1_S=0

            if (FreqMean2==0):
                FreqMean2_01=1

            else:
                FreqMean2_01=0 #no activity during hyperpolarization -0.2 nA

            if (FreqMean3==0):#60
                FreqMean3_01=1
            else:
                FreqMean3_01=0 #burst after hyperpolarization


            # if (FreqMean3>=2*FreqMean1):
            #      FreqMean3_01=1
            # else:
            #      FreqMean3_01=0} #burst after hyperpolarization


            AllCondSatON=0

            if (v1NoSpikeMean01==1 and FreqMean1_S==1 and  FreqMean2_01==1 and FreqMean3_01==1):
                AllCondSatON=1
                # f.write( "%g %g %g" %soma.gbar_nap %soma.gbar_lva %soma.ghdbar_hd)
                ghdbar_hd_ON.append(soma.ghdbar_hd)
                gbar_lva_ON.append(soma.gbar_lva)
                gbar_nap_ON.append(soma.gbar_nap)


            else:
                m=0


            soma.ghdbar_hd=soma.ghdbar_hd*1e-1 #1e-6


            #print "elapsed_time = "  + str(time.time() - start_time)

        soma.gbar_lva=soma.gbar_lva*1e-1 #2e-4

    # soma.gbar_nap=soma.gbar_nap*1e-1




'''import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(ghdbar_hd, gbar_lva, gbar_nap)
ax.scatter(ghdbar_hd_syn, gbar_lva_syn, gbar_nap_syn,c='g')

ax.set_xlabel('ghdbar_hd')
ax.set_ylabel('gbar_lva')
ax.set_zlabel('gbar_nap')

ax.plot_wireframe(ghdbar_hd, gbar_lva, gbar_nap)


ax.plot_trisurf(ghdbar_hd, gbar_lva, gbar_nap)

ax.plot_trisurf(ghdbar_hd_syn, gbar_lva_syn, gbar_nap_syn)

import numpy
import numpy.random as nprnd
import matplotlib.pyplot as plt

plt.axis([1e-4,16e-4,1e-6,18e-6])
plt.plot(gbar_lva,ghdbar_hd,linestyle='', marker='o',markersize=15,markerfacecolor='none')

plt.plot(gbar_lva, ghdbar_hd,linestyle='', marker='^',markersize=10,markerfacecolor='blue')
plt.xlabel('ghdbar_lva')
plt.ylabel('ghdbar_hd')
'''

# import matplotlib.pyplot as plt
#
# plt.axis([1e-4,16e-4,1e-6,18e-6])
# e=15,markerfacecolor='none')plt.plot(gbar_lva,ghdbar_hd,linestyle='', marker='o',markersiz
# # plt.plot(gbar_lva_syn_rd, ghdbar_hd_syn_rd,linestyle='', marker='^',markersize=10,markerfacecolor='blue')
# plt.show()


# In[3]:

ghdbar_hd_ON=np.array(ghdbar_hd_ON)
gbar_lva_ON=np.array(gbar_lva_ON)

ON_no_syn = go.Scatter(
    x = ghdbar_hd_ON,
    y = gbar_lva_ON,
    mode = 'markers',
    marker=dict(size=10,color = 'rgba(200, 300, 0,100)'),
    name='ON_no_syn')


# In[4]:

data_ON_1 = [ON_no_syn]


# In[5]:

layout = pp.Layout(
    autosize=Faghdbar_hd_ON=np.array(ghdbar_hd_ON)
gbar_lva_ON=np.array(gbar_lva_ON)

ON_no_syn = go.Scatter(
    x = ghdbar_hd_ON,
    y = gbar_lva_ON,
    mode = 'markers',
    marker=dict(size=10,color = 'rgba(200, 300, 0,100)'),
    name='ON_no_syn')lse,
    width=500,
    height=500,
    showlegend=True,
    xaxis=dict(
        title='gbar_lva[S/cm2]',
        
    ),
    yaxis=dict(
        title='gbar_hd[S/cm2]',
    )       
)

fig = pp.Figure(data = data_ON_1, layout=layout)
pp.iplot(fig)


# In[ ]:

__author__ = 'Susmita'

import sys
import copy

sys.path = ['/Applications/NEURON-7.4/nrn/lib/python'] + sys.path

import scipy.io
exc= scipy.io.loadmat('wt-ON-exc-output/wt_ON_exc_output.mat')
inh = scipy.io.loadmat('wt-ON-inh-output/wt_ON_inh_output.mat')

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
soma.gcabar_spike = 0.002
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

# soma.ghdbar_hd = 4e-6 #S/cm2,OFF-S
# soma.gbar_lva = 10e-4  #S/cm2,
# soma.gbar_nap = 5e-8 #S/cm2

'''//Check  conditions with the presence of synaptic activity:

//2.spont activity  wt-ON [6, 9] Hz/wt-OFF: [1, 28]Hz  (First Block 0,500)'''




# f = open('outputt', 'r+') #opens the file for both reading and writing
# f.write( 'gbar_nap, gbar_lva,  ghdbar_hd ,  v1NoSpikeMean , FreqMean1 ,  FreqSize1 ,  meanisi1 ,  stdev1 ,  cvisi1 , FreqMean2 ,  FreqSize2 ,  meanisi2 ,  stdev2 ,  cvisi2 , FreqMean3 ,  FreqSize3 ,  meanisi3 ,  stdev3 ,  cvisi3 , v1NoSpikeMean01 , FreqMean1_T , FreqMean1_S , FreqMean2_01 ,  FreqMean3_01 ,  AllCondSatOFF' )


tsp = h.Vector()
vCopy = h.Vector()
ghdbar_hd_wt_ON =h.Vector()
gbar_lva_wt_ON = h.Vector()
gbar_nap_wt_ON=h.Vector()



# stim = h.IClamp(soma(0))
#
# stim.amp = -0.2
# stim.dur = 500
# stim.delay = 600

d={} #list for keeping excitatory and inhibitory synaptic parameters

d["excsyn1"]= h.ExpSyn(0.5, sec=soma) # position=0.5
d["excsyn1"].tau = 5 #ms decay time constant:from Tian et al.1998
d["excsyn1"].e = 0 #mV reversal potential
d["excsyn1"].i = 0 #nA synaptic current


d["inhsyn1"] = h.ExpSyn(0.8, sec=soma)
d["inhsyn1"].tau = 10 #from Tian et al.1998
d["inhsyn1"].e = -70
d["inhsyn1"].i = 0





i = exc['centers'].size

for x in range(0,i):


    d["ppexc{0}".format(x)] = h.NetStim(0.5)
    # Creates a NetStim that will generate a stream of events that occur at times t0, t1, . . . ti, . . . such that the inter-event intervals are governed by the negative exponential distribution with mean interval equal to ISI.
    if (exc['freq'][0,x]==0):
        d["ppexc{0}".format(x)].interval = 1e100
        d["ppexc{0}".format(x)].number = 0
    else:
        d["ppexc{0}".format(x)].interval = (1.0/exc['freq'][0,x])*1000

    # The maximum number of spikes that will be generated in any simulation is "number".
    d["ppexc{0}".format(x)].number = 1e9
    # earliest possible time of synaptic activation
    d["ppexc{0}".format(x)].start = 0
    # Noise=1 means that 100% of the total number of spikes follow a negexp distribution
    d["ppexc{0}".format(x)].noise = 1

    d["ncppexc{0}".format(x)] = h.NetCon( d["ppexc{0}".format(x)], d["excsyn1"]) #connecting the poisson stimulus and the synapse

    d["ncppexc{0}".format(x)].weight[0] = -((exc['centers'][0,x])*1e-3)/(-70-0) # i = G * (v - e)  G = weight * exp(-t/tau);
    d["ncppexc{0}".format(x)].delay = 0 #g







j= inh['centers'].size

for x in range(0,j):

    d["ppinh{0}".format(x)] = h.NetStim(0.8)
    if (inh['freq'][0,x]==0):
        d["ppexc{0}".format(x)].interval = 1e1000
        d["ppinh{0}".format(x)].number = 0
    else:
        d["ppinh{0}".format(x)].interval = (1.0/inh['freq'][0,x])*1000

    d["ppinh{0}".format(x)].number = 1e9
    d["ppinh{0}".format(x)].start = 0
    d["ppinh{0}".format(x)].noise = 1
    d["ncppinh{0}".format(x)] = h.NetCon( d["ppinh{0}".format(x)], d["inhsyn1"])
    d["ncppinh{0}".format(x)].weight[0] =((inh['centers'][0,x])*1e-3)/(0+70)
    d["ncppinh{0}".format(x)].delay = 0







soma.gbar_nap=1
for zz in range(0,16):#(0,13)
    soma.gbar_lva=1

    # print 'zz=' + str(zz)

    for jj in range(0,16):#13 or 20

        # print 'jj=' + str(jj)

        soma.ghdbar_hd=1
        for ii in range(0,16):
            #start_time = time.time()

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

            # h.v_init = -65
            h.dt=0.025
            h.v_init =-65
            h.tstop = 5000
            h.init()
            h.run()
            sizetsp=tsp.size()

            StartTimeBlock1=0+100
            StartTimeBlock2=500+100
            StartTimeBlock3=1000+100
            StartTimeBlock4=1150+150#1150+100
            FinishTimeBlock4=2000+100



            # pylab.plot(t_vec, vCopy)
            # pyplot.show()



            for i in range(0,np.int(sizetsp)): # divided the tsps into diffent blocks
                if sizetsp == 0:
                    break;
                if (tsp.x[i]<StartTimeBlock2):#  if (tsp.x[i]>StartTimeBlock1 and tsp.x[i]<StartTimeBlock2)
                    tsp1.append(tsp.x[i])
                # if (tsp.x[i]>StartTimeBlock2 and tsp.x[i]<=StartTimeBlock3):
                #     tsp2.append(tsp.x[i])
                # if (tsp.x[i]>StartTimeBlock3 and tsp.x[i]<StartTimeBlock4):
                #     tsp3.append(tsp.x[i])
                # if (tsp.x[i]>StartTimeBlock4 and tsp.x[i]<FinishTimeBlock4):
                #     tsp4.append(tsp.x[i])
                i = i+1

            v1 = h.Vector()
            v1NoSpike = h.Vector()



            for k in range(0,np.int((StartTimeBlock2/h.dt)*1)):
                v1.append(vCopy.x[k]) # making the voltage vector for tsp1


            v1_slope = copy.copy(v1)
            v1_slope.deriv(1) #dx=1
            length_of_block = 2
            threshold=0.01 #unit will be 10 mv/ms

            # for k in range(0,np.int((v1_slope.size())-1)):
            #     if (v1_slope.x[k] < threshold):
                    # v1NoSpike.append(vCopy.x[k])/

            k = 0
            while (k < np.int((v1_slope.size()))):
                if (v1_slope.x[k] > threshold):
                    k=k+length_of_block
                else:
                    v1NoSpike.append(vCopy.x[k])
                    k += 1

            if (v1NoSpike.size() == 0):
                v1NoSpikeMean=0.0 # no NaN maybe?
            else:
                v1NoSpikeMean=v1NoSpike.mean() # calculating the resting voltage from block1



            isivec1 = copy.copy(tsp1)
            isivec2 =copy.copy(tsp2)
            isivec3 = copy.copy(tsp3)
            isivec4 = copy.copy(tsp4)

            freq1 = h.Vector(isivec1.size())
            freq2 = h.Vector(isivec2.size())
            freq3 = h.Vector(isivec3.size())
            freq4 = h.Vector(isivec4.size())

                 ###### First time block ######
            if (freq1.size()==0):
                FreqSize1=0; FreqMean1=0; meanisi1=0

            if (freq1.size()==1):
                FreqSize1=1;FreqMean1=0;meanisi1=0

            if (freq1.size()>=2):
               isivec1.deriv(1) #isivec contains the interspike intervals//Vector class's deriv method using Euler method and "dx" parameter == 1 transforms recorded spike times to interspike intervals at machine language speeds.//
               for i in range(0,np.int(isivec1.size())): # change it to np.int(freq1.size()-1)
                   freq1.x[i] = 1000.0/isivec1.x[i]#instanteneous frequency

               FreqSize1=freq1.size()
               FreqMean1=freq1.mean()
               meanisi1=isivec1.mean()
               stdev1=9999 #to control if FreqMean1=0 then cannot calculate stdev and cvisi
               cvisi1=9999
               if (FreqMean1 > 0):
                  stdev1=isivec1.stdev()
                  cvisi1= stdev1/(isivec1.mean())



            #
            #                   ###### Second time block######
            #
            # if (freq2.size()==0):
            #     FreqSize2=0; FreqMean2=0; meanisi2=0
            #
            # if (freq2.size()==1):
            #     FreqSize2=1;FreqMean2=0;meanisi2=0
            #
            # if (freq2.size()>=2):
            #     isivec2.deriv(1) #isivec contains the interspike intervals//Vector class's deriv method using Euler method and "dx" parameter == 1 transforms recorded spike times to interspike intervals at machine language speeds.//
            #     for i in range(0,np.int(isivec2.size())):
            #         freq2.x[i] = 1000/isivec2.x[i] #instanteneous frequency
            #     FreqSize2=freq2.size()
            #     FreqMean2=freq2.mean()
            #     meanisi2=isivec2.mean()
            #     stdev2=9999 #to control if FreqMean1=0 then cannot calculate stdev and cvisi
            #     cvisi2=9999
            #     if (FreqMean2 > 0):
            #         stdev2=isivec2.stdev()
            #         cvisi2= stdev2/(isivec2.mean())
            #
            #
            #
            #               ###### Third time block######
            #
            # if (freq3.size()==0):
            #     FreqSize3=0; FreqMean3=0; meanisi3=0
            #
            # if (freq3.size()==1):
            #     FreqSize3=1;FreqMean3=0;meanisi3=0
            #
            # if (freq3.size()>=2):
            #     isivec3.deriv() #isivec contains the interspike intervals//Vector class's deriv method using Euler method and "dx" parameter == 1 transforms recorded spike times to interspike intervals at machine language speeds.//
            #     for i in range(0,np.int(isivec3.size())):
            #         freq3.x[i] = 1000/isivec3.x[i] #instanteneous frequency
            #     FreqSize3=freq3.size()
            #     FreqMean3=freq3.mean()
            #     meanisi3=isivec3.mean()
            #     stdev1=9999 #to control if FreqMean1=0 then cannot calculate stdev and cvisi
            #     cvisi1=9999
            #     if (FreqMean3 > 0):
            #         stdev3=isivec3.stdev()
            #         cvisi3= stdev3/(isivec3.mean())
            #
            #
            #
            #                ###### Fourth time block######
            #
            # if (freq4.size()==0):
            #     FreqSize4=0; FreqMean4=0; meanisi4=0
            #
            # if (freq4.size()==1):
            #     FreqSize4=1;FreqMean4=0;meanisi4=0
            #
            # if (freq4.size()>=2):
            #     isivec4.deriv() #isivec contains the interspike intervals//Vector class's deriv method using Euler method and "dx" parameter == 1 transforms recorded spike times to interspike intervals at machine language speeds.//
            #     for i in range(0,np.int(isivec4.size())):
            #         freq4.x[i] = 1000/isivec4.x[i] #instanteneous frequency
            #     FreqSize4=freq4.size()
            #     FreqMean4=freq4.mean()
            #     meanisi4=isivec4.mean()
            #
            #     stdev4=9999 #to control if FreqMean1=0 then cannot calculate stdev and cvisi
            #     cvisi4=9999
            #
            #     if (FreqMean4 > 0):
            #         stdev4=isivec4.stdev()
            #         cvisi4= stdev4/(isivec4.mean())



                               #########--------OFF-S-------#########
            # if (v1NoSpikeMean>-60 and v1NoSpikeMean<=-50):
            #     v1NoSpikeMean01=1
            #
            # else:
            #     v1NoSpikeMean01=0

            if (FreqMean1>=6 and FreqMean1<=10):
                FreqMean1_S=1

            else:
                FreqMean1_S=0

            # if (FreqMean2==0):
            #     FreqMean2_01=1
            #
            # else:
            #     FreqMean2_01=0 #no activity during hyperpolarization -0.2 nA
            #
            # if (FreqMean3>=60):
            #     FreqMean3_01=1
            # else:
            #     FreqMean3_01=0 #burst after hyperpolarization


            # if (FreqMean3>=2*FreqMean1):
            #      FreqMean3_01=1
            # else:
            #      FreqMean3_01=0} #burst after hyperpolarization


            AllCondSatON=0

            # if (v1NoSpikeMean01==1 and FreqMean1_S==1 and  FreqMean2_01==1 and FreqMean3_01==1):
            if (FreqMean1_S==1 ):

                AllCondSatON=1
                # f.write( "%g %g %g" %soma.gbar_nap %soma.gbar_lva %soma.ghdbar_hd)

                # f.write( "%g %g %g" %soma.gbar_nap %soma.gbar_lva %soma.ghdbar_hd)
                ghdbar_hd_wt_ON.append(soma.ghdbar_hd)
                gbar_lva_wt_ON.append(soma.gbar_lva)
                gbar_nap_wt_ON.append(soma.gbar_nap)


            else:
                m=0


            soma.ghdbar_hd=soma.ghdbar_hd*1e-1

            # print "elapsed_time = "  + str(time.time() - start_time)

        soma.gbar_lva=soma.gbar_lva*1e-1

    soma.gbar_nap=soma.gbar_nap*1e-1



# In[9]:

ghdbar_hd_wt_ON=np.array(ghdbar_hd_wt_ON)
gbar_lva_wt_ON=np.array(gbar_lva_wt_ON)

wt_ON_with_syn = go.Scatter(
    x = ghdbar_hd_wt_ON,
    y = gbar_lva_wt_ON,
    mode = 'markers',
    marker=dict(size=10,color = 'rgba(200, 300, 0,100)'),
    name='wt_ON_with_syn')


# In[10]:

data_ON_2 = [wt_ON_with_syn]


# In[11]:

layout = pp.Layout(
    autosize=False,
    width=500,
    height=500,
    showlegend=True,
    xaxis=dict(
        title='gbar_lva[S/cm2]',
        
    ),
    yaxis=dict(
        title='gbar_hd[S/cm2]',
    )       
)

fig = pp.Figure(data = data_ON_2, layout=layout)
pp.iplot(fig)


# In[3]:

__author__ = 'Susmita'

import sys
import scipy.io
exc= scipy.io.loadmat('wt-OFF-exc-output/wt_OFF_exc_output.mat')
inh = scipy.io.loadmat('wt-OFF-inh-output/wt_OFF_inh_output.mat')
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
soma.gcabar_spike = 0.002
soma.gkcbar_spike = 0.00005



h.celsius = 24
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

soma.ghdbar_hd = 4e-6 #S/cm2,OFF-S
soma.gbar_lva = 10e-4 #4e-4 #S/cm2,
soma.gbar_nap = 5e-8 #S/cm2


# stim = h.IClamp(soma(0.5))
#
# stim.amp = 0.4
# stim.dur = 1000




d={} #list for keeping excitatory and inhibitory synaptic parameters

d["excsyn1"]= h.Exp2Syn(0.5, sec=soma) # position=0.5
d["excsyn1"].tau1 = 5 #ms decay time constant
d["excsyn1"].tau2 = 10 #ms decay time constant

d["excsyn1"].e = 0 #mV reversal potential
d["excsyn1"].i = 0 #nA synaptic current


d["inhsyn1"] = h.ExpSyn(0.5, sec=soma)
d["inhsyn1"].tau = 1
d["inhsyn1"].e = -70
d["inhsyn1"].i = 0





i = exc['centers'].size

for x in range(0,i):


    d["ppexc{0}".format(x)] = h.NetStim(0.5)
    # Creates a NetStim that will generate a stream of events that occur at times t0, t1, . . . ti, . . . such that the inter-event intervals are governed by the negative exponential distribution with mean interval equal to ISI.
    if (exc['freq'][0,x]==0):
        d["ppexc{0}".format(x)].interval = 1e100
        d["ppexc{0}".format(x)].number = 0
    else:
        d["ppexc{0}".format(x)].interval = (1.0/exc['freq'][0,x])*1000

    # The maximum number of spikes that will be generated in any simulation is "number".
    d["ppexc{0}".format(x)].number = 1e9
    # earliest possible time of synaptic activation
    d["ppexc{0}".format(x)].start = 0
    # Noise=1 means that 100% of the total number of spikes follow a negexp distribution
    d["ppexc{0}".format(x)].noise = 1

    d["ncppexc{0}".format(x)] = h.NetCon( d["ppexc{0}".format(x)], d["excsyn1"]) #connecting the poisson stimulus and the synapse

    d["ncppexc{0}".format(x)].weight[0] = (-(exc['centers'][0,x])*1e-3)/(-70-0) # i = G * (v - e)  G = weight * exp(-t/tau);
    d["ncppexc{0}".format(x)].delay = 0 #g







j= inh['centers'].size

for x in range(0,j):

    d["ppinh{0}".format(x)] = h.NetStim(0.5)
    if (inh['freq'][0,x]==0):
        d["ppinh{0}".format(x)].interval = 1e100
        d["ppinh{0}".format(x)].number = 0
    else:
        d["ppinh{0}".format(x)].interval = (1.0/inh['freq'][0,x])*1000

    d["ppinh{0}".format(x)].number = 1e9
    d["ppinh{0}".format(x)].start = 0
    d["ppinh{0}".format(x)].noise = 1
    d["ncppinh{0}".format(x)] = h.NetCon( d["ppinh{0}".format(x)], d["inhsyn1"])
    d["ncppinh{0}".format(x)].weight[0] =((inh['centers'][0,x])*1e-3)/(0+70)
    d["ncppinh{0}".format(x)].delay = 0




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


h.tstop = 5000 #ms
h.run()
# pyplot.figure(figsize=(8,4)) # Default figsize is (8,6)


pylab.subplot(3,1,1)
pylab.plot(t_vec, v_vec)
# pyplot.show()
# pylab.plot(t_vec, v_vec)
# pyplot.show()

pylab.subplot(3,1,2)
pylab.plot(t_vec, vecexc['i_excsyn']) #div(5000)) # divided by membrane resistance (5,000 to 100,000 o/cm2), values obtained with intracellular sharp electrodes and wholecell recordings
pylab.subplot(3,1,3)
pylab.plot(t_vec, vecinh['i_inhsyn'])#.div(5000))
pyplot.show()

# pyplot.plot(t_vec, v_vec)
# pyplot.xlabel('time (ms)')
# pyplot.ylabel('mV')


# In[4]:

import plotly_plotting as pp
import plotly.plotly as py
import plotly.graph_objs as go
syn_wt_OFF=np.array(vecexc['i_excsyn'])
time_wt_OFF=np.array(t_vec)

wt_with_syn = go.Scatter(
    x = time_wt_OFF/1000,
    y = syn_wt_OFF,
    mode = 'line',
    name='wt_with_syn'
           
)


# In[5]:

data = [wt_with_syn]   


# In[6]:

import plotly.plotly as py
layout = go.Layout(
    autosize=False,
    width=500,
    height=500,
    xaxis=dict(
        title='time(s)'
        
        ),
       
    yaxis=dict(
        title='Exc current(nA)'
        
        ))


# In[7]:

fig = pp.Figure(data = data, layout=layout)


# In[8]:

pp.iplot(fig)


# In[9]:

__author__ = 'Susmita'

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

path = 'wt-OFF-exc-output/output37.txt'
files=glob.glob(path)

i=1

for file in files:
    f = open(file, 'r')
    lines=f.readlines()

    time =[]
    current = []
    for x in lines:
        time.append(x.split()[0])
        current.append(x.split()[1])

    f.close()

    current1 = np.asarray(current,dtype = 'float64')
    time1 = np.asarray(time,dtype = 'float64')
    plt.plot(time1,current1)
    plt.show()


# In[10]:

import plotly_plotting as pp
import plotly.plotly as py
import plotly.graph_objs as go
syn_wt_OFF=np.array(current1)
time_wt_OFF=np.array(time1)

wt_with_syn_experiment = go.Scatter(
    x = time_wt_OFF,
    y = syn_wt_OFF,
    mode = 'line',
    name='wt_with_syn_experiment'
           
)


# In[11]:

data = [wt_with_syn_experiment]


# In[12]:

import plotly.plotly as py
layout = go.Layout(
    xaxis=dict(
        title='time(s)'
        
        ),
       
    yaxis=dict(
        title='Exc current_experimental(nA)'
        
        ))
fig = pp.Figure(data = data, layout=layout)
pp.iplot(fig)


# In[ ]:


