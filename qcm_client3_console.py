#! /usr/bin/python3
# -*- coding: utf-8 -*-
# (c) Angelico Denis

# Définition d'un client réseau gérant en parallèle l'émission
# et la réception des messages (utilisation de 2 THREADS).

# adresse IP et port utilisé par le serveur

import socket, sys, threading

HOSTDEFAULT = "127.0.0.1" # ou "localhost"
HOST = input("Adresse IP du serveur ? ")
if HOST == "":
    HOST = HOSTDEFAULT
PORTDEFAULT = 50026
PORT = input("Numéro du port ? ")
if PORT == "":
    PORT = PORTDEFAULT
else:
    PORT = int(PORT)
    

class ThreadReception(threading.Thread):
    """objet thread gérant la réception des messages"""
    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.connexion = conn  # réf. du socket de connexion

    def run(self):
        while True:
            try:
                # en attente de réception
                message_recu = self.connexion.recv(4096)
                message_recu = message_recu.decode(encoding='UTF-8')
                print(message_recu)
            except:
                # fin du thread
                break
            
        print("ThreadReception arrêté. Connexion interrompue.")
        self.connexion.close()

class ThreadEmission(threading.Thread):
    """objet thread gérant l'émission des messages"""
    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.connexion = conn   # réf. du socket de connexion

    def run(self):
        while True:
            message_emis = input()
            try:
                # émission
                self.connexion.send(bytes(message_emis,'UTF-8'))
            except:
                # fin du thread
                break
            
        print("ThreadEmission E arrêté. Connexion interrompue.")
        self.connexion.close()

# Programme principal - Établissement de la connexion
# protocoles IPv4 et TCP
mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mySocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
try:
    mySocket.connect((HOST, PORT))
except socket.error:
    print("La connexion a échoué.")
    sys.exit()

# Dialogue avec le serveur : on lance deux threads pour gérer
# indépendamment l'émission et la réception des messages
th_R = ThreadReception(mySocket)
th_R.start()
th_E = ThreadEmission(mySocket)
th_E.start()
