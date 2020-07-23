from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets
from .serializers import TorrentSerializer
from .models import Torrent

def index(request):
    return HttpResponse("Bitiso.org index page")

class TorrentViewSet(viewsets.ModelViewSet):
    queryset = Torrent.objects.all()
    serializer_class = TorrentSerializer
