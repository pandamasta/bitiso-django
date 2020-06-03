from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

choicesSizeUnit = (('b',  _(u'b')),
                    ('Kb',  _(u'Kb')),
                    ('Mb', _(u'Mb')),
                    ('Gb', _(u'Gb')))

class Category(models.Model):
    """
    This class represent the categorie of torrents i
    """

    class Meta:
        verbose_name        = _(u'Category')
        verbose_name_plural = _(u'Categories')

        indexes = [
            models.Index(fields=['categoryParentId'], name='ix_category_categoryParentId'),
        ]

        unique_together = (('categoryParentId', 'name'), )

    def __str__(self):
        return u'%s (ID %d)' % (self.name, self.id)

    def clean(self):
        if self.categoryParentId is not None and \
                ((self.categoryParentId.categoryParentId is not None and self.categoryParentId.categoryParentId.id == self.id) or \
                self.categoryParentId.id == self.id):
            raise ValidationError(_(u'You cannot assign a parent category if it itself refers to this category (circular reference)!'))

    id = models.AutoField(primary_key=True)
    name = models.CharField(_(u'Name'), max_length=64, null=False)
    categoryParentId = models.ForeignKey('self', verbose_name=_(u'Parent category'), blank=True, null=True, on_delete=models.PROTECT)
    creation = models.DateTimeField(auto_now_add=True, null=False)
    deletion = models.DateTimeField(_(u'Delete?'), blank=True, null=True)

class Torrent(models.Model):
    """
    Torrent with all it's meta data to rebuild it on the fly 
    Compliant with BEP 0003 
    http://www.bittorrent.org/beps/bep_0003.html
    """

    class Meta:
        verbose_name        = _(u'Torrent')
        verbose_name_plural = _(u'Torrents')

        indexes = [
            models.Index(fields=['categoryId'], name='ix_torrent_categoryId'),
            models.Index(fields=['uploader'], name='ix_torrent_uploader'),
        ]

        #unique_together = (('torrentFileName'), )

    def __str__(self):
        return u'%s (Hash %s)' % (self.name, self.hash)

    def formfield_for_foreignkey(self, dbField, request, **kwargs):
        if dbField.name == 'uploader':
            # Set current user id for uploader name
            kwargs['initial'] = request.user.id
        return super(Torrent, self).formfield_for_foreignkey(dbField, request, **kwargs)

    hash = models.CharField(_(u'Hash SHA1 of torrent'), max_length=40, primary_key=True)
    torrentFileName= models.CharField(_(u'Torrent file name'), max_length=128, null=False, default="NONAME")
    name = models.CharField(_(u'Name'), max_length=128, null=False)
    description = models.CharField(_(u'Description'), max_length=8192, null=True)
    size = models.DecimalField(_(u'Size'), max_digits=13, decimal_places=3, null=False, default=0)
    sizeUnit = models.CharField(_(u'Size unit'), max_length=2, null=False, choices=choicesSizeUnit, default=u'b')
    nbPiece = models.IntegerField(_(u'Number of piece'), null=False, default=1)
    sizePiece = models.IntegerField(_(u'Size for each piece in byte'), null=False, default=0)
    sizePieceUnit = models.CharField(_(u'Size piece unit'), max_length=2, null=False, choices=choicesSizeUnit, default=u'b')
    dlNumber = models.IntegerField(_(u'Number of download'), null=False, default=0)
    dlCompleted = models.IntegerField(_(u'Number of completed'), null=False, default=0)
    seed = models.IntegerField(_(u'Number of seed'), null=False, default=0)
    leech = models.IntegerField(_(u'Number of leech'), null=False, default=0)
    creation = models.DateTimeField(auto_now_add=True, null=False)
    deletion = models.DateTimeField(_(u'Delete?'), blank=True, null=True)
    categoryId = models.ForeignKey(Category, verbose_name=_(u'Category'), null=True, on_delete=models.PROTECT)
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_(u'Uploader'), null=True, on_delete=models.PROTECT)
    is_bitiso = models.BooleanField(_(u'Created by bitiso ?'),null=False, default=True)

class TorrentStatSL(models.Model):
    """
    Live statistic of torrent hash
    """

    def __str__(self):
        return u'Hash %s' % (self.hash)

    hash = models.CharField(_(u'Hash'), max_length=64, primary_key=True)
    seederNr = models.IntegerField(_(u'Number of seeders'), null=False, default=0)
    leecherNr = models.IntegerField(_(u'Number of leechers'), null=False, default=0)
