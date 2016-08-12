__author__ = 'Susmita' #OFF-wt_syn

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
import math



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




'''//Check  conditions with the presence of synaptic activity:

//2.spont activity  wt-ON [6, 9] Hz/wt-OFF: [1, 28]Hz  (First Block 0,500)'''




# f = open('outputt', 'r+') #opens the file for both reading and writing
# f.write( 'gbar_nap, gbar_lva,  ghdbar_hd ,  v1NoSpikeMean , FreqMean1 ,  FreqSize1 ,  meanisi1 ,  stdev1 ,  cvisi1 , FreqMean2 ,  FreqSize2 ,  meanisi2 ,  stdev2 ,  cvisi2 , FreqMean3 ,  FreqSize3 ,  meanisi3 ,  stdev3 ,  cvisi3 , v1NoSpikeMean01 , FreqMean1_T , FreqMean1_S , FreqMean2_01 ,  FreqMean3_01 ,  AllCondSatOFF' )


tsp = h.Vector()
vCopy = h.Vector()
ghdbar_hd_syn_wt_ON =h.Vector()
gbar_lva_syn_wt_ON = h.Vector()
gbar_nap_syn_wt_ON=h.Vector()



# stim = h.IClamp(soma(0))
#
# stim.amp = -0.2
# stim.dur = 500
# stim.delay = 600

d={} #list for keeping excitatory and inhibitory synaptic parameters

d["excsyn1"]= h.Exp2Syn(0.5, sec=soma) # position=0.5
d["excsyn1"].tau1 = 1 #ms decay time constant
d["excsyn1"].tau2 = 6 #ms decay time constant

d["excsyn1"].e = 0 #mV reversal potential
d["excsyn1"].i = 0 #nA synaptic current


d["inhsyn1"] = h.Exp2Syn(0.5, sec=soma)
d["inhsyn1"].tau1 = 1
d["inhsyn1"].tau2 = 63
d["inhsyn1"].e = -70
d["inhsyn1"].i = 0





i = exc['centers'].size

for x in range(0,i):


    d["ppexc{0}".format(x)] = h.NetStim(0.5)
    # Creates a NetStim that will generate a stream of events that occur at times t0, t1, . . . ti, . . . such that the inter-event intervals are governed by the negative exponential distribution with mean interval equal to ISI.
    if (exc['freq'][0,x]==0):
        d["ppexc{0}".format(x)].interval = 1e1000
        d["ppexc{0}".format(x)].number = 0
    else:
        d["ppexc{0}".format(x)].interval = (1.0/exc['freq'][0,x])*1000

    d["ppexc{0}".format(x)].seed(10)

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
        d["ppinh{0}".format(x)].interval = 1e1000
        d["ppinh{0}".format(x)].number = 0
    else:
        d["ppinh{0}".format(x)].interval = (1.0/inh['freq'][0,x])*1000

    d["ppinh{0}".format(x)].seed(10)
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



# v_vec = h.Vector()             # Membrane potential vector
# t_vec = h.Vector()             # Time stamp vector
# v_vec.record(soma(0.5)._ref_v) # References to variables are available as _ref_range variable.
# t_vec.record(h._ref_t)







soma.gbar_nap=5e-8
for zz in range(0,1):
    soma.gbar_lva=1e-3   #0 #2e-4


    for jj in range(0,10):#28

        soma.ghdbar_hd=1e-3  #0.000118

        for ii in range(0,25): #35

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

            # h.v_init = -55
            h.dt=0.025
            h.v_init =-53
            h.tstop = 50000
            h.init()
            h.run()
            sizetsp=tsp.size()

            StartTimeBlock1=0+100
            StartTimeBlock2=50000
            # StartTimeBlock3=1000+100
            # StartTimeBlock4=1150+150#1150+100
            # FinishTimeBlock4=2000+100


            for i in range(0,np.int(sizetsp)): # divided the tsps into diffent blocks
                if sizetsp == 0:
                    break
                if (tsp.x[i]>StartTimeBlock1 and tsp.x[i]<StartTimeBlock2):#  if (tsp.x[i]>StartTimeBlock1 and tsp.x[i]<StartTimeBlock2)
                    tsp1.append(tsp.x[i])
                # if (tsp.x[i]>StartTimeBlock2 and tsp.x[i]<=StartTimeBlock3):
                #     tsp2.append(tsp.x[i])
                # if (tsp.x[i]>StartTimeBlock3 and tsp.x[i]<StartTimeBlock4):
                #     tsp3.append(tsp.x[i])
                # if (tsp.x[i]>StartTimeBlock4 and tsp.x[i]<FinishTimeBlock4):
                #     tsp4.append(tsp.x[i])
                # i = i+1

            v1 = h.Vector()
            v1NoSpike = h.Vector()



            for k in range(4000,np.int((StartTimeBlock2/h.dt)*1)):
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
                v1NoSpikeMean=v1NoSpike.mean() #calculating the resting voltage from block1



            isivec1 = copy.copy(tsp1)
            # isivec2 =copy.copy(tsp2)
            # isivec3 = copy.copy(tsp3)
            # isivec4 = copy.copy(tsp4)

            freq1 = h.Vector(isivec1.size())
            # freq2 = h.Vector(isivec2.size())
            # freq3 = h.Vector(isivec3.size())
            # freq4 = h.Vector(isivec4.size())

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

                #spike duration and amplitude calculation







                               #########--------OFF-S-------#########

            if (v1NoSpikeMean>=-58 and v1NoSpikeMean<=-50):
                v1NoSpikeMean01=1

            else:
                v1NoSpikeMean01=0


            if (FreqMean1>=5 and FreqMean1<=10):
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
            if (FreqMean1_S==1 and v1NoSpikeMean01==1):

                AllCondSatON=1
                # f.write( "%g %g %g" %soma.gbar_nap %soma.gbar_lva %soma.ghdbar_hd)

                # f.write( "%g %g %g" %soma.gbar_nap %soma.gbar_lva %soma.ghdbar_hd)
                ghdbar_hd_syn_wt_ON.append(soma.ghdbar_hd)
                gbar_lva_syn_wt_ON.append(soma.gbar_lva)
                gbar_nap_syn_wt_ON.append(soma.gbar_nap)


            else:
                m=0

            print "elapsed_time = "  + str(time.time() - start_time)

            # pylab.plot(t_vec, vCopy)
            # pyplot.show()

            # sys.exit()

            soma.ghdbar_hd=soma.ghdbar_hd * math.pow(10,-0.25) #.000001


        soma.gbar_lva=soma.gbar_lva * math.pow(10,-0.25)

    #soma.gbar_nap=soma.gbar_nap*10



