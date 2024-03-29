# Trophée NSI
# Nom du projet : JDLAssistant
# Par Evann Gibrat et Matthieu Vauche
# Du lycé Albert Sorel

'''Pour l'execution du programme il vous faut Internet, l image du lycé : logo_lycee.jpg et quelques modules python : sqlite3, csv, requests, bs4 et Tkinter.'''

import sqlite3
import csv
import requests
from bs4 import BeautifulSoup
import os
from tkinter import *
from tkinter import font
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image

# creation toutes les tables
def creer_base_de_donnees(): # creation des differentes tables
    conn = sqlite3.connect('ma_base_de_donnees.db')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS eleves(id_eleve INT , Nom TEXT, prenom TEXT, genre TEXT, classe TEXT, PRIMARY KEY(id_eleve))')
    cur.execute('CREATE TABLE IF NOT EXISTS formation(id_formation INT, Nom_formation TEXT, adresse_site TEXT, DATES TEXT , horaire_1 TEXT , horaire_2 TEXT , lieu TEXT,PRIMARY KEY(id_formation))')
    cur.execute('CREATE TABLE IF NOT EXISTS inscriptions_jdl(id_formation INT NOT NULL , nombre_eleves INT NOT NULL, FOREIGN KEY (id_formation) REFERENCES formation(id_formation))')
    cur.execute('CREATE TABLE IF NOT EXISTS inscriptions(id_formation INT NOT NULL, id_eleve INT , FOREIGN KEY (id_formation) REFERENCES formation(id_formation),FOREIGN KEY (id_eleve) REFERENCES eleves(id_eleve) )')
    conn.commit()
    conn.close()

# remplissage de la base

def remplir_eleve():
    conn = sqlite3.connect('ma_base_de_donnees.db')  #connexion à la base de données
    cur = conn.cursor()
    fichier_donnees = open('Classes_Terminales_2024_.csv', 'r', encoding='utf-8') # Ouverture du fichier CSV contenant les données des élèves
    CSVClasses_Terminales_2024_ = csv.DictReader(fichier_donnees, delimiter=",")
    for ligne in CSVClasses_Terminales_2024_:   # Parcours des lignes du fichier CSV
        # Vérification si l'élève existe déjà dans la base de données
        cur.execute("SELECT id_eleve FROM eleves WHERE id_eleve = ?", (ligne['id_eleve'],))
        existe = cur.fetchone()
        if existe is None:  # Insertion de l'élève dans la base de données s'il n'existe pas déjà
            cur.execute("INSERT INTO eleves(id_eleve, Nom, Prenom, genre, Classe) VALUES (:id_eleve, :Nom, :Prenom, :genre, :Classe)", ligne)
            conn.commit()
    cur.close()
    conn.close()

def inscrire_eleve(id_formation, id_eleve):
    informations = (id_formation, id_eleve)  # tuple contenant les informations de l'inscription
    conn = sqlite3.connect('ma_base_de_donnees.db')   # connection à la base de données
    cur = conn.cursor()
    # exécuter la requête SQL pour insérer les informations dans la table 'inscriptions'
    cur.execute("INSERT INTO inscriptions (id_formation, id_eleve) VALUES (?, ?)", informations)
    conn.commit()
    conn.close()

creer_base_de_donnees()
remplir_eleve()

