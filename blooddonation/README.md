# 🩸 Blood Donation Dashboard

Un tableau de bord interactif développé avec **Python & Dash** permettant l'analyse complète d'une campagne de don de sang, à partir de deux jeux de données nettoyés :
- `Candidat_au_don_2019_cleaned.csv`
- `Donneurs_2019_cleaned.csv`

---

## 📁 Structure du projet

```
blooddonation/
│
├── central_app.py                      # Fichier principal de l’application Dash
├── assets/
│   └── styles.css                      # Feuille de style CSS pour l’apparence du dashboard
│   └── banner.png                      # Image de la bannière supérieure
│   └── down.png                        # Icône de poche de sang affichée en bas à gauche
│
├── data/
│   ├── Candidat_au_don_2019_cleaned.csv  # Base principale avec variables démographiques, cliniques et éligibilité
│   └── Donneurs_2019_cleaned.csv         # Données détaillées des dons réalisés (horodatage, groupe sanguin, etc.)
│
├── objectives/
│   ├── map_donor_distribution.py       # Carte interactive de répartition géographique des donneurs
│   ├── health_conditions.py            # Analyse des conditions médicales et inéligibilités
│   ├── donor_clustering.py             # Clustering K-Means des profils de donneurs
│   ├── campaign_effectiveness.py       # Analyse temporelle des campagnes de dons
│   ├── donor_retention.py              # Statistiques sur la fidélisation des donneurs
│   ├── sentiment_analysis.py           # Analyse de sentiment sur les retours textuels
│   └── eligibility_prediction.py       # Modèle ML + interface API de prédiction d’éligibilité
```

---

## ✅ Fonctionnalités principales

### 1. 📍 Répartition géographique des donneurs
Carte (ou bar chart) représentant le nombre de donneurs par arrondissement.

### 2. 🏥 Conditions de santé et éligibilité
Analyse de l'effet de pathologies (hypertension, diabète, etc.) sur l'éligibilité.

### 3. 🤖 Clustering des donneurs
Profilage automatique via KMeans selon l'âge, le poids, etc.

### 4. 📅 Efficacité des campagnes
Analyse temporelle des dons par mois et jour de la semaine.

### 5. 🔁 Fidélisation
Fréquence des dons par âge et sexe, analyse des tranches d'âge les plus récurrentes.

### 6. 💬 Analyse de sentiment
Analyse des retours texte des donneurs avec TextBlob.

### 7. 🧠 Prédiction d'éligibilité
Modèle Random Forest + formulaire en temps réel pour prédire l'éligibilité.

---

## ▶️ Lancer l'application

Assurez-vous d'avoir Python 3.7+ installé, puis :

```bash
pip install -r requirements.txt
python central_app.py
```

Ouvrez ensuite dans votre navigateur : http://127.0.0.1:8050

---

## 📦 Dépendances principales

- dash
- pandas
- plotly
- scikit-learn
- textblob
- geopy *(si géocodage ultérieur)*

---

## 👤 Auteur
Développé par 
[SERENA ASU BESONG]
[LUC BAUDOINF FANKOUA] 
[CYRIL BRICE FOMAZOU]
[NGU WINSTON] 

dans le cadre d’une competition.

---

## 📜 Licence
Projet de competition - libre d'utilisation avec citation.

