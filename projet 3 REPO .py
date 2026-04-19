## Liquidity Stress Testing for a bond portfolio

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


#step 1
bond1={
"ISIN":1,
"pays":"France",
"maturite":1,
"prix":100,
"haircut":3,
"liquidite":15,
"quantite":3800}

bond2={
"ISIN":2,
"pays":"Allemagne",
"maturite":2,
"prix":120,
"haircut":8,
"liquidite":17,
"quantite":2500}

bond3={
"ISIN":3,
"pays":"Italie",
"maturite":3,
"prix":90,
"haircut":6,
"liquidite":14,
"quantite":4200}

bond4={
"ISIN":4,
"pays":"Autriche",
"maturite":4,
"prix":80,
"haircut":4,
"liquidite":13,
"quantite":5000}

#step 2

portfolio=[bond1, bond2, bond3, bond4]

df_portfolio=pd.DataFrame(portfolio)
# print(df_portfolio)


#step 3

df_portfolio["valeur_de_marche"]=df_portfolio["prix"]*df_portfolio["quantite"]

df_portfolio["valeur_de_haircut"]=df_portfolio["valeur_de_marche"]*(1-df_portfolio["haircut"]/100)


#step 4 #choc uniformes à plus ou moins 20% de la valeur initiale

#noise_prix=np.random.uniform(-20,20)
#print(noise_prix)

def choc(val):
    noise=np.random.uniform(-0.2,0.2)

    return (val*(1+noise))

stress1 = choc(bond1["prix"])
#print(stress1)

#step 5: Mettre des chocs aléatoires de student

def choc_student(val):
    x=5
    student_noise=np.random.standard_t(x)
    scale=np.random.uniform(0.01,0.1)
    return(val*(1+scale*student_noise))

# Le facteur d’échelle de la loi de Student ne provient pas ici d’une calibration sur données historiques.

#Il est choisi de manière à obtenir des variations de prix d’ordre de grandeur plausible sur l’horizon considéré, tout en conservant des queues plus épaisses qu’une loi normale.

# step 6: Mettre des chocs aléatoires gaussiens

def choc_gaussien(val):
    mu=0
    sigma=np.random.uniform(0,0.01)

    gaussian_noise=np.random.normal(mu,sigma)

    return (val*(1+gaussian_noise))

#On ne connaît pas précisément la loi des variations de prix.

#On introduit donc des chocs aléatoires selon différents paramètres pour explorer plusieurs comportements possibles du portefeuille sous stress.

#Dans un contexte hors crise, on suppose que les variations de prix restent modérées et sans dérive moyenne marquée à court terme.

# Il semble donc raisonnable de modéliser les chocs par une loi normale centrée.

#Cependant, l’intensité de ces variations peut changer d’un scénario à l’autre, ce qui motive l’introduction d’une variance aléatoire.


#step 7
def afficher_comp(inventaire, nb_chocs):
    list_ISIN = []
    list_prix = []

    for bond in inventaire:
        list_ISIN.append(bond["ISIN"])
        list_prix.append(bond["prix"])

    plt.figure(figsize=(10,6))

    # courbe des prix initiaux
    plt.plot(list_ISIN, list_prix, marker="o", linewidth=3, label="Prix initial")

    # scénarios de choc
    for i in range(nb_chocs):
        chocs = []
        for bond in inventaire:
            chocs.append(choc_student(bond["prix"])) #choisir un type de choc

        if i == 0:
            plt.plot(list_ISIN, chocs, marker="o", linestyle="--", alpha=0.6, label="Prix après choc")
        else:
            plt.plot(list_ISIN, chocs, marker="o", linestyle="--", alpha=0.6)

    plt.xlabel("ISIN")
    plt.ylabel("prix")
    plt.title(f"Prix initiaux et {nb_chocs} scénarios de choc des bonds")
    plt.legend()
    plt.grid(True)

    plt.show()

afficher_comp(portfolio, 20)

# step 8: Les comparaisons des valeurs initiales vs après le choc

def comparaison_stress(val):

    return(val-choc_student(val))

comp=comparaison_stress(bond1["prix"])
print("comparaison",comp,"\n")

def comparaison_moyenne(inventaire,nb_realisations):
    for bond in inventaire:
        c=0
        for i in range (nb_realisations):
            c+=comparaison_stress(bond["prix"])
        print(f"La moyenne des variations de prix sur le bond {bond['ISIN']}  pour {nb_realisations}  réalisations est", c/nb_realisations,"\n")

comparaison_moyenne(portfolio,10)

# On vient de mesurer la perte moyenne par obligation

# On peut désormais essayer de mesurer la perte moyenne globale du portefeuille

# step 9 :

#là, il faut tenir compte de quantite
#sinon une obligation avec petite quantité "pèse" autant qu’une grosse ligne

def comparaison_portefeuille(inventaire):
    perte_portefeuille=[]
    for bond in inventaire:
        prix_initial=bond["prix"]
        prix_choque=choc_student(bond["prix"])
        quantite=bond["quantite"]

        perte_portefeuille.append((prix_initial-prix_choque)*quantite)

    perte_totale = np.sum(perte_portefeuille)

    if perte_totale < 0:
        print("Le gain total grâce au choc sur le portefeuille pour cette réalisation est", -perte_totale)

    elif perte_totale > 0:
        print("La perte totale à cause du choc sur le portefeuille pour cette réalisation est", perte_totale)

    else:
        print("Il n'y a pas eu de changement sur la valeur du portefeuille")

comparaison_portefeuille(portfolio)