if not os.path.exists('Formation_jdl.csv'):
    print("Le processus est en cours de traitement.")
    def scrape_page(soup, quotes):
        # retrieving all the quote <div> #<div class="container"> HTML element on the page
        quote_elements = soup.find_all('body')    # soup.find_all('div', class_='body')
        # iterating over the list of quote elements
        # to extract the data of interest and store it
        # in quotes
        for quote_element in quote_elements:
            # on essaie de trouver les elements suivants :
            try:
                # extracting the name of the quote
                nom = quote_element.find('h4',class_='h4-table').text
                # extracting the number of the quote
                numero=quote_element.find('h1',class_='decal h1-table').text
                tag_date=quote_element.select('tr:nth-child(10)>td:nth-child(2)')       #  le select donne la date
            # store the list of tag strings in a list of date
                list_dates = []
                for date_element in tag_date:
                    list_dates.append(date_element.text)
                tag_horaire=quote_element.select('tr:nth-child(11)>td:nth-child(2)')    #  le select donne l'horaire
                # store the list of tag strings in a list of time
                list_horaires = []
                for horaire_element in tag_horaire:
                    list_horaires.append(horaire_element.br.previous_sibling) # # donne le premier horaire
                    if horaire_element.br.next_sibling != None :
                        list_horaires.append(horaire_element.br.next_sibling)  # donne le deuxième horaire
                tag_lieu=quote_element.select('tr:nth-child(4)>td:nth-child(2)')    #  le select donne le lieu
                list_lieu = []
                for lieu_element in tag_lieu:
                    list_lieu.append(lieu_element.br.next_sibling)
                    list_lieu.append(lieu_element.br.previous_sibling) # donne l'adresse
                nbr_horaires=len(list_horaires)
                if nbr_horaires==1:     # un seul horaire à inscrire
                    quotes.append(
                        {   'Numéro de la formation': numero,
                            'Intitulé de la formation': nom,
                            'page web' : base_url,
                            'date' : list_dates[0],
                            'horaire(1)': list_horaires[0],
                            'horaire(2)': None,
                            'lieu': list_lieu[0]
                        }
                        )
                else :
                    quotes.append(
                        {   'Numéro de la formation': numero,
                            'Intitulé de la formation': nom,
                            'page web' : base_url,
                            'date' : list_dates[0],
                            'horaire(1)': list_horaires[0],
                            'horaire(2)': list_horaires[1],
                            'lieu': list_lieu[0]
                        }
                        )

                # si formation n existe pas
            except :
                pass  # Ignorer l'impression si la formation n'existe pas
    base_url ='https://jdl.ac-caen.fr/index.php?formation=1'
    # defining the User-Agent header to use in the GET request below
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    }
    # retrieving the target web page
    page = requests.get(base_url, headers=headers)
    # parsing the target web page with Beautiful Soup
    soup = BeautifulSoup(page.text, 'html.parser')
    # initializing the variable that will contain
    # the list of all quote data
    quotes = []
    # scraping the home page
    scrape_page(soup, quotes)
    page = requests.get(base_url, headers=headers)
    # parsing the new page
    soup = BeautifulSoup(page.text, 'html.parser')
    # scraping the new page
    scrape_page(soup, quotes)
    # parcourir les pages des formations
    for num_formation in range(2,438):
        # the url of the home page of the target website
        base_url ='https://jdl.ac-caen.fr/index.php?formation='+str(num_formation)
        # getting the new page
        page = requests.get(base_url, headers=headers)
        # parsing the new page
        soup = BeautifulSoup(page.text, 'html.parser')
        # scraping the new page
        scrape_page(soup, quotes)
        # reading  the "quotes.csv" file and creating it
        # if not present
        csv_file = open('Formation_jdl.csv', 'w', encoding='utf-8', newline='')
        # initializing the writer object to insert data
        # in the CSV file
        writer = csv.writer(csv_file)
        # writing the header of the CSV file
        writer.writerow(['id_formation', 'Nom_formation', 'adresse_site','date','horaire(1)','horaire(2)','lieu'])
        # writing each row of the CSV
        for quote in quotes:
            writer.writerow(quote.values())
        # terminating the operation and releasing the resources
        csv_file.close()

def remplir_formation():
    conn = sqlite3.connect('ma_base_de_donnees.db')  # Connexion à la base de données
    cur = conn.cursor()
    fichier_donnees = open('Formation_jdl.csv', 'r', encoding='utf-8')  # Ouverture du fichier CSV contenant les données des formations
    CSVFormation_jdl = csv.DictReader(fichier_donnees, delimiter=",")
    for ligne in CSVFormation_jdl:  # Parcours des lignes du fichier CSV
        # Vérification si la formation existe déjà dans la base de données
        cur.execute("SELECT id_formation FROM formation WHERE id_formation = ?", (ligne['id_formation'],))
        existe = cur.fetchone()
        if existe is None:
            #Insertion de la formation dans la base de données si elle n'existe pas déjà
            cur.execute("INSERT INTO formation(id_formation, Nom_formation, adresse_site,DATES,horaire_1,horaire_2,lieu) VALUES (:id_formation, :Nom_formation, :adresse_site,:date,:horaire(1),:horaire(2),:lieu)", ligne)
            conn.commit()
    cur.close()
    conn.close()

