# Déployer sur Render (cloud gratuit)

## Prérequis
- Compte **GitHub** (gratuit)
- Compte **Render** (gratuit) : https://render.com
- Compte **Microsoft Teams** (université)

---

## Étape 1 : Préparer le repo GitHub

1. **Créer un repo GitHub** (ou fork le vôtre)
   ```
   https://github.com/votre-username/teaching-software-manager
   ```

2. **Push le code** vers GitHub
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/votre-username/teaching-software-manager.git
   git push -u origin main
   ```

---

## Étape 2 : Configurer Teams Webhook

1. **Aller dans Microsoft Teams** → Votre Team → ⚙️ Paramètres
2. **Apps & intégrations** → **Connecteurs**
3. **Configurer** → Rechercher **"Incoming Webhook"** → **Ajouter/Configurer**
4. **Donner un nom** : "Teaching Software Manager"
5. **Créer** → Copier l'URL complète du webhook

   ✅ Vous aurez une URL du style :
   ```
   https://outlook.webhook.office.com/webhookb2/xxx/IncomingWebhook/yyy/zzz
   ```

---

## Étape 3 : Déployer sur Render

1. **Aller sur** https://render.com et créer un compte (gratuit)
2. **New Web Service** → **Connect a repository** → GitHub
3. **Autoriser Render** à accéder à GitHub
4. **Sélectionner votre repo** `teaching-software-manager`
5. **Remplir les paramètres** :
   - **Name** : `teaching-software-manager`
   - **Runtime** : `Python 3.13`
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `python web/app.py`
   - **Plan** : Free (gratuit, avec hibernation après 15 min inactivité)

6. **Environment Variables** → Ajouter :
   ```
   FLASK_ENV = production
   SECRET_KEY = (générer une clé aléatoire forte)
   TEAMS_WEBHOOK_URL = (copier l'URL du webhook Teams)
   APP_BASE_URL = (sera quelque chose comme https://teaching-software-manager-xxx.onrender.com)
   ```

7. **Create Web Service** → Attendre 2-3 min le déploiement

✅ **Votre app est maintenant accessible à** : `https://teaching-software-manager-xxx.onrender.com`

---

## Étape 4 : Configurer la base de données (YAML local)

Pour maintenant, le fichier `config/teaching_software.yml` reste en local.

**Options futures** :
- Synchroniser le YAML avec OneDrive (script cron)
- Stocker directement sur SharePoint List (plus collaboratif)

---

## Étape 5 : Tester Teams Webhook

1. **Aller sur votre app** → `https://teaching-software-manager-xxx.onrender.com/instructors`
2. **Cliquer sur un enseignant** → Cliquer sur **"💬 Envoyer via Teams (Simulation)"**
3. **Vous verrez** un aperçu du message Teams
4. **Pour vrai** : Cliquer **"💬 Envoyer via Teams"** et le message s'affichera dans votre Team !

---

## Mise à jour du code

À chaque fois que vous modifiez le code :

```bash
git add .
git commit -m "Votre message"
git push origin main
```

**Render redéploie automatiquement** en ~1 min ! 🚀

---

## Dépannage

### "Teams message failed"
- Vérifier que `TEAMS_WEBHOOK_URL` est correct dans Render
- L'URL commence par `https://outlook.webhook.office.com`

### App très lente au premier accès
- C'est normal (Render hiberne après 15 min) → ~30 sec pour démarrer
- Pas grave pour votre usage

### Changer l'URL du webhook
- Aller dans Render Dashboard
- Cliquer sur votre app → **Environment** → Éditer `TEAMS_WEBHOOK_URL`
- Sauvegarder → Render redéploie

### Voir les logs
- Render Dashboard → votre app → **Logs** (voir les erreurs)

---

## Stockage des données (futur)

Pour mettre à jour `teaching_software.yml` depuis OneDrive :

1. Créer un **OneDrive Sync Script** (Python)
2. Le configurer en **cron job** (update chaque heure)
3. Ou **utiliser SharePoint List** (natif M365)

On peut implémenter ça après si nécessaire ! 😊
