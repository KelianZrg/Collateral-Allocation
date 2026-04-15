## EGB REPO & Collateral Optimisation Project
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import math
import scipy


#Inventaire de bonds

bond1={
"ISIN":"B2020",
"pays":"France",
"maturite":30,
"coupon": 0.10,
"prix":100,
"market_value" : 95,
"haircut" : 5,
"liquidite" :8,
"rarete" : 2,
"quantite_disponible" : 3800,
}

bond2={
"ISIN":"B2021",
"pays":"Allemagne",
"maturite": 60,
"coupon":0.15,
"prix": 3500,
"market_value" : 3483,
"haircut" : 17,
"liquidite" :4,
"rarete" : 7,
"quantite_disponible" : 44,
}

bond3={
"ISIN":"B2022",
"pays":"Italie",
"maturite":45 ,
"coupon":0.12,
"prix":120,
"market_value" : 96,
"haircut" : 24,
"liquidite" :4,
"rarete" : 1,
"quantite_disponible" : 4890,
}

inventaire=[bond1,bond2,bond3]

# Besoin de collatéral

besoin1={
"contrepartie":"SG",
"montant": 10000,
"devise": "EUR" ,
"pays_acceptes":["France","Allemagne", "Italie"] ,
"haircut_max":20,
"maturite_max": 28,
"concentration_max_pays":0.6,}

besoin2={
"contrepartie":"CA",
"montant": 22000,
"devise": "EUR" ,
"pays_acceptes":["France","Allemagne", "Italie"] ,
"haircut_max":24,
"maturite_max": 90,
"concentration_max_pays":0.6,}

besoin3={
"contrepartie":"CIC",
"montant": 17000,
"devise": "EUR" ,
"pays_acceptes":["France","Allemagne"] ,
"haircut_max":16,
"maturite_max": 70,
"concentration_max_pays":0.7,}

besoins=[besoin1, besoin2, besoin3]

#Eligibilité d'un bond

def est_eligible(bond,besoin):
    return(
    bond["pays"] in besoin["pays_acceptes"]
    and bond["haircut"]<= besoin["haircut_max"]
    and bond["maturite"]<=besoin["maturite_max"]
    )

for bond in inventaire:
    for besoin in besoins:
        print( bond["ISIN"], est_eligible(bond,besoin))


for bond in inventaire:
    for besoin in besoins:
        if est_eligible(bond,besoin):
            print("Le bond d'ISIN {bond['ISIN']} est eligible pour la contrepartie {besoin['contrepartie']}")


# valeur mobilisable après haircut

valeur_post_haircut=[]

for bond in inventaire:
    valeur_post_haircut.append(
    bond["market_value"] * bond["quantite_disponible"] * (1 - bond["haircut"]/100)
)
print (valeur_post_haircut)

def valeur_collateral_disponible(bond):
    return(bond["market_value"]*bond["quantite_disponible"]*(1-bond["haircut"]/100))

# Allocation gloutonne des collateraux

#On va trier les bond par rareté croissante
# et par liquidité décroissante

def cle_tri(bond):
    rarete = bond["rarete"]
    liquidite = bond["liquidite"]
    return (rarete, -liquidite)

# bonds_eligibles = sorted(bonds_eligibles, key=cle_tri) # Le souci, c’est que pour trier selon deux critères, Python a besoin qu’on lui donne une règle. Donc il y aura toujours une forme de clé

def allouer_collateral_glouton(inventaire, besoin):
    bonds_eligibles = []

    for bond in inventaire: #les bonds dans l'inventaire servent à couvrir le montant
        if est_eligible(bond, besoin):
            bonds_eligibles.append(bond)

        bonds_eligibles = sorted(bonds_eligibles, key=cle_tri)
        montant_restant = besoin["montant"] #montant de cash à lever ou à sécuriser

    allocation = []
    for bond in bonds_eligibles:
        valeur_unitaire = bond["prix"] * (1 - bond["haircut"]/100)

        if valeur_unitaire <= 0:
            continue

        quantite_necessaire = math.ceil(montant_restant /valeur_unitaire)
        quantite_allouee=min(quantite_necessaire,bond["quantite_disponible"])

        valeur_apportee = quantite_allouee * valeur_unitaire
        allocation.append({ "ISIN": bond["ISIN"],
                            "contrepartie": besoin["contrepartie"],
                             "quantite_allouee": quantite_allouee,
                              "valeur_apportee": valeur_apportee })

        montant_restant -= valeur_apportee
        if montant_restant <= 0:
           break
    return allocation, montant_restant

allouer_collateral_glouton(inventaire, besoin2)