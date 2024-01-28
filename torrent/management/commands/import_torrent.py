import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings
from torf import Torrent as Torrenttorf
from torrent.models import Torrent, Tracker

class Command(BaseCommand):
    help = "Import torrent from existing one"

    def handle(self, *args, **kwargs):
        # Chemin du dossier contenant les torrents externes
        torrent_file_tmp = settings.TORRENT_EXTERNAL

        for i in os.listdir(torrent_file_tmp):
            absolute_path = os.path.join(torrent_file_tmp, i)
            print("Read Torrent: " + absolute_path)

            # Lire les métadonnées du .torrent existant
            t = Torrenttorf.read(absolute_path)

            # Vérifier si info_hash existe déjà dans la base de données
            if Torrent.objects.filter(info_hash=t.infohash).exists():
                print("Info hash " + t.infohash + " already exists in DB. Skip")
            else:
                print("Torrent " + t.infohash + " doesn't exist")

                # Ajouter votre tracker personnalisé à la liste des trackers
                t.trackers.append([settings.TRACKER_ANNOUNCE])

                # Afficher le contenu de l'objet Torrenttorf pour le débogage
                print("Contenu de l'objet Torrenttorf avant l'écriture :")
                print("Name:", t.name)
                print("Trackers:", t.trackers)

               # torrent_folder = os.path.join(settings.BITISO_TORRENT_STATIC, "meta")
               # if not os.path.exists(torrent_folder):
               #     os.makedirs(torrent_folder)

                torrent_file_path = os.path.join(settings.BITISO_TORRENT_STATIC, i)
                if os.path.exists(torrent_file_path):
                    print("Le fichier existe déjà. Remove")
                    os.remove(torrent_file_path)
                else:
                    print("Le fichier n'existe pas.")

                # Écrire le fichier torrent
                t.write(torrent_file_path)
                print("Fichier torrent " + torrent_file_path + " écrit avec succès.")

                # Insérer le tracker inconnu dans la base de données
                list_of_tracker_id = []
                print("Insert unknown tracker in DB")
                for sublist in t.trackers:
                    level = t.trackers.index(sublist)
                    for tracker_url in sublist:
                        print("tracker_url : " + str(tracker_url) + " level: " + str(level))
                        if not Tracker.objects.filter(url=tracker_url).exists():
                            print('Insert new tracker: ' + str(tracker_url))
                            tracker = Tracker(url=tracker_url)
                            tracker.save()
                            list_of_tracker_id.append([tracker.id, level])
                        else:
                            list_of_tracker_id.append([Tracker.objects.get(url=tracker_url).id, level])

                        print(list_of_tracker_id)

                # Format de la liste des fichiers dans le torrent
                file_list = ''
                for file in t.files:
                    file_list += str(file.name + ';' + str(file.size) + '\n')
                print("File in torrent: " + file_list)

                # Insérer les métadonnées du torrent dans la base de données
                obj = Torrent(info_hash=t.infohash, name=t.name, size=t.size, pieces=t.pieces, piece_size=t.piece_size,
                              magnet=t.magnet(), torrent_filename=t.name + '.torrent', is_bitiso=False,
                              metainfo_file='torrent/' + t.name + '.torrent', file_list=file_list, file_nbr=len(t.files))
                obj.save()

                # Attacher le tracker au torrent et définir le niveau du tracker
                for tracker_id in list_of_tracker_id:
                    obj.trackers.add(tracker_id[0])
                    t = obj.trackerstat_set.get(tracker_id=tracker_id[0])
                    t.level = tracker_id[1]
                    t.save()

                # Copier le torrent original dans "meta/external"
                #original_torrent_path = os.path.join(settings.TORRENT_EXTERNAL, i)
                #destination_torrent_path = os.path.join(settings.BITISO_TORRENT_STATIC,     i)
                #shutil.copyfile(original_torrent_path, destination_torrent_path)
                #print("Copied original torrent to: " + destination_torrent_path)
                # Supprimer le fichier torrent original
                #os.remove(original_torrent_path)
