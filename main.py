from app import create_app

app = create_app()

if __name__ == "__main__":
    """
    Point d'entrée pour exécuter l'application Flask.

    Ce script crée une instance de l'application Flask en utilisant la
    fonction `create_app` définie dans le module `app`. Si le script est
    exécuté directement (et non importé comme module), il démarre le serveur
    Flask sur le port 8080.

    Utilisation :
        Exécutez ce script pour démarrer le serveur :
        $ python main.py
        Ensuite, accédez à l'application à l'adresse :
        http://127.0.0.1:8080

    Remarque :
        Assurez-vous que toutes les dépendances et la configuration
        nécessaires sont en place avant d'exécuter le script.
    """
    app.run(port=8080)