remplir_formation()

print("Le processus est terminé.")

# Interface graphique

#fonction

def tous_prenoms_noms_par_classe(classe):
    conn = sqlite3.connect('ma_base_de_donnees.db')  # Connexion à la base de données
    cur = conn.cursor()
    cur.execute("SELECT Prenom, Nom FROM eleves WHERE Classe = ?", (classe,))  # Exécution d'une requête SQL pour récupérer les prénoms et noms des élèves de la classe donnée
    prenoms_noms = cur.fetchall()  # Récupération de tous les prénoms et noms
    conn.close()
    return prenoms_noms  # Retourner la liste des prénoms et noms

def toutes_classes_unique():
    conn = sqlite3.connect('ma_base_de_donnees.db')  # Connexion à la base de données
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT classe FROM eleves")  # Exécution d'une requête SQL pour récupérer toutes les classes de facon uniques des élèves
    classes = [row[0] for row in cur.fetchall()]  # Récupération des classes uniques sous forme d'une liste
    conn.close()
    return classes  # Retourner la liste des classes uniques

def toutes_formations():
    conn = sqlite3.connect('ma_base_de_donnees.db') # Connexion à la base de données
    cur = conn.cursor()
    cur.execute("SELECT id_formation, Nom_formation FROM formation")  # Exécution d'une requête SQL pour récupérer les ID et noms de toutes les formations
    formations = cur.fetchall()  # Récupération des données des formations sous forme de liste
    conn.close()
    return formations  # Retourner la liste des formations

def on_select_classe(event):
    classe_selectionnee = combo_classe.get()  # Récupérer la classe sélectionnée depuis la combobox des classes
    identités = tous_prenoms_noms_par_classe(classe_selectionnee)  # Appeler la fonction pour récupérer les prénoms et noms des élèves de la classe sélectionnée
    combo_eleve['values'] = identités  # Mettre à jour les valeurs de la combobox des prénoms avec les prénoms récupérés
    combo_eleve.set("Sélectionnez votre identité")  # Réinitialiser la sélection du prénom

def on_select_formation(event):
    id_formation_selectionne = combo_id_formation.get()  # Récupérer l'ID de la formation sélectionnée depuis la combobox des ID de formation

def trouver_nom_formation(id_formation):
    for formation in toutes_formations():  # Parcourir toutes les formations pour trouver celle avec l'ID spécifié
        if formation[0] == id_formation:  # Si l'ID correspond, retourner le nom de la formation
            return formation[1]
    return None  # Si aucune formation n'est trouvée avec l'ID spécifié, retourner None

def select_formations():
    id_formation = combo_id_formation.get()  # Récupérer l'ID de la formation sélectionnée depuis la combobox des ID de formation
    conn = sqlite3.connect('ma_base_de_donnees.db')  # Connexion à la base de données
    cur = conn.cursor()
    cur.execute("SELECT id_formation, Nom_formation FROM formation WHERE id_formation = ?", (id_formation,))  # Exécution d'une requête SQL pour récupérer le nom de la formation avec l'ID spécifié
    formation = cur.fetchall()  # Récupération du nom de la formation
    conn.close()

    return f"{formation[0][0]} - {formation[0][1]}" # Retourner l'id et le nom de la formation

def select_id():
    # Récupérer le prénom et le nom sélectionnés depuis la combobox des prénoms
    prenom_nom = combo_eleve.get().split()  # Séparer prénom et nom
    prenom = prenom_nom[0]
    nom = prenom_nom[-1]  #le dernier élément est le nom
    conn = sqlite3.connect('ma_base_de_donnees.db')  # Connexion à la base de données
    cur = conn.cursor()
    # Exécution d'une requête SQL pour récupérer l'ID de l'élève avec le prénom et le nom spécifiés
    cur.execute("SELECT id_eleve FROM eleves WHERE Prenom = ? AND Nom = ?", (prenom, nom))  # Passer prénom et nom comme arguments
    eleve = cur.fetchone()  # Récupération de l'ID de l'élève
    conn.close()
    return eleve  # Retourner l'ID de l'élève

