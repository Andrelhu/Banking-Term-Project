#Banking System Simulation 1.1
#E. Andre Lhuillier
#George Mason University

import random as rd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import networkx as nx

#Simulation object. This object will proceed to instantiate the banks, users and the proper
#interactions between them. It keeps track of major global variables.
    
class sim(object):
    def __init__(self):
        self.quarter = 0        
             
        #Generate a sample of a Parteto distribution (size = Population).
        self.total_w_distribution = []
        for i in range(Population):
            self.total_w_distribution.append((np.random.pareto(3,None))*10)
        #self.total_w_distribution = sorted(self.total_w_distribution, key=int) 
        
        #Create users with specific amounts of wealth provided by the Pareto sample.
        self.users = [user(x,self.total_w_distribution[x],0) for x in range(Population)]
        
        #Create investment pools.
        risk = [0.5,0.75,0.95]
        
        #MODELO ACTUAL NO CONSIDERA RIESGO = EVALUACION DE RIESGO SEGUN TIEMPO DE RETORNO Y TIEMPO ESTIMADO DE RETIRO-CLIENTE
        time = [15,10,5]
        interest = [1.15,1.10,1.05]        
        self.pools = [pools(x,risk[x],time[x],interest[x]) for x in range(3)]
        
        #Create banks (all banks share same initial conditions).
        self.bank = [bank(0,0.0,0) for x in range(Banks)]
        
        lista_nombre = ['West','East','NorEas','NorWes','SouEas','SouWes','CentSou','CentNor','Nacional','Londres']
        #Regiones:   Occidente(16.89),Oriente(20.38),Noreste(6.1),Noroeste(9.32),Sureste(4.09),Suroeste(13.19),Centrosur(12.01),Centronor(18.02)
        
        for i in range(Banks):
            self.bank[i].ID = str(lista_nombre[i])
            self.bank[i].pos = i
                
        #Network Properties            
        self.network = self.generate_network()
        #Get clients for banks.
            #self.open_banks()
        self.network_mean = self.show_network()

          
#------------------------------------------------------------------------------------------------------------STEP BEGIN
    def step(self,step_now):
        #Simulation step. Begin reseting temporal variables.
        total_notes = [0.0] * Banks
        total_guys = 0
        total_rumor = 0
       
        #Users procedures activation: Evaluate local trade conditions and money adoption. Get adopted type
        for user in self.users:
            if rd.randint(0,Population) < Population / 10: #ACTIVATION!!!!!
                user.evaluate()
                user.move_bank()
                user.adjust()
        
        #Banks procedures: Evaluate clients and investment pools quarterly (Q1,Q2,Q3,Q4)
        if self.quarter == 3:
            for bank in self.bank:
                if bank.broke == 0:
                    bank.eval_client()
                    bank.eval_pool()
            self.quarter = 0
        else:
            self.quarter += 1
        
        #Check for ROI every step.
        for bank in self.bank:
            bank.ret_pool()        
        
        #Check for broke banks.
        for bank in self.bank:
            if bank.res <= 0.0 and bank.broke == 0:
                if broke_step == True:
                    print "Step "+str(step_now)+": "+str(bank.ID)+" is Broke.\n"
                bank.broke = 1
                bank.clients = []
                bank.res = 0
                bank.notes = 0
                for user in self.users:
                    if user.bank_pref == bank.ID:
                        user.bank_pref = 1000
                        user.notes = 0.0
                        del bank.clients[user.ID]
        
        #Rumor dynamic.
        for user in self.users:
            if user.neg_rumor > 0:
                total_rumor += user.neg_rumor * 20
            for i in range(Banks):                    
                total_notes[i] = float(user.notes[i]) + float(total_notes[i])
                if user.notes[i] > 0.000:
                    total_guys += 1

        #Register information.        
        total_guys_w_notes.append(total_guys)
        total_sim_rumor.append(total_rumor)
        for i in range(Banks):
            total_reserve_list[i] = total_reserve_list[i] + [self.bank[i].res]
            total_notes_list[i] = total_notes_list[i] + [self.bank[i].notes]
        
        #Process Rumor.
        for i in range(Population):
            self.users[i].rumor_out()      
        for i in self.bank:
            i.rumor_out()
            
        #Update Bank Timeseries
        for bank in self.bank:
            bank.ts_notes.append(bank.notes)
            bank.ts_res.append(bank.res)
            
