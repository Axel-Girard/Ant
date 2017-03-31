#Utiliser librairie CSV, puis fonction DICT READER pour lire dans le fichier CSV
import csv
import matplotlib.pyplot as plt
import networkx as nx
from random import randint

nbFourmi = 100
nbGeneration = 100

def creationGraph():
    #import du fichier csv de la ville de nantes, le délimiteur est \t
    with open('VOIES_NM_.csv') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        G=nx.Graph()
        #une variable i est créée pour gérer le cas où des TENANTS ou des ABOUTISSANTS sont vides
        i = 0
        for row in reader:
            #une variable name contiendra le nom de la rue, correspondant au noeud
            name = row['COMMUNE'] + ' ' + row['LIBELLE']
            #une variable weight contiendra la taille des rues, calculée par BI_MAX - BI_MIN et BP_MAX - BP_MIN
            weight = 0
            #Si BI_MAX et BI_MIN n'est pas vide, alors on calcul la taille de la rue
            if(row["BI_MAX"] != "" and row['BI_MIN'] != ""):
                weight = int(row['BI_MAX']) - int(row['BI_MIN'])
            #Si BP_MAX et BP_MIN n'est pas vide, alors on calcul la taille de la rue
            if(row['BP_MAX'] != "" and row['BP_MIN'] != ""):
                weight = weight + int(row['BP_MAX']) - int(row['BP_MIN'])
            #Gère le cas si TENANT est vide et ABOUTISSANT ne l'est pas, et ajoute une edge
            if(row['TENANT'] == "" and row['ABOUTISSANT'] != ""):
                G.add_edge(i, row['ABOUTISSANT'], weight=weight, name=name, pheromone=0)
                i = i + 1
            #Gère le cas si ABOUTISSANT est vide et TENANT ne l'est pas, et ajoute une edge
            elif(row['ABOUTISSANT'] == "" and row['TENANT'] != ""):
                G.add_edge(row['TENANT'], i, weight=weight, name=name, pheromone=0)
                i = i + 1
            #Gère le cas si ABOUTISSANT et TENANT sont vides, et ajoute une edge
            elif((row['TENANT'] == "") and row['ABOUTISSANT'] == ""):
                G.add_edge(i, i+1, weight=weight, name=name, pheromone=0)
                i = i + 2
            #Gère le cas si ABOUTISSANT et TENANT sont remplis, et ajoute une edge
            else:
                G.add_edge(row['TENANT'], row['ABOUTISSANT'], weight=weight, name=name, pheromone=0)

        #pos=nx.spring_layout(G)
        #edge_labels=dict([((u,v,),d['rue'])for u,v,d in G.edges(data=True)])
        #nx.draw_networkx_edge_labels(G,pos,edge_labels=edge_labels)

        # nx.draw_circular(G)
        # plt.show()

        return G

def fourmiam(G):
    G = G.copy()
    visited = []
    blackListed = []
    nodes = G.nodes()
    weight = 0
    if "REZE six" in nodes:
        start = currentEdge = nodes[G.nodes().index("REZE six")]
    elif "REZE six" in G.edges():
        start = currentEdge = G.edges("REZE six")
    else:
        return G
    end = nodes[G.nodes().index("REZE deux")]
    print("start:", start)
    print("end:", end)
    visited.append(currentEdge)

    #Tant que la fourmi n'est pas arrivée on exécute
    while(currentEdge != end):
        #On check les rues voisines (G.neighbors), et on stock dans la variable rues
        neighbors = findNeighbors(G, currentEdge)
        #On fait un choix pondéré entre les rues voisines (en fonction des phéromones + en random)
        nextNode = choiceNeighbors(neighbors,visited,blackListed,G,end)

        if nextNode == -1:
            #Si on n'est pas bloqué au départ
            if(currentEdge != start):
                #On ajoute la rue bloqué dans un tableau rues invalides
                blackListed.append(currentEdge)
                #On fait marche arrière
                print("pop",visited.pop())
                currentEdge = visited[len(visited)-1]
            else:
                #Si on est bloqué au départ on arrête la fourmi
                return G
        else:
            #Créer un historique par fourmis des trajets empruntés
            visited.append(nextNode)
            currentEdge = nextNode

    pheromone = 100
    for v in visited:
        G.edges(v, data=True)[0][2]['pheromone'] = int(pheromone/len(visited))

    return G

# fait le choix du prochain noeud
def choiceNeighbors(neighbors,visited,blackListed,G,end):
    choices = []
    for edge in neighbors:
        street = edge[2]
        if(type(street) is dict and 'name' in street):
            if street['name'] in G.nodes():
                edges = G.edges(street['name'])
                for edge in edges:
                    for e in edge:
                        if(type(e) is str):
                            if e not in visited and e not in blackListed and e != 'Impasse':
                                choices.append(e)
    if len(choices) >= 1:
        newlist = []
        # déduplication des valeurs
        for i in choices:
            if i not in newlist:
                newlist.append(i)
        choice = newlist[randint(0,len(newlist)-1)]
        return choice
    else:
        return -1

# renvoie tous les edges possible à partir du currentEdge
def findNeighbors(G, currentEdge):
    edges = G.edges(currentEdge, data=True)
    for edge in G.edges(data=True):
        if edge[2]['name'] == str(currentEdge):
            edges.append(edge)
    sortEdge(edges, currentEdge)
    return edges

#Standardise les edges pour toujours avoir le prochain noeud possible dans les arguments
def sortEdge(edges, currentEdge):
    for edge in edges:
        edge = list(edge)
        if(edge[2]['name'] == str(currentEdge)):
            if(type(edge[0]) is str):
                tmp = edge[2]['name']
                edge[2]['name'] = edge[0]
                edge[0] = tmp
                if(type(edge[1]) is str):
                    e = edge
                    e[2] = e[2].copy()
                    e[2]['name'] = e[1]
                    e[1] = tmp
                    e = tuple(e)
                    edges.append(e)
            elif(type(edge[1]) is str):
                tmp = edge[2]['name']
                edge[2]['name'] = edge[1]
                edge[1] = tmp
            edge = tuple(edge)
    return edges

def main():
    G = creationGraph()
    graphes = []
    for i in range(nbGeneration):
        print('')
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("       >> New generation <<")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print('')
        graphes = []
        for j in range(nbFourmi):
            graphes.append(fourmiam(G))
        for graphe in graphes:
            for j in range(len(graphe.edges())):
                G.edges(data=True)[j][2]['pheromone'] += graphe.edges(data=True)[j][2]['pheromone']
        # on supprime une partie des phéromones pour enlever les résidues incohérent
        for edge in G.edges(data=True):
            print(edge[2]['pheromone'], edge[0], edge[1])
            if edge[2]['pheromone'] > 30:
                edge[2]['pheromone'] -= 30


main()
