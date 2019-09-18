import bisect
import csv
import math
import numpy
import random
import time


# Constant event types
ARRIVAL = 'ARRIVAL'
OBSERVATION = 'OBSERVATION'
DEPARTURE = 'DEPARTURE'

# CSV files 
eventsFile = 'events.csv'
q3File = 'q3.csv'

# Generate exponential random vairables 
def generateRv(rate): 
    U = numpy.random.uniform(0,1)
    x = -numpy.log(1.0 - U) / rate
    return ( x )

class Event(object):
    def __init__(self, type, id, time, packetLength=0):
        self.type = type # ARRIVAL, DEPARTURE, OBSERVATION
        self.id = id
        self.time = time
        self.packetLength = packetLength

    def __lt__(self, event2):
        return self.time < event2.time

    def __str__(self):
        return f"type: {self.type}, time: {self.time}, packetLength:{self.packetLength}"

# WIP 
class Simulation(object): 
    def __init__(self, lambd, L, T, alpha, C, queueSize):
        # User provided params 
        self.lambd = lambd # the interarrival rate 
        self.duration = T # sim duration 
        self.avgPacketLength = L # in bits
        self.alpha = alpha # observer rate 
        self.linkRate = C # in bps
        self.queueSize = queueSize
        # Variables from simulation 
        self.numObservations = 0
        self.numOfPackets = 0 # the total num of packets
        self.eventsList = [] # This will be sorted
        self.currentQueueLength = 0
        # Stats 
        self.Na = 0 # Number of arrivals
        self.No = 0 # Number of observations
        self.Nd = 0 # Number of departures
        self.pIdle = 0 # Idle packets, the wait time
        self.pLoss = 0 # Packets lost 
        self.avgNumPacketsInBuffer = 0 # Avg packets in buffer

    
    def processEvents(self):
        previousDepartureEvent = None

        i = 0
        while i < len(self.eventsList):
            event = self.eventsList[i]

            if event.type == ARRIVAL:
                print(event)
                self.Na += 1
                # Generate the departure if queue not full, drop packet if queue full
                if self.currentQueueLength < self.queueSize:
                    self.currentQueueLength += 1
                    departureEvent = self.generateDeparture(event, previousDepartureEvent)
                    previousDepartureEvent = departureEvent
                    bisect.insort(self.eventsList, departureEvent)
                else:
                    self.pLoss += 1
                    print("@@@@@@@@@@@@@@ DROPPED @@@@@@@@@@@@@@")
            elif event.type == DEPARTURE:
                print(event)
                self.Nd += 1
                self.currentQueueLength -= 1
            else: 
                self.No += 1
                self.avgNumPacketsInBuffer += self.Na - self.Nd 
                # If the difference between Na and Nd is 0, this means that
                # the queue is not in use and is therefore idle 
                if (self.Na - self.Nd == 0): 
                    self.pIdle += 1 
            i += 1

        # Get the avg number of packets in buffer 
        # E[N] =  sum of (Na - Nd) / No
        self.avgNumPacketsInBuffer = self.avgNumPacketsInBuffer / self.No
        # Get the avg pIdle by dividing out No 
        self.pIdle = self.pIdle / self.No
        simSummary = {
            'Na': self.Na,
            'No': self.No,
            'Nd': self.Nd,
            'E[N]': self.avgNumPacketsInBuffer,
            'pIdle': self.pIdle,
            'pLoss': int(self.pLoss / self.numPackets),
        }
        print (simSummary)
        return simSummary
    
    def sortEventsList(self): 
        """
            Generate arrival and observation events. 
            Sort the event objects based on time
        """
        # Take the unsorted list of events, and sort
        # the event objects by time 
        self.eventsList.sort(key=lambda x: x.time)

    def generateArrivals(self): 
        time = 0.0 
        i = 1 
        # Generate arrival events
        while True:
            time += generateRv(self.lambd)
            se = Event(ARRIVAL, i, time, generateRv(1.0/self.avgPacketLength))
            # If the time of packet arrival exceeds sim duration,
            # stop generating arrival events 
            if se.time > self.duration:
                break 
            i += 1
            self.eventsList.append(se)
        self.numPackets = i 
    
    def generateObservations(self):
        time = 0.0 
        i = 1 
        # Generate observation events
        while True:
            time += generateRv(self.alpha)
            se = Event(OBSERVATION, i, time)
            # If the time of observation exceeds sim duration,
            # stop generating arrival events 
            if se.time > self.duration:
                break 
            i += 1
            self.eventsList.append(se)
        self.numObservations = i 

    def generateEventsCsv(self): 
        with open(eventsFile, mode='w') as f:
            # Create the csv writer
            eventsWriter = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            # Write rows 
            eventsWriter.writerow(['EVENT', 'TIME', 'PACKET LENGTH'])
            for event in self.eventsList: 
                # Observation events do not have a packet length 
                row = [event.type, event.time, event.packetLength] if event.packetLength != 0 else [event.type, event.time, ''] 
                eventsWriter.writerow(row)
            print ("Sucessfully wrote events to file")
    
    def run(self):
        self.generateArrivals()
        self.generateObservations()
        self.sortEventsList()
        # self.generateEventsCsv()
        simSummary = self.processEvents()
        return simSummary

    def generateDeparture(self, arrivalEvent, previousDepartureEvent=None):
        # Based on the sorted list of arrivals + observations, 
        # determine when a packet departs 
        serviceTime = (arrivalEvent.packetLength/(self.linkRate))
        # If first packet being serviced, or queue is empty, departure time is arrival + service time
        if previousDepartureEvent is None or arrivalEvent.time > previousDepartureEvent.time:
            departureTime = arrivalEvent.time + serviceTime
        else:
            departureTime = previousDepartureEvent.time + serviceTime
        # Create the departure event
        departureEvent = Event(DEPARTURE, arrivalEvent.id, departureTime, arrivalEvent.packetLength)
        return departureEvent

