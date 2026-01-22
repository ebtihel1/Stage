# Création du dossier projet
mkdir finvestrack
cd finvestrack

# Création de l'environnement virtuel
python -m venv venv
# Activer l'environnement 
venv\Scripts\activate
# pour désactiver 
deactivate

# pour executer le projet 
py manage.py runserver 

# Installation des dépendances
pip install django djangorestframework (ORM) djangorestframework-simplejwt drf-spectacular pytest pytest-django

# git
git add .
git commit -m
git push