#------------------------------------------------------------------------------------------------------------STEP END    

    def open_banks(self):
        selected = []
        client_max = 0
        client_max_wanted = 0
        
        #lista_nombre = ['West','East','NorEas','NorWes','SouEas','SouWes','CentSou','CentNor',Nacional,Londres
        clients_wanted = [(Pop_w_not/100)*3.17,(Pop_w_not/100)*7.76,(Pop_w_not/100)*6.78,(Pop_w_not/100)*9.26,(Pop_w_not/100)*9.36,(Pop_w_not/100)*0.63,(Pop_w_not/100)*2.82,(Pop_w_not/100)*6.26,(Pop_w_not/100)*23.81,(Pop_w_not/100)*30.01]
        clients_rounded = []        
        for i in clients_wanted:
            clients_rounded.append(round(i))
        for n in clients_rounded:
            client_max_wanted += n
        sequence = [0,1,2,3,4,5,6,7,8,9]
        while client_max < (client_max_wanted - 50):
                client_max = 0    
                i = rd.choice(sequence)
                if len(self.bank[i].clients) == clients_rounded[i]:
                    sequence.remove(i)
                    pass
                else:
                #Nacional (8) y Londres (9):
                    if i == 8 or i == 9:
                        j = rd.randint(0,Population-1)
                        if self.users[j].ID not in selected:
                                selected.append(self.users[j].ID)
                                self.bank[i].res = float(self.bank[i].res) + float(self.users[j].res)
                                self.bank[i].deposit_mem = float(self.users[j].res)
                                self.users[j].notes[i] = float(self.users[j].res)
                                self.bank[i].notes = float(self.bank[i].notes) + float(self.users[j].notes[i])
                                self.users[j].res = 0.0
                                self.users[j].method = 1
                                self.users[j].bank_pref = i
                                self.bank[i].clients.append(self.users[j].ID)
                                self.bank[i].client_in_time.append(month)
                    else:
                        upper = [0.17,0.37,0.43,0.52,0.57,0.70,0.82,1]
                        lower = [0,0.17,0.37,0.43,0.52,0.57,0.70,0.82]
                        j = rd.randint(round(lower[i]*Population),round(upper[i]*Population)-1)
                        if self.users[j].ID not in selected and self.users[j].cluster == i:
                                selected.append(self.users[j].ID)
                                self.bank[i].res = float(self.bank[i].res) + float(self.users[j].res)
                                self.bank[i].deposit_mem = float(self.users[j].res)
                                self.users[j].notes[i] = float(self.users[j].res)
                                self.bank[i].notes = float(self.bank[i].notes) + float(self.users[j].notes[i])
                                self.users[j].res = 0.0
                                self.users[j].method = 1
                                self.users[j].bank_pref = i
                                self.bank[i].clients.append(self.users[j].ID)
                                self.bank[i].client_in_time.append(month)
                        
                for k in range(Banks):
                    client_max = client_max + len(self.bank[k].clients)
        
    #Network generation procedure.                
    def generate_network(self):
        network = []
        nodegap = common_nodes / 2
        total = Population-1
        #Regiones:   Occidente(16.89),Oriente(20.38),Noreste(6.1),Noroeste(9.32),Sureste(4.09),Suroeste(13.19),Centrosur(12.01),Centronor(18.02)
        for i in range(network_degree/2):
            for user in self.users:
                
                #1  Occidente (upper 16.89)
                lower = 0
                upper = total*0.1689
                if user.ID <= upper:
                    user.cluster = 0
                    temp_id = rd.randint(0,round(upper+nodegap)+1)
                    if self.users[temp_id].ID != user.ID:
                        if self.users[temp_id].ID not in user.neighbors:
                            user.neighbors.append(self.users[temp_id].ID)
                            self.users[temp_id].neighbors.append(user.ID)

                #2  Oriente (20.38)
                lower = upper
                upper = upper + total*0.2038
                if lower < user.ID <= upper:
                    user.cluster = 1
                    temp_id = rd.randint(round(lower-nodegap)-1,round(upper+nodegap)+1)
                    if self.users[temp_id].ID != user.ID:
                        if self.users[temp_id].ID not in user.neighbors:
                            user.neighbors.append(self.users[temp_id].ID)
                            self.users[temp_id].neighbors.append(user.ID)

                #3  Noreste (6.1)
                lower = upper
                upper = upper + total*0.061
                if lower < user.ID <= upper:
                    user.cluster = 2
                    temp_id = rd.randint(round(lower-nodegap)-1,round(upper+nodegap)+1)
                    if self.users[temp_id].ID != user.ID:
                        if self.users[temp_id].ID not in user.neighbors:
                            user.neighbors.append(self.users[temp_id].ID)
                            self.users[temp_id].neighbors.append(user.ID)
                #4  Noroeste (9.32)
                lower = upper
                upper = upper + total*0.0932
                if lower < user.ID <= upper:
                    user.cluster = 3
                    temp_id = rd.randint(round(lower-nodegap)-1,round(upper+nodegap)+1)
                    if self.users[temp_id].ID != user.ID:
                        if self.users[temp_id].ID not in user.neighbors:
                            user.neighbors.append(self.users[temp_id].ID)
                            self.users[temp_id].neighbors.append(user.ID)
                
                #5 Sureste (4,09)                
                lower = upper
                upper = upper + total*0.0409
                if lower < user.ID <= upper:
                    user.cluster = 4
                    temp_id = rd.randint(round(lower-nodegap)-1,round(upper+nodegap)+1)
                    if self.users[temp_id].ID != user.ID:
                        if self.users[temp_id].ID not in user.neighbors:
                            user.neighbors.append(self.users[temp_id].ID)
                            self.users[temp_id].neighbors.append(user.ID)
                
                #6 Suroeste (13.19)                
                lower = upper
                upper = upper + total*0.1319
                if lower < user.ID <= upper:
                    user.cluster = 5
                    temp_id = rd.randint(round(lower-nodegap)-1,round(upper+nodegap)+1)
                    if self.users[temp_id].ID != user.ID:
                        if self.users[temp_id].ID not in user.neighbors:
                            user.neighbors.append(self.users[temp_id].ID)
                            self.users[temp_id].neighbors.append(user.ID)
                
                #7 Centrosur (12.01)                
                lower = upper
                upper = upper + total*0.1201
                if lower < user.ID <= upper:
                    user.cluster = 6
                    temp_id = rd.randint(round(lower-nodegap)-1,round(upper+nodegap)+1)
                    if self.users[temp_id].ID != user.ID:
                        if self.users[temp_id].ID not in user.neighbors:
                            user.neighbors.append(self.users[temp_id].ID)
                            self.users[temp_id].neighbors.append(user.ID)
                            
                #8 Centronorte (18.02)
                lower = upper
                upper = upper + total*0.1802
                if lower < user.ID <= upper:
                    user.cluster = 7
                    temp_id = rd.randint(round(lower-nodegap)-1,round(upper)-1)
                    if self.users[temp_id].ID != user.ID:
                        if self.users[temp_id].ID not in user.neighbors:
                            user.neighbors.append(self.users[temp_id].ID)
                            self.users[temp_id].neighbors.append(user.ID)
                            
        for user in self.users:
            for i in range(len(user.neighbors)):
                network.append([user.ID,user.neighbors[i]])

        self.open_banks()
        
        for i in range(Banks):
            for j in range(len(self.bank[i].clients)):
                network.append([self.bank[i].ID,self.bank[i].clients[j]])
                
        return network
        
    def show_network(self):
        network_mean = []
        for user in self.users:
            network_mean.append(len(user.neighbors))
        network_mean = sorted(network_mean, key=int)
        return network_mean



