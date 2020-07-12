from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from torrent.models import choicesSizeUnit, Torrent
from torrent.bencodepy import decode_from_file, encode
from torrent.utils import humanSize
import os, re, hashlib, binascii

class Command(BaseCommand):
    help = 'Import new Torrent to DB'

    def handle(self, *args, **options):
        # For each torrent files
        for torrentFile in os.listdir(settings.TORRENT_ROOT_TMP):
            toMoveFile = False

            if not torrentFile.endswith(settings.TORRENT_FILE_EXT):
                continue

            # Retrieve information for current torrent file
            torrent = Torrent()
            absolutePath    = os.path.join(settings.TORRENT_ROOT, torrentFile)
            absolutePathTmp = os.path.join(settings.TORRENT_ROOT_TMP, torrentFile)
            torrentDecoded  = decode_from_file(absolutePathTmp)
            torrentInfoHash = hashlib.sha1(encode(torrentDecoded[b'info'])).hexdigest()

            try:
                Torrent.objects.get(hash = torrentInfoHash)
                toMoveFile = True
                self.stdout.write(self.style.WARNING('Torrent hash info "%s" already exist in the DB!' % torrentInfoHash))
            except:
                torrentSize, torrentSizeUnitLevel                   = humanSize(torrentDecoded[b'info'][b'length'])
                torrentSizePiece, torrentSizePieceLevelUnitLevel    = humanSize(torrentDecoded[b'info'][b'piece length'])

                torrent.hash            = torrentInfoHash
                torrent.name            = re.sub("^b'|'$", "", str(torrentDecoded[b'info'][b'name']))
                torrent.torrentFileName = torrentFile
                torrent.size            = round(torrentSize, 3)
                torrent.sizeUnit        = choicesSizeUnit[torrentSizeUnitLevel][0]
                torrent.nbPiece         = len(binascii.hexlify(torrentDecoded[b'info'][b'pieces'])) // 40
                torrent.sizePiece       = round(torrentSizePiece, 3)
                torrent.sizePieceUnit   = choicesSizeUnit[torrentSizePieceLevelUnitLevel][0]

                # Try to save information in the DB
                try:
                    torrent.save()
                    toMoveFile = True
                    self.stdout.write(self.style.SUCCESS('Successfully data saving in the DB!'))
                except:
                    self.stdout.write(self.style.ERROR('Fail saving torrent information for "%s"!' % torrentFile))
                    pass

            if toMoveFile:
                # Try to move file
                try:
                    os.rename(absolutePathTmp, absolutePath)
                    self.stdout.write(self.style.SUCCESS('Successfully torrent file "%s" moved!' % torrentFile))
                except:
                    self.stdout.write(self.style.ERROR('Fail torrent file "%s" move!' % torrentFile))
