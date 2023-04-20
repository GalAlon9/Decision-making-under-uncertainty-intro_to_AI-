import networkx as nx
import matplotlib.pyplot as plt
from pirsur import *
import numpy as np

global possible_state_to_probability

def print_graph(graph: nx.Graph):
    #remove edge from start to target, so it doesn't get drawn
    graph.remove_edge(graph.graph['start'], graph.graph['target'])
    pos = nx.spring_layout(graph)

    nx.draw_networkx_nodes(graph, pos, nodelist=[node for node in graph.nodes], node_color='b')
    nx.draw_networkx_labels(graph, pos, labels={node: f"{node}" for node in graph.nodes})
    #add the weights to the edges and draw the edges with the weights
    edge_labels = nx.get_edge_attributes(graph, 'weight')
    #draw all edges and weights except the edge from start to target
    nx.draw_networkx_edges(graph, pos, edgelist=[edge for edge in graph.edges], width=1.0, alpha=0.5)
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)
    #add label to start and target
    #write above a label "start" next to start, and not on the node, but above it
    plt.text(pos[graph.graph['start']][0], pos[graph.graph['start']][1]+0.1, "start", fontsize=8)
    plt.text(pos[graph.graph['target']][0], pos[graph.graph['target']][1]+0.1, "target", fontsize=8)

    #paint nodes with blockage probability equal to 1
    nx.draw_networkx_nodes(graph, pos, nodelist=[node for node in graph.nodes if 'blockage' in graph.nodes[node] and graph.nodes[node]['blockage'] == 1], node_color='r')
    #write text above graph that blocked nodes are red
    plt.text(0.5, 1.05, "Blocked nodes are red", fontsize=8, transform=plt.gca().transAxes)
    
    plt.show()
    #add back the edge from start to target
    graph.add_edge(graph.graph['start'], graph.graph['target'], weight=10000)

def create_state(cur_state):
    #create a state with all possible combinations of True, False and None
    #if the state is complete, add it to states_to_utilities_dict with utility 0
    if len(cur_state) == graph.graph['num_brittle_nodes']+1:
        states_to_utilities_dict[tuple(cur_state)] = 0
        return
    for i in range(3):
        if i == 0:
            create_state(cur_state+[True])
        elif i == 1:
            create_state(cur_state+[False])
        else:
            create_state(cur_state+[None])
    
def get_all_possible_probabilities(state,nodes_to_generate,probability,possible_state_to_probability):
    #gets state, with nodes_to_generate nodes that are not None (unknown)
    #for each node, generate a state with value True, and False
    #then after all nodes are generated, add the state and probability to possible_state_to_probability
    if len(nodes_to_generate) == 0:
        #all nodes are generated, so add the state and probability to possible_state_to_probability
        possible_state_to_probability[tuple(state)] = probability
        #print("ADDED ",state,probability)
        return
    #generate a state with value True, and False
    node = nodes_to_generate[0]
    state[graph.nodes[node]['index_in_state_format']]=True
    get_all_possible_probabilities(state,nodes_to_generate[1:],probability*graph.nodes[node]['blockage'],possible_state_to_probability)
    state[graph.nodes[node]['index_in_state_format']]=False
    get_all_possible_probabilities(state,nodes_to_generate[1:],probability*(1-graph.nodes[node]['blockage']),possible_state_to_probability)
    

def print_optimal_policy(state,level):
    #compute and print optimal policy
    #print(level*'    ',"CURRENT STATE: ",state,'U=',states_to_utilities_dict[tuple(state)])
    if(state[0]==graph.graph['target']):
        return
    best_action=best_action_for_state[tuple(state)]
    print(level*'    ',"Go to ", best_action)
    neighbours_to_reveal={}
    state_after_action=list(state).copy()
    state_after_action[0]=best_action
    #Add all neighbours that are brittle and Unknown to neighbours_to_reveal
    neighbours_to_reveal=[]
    for action_neighbor in graph.neighbors(best_action):
        if 'blockage' in graph.nodes[action_neighbor] and state_after_action[graph.nodes[action_neighbor]['index_in_state_format']]==None:    
            #node is brittle and unrevielied, so update the state to every possible state
            neighbours_to_reveal.append(action_neighbor)
    if len(neighbours_to_reveal)==0:
        #no brittle nodes to reveal, so print the action and continue from there
        print_optimal_policy(state_after_action,level)
    else:
        global possible_state_to_probability
        possible_state_to_probability={}
        get_all_possible_probabilities(state_after_action,neighbours_to_reveal,1,possible_state_to_probability)
        for possible_state in possible_state_to_probability.keys():
            #for each possible state, print the state and continue from there
            print((level)*'    ',"If reached state", possible_state,':')
            print_optimal_policy(possible_state,level+1)
    
