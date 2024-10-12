from django.apps import AppConfig

class TorrentConfig(AppConfig):
    name = 'torrent'

    def ready(self):
        import torrent.signals  # Importez le fichier de signaux pour enregistrer les signaux