# K3s Deployment Flight-predict

Manifests Kubernetes pour le projet flight-predict, déployé sur un cluster K3s.

## Structure

```
k3s/
├── airflow/
│   ├── values.yaml                 # Configuration du chart Airflow
│   └── values-test.yaml            # Surcharges pour les tests manuels
│
└── apis/
    ├── Chart.yaml
    ├── values.yaml                 # Valeurs par défaut (committé)
    ├── values.secret.yaml          # Surcharges locales — ignoré par Git (voir ci-dessous)
    ├── values.secret.yaml.example  # Modèle pour créer le vôtre
    └── templates/
        ├── pv.yaml                 # PersistentVolume (stockage local au nœud)
        ├── pvc.yaml                # PersistentVolumeClaim
        ├── api-prod/
        │   ├── deployment.yaml
        │   └── service.yaml
        └── api-predict/
            ├── deployment.yaml
            └── service.yaml
```

## Prérequis

1. **Environnement local** :
   - Un cluster K3s en cours d'exécution
   - `kubectl` configuré pour cibler le cluster
   - `helm` >= 3.x installé

2. **Créer le namespace `flight-project`** :
   ```bash
   kubectl create namespace flight-project
   ```

3. **Secret pour le pull des images (exemple avec GitLab)** :
   ```bash
   kubectl create secret generic gitlab-registry \
     --from-literal=GITLAB_CLIENT_ID=<votre-username-gitlab> \
     --from-literal=GITLAB_CLIENT_SECRET=<votre-token-gitlab> \
     --namespace=flight-project
   ```

4. **Compte Lufthansa Developer** : Une inscription est obligatoire pour obtenir les clés d'accès.
   - Lien : [Lufthansa API](https://developer.lufthansa.com/io-docs)
   ```bash
   kubectl create secret generic lufth-credentials \
     --from-literal=Lufth_client_id=<votre-api-key> \
     --from-literal=Lufth_client_secret=<votre-api-secret> \
     --from-literal=Lufth_grant_type=<votre-grant-type> \
     --namespace=flight-project
   ```
   > Le nom du secret `lufth-credentials` est référencé dans `values.yaml` via `credentialsSecret`.

## Configuration

Copier le fichier d'exemple et renseigner vos valeurs :

```bash
cp k3s/apis/values.secret.yaml.example k3s/apis/values.secret.yaml
```

> `values.secret.yaml` est listé dans `.gitignore` et ne sera jamais committé.

## Déploiement

Les images sont buildées et poussées automatiquement via la pipeline GitLab CI (voir `.gitlab-ci.yml` à la racine du projet).

Pour un déploiement manuel :

```bash
# APIs + Stockage
helm upgrade --install apis ./k3s/apis \
  -f k3s/apis/values.yaml \
  -f k3s/apis/values.secret.yaml \
  --set image.tag=<VERSION_TAG>

# Airflow
helm upgrade --install airflow apache-airflow/airflow \
  --version 1.21.0 \
  -f k3s/airflow/values.yaml \
  --set images.airflow.tag=<VERSION_TAG>
```

> Ajouter`-f k3s/airflow/values-test.yaml` à la commande Airflow pour appliquer des restrictions matérielles.


## Post-Déploiement

Création de l'utilisateur Airflow.

```bash
kubectl exec -it -n flight-project deployment/airflow-api-server -- \
  airflow users create \
  --username admin \
  --firstname Prenom \
  --lastname Nom \
  --role Admin \
  --email admin@example.com \
  --password <votre-password>
```