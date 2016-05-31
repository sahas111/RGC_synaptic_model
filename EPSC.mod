TITLE EPSC

UNITS{
	(pA) = (picoamp)
    (ms) = (milliseconds)
}

NEURON {
    POINT_PROCESS ExcSynapse
    RANGE onset, tau1, gmax, e, isyn, gsyn
    NONSPECIFIC_CURRENT i
    THREADSAFE
    
}

PARAMETER {

    onset = 0 (ms)
    tau1 = 1 (ms)
    gmax = 0.02    (uS)
    e = 0   (mV) : reversal potential


}

ASSIGNED {
	isyn (pA)
    amp (pA)
    freq (Hz)
}

BREAKPOINT {
    SOLVE states METHOD cnexp
    
    isyn = gsyn (t)*(v-e)
}

FUNCTION gsyn(t(ms)) {
   
   (exp(-(t-onset)/tau1)) 

}






















