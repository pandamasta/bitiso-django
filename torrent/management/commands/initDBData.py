from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from torrent.models import *

class Command(BaseCommand):
    help = 'Init DB data only for tests'

    def handle(self, *args, **options):
        if not settings.ONLINE:
            categoryOS = Category(name='OS')
            categoryOS.save()
            categoryLinux = Category(name='Linux/Unix', categoryParentId=categoryOS)
            categoryLinux.save()
            categoryBSD = Category(name='BSD', categoryParentId=categoryOS)
            categoryBSD.save()
            categoryWindows = Category(name='Windows', categoryParentId=categoryOS)
            categoryWindows.save()
            category = Category(name='Debian', categoryParentId=categoryLinux)
            category.save()
            category = Category(name='ArchLinux', categoryParentId=categoryLinux)
            category.save()
            category = Category(name='FreeBSD', categoryParentId=categoryBSD)
            category.save()
            category = Category(name='OpenBSD', categoryParentId=categoryBSD)
            category.save()
            category = Category(name='RedHat', categoryParentId=categoryLinux)
            category.save()
            category = Category(name='CentOS', categoryParentId=categoryLinux)
            category.save()
            category = Category(name='Windows 10', categoryParentId=categoryWindows)
            category.save()
            categoryMusic = Category(name='Music')
            categoryMusic.save()
            category = Category(name='Piano', categoryParentId=categoryMusic)
            category.save()
            category = Category(name='Rock', categoryParentId=categoryMusic)
            category.save()

            self.stdout.write(self.style.SUCCESS('Successfully data upload for tests!'))