class pools(object):
    #investment pools: tienen distintis tipos de riesgo A,B,C. 
    #cada fondo retorna con distinto riesgo, tiempo e intereses.
    def __init__(self,ID,risk,time,interest):
        self.ID = ID
        self.risk = risk
        self.time = time
        self.interest = interest
        
      
class bank(object):
    def __init__(self,ID,Reserve,Notes):
        self.ID = ID #str("banco" + str(ID))
        self.res = float(Reserve)
        self.notes = 0.0
        
        self.clients_wanted = []
        self.clients = []
        self.client_in_time = []     

    #Memory and evaluation of deposit time        
        self.memory = []        
        self.mean_risk = 5        
        self.higher_risk = 6
        self.lower_risk = 4

    #Memory and evaluation of deposit quantities
        self.deposit_mem = []        
        self.mean_deposit = 0
        
        self.invest = False
        self.investment = 0
        self.pool_id = None
        self.pool_time = 0
        
        self.pos = None
        self.broke = 0

    #Timeseries data for RES and NOTES
        self.ts_notes = []
        self.ts_res = []

    def eval_client(self):
        #evaluate mean time for client withdrawal
        self.mean_risk = np.mean(self.memory)
        deviation = np.std(self.memory)
        self.higher_risk = self.mean_risk + deviation
        self.lower_risk = self.mean_risk - deviation
        
        self.mean_deposit = np.mean(self.deposit_mem)
        
    def eval_pool(self):
        #according to clientrisk, reserve, poolrisk and returns: evaluate best pool and amount #for option in eco.pools:
        for i in range(len(eco.pools)):
            if eco.pools[i].time < self.lower_risk:
                self.investment = self.lower_risk * self.mean_deposit
                if self.investment < self.res:
                    self.invest = True
                    eco.pools[i].invested = self.investment
                    self.res = self.res - self.investment
                    self.pool_id = i
    
    def ret_pool(self):
        if self.invest == True:
            if self.pool_time == eco.pools[self.pool_id].time:
                self.res = self.res + (self.investment * eco.pools[self.pool_id].interest)
                self.clear_investment()
            else:
                self.pool_time += 1
    
    def clear_investment(self):
        self.investment = 0
        self.pool_time = 0
        self.pool_id = None
        self.invest = False
        
    def rumor_out(self):
        for i in self.clients:
            eco.users[i].rumor = self.pos
            
