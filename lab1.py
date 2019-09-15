import math
import random
import numpy
import csv

# Constant event types
ARRIVAL = 'ARRIVAL'
OBSERVATION = 'OBSERVATION'
DEPARTURE = 'DEPARTURE'

# CSV files 
eventsFile = 'events.csv'

# Generate exponential random vairables 
def generateRv(rate): 
    U = numpy.random.uniform(0,1)
    x = -numpy.log(1.0 - U) / rate
    return ( x )

class Event(object):
    def __init__(self):
        self.type = '' # ARRIVAL, DEPARTURE, OBSERVATION
        self.id = 0 
        self.time = 0
        self.packetLength = 0 

# WIP 
class Simulation(object): 
    def __init__(self, lambd, L, T, alpha, C, queueSize ):
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
        # Stats 
        self.Na = 0 # Number of arrivals
        self.No = 0 # Number of observations
        self.Nd = 0 # Number of departures
        self.pIdle = 0 # Idle packets, the wait time
        self.pLoss = 0 # Packets lost 
    
    # WIP, calcluate other stuff here
    def processEvents(self): 
        for event in self.eventsList: 
            if event.type == ARRIVAL:
                self.Na += 1
            elif event.type == DEPARTURE:
                self.Nd += 1
            else: 
                self.No += 1
        eventSummary = {
            'Na': self.Na,
            'No': self.No,
            'Nd': self.Nd,
        }
        print (eventSummary)
    
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
        self.generateDepartures()
        self.sortEventsList()
        self.generateEventsCsv()
        self.processEvents()

    def generateDepartures(self):
        previousEvent = None
        departureEvents = []
        for event in self.eventsList:
            if event.type == ARRIVAL:
                 # Create new departure event add to queue
                departureEvent = self.populateDeparture(event, previousEvent)
                previousEvent = departureEvent
                departureEvents.append(departureEvent)
        # Add departures events to the events list
        self.eventsList.extend(departureEvents)

    def populateDeparture(self, arrivalEvent, previousDepartureEvent): 
        # Based on the sorted list of arrivals + observations, 
        # determine when a packet departs 
        serviceTime = (arrivalEvent.packetLength/(self.linkRate))
        # If first packet being serviced, or queue is empty, departure time is arrival + service type
        if previousDepartureEvent is None or arrivalEvent.time > previousDepartureEvent.time:
            departureTime = arrivalEvent.time + serviceTime
        else:
            departureTime = previousDepartureEvent.time + serviceTime
        # Create the departure event
        departureEvent = Event()
        departureEvent.time = departureTime
        departureEvent.type = DEPARTURE
        departureEvent.packetLength = arrivalEvent.packetLength
        departureEvent.id = arrivalEvent.id
        return departureEvent

# Simulation params 
p = 0.25 # rho
L = 2000 # packet size 
C = 1000000 # link rate
# Since rho = (lambda * L) / C. Then, lambda = (rho * C) / L
lambd = (p*C)/L # packet arrival rate
# Mentioned in slides that observer rate at least 5x lambda
alpha = 5*lambd # observer rate 
k = 1 # queue size
T = 1000 # simulation time 
s = Simulation(lambd, L, T, alpha, C, k)
s.run() 
    
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
    
question1()
