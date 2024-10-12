from django.core.management.base import BaseCommand
import requests
from urllib.parse import urlparse
from django.conf import settings

class Command(BaseCommand):
    help = 'Télécharge un fichier en utilisant les données fournies'

    def add_arguments(self, parser):
        parser.add_argument('url', type=str)

    def handle(self, *args, **options):
        url = options['url']

        try:
            self.stdout.write(self.style.SUCCESS(f'Données reçues : {url}'))
            response = requests.get(url)
            response.raise_for_status()  # Vérifie si la requête a réussi

            content = response.content

            # Obtenir le nom du fichier à partir de l'URL
            parsed_url = urlparse(url)
            filename = parsed_url.path.split('/')[-1]

            # Faites quelque chose avec le contenu téléchargé, par exemple, l'enregistrez dans un fichier
            with open(settings.TORRENT_EXTERNAL+'/'+filename, 'wb') as file:
                file.write(content)
            self.stdout.write(self.style.SUCCESS('Fichier téléchargé avec succès.'))
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f'Erreur lors du téléchargement du fichier : {e}'))
        except PermissionError as e:
            self.stdout.write(self.style.ERROR(f'Probleme de permission sur : {e}'))

