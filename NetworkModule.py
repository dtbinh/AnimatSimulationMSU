
'''
Network Module
Simulates brain, contains all neurons



 #IAM JAMES
'''

from NeuronModule import InhibitoryNeuron
from NeuronModule import ExcitatoryNeuron
from NeuronModule import MotorNeuron
from NeuronModule import SensoryNeuron_A
from NeuronModule import SensoryNeuron_B
from NeuronModule import HungerNeuron
import math
import numpy as np
import random
import SimParam
print 'this is the new network module'

class Network:

    #kwargs used for evo driver
     def __init__(self,R_center,L_center,R_radii,L_radii): # mixture of neuron parameters and initializing network numbers
         #some constants/tracking numbers
         self.motor_decay = .9
         self.M1_input_sum = 0
         self.M2_input_sum = 0
         self.FIRED_VALUE = 30 # mV
         self.kSynapseDecay = 0.7
         self.default_a = np.float32(.02)     # sets default values for the Izhikivech variables
         self.default_b = np.float32(.2)
         self.default_c = np.float32(-65)
         self.default_d = np.float32(8)
         self.default_v = np.float32(-65)
         self.default_u = self.default_b*self.default_v

         # initialize arrays for the Izhikivech variables
         self.a = np.array([], dtype = np.float32)
         self.b = np.array([], dtype = np.float32)
         self.c = np.array([], dtype = np.float32)
         self.d = np.array([], dtype = np.float32)
         self.v = np.array([], dtype = np.float32)
         self.u= self.b*self.v
         self.S = np.array([[]], dtype = np.float32) # row-major order; S(2,3) is weight from #2 to #3

         self.firing_color = "#000000"
         self.color = "#ffffff"
         self.sense_B_fired = [0 for i in range(10)]
         self.sense_A_fired = [0 for i in range(10)]
         self.M1_fp = [0,0,0,0,0,0,0,0] # M1's firing pattern from the last 8 iterations of the movement in binary
         self.M2_fp = [0,0,0,0,0,0,0,0] # M2's firing pattern form the last 8 iterations of the movement in binary
         self.M1adjusted = [0,0,0,0,0,0,0,0] # M1's firing pattern from the last 8 iterations of the movement adjusted for 30% decay each iteartion
         self.M2adjusted = [0,0,0,0,0,0,0,0] # M2's firing pattern from the last 8 iterations of the movement adjusted for 30% decay each iteration
         self.count = 0 # count of iterations through eat move smell
         self.motor_neuron1_count = 0 # how many times motor neuron 1 fired
         self.motor_neuron2_count = 0 # how many times motor neuron 2 fired


         if R_center == None: # if no values are passed in (unusual) then set up some random - may want to remove this
             self.R_center = [[random.randrange(-1000,1000,1)/1000.0,random.randrange(-1000,1000,1)/1000.0] for x in range(5)] # method for setting R_center to random number between -1
             # and 1
             self.L_center = [[random.randrange(-1000,1000,1)/1000.0,random.randrange(-1000,1000,1)/1000.0] for x in range(5)]
             self.R_radii = [1.0,1.0,1.0,1.0,.5] # sets the locatins for the R_radii
             self.L_radii = [1.0,1.0,.15,.15,1] # sets the locations for the L_radii

         else:
             # if R & L center and radii are passed in then these values are set to equal the passed in args
             self.R_center = R_center
             self.L_center = L_center
             self.R_radii = R_radii
             self.L_radii = L_radii



         # arrays used for the sense neurons
         self.senseNeuronLocations_A = np.array([],ndmin=2) # holds locations on animat
         self.numSensory_A = 0
         self.senseNeuronLocations_B = np.array([],ndmin=2) # holds locations on animat
         self.numSensory_B = 0

         self.inhibitoryNeurons = [] # holds indices of inhibitory neurons
         self.excitatoryNeurons = [] # holds indices of excitatory neurons
         self.senseNeurons_A = [] # holds neuron indices
         self.senseNeurons_B = [] # holds neuron indices
         self.motorNeurons = [] # holds motor neuron indices
         self.hungerNeurons = [] # holds hunger neuron indices

         self.attribute_list = [] # used in getNeurons function to hold attributes of the gotten neuron
         self.indices_location = [] # holds the locations of the neurons based on indices
         self.fired = [] # holds indices of neurons that have fired

         #These will be dictionaries of Lists eventually for different types of sensory neurons!
         self.sensitivity_A = np.array([], ndmin = 2) # sensitivity to smell A: hard-coded to
         self.sensitivity_B = np.array([], ndmin = 2) # sensitivity to smell A: hard-coded to
         self.indices_list = []        # initializes list to store indices of neurons
         self.neuron_circle_loc = {'inhibitory':[], 'excitatory':[], 'motor':[], 'sensory_A':[], 'sensory_B':[], 'hunger':[]} # contains indices and xy position [indice, x, y]


     def add_neuron(self, typea, neuron_index, position, circle, sensitivity = 100):         #adds specific types of neurons
         self.a = np.insert(self.a, neuron_index, self.default_a)        # sets a
         self.b = np.insert(self.b, neuron_index, self.default_b)        # sets b
         self.c = np.insert(self.c, neuron_index, self.default_c)        # sets c
         self.d = np.insert(self.d, neuron_index, self.default_d)        # sets d
         self.v = np.insert(self.v, neuron_index, self.default_v)        # sets v
         self.u = np.insert(self.u, neuron_index, self.default_u)        # sets u = b*v
         if typea == 'inhibitory':                    #  can be used later to change specific variables for types of neurons
              circle['inhibitory'].append([neuron_index, position]) # appends neuron's location and index to dictionary
              self.inhibitoryNeurons.append(neuron_index) # adds neuron to its own type's list
              self.indices_location.append(position) # appends position to indice location list
         if typea == 'excitatory':
              circle['excitatory'].append([neuron_index, position]) # appends neuron's location and index to dictionary
              self.excitatoryNeurons.append(neuron_index) # adds neuron to its own type's list
              self.indices_location.append(position) # appends position to indice location list
         if typea == 'sensory_A':
              circle['sensory_A'].append([neuron_index, position]) # appends neuron's location and index to dictionary
              self.sensitivity_A = np.append(self.sensitivity_A, sensitivity) # appends the sensitivity of the A neurons to list
              self.senseNeurons_A.append(neuron_index) # adds neuron to its own type's list
              self.indices_location.append(position) # appends position to indice location list
         if typea == 'sensory_B':
              circle['sensory_B'].append([neuron_index, position]) # appends neuron's location and index to dictionary
              self.sensitivity_B = np.append(self.sensitivity_B, sensitivity) # appends the sensitivity to the B neurons list
              self.senseNeurons_B.append(neuron_index) # adds neuron to its own type's list
              self.indices_location.append(position) # appends position to indice location list
         if typea == 'motor':
              circle['motor'].append([neuron_index, position]) # appends neuron's location and index to dictionary
              self.motorNeurons.append(neuron_index) # adds neuron to its own type's list
              self.indices_location.append(position) # appends position to indice location list
         if typea == 'hunger':
              circle['hunger'].append([neuron_index, position]) # appends neuron's location and index to dictionary
              self.hungerNeurons.append(neuron_index) # adds neuron to its own type's list
              self.indices_location.append(position) # appends position to indice location list


     def generateNeurons(self):
          NeuronIndex = 0               # index of neuron
          for i in xrange(40): # 0 to 39
               loc = (np.cos(2*np.pi*(i+0.5)/40),np.sin(2*np.pi*(i+0.5)/40)) # used to find all the neuron locations on the circle
               if i < 20: # upper half-circle
                    if i % 2 == 0: # used to get every other neuron
                         self.add_neuron("sensory_A", NeuronIndex, loc, self.neuron_circle_loc) # adds sense A neuron
                         if self.numSensory_A == 0: self.senseNeuronLocations_A = np.array([loc[0],loc[1]],ndmin=2) # used to put first entry into locations array
                         else: self.senseNeuronLocations_A = np.insert(self.senseNeuronLocations_A, self.numSensory_A, np.array((loc[0], loc[1])), axis = 0)
                         self.numSensory_A += 1
                    else:
                         self.add_neuron("sensory_B", NeuronIndex, loc, self.neuron_circle_loc) # adds sense B neuron
                         if self.numSensory_B == 0: self.senseNeuronLocations_B = np.array([loc[0],loc[1]],ndmin=2) # used to put first entry into locations array
                         else: self.senseNeuronLocations_B = np.insert(self.senseNeuronLocations_B, self.numSensory_B, np.array((loc[0], loc[1])), axis = 0)
                         self.numSensory_B += 1
               else:
                    self.add_neuron("excitatory", NeuronIndex, loc, self.neuron_circle_loc) # adds neuron
               NeuronIndex += 1
          #Generate hunger and motor neurons
          self.add_neuron("hunger", NeuronIndex, (0,0), self.neuron_circle_loc)
          NeuronIndex += 1
          self.add_neuron("motor", NeuronIndex, (1.2, 0), self.neuron_circle_loc)
          NeuronIndex += 1
          self.add_neuron("motor", NeuronIndex, (-1.2, 0), self.neuron_circle_loc)
          NeuronIndex += 1
          temp_value_list = self.neuron_circle_loc.values() # gets the value ( in the form [indice,(x,y)])
          for value in temp_value_list:
               for value2 in value:
                    if len(value2) > 0:
                         self.indices_list.append(value2[0])          # appends the indices of the neurons to indices_list

     def connectNetwork(self):
         #Parameters
          A = 2.0
          B = 20.0

          #Set up connection variables
          #set up ligand and receptor lists for each neuron in circle based on parameters

          # initializes self.S which will later hold connection weights
          self.S = np.zeros((len(self.indices_list), len(self.indices_list)), dtype = np.float32) # creates an array for all connection weights filled with zeros
          rl_array = np.zeros((len(self.indices_list), 10), dtype= np.float32)   # sets up array for receptor and ligand lists, [index, r, r, r, r, r, l, l, l, l, l]

          for type_list in self.neuron_circle_loc['excitatory'], self.neuron_circle_loc['sensory_A'], self.neuron_circle_loc['sensory_B']: # sets r and l values for excitatory,
          # A and B neurons
               for index in type_list:
                    x, y = index[1][0], index[1][1]         # sets x and y equal to the neurons circle location x y
                    for i in xrange(5): # the four quadrants and the center hunger neuron all have circles in varying locations and radii used to determine connections
                         rVal = self.R_radii[i] - np.sqrt( np.square(x - self.R_center[i][0]) + np.square(y - self.R_center[i][1])) # sets r val
                         lVal = self.L_radii[i] - np.sqrt( np.square(x - self.L_center[i][0]) + np.square(y - self.L_center[i][1])) # sets l val
                         #rVal = random.random()
                         #lVal = random.random()
                         if rVal < 0.0: rVal = 0.0 # if below zero, set to zero
                         if lVal < 0.0: lVal = 0.0
                         # print 'rVal', rVal
                         # print 'lVal', lVal
                         rl_array[index[0]][i] = rVal # sets the rval
                         rl_array[index[0]][i+5] = lVal # sets the lval

          for index in self.neuron_circle_loc['hunger']:
               rl_array[index[0]][4] = 1    # setting rl arrays for hunger so it gets connected to the right neurons

          for index in self.neuron_circle_loc['motor']:
               if index[0] % 2 == 0:
                    rl_array[index[0]][8] = 1 # sets the rl array for motor so they are connected only to the excitatory neurons
               if index[0] % 2 != 0:
                    rl_array[index[0]][9] = 1 # sets the rl array for motor so they are connected only to the excitatory neurons

          #Set up connection weights
          for n1 in self.indices_list:
               for n2 in self.indices_list:
                    receptor = rl_array[n1]      # sets receptor equal to list of values in array from corresponding indice
                    ligand = rl_array[n2]        # sets ligand equal to list of values in array from corresponding indice
                    # if n1 == 41 or n1== 42:
                    #      print receptor[:5], ligand[5:]
                    W = np.sum( np.multiply(receptor[:5], ligand[5:])) # r and l's are multiplied by column. if one has a zero in that column, the column's multiplication is zero. if
                    #  there are no overlapping nonzero numbers, W will be zero.
                    max_synapse_strength = 30 # highest value for number in self.S
                    connectionWeight = max_synapse_strength*np.exp(A* W) / (B + np.exp(A*W))
                    ### bring in multiplier from runNetwork
                    if connectionWeight <= 3.0/2.0: connectionWeight = 0
                    rl_array[n1][:5] = receptor[:5]
                    rl_array[n2][5:] = ligand[5:]
                    self.S[n1][n2] = connectionWeight  # sets connection between two neurons based on a value within that neurons array

          # initialize I
          self.I = 2*np.ones( (len(self.indices_list)), dtype = np.float32) # creates an array for self.I filled with 2s


     def copyDynamicState(self): # copies all data for simulation engine 
         state = []
         state.append(self.a.copy())
         state.append(self.b.copy())
         state.append(self.c.copy())
         state.append(self.d.copy())
         state.append(self.u.copy())
         state.append(self.v.copy())
         state.append(self.S.copy())
         try:
             state.append(self.I.copy())
         except AttributeError:
             pass #means its first frame and I has not been set yet ... should be fixed if Initialize() method is made
         return state

     def loadDynamicState(self, state): # for GUI: after pause, allows one to load back previously copied state
         self.a = state[0]
         self.b = state[1]
         self.c = state[2]
         self.d = state[3]
         self.u = state[4]
         self.v = state[5]
         self.S = state[6]
         try:
            self.I = state[7]
         except IndexError:
             pass #not set yet


     def get_neurons_firing(self): # used in GUI driver to change colors
         return (self.v >= self.FIRED_VALUE).nonzero()

     def get_color(self, index): # used in GUI driver for colors
         if index in self.inhibitoryNeurons:
             self.color = "#b1b1ff"
         elif index in self.excitatoryNeurons:
             self.color = "#ff0000"   # Red
         elif index in self.senseNeurons_A:
             self.color = "#009900"     #Green
         elif index in self.senseNeurons_B:
             self.color = "#0000FF"   #Blue
         elif index in self.motorNeurons:
             self.color = "#808080"  #Grey
         elif index in self.hungerNeurons:
             self.color = "#660066"    #Purple
         return self.color

     def getNeurons(self):  #populates neuron objects with vectorized data so that upper levels (e.g. GUIDriver) can use them in an OO manner
         for i in range(0, len(self.indices_list)):
             self.attribute_list.append([i, self.indices_location[i], self.a, self.b, self.v, self.c, self.d, self.u])
         return self.attribute_list

     def runNetwork(self,t,dt): # runs Izhikevich model code

         self.fired = (self.v >= 30).nonzero()[0] # .nonzero() returns indices from 1/0 (T/F) of v >= 30

         for i in range(22,32):
             if self.v[i] >= 30:
                self.sense_A_fired[i-22] += 1
         for i in range(32,42):
             if self.v[i] >= 30:
                self.sense_B_fired[i-32] += 1

         self.v[self.fired] = self.c[self.fired] # takes neurons that fired and sets the voltage back to equal c
         self.u[self.fired] = self.u[self.fired] + self.d[self.fired] # resets the u value of those that fired
         newI = np.sum(self.S[self.fired],axis=0) # gathers the new I of the fired neurons based on their connection weights held in self.S

         self.I = self.kSynapseDecay*self.I + newI  # decays the old value of self.I, and then adds the newI
         self.M1_input_sum = self.M1_input_sum*self.motor_decay     # decays previous motor output by 90%
         self.M1_input_sum += (sum(self.S[self.fired][:,self.motorNeurons[0]]))*.005    # sums input from neurons that fired that are connected to the motor
         print 'M1', self.M1_input_sum
         self.M2_input_sum = self.M2_input_sum*self.motor_decay     # decays previous motor output by 90%
         self.M2_input_sum += (sum(self.S[self.fired][:,self.motorNeurons[1]]))*.005    # sums input from neurons that fired that are connected to the motor
         print 'M2', self.M2_input_sum
         self.cap_I = (self.I >= 50).nonzero()[0]
         self.I[self.cap_I] = 50

         self.v=self.v+0.5*(0.04*(self.v**2) + 5*self.v + 140-self.u + self.I)  # formulat that alters V based on v, u and i
         self.v=self.v+0.5*(0.04*(self.v**2) + 5*self.v + 140-self.u + self.I)
         self.cap_v = (self.v >= 50).nonzero()[0]   # caps v at 50
         self.v[self.cap_v] = 50

         self.u=self.u+self.a*(self.b*self.v - self.u)


     def Bfired(self):
         return self.sense_B_fired
     def Afired(self):
         return self.sense_A_fired


     #uses voltages of firing motorNeurons to return new motor data to AnimatShell to determine wheel (called in animatMovement)
     # NEEDS attention to operate smoothly
     def getMotorData(self):

         # newM1 = 0 if(self.v[self.motorNeurons[0]] <= 30) else 1    #(self.v[self.motorNeurons[0]]) # returns 0 if motorNeuron doesn't fire and 1 if it does
         # if newM1 == 1:
         #    self.motor_neuron1_count += 1
         # newM2 = 0 if(self.v[self.motorNeurons[1]] <= 30) else 1    #(self.v[self.motorNeurons[1]]) # returns 0 if motorNeuron doesn't fire and 1 if it does
         # if newM2 == 1:
         #    self.motor_neuron2_count += 1
         # # self.count += 1
         #
         #
         # self.M1_fp= self.M1_fp[:7] # firing pattern of motor neuron 1, M1_fp[0] is the most recent 0/1 and M1_fp[3] gets left, only last three 0/1's are stored at this point
         # self.M1_fp.insert(0,newM1) # wether or not the motor neuron fired this run through network is inserted into M1_fp[0] here, so M1_fp[0] is always the latest 0/1
         # self.M2_fp= self.M2_fp[:7] # firing pattern of motor neuron 2, M2_fp[0] is the most recent 0/1 and M2_fp[3] gets left, only last three 0/1's are stored at this point
         # self.M2_fp.insert(0,newM2) # wether or not the motor neuron fired this run through network is inserted into M2_fp[0] here, so M2_fp[0] is always the latest 0/1
         # for i in range(8): # for all four indices in M_fp lists
         #     self.M1adjusted[i] = self.M1_fp[i]*(.8**i) # gets the adjusted weight of the neuron having fired in the past, 20% reduction for each run in the past
         #     self.M2adjusted[i] = self.M2_fp[i]*(.8**i) # gets the adjusted weight of the neuron having fired in the past, 20% reduction for each run in the past
         # # if self.M1adjusted != self.M2adjusted:
         # #    print 'sums: ',sum(self.M1adjusted),sum(self.M2adjusted)
         #
         #
         # # print '{:36s}{:2s}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}'.format('self.I[self.senseNeurons_A]',': '\
         # #                                                                                                            ,self.I[self.senseNeurons_A][0],self.I[self.senseNeurons_A][1],self.I[self.senseNeurons_A][2]\
         # #                                                                                                            ,self.I[self.senseNeurons_A][3],self.I[self.senseNeurons_A][4],self.I[self.senseNeurons_A][5]\
         # #                                                                                                            ,self.I[self.senseNeurons_A][6],self.I[self.senseNeurons_A][7],self.I[self.senseNeurons_A][8]\
         # #                                                                                                            ,self.I[self.senseNeurons_A][9])
         #
         #
         # # print self.motor_neuron1_count, self.motor_neuron2_count
         # # print self.count
         # return sum(self.M1adjusted),sum(self.M2adjusted)   # returns the adjusted sum of the M_fp's (a+(b*.8)+(c*.64)+(d*.512))
         return self.M1_input_sum, self.M2_input_sum

         # if newM1 != newM2: print 'newM1, newM2', newM1, newM2
         # if newM1 or newM2 != 0: print 'newM1,newM2', newM1, newM2, '\n'
         # print 'self.I motor', self.I[self.motorNeurons]
         # print 'self.I sensory_A', self.I[self.senseNeurons_A]
         # print 'self.I sensory_B', self.I[self.senseNeurons_B]
         # return newM1,newM2

     def getTotalNeuronNum(self):
         return self.totalNum