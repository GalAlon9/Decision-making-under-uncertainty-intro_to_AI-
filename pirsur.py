import networkx as nx
import matplotlib.pyplot as plt

def parse(file:str):
    graph = nx.Graph()
    #open file
    #print directory
    f = open(file, 'r')
    #remove empty lines
    lines = [line for line in f if line.strip()]
    #first line after "#N" is the number of nodes
    num_nodes = int(lines[0].split(' ')[1])
    lineNum = 1

    #add edges
    while(lineNum < len(lines) and lines[lineNum][1] == 'E'):
        line = lines[lineNum].split(' ')
        graph.add_edge(int(line[1]), int(line[2]), weight=float(line[3][1:]))
        lineNum += 1
    #add blockage probabilities
    #input is in the form of "B 1 0.5" where 1 is the node and 0.5 is the blockage probability
    num_brittle_nodes=0
    while(lineNum < len(lines) and lines[lineNum][1] == 'B'):
        line = lines[lineNum].split(' ')
        graph.nodes[int(line[1])]['blockage'] = float(line[2])
        graph.nodes[int(line[1])]['index_in_state_format'] = num_brittle_nodes+1
        #index_in_state_format is the index of the node in the state list
        lineNum += 1
        num_brittle_nodes += 1
    
    graph.graph['num_brittle_nodes'] = num_brittle_nodes

    #read start and target
    start = int(lines[lineNum].split(' ')[1])
    graph.graph['start'] = start
    target = int(lines[lineNum+1].split(' ')[1])
    graph.graph['target'] = target
    #add edge from start to target with cost of 10000
    graph.add_edge(start, target, weight=10000)
    return graph