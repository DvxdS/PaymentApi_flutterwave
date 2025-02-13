# PaymentApi_flutterwave

Voici une documentation claire et bien structurée en français, incluant l’endpoint manquant pour l'initialisation de paiement.  

---

# **Service de Vérification et d’Initiation de Paiement – FastAPI**  

Ce service permet d’initier et de vérifier les paiements via **Flutterwave** en utilisant **FastAPI** et **PostgreSQL**.  

## **Installation**  

### **1. Prérequis**  
- Python 3.8+  
- PostgreSQL  
- `virtualenv` (optionnel mais recommandé)  

### **2. Cloner le projet**  
```sh
git clone <repository_url>
cd <nom_du_projet>
```

### **3. Créer un environnement virtuel (optionnel)**  
```sh
python -m venv venv
source venv/bin/activate  # Sous Windows : venv\Scripts\activate
```

### **4. Installer les dépendances**  
```sh
pip install -r requirements.txt
```

### **5. Configurer les variables d’environnement**  
Créez un fichier `.env` à la racine du projet et ajoutez :  
```
DATABASE_URL=postgresql://user:password@localhost:5432/nom_de_la_base
FLUTTERWAVE_SECRET_KEY=your_flutterwave_secret
```

---

## **Utilisation**  

### **1. Appliquer les migrations de base de données**  
```sh
alembic upgrade head
```

### **2. Démarrer le serveur**  
```sh
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### **3. Endpoints disponibles**  

#### 🔹 **1. Initier un paiement (via carte bancaire)**  
**Méthode :** `POST /payments/initiate`  
**Body :**  
```json
{
  "amount": 1000,
  "currency": "XOF",
  "email": "client@example.com",
  "fullname": "Jean Dupont",
  "card_number": "5531886652142950",
  "cvv": "564",
  "expiry_month": "09",
  "expiry_year": "32"
}
```
**Réponse :**  
```json
{
  "status": "success",
  "message": "Payment successful",
  "data": {
    "id": 288192886,
    "status": "successful",
    "flw_ref": "FLW-MOCK-REF",
    "amount": 1000
  },
  "meta": {}
}
```

#### 🔹 **2. Vérifier un paiement**  
**Méthode :** `GET /payments/verify?transaction_id=<transaction_id>`  
**Exemple d’appel :**  
```sh
curl -X GET "http://localhost:8000/payments/verify?transaction_id=288192886"
```
**Réponse :**  
```json
{
  "status": "successful",
  "amount": 1000,
  "currency": "XOF",
  "customer_email": "client@example.com",
  "customer_name": "Jean Dupont",
  "transaction_id": 288192886,
  "created_at": "2024-02-12T14:06:55.000Z"
}
```

---

## **Déploiement**  

### **1. Avec Docker **  
**Construire l’image :**  
```sh
docker build -t fastapi-paiement .
```
**Lancer le conteneur :**  
```sh
docker run -d -p 8000:8000 --env-file .env fastapi-paiement
```

### **2. Sur un serveur cloud (ex: AWS, DigitalOcean)**  
**Lancer avec Gunicorn & Uvicorn :**  
```sh
pip install gunicorn
gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

### **3. Configurer un proxy inverse avec Nginx**  
Ajoutez cette configuration :  
```nginx
server {
    listen 80;
    server_name votredomaine.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```
Redémarrer Nginx :  
```sh
sudo systemctl restart nginx
```![flutter_wave_notifactions](https://github.com/user-attachments/assets/a5dc5132-3a27-46d5-9bad-f28a201a7343)
![transaction_screen](https://github.com/user-attachments/assets/de2c829f-1945-402f-aeb5-43e01900a83d)
![initiate payments](https://github.com/user-attachments/assets/77a59c55-6323-484e-a9f3-b7e0065bf5c1)


---

## **Prochaines étapes**  
- Ajouter une authentification pour sécuriser les endpoints.  
- Mettre en place un système de logs et monitoring (Prometheus, Loki).  
- Automatiser le déploiement avec CI/CD.  

---
