#! /usr/bin/python3
# -*- coding: utf-8 -*-

# python 3
# (C) Angelico Denis

import socket, sys, threading, time

# variables globales

# adresse IP et port utilisés par le serveur
HOST = ""
PORT = 50026

NOMBREJOUEUR = 5 # nmbnre des joueurs
dureemax = 120 # durée max question ; en secondes
pause = 5 # pause entre deux questions  ; en secondes

dict_clients = {}  # dictionnaire des connexions clients
dict_pseudos = {}  # dictionnaire des pseudos
dict_reponses = {}  # dictionnaire des réponses des clients
dict_scores = {} # dictionnaire des scores de la dernière question
dict_scores_total = {}

# liste des questions
list_question = []
sujet = """
Quel système d'exploitation est sous licence libre ?
    1) Windows
    2) MacOS
    3) Linux
    0) Je ne sais pas"""

bonnereponse = 3
list_question.append((sujet,bonnereponse))

sujet = """
Le Web et Internet...
    1) C'est la même chose !
    2) Le Web fait parti d'Internet
    3) Internet fait parti du Web
    0) Je ne sais pas"""

bonnereponse = 2
list_question.append((sujet,bonnereponse))

sujet = """
Parmi ces langages informatiques, lequel n'est pas un langage de programmation ?
    1) langage HTML
    2) langage C
    3) langage Python
    0) Je ne sais pas"""

bonnereponse = 1
list_question.append((sujet,bonnereponse))


class ThreadClient(threading.Thread):
    '''dérivation de classe pour gérer la connexion avec un client'''
    
    def __init__(self,conn):

        threading.Thread.__init__(self)
        self.connexion = conn
        
        # Mémoriser la connexion dans le dictionnaire
        
        self.nom = self.getName() # identifiant du thread "<Thread-N>"
        dict_clients[self.nom] = self.connexion
        dict_scores[self.nom] = 0
        dict_scores_total[self.nom] = 0
        
        print("Connexion du client", self.connexion.getpeername(),self.nom ,self.connexion)
        
        message = bytes("Vous êtes connecté au serveur.\n","utf-8")
        self.connexion.send(message)
        
        
    def run(self):
        
        # Choix du pseudo    
        
        self.connexion.send(b"Entrer un pseudo :\n")
        # attente réponse client
        pseudo = self.connexion.recv(4096)
        pseudo = pseudo.decode(encoding='UTF-8')
        
        dict_pseudos[self.nom] = pseudo
        
        print("Pseudo du client", self.connexion.getpeername(),">", pseudo)
        
        message = b"Attente des autres clients...\n"
        self.connexion.send(message)
    
        # Réponse aux questions
       
        while True:
            
            try:
                # attente réponse client
                reponse = self.connexion.recv(4096)
                reponse = reponse.decode(encoding='UTF-8')
            except:
                # fin du thread
                break
                
            # on enregistre la première réponse
            # les suivantes sont ignorées
            if self.nom not in dict_reponses:
                dict_reponses[self.nom] = reponse, time.time()
                print("Réponse du client",self.nom,">",reponse)

        print("\nFin du thread",self.nom)
        self.connexion.close()

def MessagePourTous(message):
    """ message du serveur vers tous les clients"""
    for client in dict_clients:
        dict_clients[client].send(bytes(message,"utf8"))
        
        
# Initialisation du serveur
# Mise en place du socket avec les protocoles IPv4 et TCP
mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mySocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
try:
    mySocket.bind((HOST, PORT))
except socket.error:
    print("La liaison du socket à l'adresse choisie a échoué.")
    sys.exit()
print("Serveur prêt (port",PORT,") en attente de clients...")
mySocket.listen(5)


# len(dict_clients) -> nb de joueurs connectés

while len(dict_clients) < NOMBREJOUEUR:
    # Attente connexion nouveau client
    try:
        connexion, adresse = mySocket.accept()
    except:
        sys.exit()
    # Créer un nouvel objet thread pour gérer la connexion
    th = ThreadClient(connexion)
    # The entire Python program exits when no alive non-daemon threads are left
    th.setDaemon(1)
    th.start()
    

while len(dict_pseudos) < NOMBREJOUEUR:
    # on attend que tout le monde ait entré son pseudo
    pass


MessagePourTous("\nLa partie va commencer !\n")

# questions
index = 0
for question in list_question:
    index += 1
    MessagePourTous("\nNouvelle question dans " + str(pause) + " secondes...\n")
    time.sleep(pause)

    timedebut = time.time()
    timefin = timedebut + dureemax
    dict_reponses = {}  # liste des réponses des clients
    dict_scores = {}

    message = """--------------------
Question """ +str(index)
    message += question[0]
    message += """
Réponse > """
    MessagePourTous(message)
        
    while time.time() < timefin and len(dict_reponses) <  NOMBREJOUEUR:
         # on attend que tout le monde ait répondu
         # ou que le délai soit écoulé
         pass

    # résultats et scores
    bonnereponse = question[1]

    clientbonus = ""
    for client in dict_reponses:
        try:
            reponse = int(dict_reponses[client][0])
            if reponse == bonnereponse:
                # bonne réponse 2 pts
                dict_scores[client] = 2
                
                if clientbonus == "":
                    clientbonus = client
                else:
                    # comparaison des durées
                    if dict_reponses[client][1] < dict_reponses[clientbonus][1]:
                        clientbonus = client
                
            elif reponse != 0:
                # mauvaise réponse -1 pt
                dict_scores[client] = -1
                
            else:
                # réponse je ne sais pas 0 pt
                dict_scores[client] = 0
            
        except:
            # mauvaise réponse -1 pt
            dict_scores[client] = -1
            
        dict_scores_total[client] += dict_scores[client]    
                
    # bonus pour la première bonne réponse
    if clientbonus != "":
        dict_scores[clientbonus] += 1
        dict_scores_total[clientbonus] += 1


    message = """

Résultat :
Client       Score    Temps
"""

    for client in dict_reponses:
        duree = dict_reponses[client][1] - timedebut
        message += "%-10s  %3d pt    %3.2f\"\n"  %(dict_pseudos[client],dict_scores[client],duree)
    message +="""    
Total :
Client       Score
""" 

    for client in dict_scores_total:
        message += "%-10s  %3d pt\n"  %(dict_pseudos[client],dict_scores_total[client])

    MessagePourTous(message)

# Fin
MessagePourTous("\nFIN\nVous pouvez fermer l'application...\n")

# fermeture des sockets
for client in dict_clients:
    dict_clients[client].close()
    print("Déconnexion du socket", client)

input("\nAppuyer sur Entrée pour quitter l'application...\n")
# fermeture des threads (daemon) et de l'application