#User agent.                         
class user(object):
    def __init__(self,ID,Gold,Preference):
        self.ID = ID
        self.res = float(Gold)
        self.pref = Preference
        self.notes = [0.0] * Banks
        self.method = 0
        self.bank_old_pref = 1000
        self.bank_pref = 1000
        self.im_moving = False
        self.neighbors = []
        self.neighbors_met = []
        self.rumor = None
        self.neg_rumor = 0
        self.cluster = None
    
    #Evaluate my option according to my threshold (neighbor_needed) and effective trade (bounded_perception).
    def evaluate(self):
        self.neighbors_met = []
        neighbor_options = []
        neighbors_total_notes = []
        for i in eco.bank:
            neighbors_total_notes.append([])
            
        #Look through neighbors.
        for i in self.neighbors:
            if type(i) is not str:
                if rd.randint(0,100) <= bounded_perception:
                    self.neighbors_met.append(eco.users[i].ID)
                    neighbor_options.append(eco.users[i].method)
                    for j in range(len(neighbors_total_notes)):
                        neighbors_total_notes[j].append(eco.users[i].notes[j])
            
        if (sum(neighbor_options)) > (len(neighbor_options) * ((neighbor_needed + self.neg_rumor)/100)): # / (float(neighbor_needed) * float(1 + self.rumor)) ):
            self.method = 1
            self.neg_rumor = 0
            sum_total_notes = []

            if GLOBAL_BIAS == True:
                if neighbors_total_notes[8] != []:
                    neighbors_total_notes[8] = sum(neighbors_total_notes[8]) * 0.6
                if neighbors_total_notes[9] != []:                        
                    neighbors_total_notes[9] = sum(neighbors_total_notes[9]) * 0.6

            for i in neighbors_total_notes:
                if type(i) == float:
                    sum_total_notes.append(i)
                else:
                    sum_total_notes.append(sum(i))

            for i in range(len(sum_total_notes)):
                if sum_total_notes[i] == 0.0:
                    sum_total_notes[i] = None
                    
            if self.rumor != None:
                if sum_total_notes[self.rumor] != None:
                    sum_total_notes[self.rumor] = float(sum_total_notes[self.rumor]) * float(float(100 + rumor_effect)/100)
            
            
            for i in range(len(sum_total_notes)):
                if sum_total_notes[i] == max(sum_total_notes) and sum_total_notes[i] != None:
                    if eco.bank[i].broke == 1:
                        self.im_moving = False
                    else:
                        self.bank_old_pref = self.bank_pref                    
                        self.bank_pref = i
                        self.im_moving = True
                    break
        else:
            self.method = 0

    #Move gold to other bank. Bank modifies.
    def move_bank(self):
        if self.im_moving == True and self.bank_old_pref != 1000 and eco.bank[self.bank_old_pref].broke == 0:
            self.im_moving = False
            #Get gold from old bank.
            i = self.bank_old_pref
            self.res = float(self.notes[i])
            eco.bank[i].res = float(eco.bank[i].res) - float(self.notes[i])
            eco.bank[i].notes = float(eco.bank[i].notes) - float(self.notes[i])
            self.notes[i] = 0.0
            for j in range(len(eco.bank[i].clients)):
                if eco.bank[i].clients[j] == self.ID:       #GET THE CLIENT OUT AND REMEMBER HOW LONG WAS THE DEPOSIT IN
                    del eco.bank[i].clients[j]
                    deposit_lifetime = month - eco.bank[i].client_in_time[j]
                    eco.bank[i].memory.append(deposit_lifetime)
                    del eco.bank[i].client_in_time[j]
                    break
            #Get gold into new bank.
            i = self.bank_pref
            eco.bank[i].res = float(eco.bank[i].res) + float(self.res)
            eco.bank[i].deposit_mem = float(self.res)
            if self.ID not in eco.bank[i].clients:
                eco.bank[i].clients.append(self.ID) #Maybe get exclusivity! non repeatred IDs
            eco.bank[i].client_in_time.append(month)
            self.notes[i] = float(self.res)
            eco.bank[i].notes = float(eco.bank[i].notes) + float(self.notes[i])
            self.res = 0.0
    
    #According to 
    def adjust(self):
        i = int(self.bank_pref)
        if i < Banks:
            bank_exists = 0
            for j in eco.bank:
                if i == j.pos:
                    bank_exists = 1
            if bank_exists == 0:
                self.bank_pref = 1000
            if self.method == 0:
                self.res = float(self.notes[i])
                eco.bank[i].res = float(eco.bank[i].res) - float(self.notes[i])
                eco.bank[i].notes = float(eco.bank[i].notes) - float(self.notes[i])
                self.notes[i] = 0.0
                self.bank_pref = 1000
                for j in range(len(eco.bank[i].clients)):
                    if eco.bank[i].clients[j] == self.ID:       #GET THE CLIENT OUT AND REMEMBER HOW LONG WAS THE DEPOSIT IN
                        del eco.bank[i].clients[j]
                        deposit_lifetime = month - eco.bank[i].client_in_time[j]
                        eco.bank[i].memory.append(deposit_lifetime)
                        del eco.bank[i].client_in_time[j]
                        break
                
            if self.method == 1 and self.notes[i] == 0.0:
                eco.bank[i].res = float(eco.bank[i].res) + float(self.res)
                eco.bank[i].deposit_mem = float(self.res)
                if self.ID not in eco.bank[i].clients:
                    eco.bank[i].clients.append(self.ID) #Maybe get exclusivity! non repeatred IDs
                eco.bank[i].client_in_time.append(month)
                self.notes[i] = float(self.res)
                eco.bank[i].notes = float(eco.bank[i].notes) + float(self.notes[i])
                self.res = 0.0
    
    #Users spread the rumor they have. Each time the rumor is spread among neighbors it weakens.
    def rumor_out(self):
        if np.abs(self.neg_rumor) < 0.01:
            self.neg_rumor = 0
        if self.neg_rumor == 0 and rd.randint(0,5000) < 1: #Freq of negative rumors!!
            self.neg_rumor = rd.gauss(0,neg_rumor_effect)
        if self.rumor != None:
            for i in self.neighbors_met:
                eco.users[i].rumor = self.rumor
        if self.neg_rumor != 0:
            for i in self.neighbors_met:
                eco.users[i].neg_rumor = self.neg_rumor - (self.neg_rumor / neg_rumor_discnt)
     
         
     
     
     
