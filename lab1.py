import math
import random
import numpy

# Constant event types
ARRIVAL = "ARRIVAL"
OBSERVATION = "OBSERVATION"
DEPARTURE = "DEPARTURE"

# Generate exponential random vairables 
def generateRv(rate): 
    U = numpy.random.uniform(0,1)
    x = -numpy.log(1.0 - U) / rate
    return ( x )

class Event(object):
    def __init__(self):
        self.type = "" # ARRIVAL, DEPARTURE, OBSERVATION
        self.id = 0 
        self.time = 0
        self.packetLength = 0 

# WIP 
class Simulation(object): 
    def __init__(self, lambd, L, T, alpha, C, queueSize ):
        # User provided params 
        self.lambd = lambd # the interarrival rate 
        self.duration = T # sim duration 
        self.avgPacketLength = L
        self.alpha = alpha # observer rate 
        self.linkRate = C 
        self.queueSize = queueSize
        # Variables from simulation 
        self.numObservations = 0
        self.numOfPackets = 0 # the total num of packets
        self.eventsList = [] # This will be sorted
        # Stats 
        self.Na = 0 # Number of arrivals
        self.No = 0 # Number of observations
        self.Nd = 0 # Number of departures
        self.pIdle = 0 # Idle packets, the wait time
        self.pLoss = 0 # Packets lost 
    
    def sortEventsList(self): 
        """
            Generate arrival and observation events. 
            Sort the event objects based on time
        """
        # Take the unsorted list of events, and sort
        # the event objects by time 
        self.eventsList.sort(key=lambda x: x.time)
        for event in self.eventsList:
            print ("************")
            print (f"{event.type} {event.id}")
            print (event.time)
    
    def generateArrivals(self): 
        time = 0.0 
        i = 1 
        # Generate arrival events
        while True:
            se = Event()
            se.type = ARRIVAL
            se.id = i 
            se.packetLength = generateRv(1.0/self.avgPacketLength)
            time += generateRv(self.lambd)
            se.time = time
            # If the time of packet arrival exceeds sim duration,
            # stop generating arrival events 
            if se.time > self.duration:
                break 
            i += 1
            self.eventsList.append(se)
        self.numPackets = i 
        # print (self.eventsList)
    
    def generateObservations(self):
        time = 0.0 
        i = 1 
        # Generate observation events
        while True:
            se = Event()
            se.type = OBSERVATION
            se.id = i 
            time += generateRv(self.alpha)
            se.time = time
            # If the time of observation exceeds sim duration,
            # stop generating arrival events 
            if se.time > self.duration:
                break 
            i += 1
            self.eventsList.append(se)
        self.numObservations = i 
        # print (self.eventsList)
    
    def run(self):
        self.generateArrivals()
        self.generateObservations()
        self.sortEventsList()
        self.generateDepartures()
  
        self.sortEventsList()

    def generateDepartures(self):
        previousEvent = None
        departureEvents = []
        for event in self.eventsList:
            if event.type == ARRIVAL:
                 # Create new departure event add to queue
                departureEvent = self.populateDeparture(event, previousEvent)
                previousEvent = departureEvent
                departureEvents.append(departureEvent)
        self.eventsList.extend(departureEvents)

    def populateDeparture(self, arrivalEvent, previousDepartureEvent): 
        # Based on the sorted list of arrivals + observations, 
        # determine when a packet departs 
        serviceTime = (arrivalEvent.packetLength/(self.linkRate * 1000000))
        # If first packet being serviced, or queue is empty, departure time is arrival + service type
        if previousDepartureEvent is None or arrivalEvent.time > previousDepartureEvent.time:
            departureTime = arrivalEvent.time + serviceTime
        else:
            departureTime = previousDepartureEvent.time + serviceTime

        departureEvent = Event()
        departureEvent.time = departureTime
        departureEvent.type = DEPARTURE
        departureEvent.packetLength = arrivalEvent.packetLength
        departureEvent.id = arrivalEvent.id
        return departureEvent

            

# These numbers are arbitrary    
# s = Simulation(0.25, 2000, 500, 1,1, 1)
# s.run() 
    
def question1():
    # We would expect the average to be close to 1/rate 
    rate = 75
    vars = []
    for i in range(1000):
        vars.append(generateRv(rate))
    print ("Mean: ")
    # Get the mean
    print (numpy.mean(vars))
    # Get the average
    print ("Variance: ")
    print (numpy.var(vars))
    # Check if mean is close to 1/rate
    print ("1/rate: ")
    print (1/rate)
    
question1()


