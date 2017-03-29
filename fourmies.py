#Utiliser librairie CSV, puis fonction DICT READER pour lire dans le fichier CSV
import csv
import matplotlib.pyplot as plt
import networkx as nx

def creationGraph():
    #import du fichier csv de la ville de nantes, le délimiteur est \t
    with open('VOIES_NM_.csv') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        G=nx.Graph()
        #une variable i est créée pour gérer le cas où des TENANTS ou des ABOUTISSANTS sont vides
        i = 0
        for row in reader:
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
                G.add_edge(i, row['ABOUTISSANT'], weight=weight)
                i = i + 1
            #Gère le cas si ABOUTISSANT est vide et TENANT ne l'est pas, et ajoute une edge
            elif(row['ABOUTISSANT'] == "" and row['TENANT'] != ""):
                G.add_edge(row['TENANT'], i, weight=weight)
                i = i + 1
            #Gère le cas si ABOUTISSANT et TENANT sont vides, et ajoute une edge
            elif((row['TENANT'] == "") and row['ABOUTISSANT'] == ""):
                G.add_edge(i, i+1, weight=weight)
                i = i + 2
            #Gère le cas si ABOUTISSANT et TENANT sont remplis, et ajoute une edge
            else:
                G.add_edge(row['TENANT'], row['ABOUTISSANT'], weight=weight)

        # nx.draw_circular(G)
        # plt.show()

        return G

def fourmiam(G):
    visited = []
    blackListed = []
    nodes = G.nodes()
    depart = currentNode = nodes[G.nodes().index("REZE six")]
    arrive = nodes[G.nodes().index("REZE deux")]
    print("depart:", depart)
    print("arrive:", arrive)
    visited.append(currentNode)
    #Tant que la fourmi n'est pas arrivée on exécute
    while(currentNode != arrive):
        #On check les rues voisines (G.neighbors), et on stock dans la variable rues
        neighbors = G.edges(currentNode, data=True)
        # print("currentNode:", currentNode)
        # print("neighbors:",neighbors)
        #On fait un choix pondéré entre les rues voisines (en fonction des phéromones + en random)
        nextNode = choiceNeighbors(neighbors,visited,blackListed)
        # print(nextNode)

        if nextNode == -1:
            #Tant que la fourmie est bloquée (impasse ou chemin déjà visité)
            while(len(visited) > 1 and len(G.neighbors(currentNode)) < 1):
                #On ajoute la rue bloqué dans un tableau rues_invalides
                blackListed.append(visited[len(visited) -1])
                visited.pop()
                #On fait marche arrière
                currentNode = visited[len(visited) -1]
                #Si retour au point d'origine et que l'on a pas d'autre chemin utilisables on s'arrête
                if depart == currentNode:
                    return -1
        else:
            #Créer un historique par fourmies des trajets empruntés
            visited.append(nextNode)
            currentNode = nextNode

    print("Fini")

# fait le choix du prochain noeud
def choiceNeighbors(neighbors,visited,blackListed):
    print(len(neighbors))
    print(neighbors)
    for i in range(len(neighbors)):
        if neighbors[i] not in visited and neighbors[i] not in blackListed:
            return neighbors[i]
    return -1

def main():
    G = creationGraph()
    fourmiam(G)

# le départ d'une fourmie est
main()

    #pos=nx.spring_layout(G)
    #edge_labels=dict([((u,v,),d['rue'])for u,v,d in G.edges(data=True)])
    #nx.draw_networkx_edge_labels(G,pos,edge_labels=edge_labels)

    #nx.draw_circular(G)
    #plt.show()
        #print(row['COMMUNE'], row['BI_MAX'])