def run_random_simulation():
    #generate blocking locations according to their distributions, and run the agent from start to target
    #Display the graph instance and sequence of actions
    new_graph=graph.copy()
    state=[new_graph.graph['start']]
    for node in new_graph.nodes:
        if 'blockage' in new_graph.nodes[node]:
            isBlocked= np.random.binomial(1, new_graph.nodes[node]['blockage'])
            state.append(isBlocked==1)
            new_graph.nodes[node]['blockage']=isBlocked 
    print_graph(new_graph)
    print("Simulation start state:",state)
    print("Optimal policy:")
    while state[0]!=new_graph.graph['target']:
        best_action=best_action_for_state[tuple(state)]
        print("Go to ", best_action)
        state[0]=best_action

def run_user_simulation():
    #get blocking locations from user, and run the agent from start to target
    #Display the graph instance and sequence of actions
    new_graph=graph.copy()
    state=[new_graph.graph['start']]
    for node in new_graph.nodes:
        if 'blockage' in new_graph.nodes[node]:
            isBlocked= input("Is node "+str(node)+" blocked? (y/n):")
            if isBlocked=='y':
                state.append(True)
                new_graph.nodes[node]['blockage']=1
            else:
                state.append(False)
                new_graph.nodes[node]['blockage']=0
    print_graph(new_graph)
    print("Simulation start state:",state)
    print("Optimal policy:")
    while state[0]!=new_graph.graph['target']:
        best_action=best_action_for_state[tuple(state)]
        print("Go to ", best_action)
        state[0]=best_action

def is_state_reachable_from_start(start_state,state):
    #check if state is reachable from the start_state
    #path can not go through a node with blockage=1
    #start_state and state have same values for all nodes except the first one
    if start_state[0]==state[0]:
        #same node, so state is reachable
        return True
    if state[0]==graph.graph['target']:
        return False
    if 'blockage' in graph.nodes[state[0]] and state[graph.nodes[state[0]]['index_in_state_format']]:
        #state is blocked, so it is not reachable
        return False
    if start_state[0] in graph.neighbors(state[0]):
        #state is reachable from start state
        return True
    for neighbour in graph.neighbors(start_state[0]):
        if 'blockage' in graph.nodes[neighbour] and start_state[graph.nodes[neighbour]['index_in_state_format']]:
            #neighbour is blocked, so skip it
            continue
        if is_state_reachable_from_start(list(start_state),[neighbour]+list(state[1:])):
            return True
    return False

def find_unreachable_states():
    #find states that are unreachable from the start state
    #for each state, check if it is reachable from the start state
    #path can not go through a node with blockage=1
    #if state is unreachable, add it to is_state_unreachable
    for possible_start_state in states_to_utilities_dict:
        if possible_start_state[0]==graph.graph['start']:
            is_state_reachable[possible_start_state]=True
            is_state_reachable[tuple([graph.graph['target']]+list(possible_start_state[1:]))]=True
            #go through every node with same values as possible_start_state, and check if it is reachable from the start state
            for node in graph.nodes:
                new_state=tuple([node]+list(possible_start_state[1:]))
                if node != graph.graph['start'] and node != graph.graph['target'] and new_state not in is_state_reachable:
                    if is_state_reachable_from_start(possible_start_state,[node]+list(possible_start_state[1:])):
                        #state is unreachable
                        is_state_reachable[new_state]=True
                    else:
                        is_state_reachable[new_state]=False

