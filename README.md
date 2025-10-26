# AI-PCB-Predictor 

Outil qui **génère, évalue et optimise** le placement de composants électroniques sur une grille type PCB.  
Il combine une **fonction de coût physique** (longueur des nets, zones interdites, proximité thermique) et un **modèle ML (RandomForest)** pour estimer rapidement la qualité d’un placement.

# Fonctionnalités
- Génération d’un dataset de placements synthétiques
- Fonction de coût : longueur des nets pondérée + pénalités “keep-out” + voisinage thermique
- Entraînement d’un modèle ML (RandomForestRegressor)
- Optimisation : recherche du **meilleur placement** et visualisation claire
- Visualisation comparative (bon / mauvais / aléatoire) pour la démo

#  Structure
AI-PCB-Predictor/
├─ data/
│  ├─ pcb_dataset.csv
│  └─ placements_examples/          
│
├─ images/
│  └─ example.png                   # capture de visualisation
│
├─ models/
│  └─ placement_model.pkl
│
├─ AI_PCB_Predictor.py              # génération du dataset
├─ train_model.py                   # entraînement + sauvegarde du modèle
├─ optimize.py                      # tests en arrière-plan → meilleur placement
├─ visualize_3cas_secondaire.py     # démo : bon vs mauvais vs aléatoire
│
├─ requirements.txt                 # dépendances (pandas, sklearn, matplotlib…)
├─ .gitignore                       # fichiers/dossiers ignorés par Git
└─ README.md                        # page d’accueil GitHub (explications + image)

