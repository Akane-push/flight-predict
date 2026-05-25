# Flight-predict

Projet personnel de Data Engineering visant à concevoir une architecture de prédiction de retards de vols (Lufthansa, vols directs).

Ce dépôt est un miroir du projet principal hébergé sur [GitLab](https://gitlab.com/Akane-Push/flight-predict)

## Objectif

Le système intègrera un pipeline ELT orchestré par Airflow, un stockage au format Parquet et un modèle de machine learnin, entrainé avec scikit-learn. Les données seront consultable à l'aide d'une API FastAPI. 

## Prérequis

**Ce projet ne contient pas encore de Fake Datas.** Pour exécuter le code vous devez disposer de vos propres identifiants API.

1.  **Compte Lufthansa Developer** : Une inscription est obligatoire pour obtenir les clés d'accès.
    -   Lien : [LufthansaAPI](https://developer.lufthansa.com/io-docs)
2.  **Environnement Local** :
    -   Docker & Docker Compose (recommandé pour Airflow et PostgreSQL)

---

## Avancement

### Phase 1:
- [x] Récupération des données vols (Lufthansa) et météo (Open-Meteo)
- [x] Stockage des données
- [x] Orchestration (Airflow)
- [x] Nettoyage des données pour le modèle
- [x] Entraînement du modèle avec scikit-learn

### Phase 2:
- [x] FastAPI - Core (API Prod)
- [ ] FastAPI - Prédiction (API Predict)
- [ ] FastAPI - Démo (API Demo)

### Phase 3:
- [x] Pipeline CI
- [ ] Kubernetes
- [ ] Monitoring (Prometheus + Grafana)
- [ ] Pipeline CD

---

## Configuration

Le projet repose sur un fichier d'environnement `.env` pour la gestion des secrets et des chemins. Ce fichier n'est **pas versionné** pour des raisons de sécurité.

Créez un fichier `.env` à la racine du projet avec la structure suivante :

```ini
# --- Lufthansa API ---
Lufth_client_id=VOTRE_CLIENT_ID
Lufth_client_secret=VOTRE_CLIENT_SECRET
Lufth_grant_type=client_credentials

# --- Base de données PostgreSQL pour Airflow ---
POSTGRES_USER=votre_user
POSTGRES_PASSWORD=votre_mot_de_passe_fort

# --- Airflow ---
AIRFLOW_USER=votre_user
AIRFLOW_PASSWORD=votre_mot_de_passe_fort
AIRFLOW_LOGS_PATH=./airflow/logs
AIRFLOW_API_ISSUER=votre_issuer
AIRFLOW_API_SECRET=votre_secret_fort
AIRFLOW_UID=1000

# --- Chemins de stockage ---
EXTRACTED_PATH=./chemin_absolu_vers_votre_dossier/datas
PENDING_PATH=./chemin_absolu_vers_votre_dossier/pending
ARCHIVES_PATH=./chemin_absolu_vers_votre_dossier/archives
MODEL_PATH=./chemin_absolu_vers_votre_dossier/model
```