def count_formations(id_formation):
    # Connexion à la base de données
    conn = sqlite3.connect('ma_base_de_donnees.db')
    cur = conn.cursor()
    # Exécution d'une requête SQL pour compter le nombre d'élèves inscrits à une formation spécifique
    cur.execute("SELECT nombre_eleves FROM inscriptions_jdl WHERE id_formation = ?", (id_formation,))
    nombre_eleves_formation=cur.fetchone() # Récupération du résultat de la requête (nombre d'élèves inscrits)
    # Fermeture de la connexion à la base de donnée
    conn.commit()
    conn.close()
    return nombre_eleves_formation    # Retourner le nombre d'élèves inscrits

def update_inscriptions_jdl(id_formation, nombre_eleves_formation):
    # Connexion à la base de données
    conn = sqlite3.connect('ma_base_de_donnees.db')
    cur = conn.cursor()
    # Exécution d'une requête SQL pour mettre à jour le nombre d'élèves inscrits à une formation dans la table inscriptions_jdl
    cur.execute("UPDATE inscriptions_jdl SET nombre_eleves = ? WHERE id_formation = ?",(nombre_eleves_formation, id_formation))
    # Validation de la transaction et fermeture de la connexion à la base de données
    conn.commit()
    conn.close()

def insert_inscriptions_jdl(id_formation, nombre_eleves_formation):
    conn = sqlite3.connect('ma_base_de_donnees.db') # Connexion à la base de données
    cur = conn.cursor()
    # Exécution d'une requête SQL pour insérer une nouvelle ligne dans la table inscriptions_jdl
    cur.execute("INSERT INTO inscriptions_jdl (id_formation, nombre_eleves) VALUES (?, ?)", (id_formation, nombre_eleves_formation))
    conn.commit()
    conn.close()

def formations_inscrites_par_eleve(id_eleve):
    conn = sqlite3.connect('ma_base_de_donnees.db') # Connexion à la base de données
    cur = conn.cursor()
    # Exécution de la requête SQL pour récupérer les formations inscrites par l'élève spécifié
    cur.execute("SELECT f.id_formation, f.Nom_formation FROM formation f INNER JOIN inscriptions i ON f.id_formation = i.id_formation WHERE i.id_eleve = ?", (id_eleve,))
    # Récupération de toutes les formations inscrites par l'élève sous forme de liste de tuples
    formations_inscrites = cur.fetchall()
    conn.close()
    return formations_inscrites  # Retourne la liste des formations inscrites par l'élève

def select_identite_eleve(event):
    var.set("Formations séléctionnées")
    # Récupérer le prénom et le nom sélectionnés depuis la combobox des prénoms
    prenom_nom = combo_eleve.get().split()
    prenom = prenom_nom[0]
    nom = prenom_nom[-1]
    # Récupérer l'ID de l'élève correspondant au prénom et nom sélectionnés
    id_eleve_tuple = select_id()
    # Vérifier si l'ID de l'élève a été trouvé
    if id_eleve_tuple is not None:
        #modification du Label modifiable
        var.set("Formations séléctionnées pour : {} {}".format(prenom, nom))
        # Extraire l'ID de l'élève
        id_eleve = id_eleve_tuple[0]
        # Récupérer les formations inscrites par cet élève
        formations = formations_inscrites_par_eleve(id_eleve)
        listbox_formations_selectionnees.delete(0, END)  # Effacer les anciennes formations sélectionnées
        # Ajouter les formations inscrites par l'élève à la Listbox
        for formation in formations:
            listbox_formations_selectionnees.insert(END, f"{formation[0]} - {formation[1]}")

