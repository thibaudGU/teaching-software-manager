# Guide : Synchronisation Excel avec OneDrive

## Résumé

L'application peut maintenant **lire et écrire des données Excel** stockées sur OneDrive. Cela permet aux enseignants et aux administrateurs de :
- **Mettre à jour les données directement dans Excel** (si préféré)
- **Synchroniser** entre la web interface et Excel
- **Partager un fichier Excel** avec toute l'équipe

---

## Comment utiliser

### **1. Exporter les données vers Excel**

1. Accéder à la page **"Rapports et Notifications"**
2. Sous **"📊 Synchronisation Excel"**, cliquer sur **"💾 Exporter vers Excel"**
3. Un fichier `teaching_software.xlsx` est créé dans le dossier `config/`

### **2. Partager le fichier sur OneDrive**

1. **Localiser le fichier** :
   - Chemin : `config/teaching_software.xlsx`
   
2. **Copier dans OneDrive** :
   - Ouvrir OneDrive (https://onedrive.live.com)
   - Créer un dossier "Teaching Software"
   - Télécharger `teaching_software.xlsx` là-bas
   - Cliquer **Partager** → Partager avec les enseignants
   - Donner accès **"Lecture et modification"**

3. **Ou utiliser un raccourci local** :
   - Si OneDrive Sync est installé, mettre le fichier dans :
     ```
     C:\Users\[username]\OneDrive - Université de La Rochelle\Teaching Software\
     ```

### **3. Modifier dans Excel**

Les enseignants peuvent ouvrir le fichier Excel et :
- Ajouter/modifier enseignants dans la feuille **"Instructors"**
- Ajouter/modifier modules dans la feuille **"Modules"**
- Ajouter/modifier logiciels dans la feuille **"Software"**

### **4. Importer les modifications**

Après que quelqu'un a modifié l'Excel :
1. Accéder à **"Rapports et Notifications"**
2. Cliquer **"📥 Importer depuis Excel"**
3. Les données Excel remplacent la base YAML
4. L'app redémarre automatiquement avec les nouvelles données

---

## Structure du fichier Excel

### **Feuille "Instructors"**
| ID | Name | Email | Department | Modules | Last Review |
|----|------|-------|------------|---------|-------------|
| prof_001 | Dr. Thibaud Guilhen | thibaud.guilhen@univ-lr.fr | Informatique | mobile_development,web_dev | 2025-01-01 |

### **Feuille "Modules"**
| ID | Code | Name | Description | Year | Semester | Instructor |
|----|------|------|-------------|------|----------|------------|
| web_development | INFO-S3-WEB | Web Development | HTML, CSS, JS... | 2 | 3 | prof_001 |

### **Feuille "Software"**
| Module ID | Software Name | Version | Purpose | Critical | Notes | Last Verified | Verified By |
|-----------|---------------|---------|---------|----------|-------|----------------|-------------|
| web_development | VS Code | 1.95 | Code editor | No | IDE recommandé | 2025-01-01 | Dr. Guilhen |
| web_development | Node.js | v20.x | Backend runtime | Yes | Framework Express | 2025-01-01 | Dr. Guilhen |

---

## Avantages

✅ **Collaboratif** : Plusieurs personnes peuvent éditer l'Excel en même temps (OneDrive)
✅ **Offline-friendly** : Fonctionnedans Excel même sans connexion internet
✅ **Versioning** : OneDrive garde l'historique des versions
✅ **Flexible** : Choisir entre web form OU Excel selon vos préférences
✅ **Pas de dépendance M365** : Fonctionne avec Excel local aussi

---

## Bonnes pratiques

1. **Faire une export avant une import** 
   - Cliquer "Vérifier l'état" pour voir les différences
   
2. **Ne pas avoir deux personnes qui éditent en même temps**
   - Attendre la fin des modifications avant une import

3. **Backup du YAML**
   - L'app garde une copie de sauvegarde : `config/teaching_software.yml.backup`

4. **Synchroniser régulièrement**
   - Export Excel une fois par semaine
   - Import quand modifications importantes

---

## Troubleshooting

### "Error: Excel file not found"
- Assurer que le fichier `config/teaching_software.xlsx` existe
- Cliquer "Exporter vers Excel" d'abord

### "Error importing from Excel"
- Vérifier que les colonnes Excel ont les bons noms
- Ne pas supprimer les en-têtes
- Les IDs doivent être uniques

### "Données importées mais page ne se met pas à jour"
- L'app redémarre automatiquement (~5 sec)
- Attendre puis rafraîchir le navigateur
