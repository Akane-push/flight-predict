# Flight-predict

Projet personnel de Data Engineering visant à concevoir une architecture de prédiction de retards de vols (Lufthansa, vols directs).

Le dépôt Github est un miroir du projet principal hébergé sur [GitLab](https://gitlab.com/Akane-Push/flight-predict)

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
- [x] Kubernetes
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
POSTGRES_USER=
POSTGRES_PASSWORD=

# --- Airflow ---
AIRFLOW_USER=admin
AIRFLOW_PASSWORD=admin
AIRFLOW_LOGS_PATH=
AIRFLOW_API_ISSUER=
AIRFLOW_API_SECRET=
AIRFLOW_UID=50000           # Évite l'erreur ModuleNotFoundError/PermissionError lors des imports Python (urllib3).

# --- Config ---
API_KEY=                    # Mot de passe pour l'API predict
DOCKERFILE=Dockerfile.lts   # Retirez le ".lts" uniquement si votre processeur est compatible avec le langage Rust.
# Si vous n'êtes pas sûr, vous pouvez supprimer cette ligne et lancer le script lts-check.sh à la racine de ce dossier.

# --- Chemins de stockage ---
EXTRACTED_PATH=./datas/extracted
PENDING_PATH=./datas/pending
ARCHIVES_PATH=./datas/archives
MODEL_PATH=./datas/model
```