def valider_b():
    # Récupérer les informations sélectionnées dans les combobox
    classe = combo_classe.get()
    identite = combo_eleve.get()
    id_formation = combo_id_formation.get()
    # Afficher les informations sélectionnées
    print("Classe sélectionnée : ", classe)
    print("Elève sélectionné : ", identite)
    print("Formation sélectionnée : ", id_formation)
    id_eleve_tuple = select_id() # Récupérer l'ID de l'élève
    if id_eleve_tuple is not None: # Vérifier si l'ID de l'élève a été trouvé
        id_eleve = id_eleve_tuple[0] # extraction de l'ID de l'élève
        print("ID de l'élève : ", id_eleve)
        # Connexion à la base de données pour vérifier si l'élève est déjà inscrit à la formation
        conn = sqlite3.connect('ma_base_de_donnees.db')
        cur = conn.cursor()
        # Exécution d'une requête SQL pour vérifier si l'élève est déjà inscrit à la formation
        cur.execute("SELECT * FROM inscriptions WHERE id_formation = ? AND id_eleve = ?", (id_formation, id_eleve))
        existing = cur.fetchone()
        conn.close()
        if existing:   # Vérifier si l'élève est déjà inscrit à la formation
            print("L'élève est déjà inscrit à cette formation.")
        else:
            # Si l'élève n'est pas déjà inscrit, l'inscrire
            inscrire_eleve(id_formation, id_eleve)
            # Ajouter la formation sélectionnée à la Listbox des formations sélectionnées
            formation_selectionnee = f"{select_formations()}"  # Récupérer le nom de la formation
            listbox_formations_selectionnees.insert(END, formation_selectionnee)
            # Mettre à jour ou insérer les données dans la table inscriptions_jdl
            conn = sqlite3.connect('ma_base_de_donnees.db')
            cur = conn.cursor()
            cur.execute("SELECT nombre_eleves FROM inscriptions_jdl WHERE id_formation = ?", (id_formation,))
            existing = cur.fetchone()
            if existing is not None:
                nombre_eleves_formation = existing[0] + 1  # Ajouter 1 au nombre actuel d'élèves inscrits
                update_inscriptions_jdl(id_formation, nombre_eleves_formation)
            else:
                insert_inscriptions_jdl(id_formation, 1)  # Le premier élève inscrit
            conn.commit()
            conn.close()
            bouton_terminer.config (state = NORMAL)     #passage du bouton terminer en mode NORMAL, on peut maintenant utiliser ce bouton car la base de données a commencé à être remplie
            var.set("Formations séléctionnées pour : {}".format(identite))      #modification du Label modifiable
            return identite

def recup_inscriptions_jdl():
    # initialisation des listes pour stocker les données récupérées
    liste_eleves = []
    liste_id_formations = []
    liste_noms_formations = []
    # connexion à la base de données
    conn = sqlite3.connect('ma_base_de_donnees.db')
    cur = conn.cursor()
    # récupération des ID de formation depuis la table 'inscriptions_jdl'
    cur.execute("SELECT id_formation FROM inscriptions_jdl")
    id_formations = cur.fetchall()
    # boucle pour parcourir chaque ID de formation
    for id_formation in id_formations:
        # ajout de l'ID de formation à la liste correspondante
        liste_id_formations.append(id_formation[0])
        # récupération du nombre d'élèves inscrits à cette formation
        cur.execute("SELECT nombre_eleves FROM inscriptions_jdl WHERE id_formation = ?", (id_formation[0],))
        eleve = cur.fetchone()
        # Ajout du nombre d'élèves à la liste correspondante
        liste_eleves.append(eleve)
    for id_formation in liste_id_formations:   # boucle pour récupérer les ids des formations à partir de leurs IDs (nom)
        cur.execute("SELECT id_formation FROM formation WHERE id_formation = ?", (id_formation,))
        nom_formation = cur.fetchone()
        # ajout de l'id de la formation à la liste correspondante
        liste_noms_formations.append(nom_formation[0])
    conn.close()
    # retourne les listes contenant les noms des formations et le nombre d'élèves inscrits
    return liste_noms_formations, liste_eleves

def creer_csv():
    # récupération des données sur les inscriptions
    liste_noms_formations, liste_eleves = recup_inscriptions_jdl()
    # initialisation d'un dictionnaire pour stocker les données
    dictionnaire = {}
    # création du dictionnaire avec les noms des formations et le nombre d'élèves inscrits
    for i in range(len(liste_eleves)):
        eleves = liste_eleves[i][0] if liste_eleves[i] is not None else 0
        dictionnaire[liste_noms_formations[i]] = eleves
    print(dictionnaire)
    # création des données à écrire dans le fichier CSV
    data = [
        liste_noms_formations,
        [eleve[0] if eleve is not None else 0 for eleve in liste_eleves]
    ]
    # transposition des données
    data_transposed = list(zip(*data))
    # ecriture des données dans le fichier CSV
    with open('fichier_jdl.csv', 'w', newline='', encoding='utf-8') as fichier_csv:
        writer = csv.writer(fichier_csv)
        # ecriture de l'en-tête du fichier CSV
        headers = ["ID formation", "nombre d'élèves inscrits"]
        writer.writerow(headers)
        writer.writerows(data_transposed)