# import matplotlib.pyplot as plt

# plt.axis([0,28e-5,115e-6,160e-6])
# plt.plot(gbar_lva_syn_wt_ON, ghdbar_hd_syn_wt_ON,linestyle='', marker='^',markersize=10,markerfacecolor='blue')
# plt.show()


gbar_lva_syn_wt_ON1 = np.asarray(gbar_lva_syn_wt_ON,dtype = 'float64')
ghdbar_hd_syn_wt_ON1 = np.asarray(ghdbar_hd_syn_wt_ON,dtype = 'float64')

import numpy as np
import os.path
import glob

save_path = 'simulation_results'
outputfile = 'wt-ON-final_better_res'
completeName = os.path.join(save_path, outputfile+".txt")
text=np.savetxt(completeName,zip(gbar_lva_syn_wt_ON1,ghdbar_hd_syn_wt_ON1))


file= 'simulation_results/wt-ON-final_better_res.txt'
f = open(file, 'r')
lines=f.readlines()

gbar_lva_syn_wt_ON =[]
ghdbar_hd_syn_wt_ON = []
for x in lines:
    gbar_lva_syn_wt_ON.append(x.split()[0])
    ghdbar_hd_syn_wt_ON.append(x.split()[1])

    f.close()

gbar_lva_syn_wt_ON1 = np.asarray(gbar_lva_syn_wt_ON,dtype = 'float64')
ghdbar_hd_syn_wt_ON1 = np.asarray(ghdbar_hd_syn_wt_ON,dtype = 'float64')


ghdbar_hd_all= h.Vector()
gbar_lva_all=h.Vector()

soma.gbar_nap=5e-8
for zz in range(0,1):
    soma.gbar_lva=1 #2e-4


    for jj in range(0,64):#28

        soma.ghdbar_hd=1

        for ii in range(0,64): #35

            start_time = time.time()



            print "elapsed_time = "  + str(time.time() - start_time)


            ghdbar_hd_all.append(soma.ghdbar_hd)
            gbar_lva_all.append(soma.gbar_lva)

            soma.ghdbar_hd=soma.ghdbar_hd * math.pow(10,-0.25)


        soma.gbar_lva=soma.gbar_lva * math.pow(10,-0.25)

    #soma.gbar_nap=soma.gbar_nap*10


gbar_lva_all1 = np.asarray(gbar_lva_all,dtype = 'float64')
ghdbar_hd_all1 = np.asarray(ghdbar_hd_all,dtype = 'float64')


save_path = 'simulation_results'
outputfile = 'wt-ON-final_better_res_allpoints_seed10'
completeName = os.path.join(save_path, outputfile+".txt")
text=np.savetxt(completeName,zip(gbar_lva_all1,ghdbar_hd_all1))


import matplotlib.pyplot as plt
plt.plot(gbar_lva_all1,ghdbar_hd_all1,linestyle='', marker='o',markersize=8,markerfacecolor='none')
plt.plot(gbar_lva_syn_wt_ON1, ghdbar_hd_syn_wt_ON1,linestyle='', marker='^',markersize=7,markerfacecolor='blue')
plt.show()

#
#
# t_vec1 = np.asarray(t_vec,dtype = 'float64')
# v_vec1 = np.asarray(vCopy,dtype = 'float64')
#
#
# save_path = 'simulation_results'
# outputfile = 'wt-ON-voltage_trace_6'
# completeName = os.path.join(save_path, outputfile+".txt")
# text=np.savetxt(completeName,zip(t_vec1,v_vec1))
#
#
#
# file= 'simulation_results/wt-ON-voltage_trace_6.txt'
# f = open(file, 'r')
# lines=f.readlines()
#
# t_vec =[]
# v_vec = []
# for x in lines:
#    t_vec.append(x.split()[0])
#    v_vec.append(x.split()[1])
#
#    f.close()
#
# t_vec1 = np.asarray(t_vec,dtype = 'float64')
# v_vec1 = np.asarray(v_vec,dtype = 'float64')
#
# plt.figure()
# plt.plot(t_vec1,v_vec1)
# plt.show()
#
#
#
#
# pylab.subplot(3,1,1)
# pylab.plot(t_vec, vCopy)
# # pyplot.show()
# # pylab.plot(t_vec, v_vec)
# # pyplot.show()
#
# pylab.subplot(3,1,2)
# pylab.plot(t_vec, vecexc['i_excsyn']) #div(5000)) # divided by membrane resistance (5,000 to 100,000 o/cm2), values obtained with intracellular sharp electrodes and wholecell recordings
# pylab.subplot(3,1,3)
# pylab.plot(t_vec, vecinh['i_inhsyn'])#.div(5000))
# pyplot.show()