def question1():
    # We would expect the average to be close to 1/rate 
    rate = 75
    vars = []
    for i in range(1000):
        vars.append(generateRv(rate))
    summary = {
        'Actual mean': numpy.mean(vars), 
        'Actual variance': numpy.var(vars), 
        # Check if mean is close to 1/rate
        'Expected mean': 1/rate, 
        # Check if variance is close to 1/rate^2 
        'Expected variance': math.pow((1/rate), 2)
    }

    print (summary)

# M/M/1 Queue sim constants 
L = 2000 # packet size  
C = 1000000 # link rate 
k = float("inf") # queue size
T = 1000 # simulation time 
def question3(): 

    # M/M/1 Queue
    # The rhos to test for q3 
    q3Summary = {} 
    rhoList = [0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95]
    for rho in rhoList: 
        p = rho 
        # Since rho = (lambda * L) / C. Then, lambda = (rho * C) / L
        lambd = (p*C)/L # packet arrival rate
        # Mentioned in slides that observer rate at least 5x lambda
        alpha = 5*lambd # observer rate 
        print ('Starting sim for rho=%s' % p)
        mm1 = Simulation(lambd, L, T, alpha, C, k)
        summary = mm1.run() 
        q3Summary[p] = summary 
    
    with open(q3File, mode='w') as f:
        # Create the csv writer
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        # Write rows 
        writer.writerow(['rho', 'Na', 'Nd', 'No', 'E[N]', 'pIdle'])
        for rho, summary in q3Summary.items(): 
            # Observation events do not have a packet length 
            Na = summary['Na']
            Nd = summary['Nd']
            No = summary['No']
            packets = summary['E[N]']
            pIdle = summary['pIdle']
            row = [rho, Na, Nd, No, packets, pIdle]
            writer.writerow(row)
        print ("Sucessfully wrote q3 results to file")  

def question4(): 
    p = 1.2
    # Since rho = (lambda * L) / C. Then, lambda = (rho * C) / L
    lambd = (p*C)/L # packet arrival rate
    # Mentioned in slides that observer rate at least 5x lambda
    alpha = 5*lambd # observer rate 
    print ('Starting sim for rho=%s' % p)
    mm1 = Simulation(lambd, L, T, alpha, C, k)
    summary = mm1.run() 

def question6():
    q6Summary = {}
    queueLengths = [10, 25, 50]
    rhoList = [0.6, 0.7, 0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4]

    for k in queueLengths:
        q6Summary[k] = {}
        for p in rhoList:
            lambd = (p*C)/L # packet arrival rate
            alpha = 5*lambd # observer rate
            mm1k = Simulation(lambd, L, T, alpha, C, 10)
            print (f"Starting sim for rho={p}, queueLength={k}")
            summary = mm1k.run()
            q6Summary[k][p] = summary

    with open(q6File, mode='w') as f:
        # Create the csv writer
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        # Write rows
        writer.writerow(['k', 'rho', 'Na', 'Nd', 'No', 'E[N]', 'pIdle', 'pLoss'])
        for k, summaries in q3Summary.items():
            for rho, summary in summaries.items():
                # Observation events do not have a packet length
                Na = summary['Na']
                Nd = summary['Nd']
                No = summary['No']
                packets = summary['E[N]']
                pIdle = summary['pIdle']
                pLoss = summary['pLoss']
                row = [k, rho, Na, Nd, No, packets, pIdle, pLoss]
                writer.writerow(row)
        print ("Sucessfully wrote q3 results to file")

# Answer the questions    
# question1()
# question3()
# question4()
question6()
