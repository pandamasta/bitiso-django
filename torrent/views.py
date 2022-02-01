from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets
from .serializers import TorrentSerializer
from .models import Torrent

def index(request):

    #torrent_list = Torrent.objects.filter(is_active=True).order_by('-creation')
    #torrent_list = "test" 
    try:
      torrent_list =  Torrent.objects.filter(is_active=True).order_by('-creation')
    except Torrent.DoesNotExist:
      torrent_list = None

    context = {'torrent_list': torrent_list}

    return render(request, 'torrent/index.html', context)

def detail(request, info_hash):

    torrent_detail = Torrent.objects.get(info_hash=info_hash)
    context = {'torrent_detail': torrent_detail}

    return render(request, 'torrent/details.html', context)

def category(request, category_id):

    torrent_list = Torrent.objects.filter(is_active=True).filter(category_id=category_id).order_by('-creation')
    context = {'torrent_list': torrent_list}

    return render(request, 'torrent/index.html', context)

class TorrentViewSet(viewsets.ModelViewSet):
    queryset = Torrent.objects.all()
    serializer_class = TorrentSerializer
