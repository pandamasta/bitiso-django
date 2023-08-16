from .models import Torrent, Project
from django.http import HttpResponse
from django.core.management import call_command
from django.shortcuts import render, get_object_or_404

def project_detail(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    return render(request, 'path_to_your_template.html', {'project': project})

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
    tracker_detail = torrent_detail.trackerstat_set.all()
    context = {'torrent_detail': torrent_detail ,'tracker_detail': tracker_detail}

    return render(request, 'torrent/details.html', context)

def category(request, category_id):

    torrent_list = Torrent.objects.filter(is_active=True).filter(category_id=category_id).order_by('-creation')
    context = {'torrent_list': torrent_list}

    return render(request, 'torrent/index.html', context)

def project(request):

    project_list = Project.objects.all()
    context = {'projects': project_list}

    return render(request, 'torrent/project.html', context)


def project_detail(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    return render(request, 'torrent/project_detail.html', {'project': project})

# Admin custom

def custom_admin_page(request):
    return render(request, 'admin/custom_admin_page.html')

def get_script_name(script_param):
    mapping = {
        'import_torrent': 'import_torrent',
        'scraper': 'scraper',
    }
    return mapping.get(script_param, None)

def run_management_script(request, script):
    script_name = get_script_name(script)
    if script_name:
        try:
            call_command(script_name)
            return HttpResponse(f"Le script de gestion '{script_name}' a été déclenché avec succès.")
        except Exception as e:
            return HttpResponse(f"Une erreur s'est produite : {e}", status=500)
    else:
        return HttpResponse("Script inconnu.", status=400)




    # categories = Category.objects.all()
    # projects = Project.objects.all()
    return render(request, 'upload_image.html')