#========================================================================================================================   
#========================================== PLOT BEGIN ==================================================================
#========================================================================================================================

#Plotting procedures:

#Visualization of network.
def draw_graph(graph):
    #Get nodes and create graph.
    nodes = set([n1 for n1, n2 in graph] + [n2 for n1, n2 in graph])
    G=nx.Graph()
    for node in nodes:              # add nodes
        G.add_node(node)
    for edge in graph:              # add edges
        G.add_edge(edge[0], edge[1])
    pos = nx.spring_layout(G,scale=600)       # draw graph
    
    #Nodes
    lista_oro = []
    lista_notas = [[]] * Banks
        
    for user in eco.users:
        if user.method == 0:
            lista_oro.append(user.ID)
        if user.method == 1:
            for i in range(Banks):
                if user.bank_pref == i:
                    lista_notas[i] = lista_notas[i] + [user.ID]            
    color_list = ['b','g','r','y','c','m','#000000','#A52A2A','#B8860B','#E9967A']
    for i in range(Banks):
        nx.draw_networkx_nodes(G,pos,nodelist=lista_notas[i],
                               node_color=color_list[i],
                               node_size=50,                    
                               alpha=0.8)
    nx.draw_networkx_nodes(G,pos,nodelist=lista_oro,
                       node_color='y',
                       node_size=50,
                   alpha=0.8)      
    banks_IDs = []
    for i in eco.bank:
        banks_IDs.append(i.ID)
    nx.draw_networkx_nodes(G,pos,nodelist=banks_IDs,
                       node_color=color_list,
                       node_size=500,
                       alpha=0.8)
    #Labels
    labels={}
    for i in banks_IDs:
        labels[i]=r''+ str(i)    
    nx.draw_networkx_labels(G,pos,labels,font_color='w',font_size=10,font_weight=1000)   
    #Edges
    nx.draw_networkx_edges(G,pos,width=0.5,alpha=0.5,edge_color="black")

    #Graph.
    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    return ()
    