# Création de la fenêtre principale avec la classe Tk
fenetre = Tk()
#titre à la fenêtre principale
fenetre.title("Inscription au JDL")
#couleur de l'arrière-plan de la fenêtre principale
fenetre.config(bg = "grey")
#dimensions par défaut la fenêtre principale
fenetre.geometry("1250x1000")
#création d'une variable pré-remplie pour la mise en page du texte
f = font.Font(family='Times New Roman', weight="bold")

#texte qui permet de guider l'utlisateur
#les labels pour afficher du texte
texte_classe = Label(fenetre, text="Veuillez séléctionner votre classe:",bg="gray")
texte_classe['font'] = f
texte_classe.pack()
texte_classe.place(x=50, y=50)

#texte qui permet de guider l'utlisateur
texte_prenom = Label(fenetre, text="Veuillez séléctionner votre identité:", bg='gray')
texte_prenom['font'] = f
texte_prenom.pack()
texte_prenom.place(x=50, y=150)

#texte qui permet de guider l'utlisateur
texte_formation = Label(fenetre, text="Veuillez séléctionner l'identifiant de \n votre formation", bg='gray')
texte_formation['font'] = f
texte_formation.pack()
texte_formation.place(x=50, y=250)

#menu deroulant pour choisir l'identité d'un éleve
combo_eleve = ttk.Combobox(fenetre, width=24)
combo_eleve.set("Sélectionnez votre identité")
combo_eleve.pack(pady=20)
combo_eleve.place(x=400, y=150)
combo_eleve.bind("<<ComboboxSelected>>", select_identite_eleve)

#menu deroulant pour choisir une classe
combo_classe = ttk.Combobox(values=list(toutes_classes_unique()), width=23)
combo_classe.set("Sélectionnez votre classe")  # Texte par défaut
combo_classe.bind("<<ComboboxSelected>>", on_select_classe)
combo_classe.pack(pady=20)
combo_classe.place(x=400, y=50)

#texte qui presente une lisbox qui contient toutes les formations
texte_formation = Label(fenetre, text="Toutes les formations:", bg="blue")
texte_formation.pack()
texte_formation.place(x=900, y=20)

#création d'un label avec un texte modifiable
var = StringVar()
formations_selectionnees = Label(fenetre, textvariable = var, bg='blue')
formations_selectionnees.pack()
formations_selectionnees.place(x=900, y=295)
texte="Formations séléctionnées"
var.set(texte)

#ce bouton permet d'appliquer les formations pour chaque eleves, et de mettres les informations souhaiter dans un fichier csv
bouton_terminer= Button(fenetre, text="Cliquez ici lorsque tous les élèves \n ont terminé de saisir leurs formations", bg='red', font=('bold', 11), command = creer_csv)
bouton_terminer.config (state = DISABLED)
bouton_terminer.pack()
bouton_terminer.place(x=220, y=450)

#bouton pour appliquer une formation a un eleve
bouton_valider = Button(fenetre, text="Cliquez ici lorsque vous avez \n terminé de remplir votre classe, votre identité \n et la formation que vous avez séléctionné", bg='red', font=('bold', 11), command=valider_b)
bouton_valider.pack()
bouton_valider.place(x=220, y=340)

#creer une Listbox pour afficher toutes les formations
listbox_toutes_formations = Listbox(fenetre, height=13, width=100)
listbox_toutes_formations.pack()
listbox_toutes_formations.place(x=620, y=50)

#ajouter une barre de défilement verticale a cote de la Listbox
scrollbar_vertical_toutes_formations = Scrollbar(fenetre, orient=VERTICAL, command=listbox_toutes_formations.yview)
scrollbar_vertical_toutes_formations.pack(side=RIGHT, fill=Y)
listbox_toutes_formations.config(yscrollcommand=scrollbar_vertical_toutes_formations.set)
scrollbar_vertical_toutes_formations.place(x=1222, y=50, height=211)

