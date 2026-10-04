# Widget Météo Windows — version EXE

Cette version est conçue pour produire un vrai `MeteoLocale.exe` autonome.

## Méthode recommandée : GitHub Actions

1. Crée un dépôt GitHub vide.
2. Envoie tout le contenu de ce dossier dans le dépôt.
3. Va dans **Actions**.
4. Lance **Build Windows EXE** avec **Run workflow**.
5. Une fois terminé, ouvre l'exécution puis télécharge l'artefact **MeteoLocale-Windows**.
6. Décompresse-le et lance `MeteoLocale.exe`.

Le PC Windows sur lequel tu lances le `.exe` n'a pas besoin de Python.

## Données météo

Le programme utilise Open-Meteo et une localisation approximative par IP.
Une connexion Internet est nécessaire.

## Remarque Windows

Au premier lancement, Windows Defender / SmartScreen peut afficher un avertissement parce que le programme n'est pas signé numériquement. Il faut alors vérifier que le fichier vient bien de ton dépôt avant de l'autoriser.
