# ComputerAidedSimulationsCourse

## Introduction
Laboratories developed during the Computer Aided Simulations and Performance Evaluation course at PoliTo.

## Description
The course aims to provide some knowledge on performance evaluation of dynamic systems via computer simulations, and the skills of using some fundamental methodologies for the assessment, design and understanding of  data processing systems. The course introduces analytical modeling based on queuing theory and stochastic processes and simulation techniques, which can be applied to study the dynamic evolution of a system as a function of time.

## Topics covered by labs

1. Simulations of queuing systems with comparison of simulation results with theoretical ones. <br/>Some queues analyzed:
	* MM1,
	* MM1B,
	* MG1,
	* MGM.

2.  * The Bins and Balls problem: this problem involves m balls and n boxes (or "bins"). Each time, a single ball is placed into one of the bins. After all balls are in the bins, we look at the number of balls in each bin; we call this number the load on the bin. <br/>Implementations:
      * Random Dropping policy: for each ball a single random bin is chosen and the ball is put in it;
      * Load Balacing policy: for each ball d random bins are chosen and the ball is put only in the one with the lowest occupancy.
    * Birthday Paradox concerns the probability that, in a set of n randomly chosen people, some pair of them will have the same birthday. <br/>Implementations:
      * Normal Birthday Paradox: 365 days;
      * Generalized Birthday Paradox: M days.
      
3. Aim of this laboratory is to design probabilistic data structures for storage and to evaluate their performance, in particular when dealing with membership problem that tries to answer the question: "is an element present?". <br/>Data structures used:
	* Simple set,
	* Fingerprint set,
	* Bit String Array,
	* Bloom Filter.
    
4. Aim of the lab is to implement a epidemic SIR model through a agent-based approach and to devise extensions to improve it. <br/>Implementation:
	* Numerical SIR model;
	* Simulative SIR model;
	* Simulative SIR model with movement of individuals.