if __name__ == '__main__':
    global graph
    graph = parse('input4.txt')
    print_graph(graph)
    global states_to_utilities_dict
    states_to_utilities_dict={}
    global best_action_for_state
    best_action_for_state={}
    global is_state_reachable
    is_state_reachable={}
    for node in graph.nodes:
        create_state([node])
    #a state is a list containing the current node and information about the blockages for each node with blockage (could be True,False or None)
    #states_to_utilities_dict is a dictionary containing all possible states_to_utilities_dict, and their utility values
    #for example, states_to_utilities_dict[3, True, False, None] = -1.5
    change=True
    while change:
        change=False
        for state in states_to_utilities_dict:
            if(state[0]==graph.graph['target']):
                #always 0, so skip to next state
                continue
            # print("STATE: ",state)
            #update the utility value of the state, by checking all possible actions and finding the best one
            max_utility_of_action = -float('inf') 
            for action in graph.neighbors(state[0]):
                #action is the node to go to
                #check if action is illegal due to blockage, by checking if graph.nodes[action] has 'blockage' attribute
                if 'blockage' in graph.nodes[action] and state[graph.nodes[action]['index_in_state_format']]==True:
                    #node is blocked, skip to next action
                    continue
                #if state after action is unrachable, skip to next action
                if tuple([action]+list(state[1:])) in is_state_reachable and not is_state_reachable[tuple([action]+list(state[1:]))]:
                    is_state_reachable[tuple([action]+list(state[1:]))]=False
                    continue
                # print("ACTION: ",action)
                #calculate the utility of the state after taking the action
                state_after_action = list(state+tuple())
                #+tuple() makes a copy
                state_after_action[0]=action
                #if there are unknown brittle neighbours of action, then update their value to every possible value
                neighbours_to_reveal = []
                for action_neighbor in graph.neighbors(action):
                    if 'blockage' in graph.nodes[action_neighbor] and state_after_action[graph.nodes[action_neighbor]['index_in_state_format']]==None:    
                        #node is brittle and unrevielied, so update the state to every possible state
                        neighbours_to_reveal.append(action_neighbor)
                #calculate the utility of the state after taking the action, by checking all possible states_to_utilities_dict of the neighbours
                possible_state_to_probability = {}
                get_all_possible_probabilities(state_after_action, neighbours_to_reveal, 1.0 , possible_state_to_probability)
                #possible_state_to_probability is a dictionary containing all possible states_to_utilities_dict of the neighbours, and their probability
                #for example, possible_state_to_probability={(V2,True, False): 0.25, (V2,False, False): 0.75} 

                #print("state ",state," action ",action," possible_state_to_probability ",possible_state_to_probability)
                action_utility= -graph[state[0]][action]['weight']
                
                for state_option in possible_state_to_probability.keys():
                    #print("HERE ",state_option,possible_state_to_probability[state_option])                    
                    action_utility+= possible_state_to_probability[state_option]*states_to_utilities_dict[tuple(state_option)]
                #print(f"state {state} action {action} utility {action_utility}")
                if action_utility > max_utility_of_action:
                    max_utility_of_action = action_utility
                    best_action_for_state[tuple(state)] = action
            if max_utility_of_action != states_to_utilities_dict[state]:
                if max_utility_of_action < -11000:
                    is_state_reachable[state]=False
                    continue
                #print(f"state {state} changed from {states_to_utilities_dict[state]} to {max_utility_of_action}")
                change=True                
            states_to_utilities_dict[state] = max_utility_of_action

    find_unreachable_states()
    print("States: ")
    for state in states_to_utilities_dict:
        if is_state_reachable[state]:
            print(state,'U:',states_to_utilities_dict[state])
        else:
            print(state,'U:','unreachable')

    #print the state of the start node with None for every brittle node
    print("final utility:",states_to_utilities_dict[tuple([graph.graph['start']]+[None]*graph.graph['num_brittle_nodes'])])
    print("Optimal policy:")
    print_optimal_policy(tuple([graph.graph['start']]+[None]*graph.graph['num_brittle_nodes']),0)
    choice=input("Enter 1 for random simulation, or 2 for user simulation, 3 for exit:")
    while(choice != '3'):
        if choice == '1':
            run_random_simulation()
        else:
            run_user_simulation()
        choice=input("Enter 1 for random simulation, or 2 for user simulation, 3 for exit:")
    print("Goodbye!")
