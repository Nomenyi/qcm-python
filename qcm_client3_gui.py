#! /usr/bin/python3
# -*- coding: utf-8 -*-

# python version 3
# (C) Angelico Denis

# 1 seul thread (en réception)

from tkinter import *
from tkinter.messagebox import *

import socket, threading

class ThreadReception(threading.Thread):
    """objet thread gérant la réception des messages"""
    def __init__(self, conn):
        threading.Thread.__init__(self)
        ref_socket[0] = conn
        self.connexion = conn  # réf. du socket de connexion
              
    def run(self):
        while True:
            try:
                # en attente de réception
                message_recu = self.connexion.recv(4096)
                message_recu = message_recu.decode(encoding='UTF-8')
                
                ZoneReception.config(state=NORMAL)
                ZoneReception.insert(END,message_recu)
                # défilement vers le bas
                ZoneReception.yview_scroll(1,"pages")
                # lecture seule
                ZoneReception.config(state=DISABLED)
                
                if "FIN" in message_recu:
                    # fin du qcm
                    global CONNEXION
                    CONNEXION = False
                    
            except socket.error:
                pass
                
def envoyer():
    if CONNEXION == True:
        try:
            message = MESSAGE.get()
            MESSAGE.set("")
            
            ZoneReception.config(state=NORMAL)
            ZoneReception.insert(END,message+"\n")
            
            # lecture seule
            ZoneReception.config(state=DISABLED)
        
            # émission 
            ref_socket[0].send(bytes(message,"UTF8"))
            
        except socket.error:
            pass
        

def ConnexionServeur():
    
    # Établissement de la connexion
    # protocoles IPv4 et TCP
    global CONNEXION

    if CONNEXION == False:
        try:
            mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            mySocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            mySocket.connect((HOST.get(), PORT.get()))
            # Dialogue avec le serveur : on lance un thread pour gérer la réception des messages
            th_R = ThreadReception(mySocket)
            th_R.start()
            CONNEXION = True
            ButtonEnvoyer.configure(state = NORMAL)
            ButtonConnexion.configure(state = DISABLED)
            
        except socket.error:
            showerror('Erreur','La connexion au serveur a échoué.')
        
        
# état de la connexion
CONNEXION = False

# création ref
ref_socket = {}

# Création de la fenêtre principale (main window)
Mafenetre = Tk()

Mafenetre.title('QCM en réseau - client GUI')

# Frame1 : paramètres serveur
Frame1 = Frame(Mafenetre,borderwidth=2,relief=GROOVE)

Label(Frame1, text = "Hôte").grid(row=0,column=0,padx=5,pady=5,sticky=W)
HOST = StringVar()
HOST.set('192.168.10.3')
Entry(Frame1, textvariable= HOST).grid(row=0,column=1,padx=5,pady=5)

Label(Frame1, text = "Port").grid(row=1,column=0,padx=5,pady=5,sticky=W)
PORT = IntVar()
PORT.set(50026)
Entry(Frame1, textvariable= PORT).grid(row=1,column=1,padx=5,pady=5)

ButtonConnexion = Button(Frame1, text ='Connexion au serveur',command=ConnexionServeur)
ButtonConnexion.grid(row=0,column=2,rowspan=2,padx=5,pady=5)

Frame1.grid(row=0,column=0,padx=5,pady=5,sticky=W+E)


# Frame 2 : zone de réception (zone de texte + scrollbar)
Frame2 = Frame(Mafenetre,borderwidth=2,relief=GROOVE)

# height = 10 <=> 10 lignes
ZoneReception = Text(Frame2,width =80, height =30,state=DISABLED)
ZoneReception.grid(row=0,column=0,padx=5,pady=5)

scroll = Scrollbar(Frame2, command = ZoneReception.yview)

ZoneReception.configure(yscrollcommand = scroll.set)

scroll.grid(row=0,column=1,padx=5,pady=5,sticky=E+S+N)

Frame2.grid(row=1,column=0,padx=5,pady=5)

# Frame 3 : envoi de message au serveur
Frame3 = Frame(Mafenetre,borderwidth=2,relief=GROOVE)

MESSAGE = StringVar()
Entry(Frame3, textvariable= MESSAGE).grid(row=0,column=0,padx=5,pady=5)


ButtonEnvoyer = Button(Frame3, text ='Envoyer', command = envoyer,state=DISABLED)
ButtonEnvoyer.grid(row=0,column=1,padx=5,pady=5)

Frame3.grid(row=2,column=0,padx=5,pady=5,sticky=W+E)

Mafenetre.mainloop()