#Visualization of time series.
def plot_out():
    x = [i+1 for i in xrange(steps)]
    global mexmap
    #mexico map
    mexmap = mpimg.imread('mapa-mexico.png')
    
    total_wealth_d = []
    total_friends = []
    
    for i in eco.users:    
        total_wealth_d.append(float(i.res))
        for j in range(Banks):
            total_wealth_d.append(float(i.notes[j]))
        total_friends.append(len(i.neighbors))
    print "Average degree: " + str(np.average(total_friends))
    print "Guys with Notes: " + str(total_guys_w_notes[-1])
    print "Total Wealth: " + str(float(sum(total_wealth_d)))
    
    if plot_1 == True:
        if plot_2 == True:
            plt.subplot(221)
        leg_list = []
        color_list = ['b','g','r','y','c','m','#000000','#A52A2A','#B8860B','#E9967A']
        for i in range(Banks):
            y = total_notes_list[i]
            leg_list.append("Bank "+str(i+1))
            plt.plot(x,y,color=color_list[i])  #COLOR!  
        y = total_guys_w_notes
        leg_list.append("Users w/Notes")
        plt.plot(x,y)
        plt.grid()
    plt.subplot(222)
    y = total_sim_rumor
    leg_list = []
    leg_list.append("Rumor")
    plt.plot(x,y)
    plt.legend(leg_list, loc="upper right")
    plt.grid()
    
    if plot_2 == True:
        if plot_1 == True:
            if ONLY_NETWORK == False:
                plt.subplot(212)
            else:
                plt.subplot(111)
        graph = eco.network
        draw_graph(graph)
  # plt.imshow(mexmap,aspect=0.5,vmin=0,vmax=1)
    plt.show()
    return
   


#========================================================================================================================   
#========================================== PLOT END + ==================================================================
#========================================================================================================================


#########################################################################################################################
##################### MAIN BEGIN  #######################################################################################
#########################################################################################################################

GLOBAL_BIAS = True
RUMOR = True

ONLY_NETWORK = True
broke_step = False
EXPERIMENT = False
runs = 100

# Parameters: #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#1903:: 6%,3%(SUR); %, %(NORTE);30%,22%(NACIONALES) 
#Censo de Poblacion 13.500.000 personas (FUENTE: Censo General de la Rep. Mexicana de 1900)
#NORTE:   327.000 personas #SUR:     312.000 personas
#1ro = Yucateco #2do = Mercantil de Yucatan #3ro = Minero  #4to = XXX #5to = NACIONAL #6to = LONDRES 
#NORTE XX% con 1 BANCO  #SUR XX% con otro BANCO
    
