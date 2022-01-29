from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    """
    This class represent the categorie of torrents
    """

    class Meta:
        verbose_name        = _(u'Category')
        verbose_name_plural = _(u'Categories')

        #indexes = [
        #    models.Index(fields=['categoryParentId'], name='ix_category_categoryParentId'),
        #]

        #unique_together = (('categoryParentId', 'name'), )

    def __str__(self):
        return u'%s (ID %d)' % (self.name, self.id)

    #def clean(self):
    #    if self.category_parent_id is not None and \
    #            ((self.category_parent_id.category_parent_id is not None and self.category_parent_id.category_parent_id.id == self.id) or \
    #            self.category_parent_id.id == self.id):
    #        raise ValidationError(_(u'You cannot assign a parent category if it itself refers to this category (circular reference)!'))

    id = models.AutoField(primary_key=True)
    name = models.CharField(_(u'Name'), max_length=64, null=False)
    category_parent_id = models.ForeignKey('self', verbose_name=_(u'Parent category'), blank=True, null=True, on_delete=models.PROTECT)
    creation = models.DateTimeField(auto_now_add=True, null=False)
    deletion = models.DateTimeField(_(u'Delete?'), blank=True, null=True)

class Tracker(models.Model):
    # ...
    name = models.CharField(max_length=32,default='NONAME')
    url = models.CharField(max_length=1000)

    def __str__(self):
        return self.name 

class Torrent(models.Model):
    """
    Torrent with all it's meta data to rebuild it on the fly 
    Compliant with BEP 0003 
    http://www.bittorrent.org/beps/bep_0003.html
    """

    class Meta:
        verbose_name        = _(u'Torrent')
        verbose_name_plural = _(u'Torrents')

        #indexes = [
        #    models.Index(fields=['categoryId'], name='ix_torrent_categoryId'),
        #    models.Index(fields=['uploader'], name='ix_torrent_uploader'),
        #]

        #unique_together = (('torrentFileName'), )

    def __str__(self):
        return u'%s (Hash %s)' % (self.name, self.info_hash)

    #def formfield_for_foreignkey(self, dbField, request, **kwargs):
    #    if dbField.name == 'uploader':
    #        # Set current user id for uploader name
    #        kwargs['initial'] = request.user.id
    #    return super(Torrent, self).formfield_for_foreignkey(dbField, request, **kwargs)


    # Fields extraced from .torrent file with management import2db.py

    info_hash = models.CharField(_(u'SHA1 of torrent'), max_length=40, primary_key=True)
    name = models.CharField(_(u'Name'), max_length=128, null=False)
    size = models.IntegerField(_(u'Size'), null=False, default=0)
    pieces = models.IntegerField(_(u'Number of piece'), null=False, default=1)
    piece_size = models.IntegerField(_(u'Piece size in byte'), null=False, default=0)
    magnet= models.CharField(_(u'Magnet URI'), max_length=256, null=False, default="NONAME")
    torrent_filename= models.CharField(_(u'Torrent file name'), max_length=128, null=False, default="NONAME")
    comment = models.CharField(_(u'Comment'), max_length=256, null=False, default="NONAME")
    trackers = models.ManyToManyField(Tracker)
    file_list = models.TextField(_(u'List of files'), null=False, default="NONAME")
    file_nbr = models.IntegerField(_(u'Number of file'), null=False, default=1)

    # Other field that describe the torrent

    category_id = models.ForeignKey(Category, verbose_name=_(u'Category'), null=True, on_delete=models.PROTECT)
    is_active = models.BooleanField(_(u'Show in the front end'),null=False, default=False)
    is_bitiso = models.BooleanField(_(u'Created by bitiso ?'),null=False, default=True)
    description = models.CharField(_(u'Description'), max_length=8192, blank=True, null=True, default='')
    website_url = models.CharField(_(u'URL of official website'), max_length=2000, blank=True, null=True)
    website_url_download = models.CharField(_(u'URL of official download page'), max_length=2000, blank=True)
    website_url_repo = models.CharField(_(u'URL of repository'), max_length=2000, blank=True)
#    architecture = models.ForeignKey(Architecture, verbose_name=_(u'Architecure'), on_delete=models.PROTECT)
    version =  models.CharField(_(u'Version of the software'), max_length=16,blank=True)
    gpg_signature = models.FileField(upload_to='torrent/',blank=True)
    metainfo_file = models.FileField(upload_to='torrent/',blank=True)


    creation = models.DateTimeField(auto_now_add=True)
    deletion = models.DateTimeField(_(u'Delete?'), blank=True, null=True)
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_(u'Uploader'), null=True, blank=True, default='', on_delete=models.PROTECT)
    
    # Stats

    seed = models.IntegerField(_(u'Number of seed'), default=0)
    leech = models.IntegerField(_(u'Number of leech'), default=0)
    dl_number = models.IntegerField(_(u'Number of download'), default=0)
    dl_completed = models.IntegerField(_(u'Number of completed'), default=0)

#class Architecture(models.Model):
#    """
#    Architecture of the software
#    """
#    ARCHITECTURE_CHOICES = [
#        (I386, '32bit'),
#        (AMD64, '64bit'),
#        (ARM, 'ARM'),
#        (NONE, ''),
#    ]
#    flavor = models.CharField(
#        max_length=8,
#        choices=ARCHITECTURE_CHOICES,
#        default="",
#    )
#
#    class Meta:
#        verbose_name        = _(u'Torrent')
#        verbose_name_plural = _(u'Torrents')

class TorrentStatSL(models.Model):
    """
    Live statistic of torrent hash
    """

    def __str__(self):
        return u'Hash %s' % (self.info_hash)

    info_hash = models.CharField(_(u'Hash'), max_length=64, primary_key=True)
    seederNr = models.IntegerField(_(u'Number of seeders'), null=False, default=0)
    leecherNr = models.IntegerField(_(u'Number of leechers'), null=False, default=0)
