from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    """
    Categorie of torrents
    """
    class Meta:
        verbose_name        = _(u'Category')
        verbose_name_plural = _(u'Categories')

    def __str__(self):
        return u'%s (ID %d)' % (self.name, self.id)

    id = models.AutoField(primary_key=True)
    name = models.CharField(_(u'Name'), max_length=64, null=False)
    category_parent_id = models.ForeignKey('self', verbose_name=_(u'Parent category'), blank=True, null=True, on_delete=models.PROTECT)
    creation = models.DateTimeField(auto_now_add=True, null=False)
    deletion = models.DateTimeField(_(u'Delete?'), blank=True, null=True)


class Tracker(models.Model):
    """
    Tracker info
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32,default='NONAME')
    url = models.CharField(max_length=1000)

    def __str__(self):
        return self.name 


class Torrent(models.Model):
    """
    Torrent data
    http://www.bittorrent.org/beps/bep_0003.html
    """

    class Meta:
        verbose_name        = _(u'Torrent')
        verbose_name_plural = _(u'Torrents')

    def __str__(self):
        return u'%s (Hash %s)' % (self.name, self.info_hash)

    # Fields extraced from .torrent file with management import2db.py

    info_hash = models.CharField(_(u'SHA1 of torrent'), max_length=40, primary_key=True)
    name = models.CharField(_(u'Name'), max_length=128, null=False)
    size = models.PositiveBigIntegerField(_(u'Size'), null=False, default=0)
    pieces = models.IntegerField(_(u'Number of piece'), null=False, default=1)
    piece_size = models.IntegerField(_(u'Piece size in byte'), null=False, default=0)
    magnet= models.TextField(_(u'Magnet URI'), null=False, default="NONAME")
    torrent_filename= models.CharField(_(u'Torrent file name'), max_length=128, null=False, default="NONAME")
    comment = models.CharField(_(u'Comment'), max_length=256, null=False, default="NONAME")
    trackers = models.ManyToManyField(Tracker)
    file_list = models.TextField(_(u'List of files'), null=False, default="NONAME")
    file_nbr = models.IntegerField(_(u'Number of file'), null=False, default=1)

    # Other field that describe the torrent

    category_id = models.ForeignKey(Category, verbose_name=_(u'Category'), null=True, on_delete=models.PROTECT)
    is_active = models.BooleanField(_(u'Show in the front end'),null=False, default=False)
    is_bitiso = models.BooleanField(_(u'Created by bitiso ?'),null=False, default=True)
    description = models.TextField(_(u'Description'), blank=True, null=True, default='')
    website_url = models.CharField(_(u'URL of official website'), max_length=2000, blank=True, null=True)
    website_url_download = models.CharField(_(u'URL of official download page'), max_length=2000, blank=True)
    website_url_repo = models.CharField(_(u'URL of repository'), max_length=2000, blank=True)
    version =  models.CharField(_(u'Version of the software'), max_length=16,blank=True)
    gpg_signature = models.FileField(upload_to='torrent/',blank=True)
    metainfo_file = models.FileField(upload_to='torrent/',blank=True)
    hash_signature =  models.CharField(_(u'Any hash signature'), max_length=128, blank=True, null=True)


    creation = models.DateTimeField(auto_now_add=True)
    deletion = models.DateTimeField(_(u'Delete?'), blank=True, null=True)
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_(u'Uploader'), null=True, blank=True, default='', on_delete=models.PROTECT)
    
    # Stats

    seed = models.IntegerField(_(u'Number of seed'), default=0)
    leech = models.IntegerField(_(u'Number of leech'), default=0)
    dl_number = models.IntegerField(_(u'Number of download'), default=0)
    dl_completed = models.IntegerField(_(u'Number of completed'), default=0)