Banks = 10

Population = 2000

#MUCHAS ZONAS, 1 BANCO POR ZONA: COMPETENCIA INTERZONA

#1903 - 58% de poblacion usa billete FUENTE: Tesis Monica Gomez
Pop_w_not = (Population)*0.58
#1897 - 50% de poblacion usa billete Fuente: Tesis M.Gomez
#Pop_w_not = (Population/100)*51

#1897 #clients_wanted = [(Pop_w_not/100)*3,(Pop_w_not/100)*2.2,(Pop_w_not/100)*3,(Pop_w_not/100)*5,(Pop_w_not/100)*54,(Pop_w_not/100)*32]
#1903 clients_wanted = [(Pop_w_not/100)*6,(Pop_w_not/100)*3,(Pop_w_not/100)*4,(Pop_w_not/100)*5,(Pop_w_not/100)*30,(Pop_w_not/100)*23]

steps = 120
month = 0

network_degree = 15
common_nodes = 10

bounded_perception = 50 # 0%-100% [33 / 66 / 99]

neighbor_needed = 50    # 0-100% [25 / 50 / 75]
##################################################################################################################################
##################################################################################################################################
##################################################################################################################################

#Rumor values (currently only with negative rumor).
if RUMOR == True:
    neg_rumor_effect = 20
    neg_rumor_discnt = 4
else:
    neg_rumor_effect = 0
    neg_rumor_discnt = 0
rumor_effect = 0 # 0-100%

# Default lists: #
total_notes_list = [[]] * Banks
total_reserve_list = [[]] * Banks
total_guys_w_notes = []
total_sim_rumor = []
samples_reserve_bank = [[]] * Banks
samples_GWN = []

def process_list(lista):
    new_lista = []
    new_std_up = []
    new_std_down = []
    for i in range(120):
        temp_list = []
        for j in range(runs):
            temp_list.append(lista[j][i])            
        item = np.mean(temp_list)
        item2 = np.std(temp_list)        
        new_lista.append(item)
        new_std_up.append(item + item2)
        new_std_down.append(item - item2)
    return new_lista, new_std_up, new_std_down

def clear_lists():
    global total_guys_w_notes, total_notes_list, total_reserve_list, total_sim_rumor, samples_reserve_bank, samples_GWN    
    total_notes_list = [[]] * Banks
    total_reserve_list = [[]] * Banks
    total_guys_w_notes = []
    total_sim_rumor = []
    samples_reserve_bank = [[]] * Banks
    samples_GWN = []    
clear_lists()

#Experiment list:
bank_experiment_res = []
bank_reserve_list = []
bank_reserve_run = [[0]*Banks] * steps

#Experiment Procedure (Needs just 1 bank).

