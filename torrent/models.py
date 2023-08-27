from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
import os

class Category(models.Model):
    """
    Categorie of torrents
    """

    class Meta:
        verbose_name = _(u'Category')
        verbose_name_plural = _(u'Categories')

    def __str__(self):
        return u'%s (ID %d)' % (self.name, self.id)

    # id = models.AutoField(primary_key=True)
    name = models.CharField(_(u'Name'), max_length=64, null=False)
    # slug = models.SlugField(unique=False, blank=True)
    slug = models.SlugField(blank=True, null=True)

    category_parent_id = models.ForeignKey('self', verbose_name=_(u'Parent category'), blank=True, null=True,
                                           on_delete=models.PROTECT)
    creation = models.DateTimeField(auto_now_add=True, null=False)
    deletion = models.DateTimeField(_(u'Delete?'), blank=True, null=True)

    def _generate_unique_slug(self):
        value = self.name
        slug_candidate = slugify(value)
        unique_slug = slug_candidate
        number = 1
        while Category.objects.filter(slug=unique_slug).exists():
            unique_slug = '{}-{}'.format(slug_candidate, number)
            number += 1
        return unique_slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
            # self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Tracker(models.Model):
    """
    Tracker info
    """
    # id = models.AutoField(primary_key=True)
    url = models.CharField(max_length=1000)

    def __str__(self):
        return self.url

class Project(models.Model):
    """
    Project
    """
    # id = models.AutoField(primary_key=True)
    name = models.CharField(_(u'Project name'), max_length=128, null=False)
    is_active = models.BooleanField(_(u'Show in the front end'), null=False, default=False)
    description = models.TextField(_(u'Description of project'), blank=True, null=True, default='')
    website_url = models.CharField(_(u'URL of official website'), max_length=2000, blank=True, null=True)
    website_url_download = models.CharField(_(u'URL of official download page'), max_length=2000, blank=True)
    website_url_repo = models.CharField(_(u'URL of repository'), max_length=2000, blank=True)

    # Image

    image = models.ImageField(upload_to='img/project/original/', null=True, blank=True)
    # original_image = models.ImageField(upload_to='img/project/original/',null=True, blank=True)
    mini_image = models.ImageField(upload_to='img/project/mini/', blank=True)
    small_image = models.ImageField(upload_to='img/project/small/', blank=True)
    medium_image = models.ImageField(upload_to='img/project/medium/', blank=True)
    large_image = models.ImageField(upload_to='img/project/large/', blank=True)


    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # sauvegarde de l'image originale
        self.create_resized_images()

    def create_resized_images(self):
        if not self.image:
            return

        from PIL import Image
        sizes = {
            'mini': (12, 12),
            'small': (150, 150),
            'medium': (600, 600),
            'large': (900, 900),
        }

        for size_name, size in sizes.items():
            # Ouvrez l'image originale
            img = Image.open(self.image.path)
            img.thumbnail(size)

            # Construisez le chemin pour la nouvelle image redimensionnée
            filename = os.path.basename(self.image.name)
            new_path = f'img/project/{size_name}/{filename}'

            # Assurez-vous que le dossier de destination existe
            full_path = os.path.join(settings.MEDIA_ROOT, new_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            # Sauvegardez l'image redimensionnée
            img.save(full_path)

            # Mettez à jour le champ correspondant dans le modèle
            setattr(self, f'{size_name}_image', new_path)

        super().save(update_fields=['mini_image','small_image', 'medium_image', 'large_image'])

class Torrent(models.Model):
    """
    Torrent data
    http://www.bittorrent.org/beps/bep_0003.html
    """

    class Meta:
        verbose_name = _(u'Torrent')
        verbose_name_plural = _(u'Torrents')

    def __str__(self):
        return u'%s (Hash %s)' % (self.name, self.info_hash)

    # Fields extracted from .torrent file with management import2db.py
    # id = models.AutoField(primary_key=True)
    info_hash = models.CharField(_(u'SHA1 of torrent'), max_length=40, unique=True)
   #  info_hash = models.CharField(_(u'SHA1 of torrent'), max_length=40, primary_key=True)
    name = models.CharField(_(u'Name'), max_length=128, null=False)
    size = models.PositiveBigIntegerField(_(u'Size'), null=False, default=0)
    pieces = models.IntegerField(_(u'Number of piece'), null=False, default=1)
    piece_size = models.IntegerField(_(u'Piece size in byte'), null=False, default=0)
    magnet = models.TextField(_(u'Magnet URI'), null=False, default="NONAME")
    torrent_filename = models.CharField(_(u'Torrent file name'), max_length=128, null=False, default="NONAME")
    comment = models.CharField(_(u'Comment'), max_length=256, null=False, default="NONAME")
    trackers = models.ManyToManyField(Tracker, through="TrackerStat")
    file_list = models.TextField(_(u'List of files'), null=False, default="NONAME")
    file_nbr = models.IntegerField(_(u'Number of file'), null=False, default=1)

    # Other field that describe the torrent

    category = models.ForeignKey(Category, verbose_name=_(u'Category'), null=True, on_delete=models.PROTECT)
    is_active = models.BooleanField(_(u'Show in the front end'), null=False, default=False)
    is_bitiso = models.BooleanField(_(u'Created by bitiso ?'), null=False, default=True)
    description = models.TextField(_(u'Description'), blank=True, null=True, default='')
    website_url = models.CharField(_(u'URL of official website'), max_length=2000, blank=True, null=True)
    website_url_download = models.CharField(_(u'URL of official download page'), max_length=2000, blank=True)
    website_url_repo = models.CharField(_(u'URL of repository'), max_length=2000, blank=True)
    version = models.CharField(_(u'Version of the software'), max_length=16, blank=True)
    gpg_signature = models.FileField(upload_to='torrent/', blank=True)
    metainfo_file = models.FileField(upload_to='torrent/', blank=True)
    hash_signature = models.CharField(_(u'Any hash signature'), max_length=128, blank=True, null=True)

    creation = models.DateTimeField(auto_now_add=True)
    deletion = models.DateTimeField(_(u'Delete?'), blank=True, null=True)
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_(u'Uploader'), null=True, blank=True,
                                 default='', on_delete=models.PROTECT)

    # Stats

    seed = models.IntegerField(_(u'Number of seed'), default=0)
    leech = models.IntegerField(_(u'Number of leech'), default=0)
    dl_number = models.IntegerField(_(u'Number of download'), default=0)
    dl_completed = models.IntegerField(_(u'Number of completed'), default=0)

    # Project

    project = models.ForeignKey(Project, verbose_name=_(u'Project'), null=True, on_delete=models.PROTECT)

class TrackerStat(models.Model):
    """
    Torrent statistic on trackers
    """
    torrent = models.ForeignKey(Torrent, on_delete=models.CASCADE)
    tracker = models.ForeignKey(Tracker, on_delete=models.CASCADE)
    level = models.IntegerField(_(u'Announce level'), default=0)
    seed = models.IntegerField(_(u'Number of seed'), default=0)
    leech = models.IntegerField(_(u'Number of leech'), default=0)

class ExternalTorrent(models.Model):
    url = models.CharField(_(u'URL of official website'), max_length=2000, blank=True, null=True)

    def __str__(self):
        return self.url