#ajouter une barre de défilement horizontale en dessous de la Listbox
scrollbar_horizontal_toutes_formations = Scrollbar(fenetre, orient=HORIZONTAL, command=listbox_toutes_formations.xview)
scrollbar_horizontal_toutes_formations.pack(side=BOTTOM, fill=X)
listbox_toutes_formations.config(xscrollcommand=scrollbar_horizontal_toutes_formations.set)
scrollbar_horizontal_toutes_formations.place(x=620, y=265, width=620, height=17)

# recuperer toutes les formations et les ajouter à la Listbox
formations = toutes_formations()
for formation in formations:
    listbox_toutes_formations.insert(END, f"{formation[0]} - {formation[1]}")  # Formatage ID et nom

#menu deroulant contenant les id des formations
combo_id_formation = ttk.Combobox(values=[formation[0] for formation in formations], width=29)
combo_id_formation.set("Sélectionnez l'ID de la formation")  # Texte par défaut
combo_id_formation.bind("<<ComboboxSelected>>", on_select_formation)
combo_id_formation.pack(pady=20)
combo_id_formation.place(x=400, y=250)

#creer une Listbox pour afficher les formations sélectionnées
listbox_formations_selectionnees = Listbox(fenetre, height=13, width=100)
listbox_formations_selectionnees.pack()
listbox_formations_selectionnees.place(x=620, y=320)

#creer une barre de défilement horizontale à la liste box formations séléctionées
scrollbar_horizontal_formation_selectionnee = Scrollbar(fenetre, orient=HORIZONTAL, command=listbox_formations_selectionnees.xview)
scrollbar_horizontal_formation_selectionnee.pack(side=BOTTOM, fill=X)
listbox_formations_selectionnees.config(xscrollcommand=scrollbar_horizontal_formation_selectionnee.set)
scrollbar_horizontal_formation_selectionnee.place(x=620, y=522, width=620, height=17)

#créer une barre de défilement verticale à la liste box formations séléctionnées
scrollbar_verticale_formation_selectionnee = Scrollbar(fenetre, orient=VERTICAL, command=listbox_formations_selectionnees.yview)
scrollbar_verticale_formation_selectionnee.pack(side=RIGHT, fill=Y)
listbox_formations_selectionnees.config(xscrollcommand=scrollbar_verticale_formation_selectionnee.set)
scrollbar_verticale_formation_selectionnee.place(x=1222, y=320, width=20, height=200)

# affichage de notre signature:
#logo de notre lycée
image_nom = "logo_lycee.jpg"
image = Image.open(image_nom)
image = image.resize((80, 80), Image.ANTIALIAS)
photo = ImageTk.PhotoImage(image)
label_image = tk.Label(fenetre, image=photo)
label_image.place(x=800, y=550)
#signature des membres de l'equipes
texte_signature = Label(fenetre, text="Evann Gibrat & Matthieu Vauche \n & M.Th",bg="gray")
texte_signature['font'] = f
texte_signature.pack()
texte_signature.place(x=900, y=570)

