import os
import requests
from ..models import Torrent
from django.http import HttpResponse
from django.shortcuts import redirect
from ..forms import URLDownloadForm
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from torf import Torrent as Torrenttorf, BdecodeError,  ReadError, WriteError
from torrent.models import Torrent, Tracker
from django.core.files.base import ContentFile
from urllib.parse import urlparse


@login_required
def download_torrent(request):
    if request.method == 'POST':
        form = URLDownloadForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            try:
                response = requests.get(url)
                response.raise_for_status()  # Vérifie si la requête a réussi
                print(f"Successfully downloaded content from {url}")

                # Télécharger le fichier en mémoire
                content = ContentFile(response.content)

                # Obtenir le nom du fichier à partir de l'URL
                parsed_url = urlparse(url)
                filename = parsed_url.path.split('/')[-1]
                print(f"Filename obtained: {filename}")

                # Sauvegarder le fichier temporairement pour l'importation
                fs = FileSystemStorage(location=settings.MEDIA_TORRENT)
                temp_file_path = fs.save(filename, content)
                temp_file_full_path = os.path.join(settings.MEDIA_TORRENT, temp_file_path)
                print(f"File saved temporarily at {temp_file_full_path}")

                # Vérifier si le fichier existe réellement à ce chemin
                if not os.path.exists(temp_file_full_path):
                    raise FileNotFoundError(f"File not found at {temp_file_full_path}")

                # Lancer l'importation du fichier torrent dans la base de données
                t = Torrenttorf.read(temp_file_full_path)
                if Torrent.objects.filter(info_hash=t.infohash).exists():
                    messages.warning(request, f"Info hash {t.infohash} already exists in the database.")
                else:
                    t.trackers.append([settings.TRACKER_ANNOUNCE])
                    file_list = ''.join([f"{file.name};{file.size}\n" for file in t.files])
                    magnet_uri = str(t.magnet())  # Ensure magnet URI is a string

                    torrent_name_with_extension = (t.name + '.torrent')[:128]  # Truncate to fit the database field length

                    # Écrire le fichier torrent dans media/torrent
                    torrent_dir = os.path.join(settings.MEDIA_TORRENT)
                    if not os.path.exists(torrent_dir):
                        os.makedirs(torrent_dir)

                    torrent_file_path = os.path.join(torrent_dir, torrent_name_with_extension)

                    if os.path.exists(torrent_file_path):
                        print("Le fichier existe déjà. Remove")
                        os.remove(torrent_file_path)
                    else:
                        print("Le fichier n'existe pas.")

                    t.write(torrent_file_path)
                    print("Fichier torrent " + torrent_file_path + " écrit avec succès.")

                    obj = Torrent(
                        info_hash=t.infohash[:40],  # Truncate to fit the database field length
                        name=t.name[:128],  # Truncate to fit the database field length
                        size=t.size,
                        pieces=t.pieces,
                        piece_size=t.piece_size,
                        magnet=magnet_uri[:2048],  # Truncate to fit the database field length
                        torrent_filename=(t.name + '.torrent')[:128],  # Truncate to fit the database field length
                        is_bitiso=False,
                        metainfo_file='torrent/' + (t.name + '.torrent')[:128],  # Truncate to fit the database field length
                        file_list=file_list[:2048],  # Truncate to fit the database field length
                        file_nbr=len(t.files),
                        uploader=request.user,
                        comment="Default comment"[:256],  # Truncate to fit the database field length
                        slug=t.name[:50],  # Truncate to fit the database field length
                        category=None,
                        is_active=False,
                        description="Default description"[:2000],  # Truncate to fit the database field length
                        website_url="",  # Leave empty
                        website_url_download=url[:2000],  # Store the download URL
                        website_url_repo="",  # Leave empty
                        version="1.0"[:16],  # Truncate to fit the database field length
                        gpg_signature=None,
                        hash_signature=""[:128],  # Truncate to fit the database field length
                        seed=0,
                        leech=0,
                        dl_number=0,
                        dl_completed=0,
                        project=None
                    )
                    obj.save()
                    print(f"Torrent {obj.name} with hash {obj.info_hash} saved to database.")

                    list_of_tracker_id = []
                    for sublist in t.trackers:
                        level = t.trackers.index(sublist)
                        for tracker_url in sublist:
                            if not Tracker.objects.filter(url=tracker_url).exists():
                                tracker = Tracker(url=tracker_url)
                                tracker.save()
                                list_of_tracker_id.append([tracker.id, level])
                            else:
                                list_of_tracker_id.append([Tracker.objects.get(url=tracker_url).id, level])

                    for tracker_id in list_of_tracker_id:
                        obj.trackers.add(tracker_id[0])
                        tracker_stat = obj.trackerstat_set.get(tracker_id=tracker_id[0])
                        tracker_stat.level = tracker_id[1]
                        tracker_stat.save()

                    messages.success(request, "Download, upload, and import succeeded.")
            except requests.exceptions.RequestException as e:
                print(f"Error downloading file: {e}")
                messages.error(request, f'Error downloading file: {e}')
            except PermissionError as e:
                print(f"Permission error: {e}")
                messages.error(request, f'Permission error: {e}')
            except BdecodeError:
                print("Invalid torrent file format.")
                messages.error(request, "Invalid torrent file format.")
            return redirect('dashboard')
    return redirect('dashboard')