if EXPERIMENT == True:    
    plot_1 = False
    plot_2 = False
    month = 0    

    total_bank_TS_notes = [[]] * Banks
    bank_0_TS_notes = [[]] * runs
    bank_1_TS_notes = [[]] * runs
    bank_2_TS_notes = [[]] * runs
    bank_3_TS_notes = [[]] * runs
    bank_4_TS_notes = [[]] * runs
    bank_5_TS_notes = [[]] * runs
    bank_6_TS_notes = [[]] * runs
    bank_7_TS_notes = [[]] * runs
    bank_8_TS_notes = [[]] * runs
    bank_9_TS_notes = [[]] * runs

    print "\n Banking Systems Sim 1.1 / Experiment \n"
    print "Runs = " + str(runs)
    for j in range(runs):
        print "Run #" + str(j+1)
        eco = sim()
        clear_lists()
    
        for i in range(steps):
            eco.step(i)
            month += 1
        
        bank_0_TS_notes[j] = eco.bank[0].ts_notes
        bank_1_TS_notes[j] = eco.bank[1].ts_notes
        bank_2_TS_notes[j] = eco.bank[2].ts_notes
        bank_3_TS_notes[j] = eco.bank[3].ts_notes
        bank_4_TS_notes[j] = eco.bank[4].ts_notes
        bank_5_TS_notes[j] = eco.bank[5].ts_notes
        bank_6_TS_notes[j] = eco.bank[6].ts_notes
        bank_7_TS_notes[j] = eco.bank[7].ts_notes
        bank_8_TS_notes[j] = eco.bank[8].ts_notes
        bank_9_TS_notes[j] = eco.bank[9].ts_notes

    mean_0_TS_notes,std_0_TS_notes,stdd_0_TS_notes = process_list(bank_0_TS_notes)
    mean_1_TS_notes,std_1_TS_notes,stdd_1_TS_notes = process_list(bank_1_TS_notes)
    mean_2_TS_notes,std_2_TS_notes,stdd_2_TS_notes = process_list(bank_2_TS_notes)
    mean_3_TS_notes,std_3_TS_notes,stdd_3_TS_notes = process_list(bank_3_TS_notes)
    mean_4_TS_notes,std_4_TS_notes,stdd_4_TS_notes = process_list(bank_4_TS_notes)
    mean_5_TS_notes,std_5_TS_notes,stdd_5_TS_notes = process_list(bank_5_TS_notes)
    mean_6_TS_notes,std_6_TS_notes,stdd_6_TS_notes = process_list(bank_6_TS_notes)
    mean_7_TS_notes,std_7_TS_notes,stdd_7_TS_notes = process_list(bank_7_TS_notes)
    mean_8_TS_notes,std_8_TS_notes,stdd_8_TS_notes = process_list(bank_8_TS_notes)
    mean_9_TS_notes,std_9_TS_notes,stdd_9_TS_notes = process_list(bank_9_TS_notes)
    
    total_TS_at_last = [mean_0_TS_notes,mean_1_TS_notes,mean_2_TS_notes,mean_3_TS_notes,mean_4_TS_notes,mean_5_TS_notes,mean_6_TS_notes,mean_7_TS_notes,mean_8_TS_notes,mean_9_TS_notes]
    total_TS_std_up = [std_0_TS_notes,std_1_TS_notes,std_2_TS_notes,std_3_TS_notes,std_4_TS_notes,std_5_TS_notes,std_6_TS_notes,std_7_TS_notes,std_8_TS_notes,std_9_TS_notes]
    total_TS_std_down = [stdd_0_TS_notes,stdd_1_TS_notes,stdd_2_TS_notes,stdd_3_TS_notes,stdd_4_TS_notes,stdd_5_TS_notes,stdd_6_TS_notes,stdd_7_TS_notes,stdd_8_TS_notes,stdd_9_TS_notes]
    
    #PLOT EXPERIMENT
    x = [i+1 for i in xrange(steps)]
    leg_list = []
    lista_nombre = ['West','East','NorEas','NorWes','SouEas','SouWes','CentSou','CentNor','Nacional','Londres']
    color_list = ['b','g','r','y','c','m','#000000','#A52A2A','#B8860B','#E9967A']
    for i in range(Banks):
        y = total_TS_at_last[i]
        leg_list.append("Bank "+ str(lista_nombre[i]))
        plt.plot(x,y,color=color_list[i],linewidth=3,label=lista_nombre[i])  #COLOR!  
        plt.legend(lista_nombre, loc="upper right")
    for i in range(Banks):
        y = total_TS_std_up[i]
        plt.plot(x,y,color=color_list[i],linewidth=0.5)
        y = total_TS_std_down[i]
        plt.plot(x,y,color=color_list[i],linewidth=0.5)
    y = total_guys_w_notes
    plt.plot(x,y)
    plt.grid()
    plt.show()
    
#If EXPERIMENT == FALSE: Execute normal run of simulation.

else:
    print "\n Banking Systems Sim 1.1 \n"    
    eco = sim()
    print "Ecosystem generated."
    plot_1 = True
    plot_2 = True
    month = 0
    
    for i in range(steps):
            eco.step(i)
            month += 1
            
    for i in range(Banks):
          samples_reserve_bank[i].append(eco.bank[i].res)
          samples_GWN.append(total_guys_w_notes[-1])

    #print eco.bank[0].memory
    for i in range(Banks):
        print "Bank "+str(i)+":" 
        print "   Notes: " + str(eco.bank[i].notes)
        print "   Clients: " + str(len(eco.bank[i].clients))
        print "   Mean Risk: " + str(eco.bank[i].mean_risk) + " \n"
    
    plot_out()

   
print "Done."