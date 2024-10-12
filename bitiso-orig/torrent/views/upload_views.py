import os
from ..models import Torrent
from django.shortcuts import  redirect
from ..forms import FileUploadForm
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from torf import Torrent as Torrenttorf, BdecodeError,  ReadError, WriteError
from torrent.models import Torrent, Tracker

@login_required
def file_upload(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            fs = FileSystemStorage(location=settings.MEDIA_TORRENT)
            filename = file.name

            # Vérifiez si le fichier existe déjà
            if fs.exists(filename):
                messages.error(request, f"The file '{filename}' already exists. Please rename your file and try again.")
                return redirect('dashboard')

            # Enregistrez le fichier
            filename = fs.save(file.name, file)
            try:
                torrent_file_path = os.path.join(settings.MEDIA_TORRENT, filename)
                print(f"File saved temporarily at {torrent_file_path}")

                if not os.path.exists(torrent_file_path):
                    raise FileNotFoundError(f"File not found at {torrent_file_path}")

                t = Torrenttorf.read(torrent_file_path)

                # Ajouter les trackers Bitiso si nécessaire
                bitiso_trackers = [settings.TRACKER_ANNOUNCE]
                existing_trackers = [tracker for sublist in t.trackers for tracker in sublist]
                for tracker in bitiso_trackers:
                    if tracker not in existing_trackers:
                        t.trackers.append([tracker])

                print(f"Trackers after adding Bitiso: {t.trackers}")

                # Supprimez l'ancien fichier avant d'écrire le nouveau
                if os.path.exists(torrent_file_path):
                    os.remove(torrent_file_path)
                t.write(torrent_file_path)
                print(f"Torrent file with added trackers saved at {torrent_file_path}")

                if Torrent.objects.filter(info_hash=t.infohash).exists():
                    messages.warning(request, f"Info hash {t.infohash} already exists in the database.")
                else:
                    file_list = ''.join([f"{file.name};{file.size}\n" for file in t.files])
                    magnet_uri = str(t.magnet())
                    obj = Torrent(
                        info_hash=t.infohash[:40],
                        name=t.name[:128],
                        size=t.size,
                        pieces=t.pieces,
                        piece_size=t.piece_size,
                        magnet=magnet_uri[:2048],
                        torrent_filename=(t.name + '.torrent')[:128],
                        is_bitiso=False,
                        metainfo_file='torrent/' + os.path.basename(torrent_file_path),
                        file_list=file_list[:2048],
                        file_nbr=len(t.files),
                        uploader=request.user,
                        comment="Default comment"[:256],
                        slug=t.name[:50],
                        category=None,
                        is_active=False,
                        description="Default description"[:2000],
                        website_url="",
                        website_url_download="",
                        website_url_repo="",
                        version="1.0"[:16],
                        gpg_signature=None,
                        hash_signature=""[:128],
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
                                print(f"New tracker {tracker_url} added to the database.")
                            else:
                                list_of_tracker_id.append([Tracker.objects.get(url=tracker_url).id, level])
                                print(f"Existing tracker {tracker_url} found in the database.")

                    for tracker_id in list_of_tracker_id:
                        obj.trackers.add(tracker_id[0])
                        tracker_stat = obj.trackerstat_set.get(tracker_id=tracker_id[0])
                        tracker_stat.level = tracker_id[1]
                        tracker_stat.save()
                        print(f"Tracker {tracker_id[0]} linked to torrent {obj.name}.")

                    messages.success(request, "Upload and import succeeded.")
            except FileNotFoundError as e:
                print(f"File not found error: {e}")
                messages.error(request, f"File not found error: {e}")
            except ReadError as e:
                print(f"Read error: {e}")
                messages.error(request, f"Read error: {e}")
            except WriteError as e:
                print(f"Write error: {e}")
                messages.error(request, f"Write error: {e}")
            except BdecodeError as e:
                print(f"Invalid torrent file format: {e}")
                messages.error(request, "Invalid torrent file format.")
            return redirect('dashboard')
    return redirect('dashboard')