def afficher_info_supplementaire():
    # creation une nouvelle fenêtre
    fenetre_info = Toplevel(fenetre)
    fenetre_info.title("Informations supplémentaires")
    fenetre_info.geometry("900x500")

    # label pour afficher les informations supplémentaires
    label_info = Label(fenetre_info, text="Voici des informations supplémentaires :")
    label_info.pack()

    # fonction qui permet d'afficher les informations de la formation demandé dans differentes listboxs
    def valider():
        conn = sqlite3.connect('ma_base_de_donnees.db')
        cur = conn.cursor()
        id_formation_selectionnee = combo_id_formation.get()
        # Recherche du lieu de la formation dans la base de données
        cur.execute("SELECT lieu FROM formation WHERE id_formation=?", (id_formation_selectionnee,))
        lieu = cur.fetchone()
        if lieu:
            listbox_lieu.delete(0, 'end')  # Effacer le contenu précédent de la listbox
            listbox_lieu.insert('end', lieu[0])  # Afficher le lieu dans la listbox
        cur.execute("SELECT DATES FROM formation WHERE id_formation=?", (id_formation_selectionnee,))
        date = cur.fetchone()
        if date:
            listbox_date.delete(0, 'end')  # Effacer le contenu précédent de la listbox
            listbox_date.insert('end', date[0])  # Afficher la date dans la listbox
        cur.execute("SELECT horaire_1, horaire_2 FROM formation WHERE id_formation=?", (id_formation_selectionnee,))
        horaires = cur.fetchone()
        if horaires:
            listbox_horaire.delete(0, 'end')  # Effacer le contenu précédent de la listbox
            listbox_horaire.insert('end', horaires[0], horaires[1])  # Afficher le(s) horaire(s) dans la listbox
        cur.execute("SELECT adresse_site FROM formation WHERE id_formation=?", (id_formation_selectionnee,))
        adresse_site = cur.fetchone()
        if adresse_site:
            listbox_adresse_site.delete(0, 'end')  # Effacer le contenu précédent de la listbox
            listbox_adresse_site.insert('end', adresse_site[0])  # Afficher l'adresse du site dans la listbox

    def on_select_formation(event):
        # recuperation de l'ID de la formation selectionnee
        selected_formation_id = combo_id_formation.get()

    #menu deroulant contenant les id des formations
    combo_id_formation = ttk.Combobox(fenetre_info, values=[formation[0] for formation in formations], width=30)
    combo_id_formation.set("Sélectionnez l'ID de la formation")  # Texte par défaut
    combo_id_formation.bind("<<ComboboxSelected>>", on_select_formation)
    combo_id_formation.pack(pady=20)
    combo_id_formation.place(x=50, y=200)

    # bouton de validation qui permet d'appliquer le choix de la formation
    bouton_valider = Button(fenetre_info, text="Validé!", bg='red', font=('bold', 11), command=valider)
    bouton_valider.pack()
    bouton_valider.place(x=260, y=200)

    #texte qui indique a l'utilisateur de choisir une formationdans la listbox
    texte_ = Label(fenetre_info, text="Veuillez séléctionner l'identifiant de \n votre formation")
    texte_['font'] = f
    texte_.pack()
    texte_.place(x=50, y=100)

    #texte qui indique a l'utilisateur la lisbox qui affiche le lieu de la formation
    texte_adresse = Label(fenetre_info, text="Lien vers la formation :", bg="blue")
    texte_adresse.pack()
    texte_adresse.place(x=580, y=75)

    #texte qui indique a l'utilisateur la lisbox qui affiche le lieu de la formation
    texte_date = Label(fenetre_info, text="Date de la porte ouverte :", bg="blue")
    texte_date.pack()
    texte_date.place(x=580, y=375)

    #texte qui indique a l'utilisateur la lisbox qui affiche l'horaire(s) de la formation
    texte_horaire = Label(fenetre_info, text="Horaire(s) de la formation :", bg="blue")
    texte_horaire.pack()
    texte_horaire.place(x=580, y=175)

    #texte qui indique a l'utilisateur la lisbox qui affiche l'adresse de la formation
    texte_lieu = Label(fenetre_info, text="Adresse de la formation :", bg="blue")
    texte_lieu.pack()
    texte_lieu.place(x=580, y=275)

    #listbox qui permet d'afficher le lieu de la formation
    listbox_lieu = Listbox(fenetre_info, height=4, width=50)
    listbox_lieu.pack()
    listbox_lieu.place(x=500, y=300)

    #listbox qui permet d'afficher la date de la formation
    listbox_date = Listbox(fenetre_info, height=4, width=50)
    listbox_date.pack()
    listbox_date.place(x=500, y=400)

    #listbox qui permet d'afficher l'horaire de la formation
    listbox_horaire = Listbox(fenetre_info, height=4, width=50)
    listbox_horaire.pack()
    listbox_horaire.place(x=500, y=200)

    #listbox qui permet d'afficher l'adresse du site de la formation
    listbox_adresse_site = Listbox(fenetre_info, height=4, width=50)
    listbox_adresse_site.pack()
    listbox_adresse_site.place(x=500, y=100)

    #bouton pour fermer la fenêtre
    bouton_fermer = Button(fenetre_info, text="Fermer", command=fenetre_info.destroy)
    bouton_fermer.pack()
    bouton_fermer.place(x=850, y=5)

# bouton pour afficher les informations supplémentaires
bouton_info = Button(fenetre, text="Souhaitez-vous plus d'informations sur les formations ?", command=afficher_info_supplementaire)
bouton_info.pack()
bouton_info.place(x=30, y=570)

fenetre.mainloop()