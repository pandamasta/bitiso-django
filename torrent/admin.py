from django.contrib import admin
from django.forms import *
from django.db.models import Q
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from .models import *
from datetime import datetime
from tinymce.widgets import TinyMCE
from torrent.models import *
from .bencodepy import *
import binascii

# Category ***********************************
class CategoryModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(CategoryModelForm, self).__init__(*args, **kwargs)
        if self.instance.id is not None:
            self.fields['categoryParentId'].queryset = Category.objects.filter(Q(id__lt=self.instance.id) | Q(id__gt=self.instance.id)).filter(deletion__isnull=True).order_by('name')
        else:
            self.fields['categoryParentId'].queryset = Category.objects.filter(deletion__isnull=True).order_by('name')
        self.fields['categoryParentId'].label_from_instance = lambda obj: u'%s' % (obj.name)

    class Meta:
        model   = Category
        fields  = '__all__'

class CategoryAdmin(admin.ModelAdmin):
    # TO DO:
    #  - Review default filter with Django, because changelist_view() doesn't work to show all values :'(
    #  - Review sort and presentation related parent category
    # Display table
    def changelist_view(self, request, extra_context = None):
        if not request.GET.get('deletion__isnull') and not request.GET.get('deletion__gte'):
            requestGet = request.GET.copy()
            requestGet['deletion__isnull'] = 'True'
            request.GET = requestGet
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super(CategoryAdmin, self).changelist_view(request, extra_context = extra_context)

    # Get parent category name for current category with hypertext link to modify this parent category object
    def linkEditCategoryParentId(self, obj):
        if obj.categoryParentId is not None:
            return format_html("<a href='{url}'>{printName}</a>", url=str(obj.categoryParentId.id) + '/change/', printName=obj.categoryParentId.name)
        else:
            return ''

    # Actions
    def delete_category_selected(modeladmin, request, queryset):
        queryset.update(deletion = datetime.now())

    def undelete_category_selected(modeladmin, request, queryset):
        queryset.update(deletion = None)

    linkEditCategoryParentId.short_description  = _(u'Parent category')
    linkEditCategoryParentId.admin_order_field  = 'categoryParentId__name'
    linkEditCategoryParentId.allow_tags         = True
    list_display                                = ('linkEditCategoryParentId', 'name', 'deletion')
    list_display_links                          = ('linkEditCategoryParentId', 'name')
    list_filter                                 = ('deletion', 'categoryParentId__name', 'name', 'creation', )
    ordering                                    = ('categoryParentId__name', )
    form                                        = CategoryModelForm
    actions                                     = [delete_category_selected, undelete_category_selected]

# Torrent ***********************************
class TorrentModelForm(ModelForm):
    class Meta:
        model   = Torrent
        fields  = ['hash','uploader','torrentFileName','categoryId','name','description','deletion']
        widgets = {
            'description': TinyMCE(attrs={'cols': 80, 'rows': 100}),
        }

    def __init__(self, *args, **kwargs):
        super(TorrentModelForm, self).__init__(*args, **kwargs)

        try:
            # If field is present of form. Turn readonly
            self.fields['hash'].widget.attrs['readonly'] = True
        except:
            pass

        self.fields['categoryId'].queryset = Category.objects.all().filter(deletion__isnull=True).order_by('name')
        self.fields['categoryId'].label_from_instance = lambda obj: u'%s' % (obj.name)
    '''
    def clean(self):
        print('clean_admin')
        if self.cleaned_data['torrentFileName'] is not None:
            torrentDecoded  = decode_from_file(self.cleaned_data['torrentFileName'])
            torrentInfoHash = hashlib.sha1(encode(torrentDecoded[b'info'])).hexdigest()

            try:
                if self.cleaned_data['hash'] != torrentInfoHash:
                    raise ValidationError('You cannot change torrent file if the info hash is different!')
            # self.cleaned_data['hash'] does not exist: case if field does not displayed
            except KeyError:
                pass

            # Using self.instance.fieldName because if this field is exclude, we cannot set value
            self.instance.hash      = torrentInfoHash
            self.instance.size      = torrentDecoded[b'info'][b'length']
            self.instance.nbPiece   = len(binascii.hexlify(torrentDecoded[b'info'][b'pieces'])) // 40
            self.instance.sizePiece = torrentDecoded[b'info'][b'piece length']
    '''
class TorrentAdmin(admin.ModelAdmin):
    '''
    Un peut rude au debut non ? ;)

    def has_add_permission(self, request):
        return False
    '''
    '''
    def get_form(self, request, obj=None, **kwargs):
        # If current page is to add a new torrent
        if request.path_info.endswith('/add/'):
             # Exclude specific fields
            self.exclude = [ 'hash','deletion' ]
        else:
            # It seems a cache?
            # Because if we do not remove values in exclude
            # Form change continue to exclude field of form add
            self.exclude = []
        return super(TorrentAdmin, self).get_form(request, obj=obj, **kwargs)
    '''

    list_display = ('hash', 'torrentFileName', 'name', 'description', 'size', 'sizeUnit', 'nbPiece', 'sizePiece', 'dlNumber', 'dlCompleted', 'seed', 'leech', 'creation','deletion','categoryId','uploader','is_bitiso')

admin.site.register(Torrent, TorrentAdmin)

admin.site.disable_action('delete_selected') # Disable default action manage by Django
admin.site.register(Category, CategoryAdmin)
