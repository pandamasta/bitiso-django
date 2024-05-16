from .models import Torrent, Project, Category
from django.http import HttpResponse
from django.core.management import call_command
from django.shortcuts import render, get_object_or_404, redirect
from .forms import SearchForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .ratelimit import RateLimit, RateLimitExceeded
from .forms import FileUploadForm
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib import messages


# def project_detail(request, project_id):
#     project = get_object_or_404(Project, pk=project_id)
#     return render(request, 'path_to_your_template.html', {'project': project})

def index(request):

    try:
      torrent_list =  Torrent.objects.filter(is_active=True).order_by('-creation')
    except Torrent.DoesNotExist:
      torrent_list = None

    paginator = Paginator(torrent_list, 10)

    # Get page number in GET
    page = request.GET.get('page')

    try:
        torrents = paginator.page(page)
    except PageNotAnInteger:
        torrents = paginator.page(1)
    except EmptyPage:
        torrents = paginator.page(paginator.num_pages)

    context = {'torrent_list': torrent_list}
    return render(request, 'torrent/index.html', context)

def detail(request, torrent_name):

    torrent_detail = Torrent.objects.get(name=torrent_name)
    tracker_detail = torrent_detail.trackerstat_set.all()
    context = {'torrent_detail': torrent_detail ,'tracker_detail': tracker_detail}

    return render(request, 'torrent/details.html', context)

def category(request, category_id):

    torrent_list = Torrent.objects.filter(is_active=True).filter(category_id=category_id).order_by('-creation')
    context = {'torrent_list': torrent_list}

    return render(request, 'torrent/category.html', context)

def project(request):

    project_list = Project.objects.filter(is_active=True)
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

def torrent_list_view(request):
    try:
        RateLimit(
            key=f"{request.user.id}:torrent_list",
            limit=20,  # par exemple, limitez à 5 requêtes par minute
            period=60,  # en secondes
            request=request,
        ).check()
    except RateLimitExceeded as e:
        return HttpResponse(
            f"Rate limit exceeded. You have used {e.usage} requests, limit is {e.limit}.",
            status=429,
        )

    form = SearchForm(request.GET or None)
    torrents = Torrent.objects.filter(is_active=True).order_by('-creation')

    if form.is_valid() and form.cleaned_data['query']:
        query = form.cleaned_data['query']
        torrents = torrents.filter(name__icontains=query)

    # Pagination
    paginator = Paginator(torrents, 60)  # 10 torrents par page, ajustez si nécessaire

    page = request.GET.get('page')
    try:
        torrents = paginator.page(page)
    except PageNotAnInteger:
        # Si la page n'est pas un entier, donnez la première page.
        torrents = paginator.page(1)
    except EmptyPage:
        # Si la page est en dehors de la plage (par exemple, 9999), donnez la dernière page des résultats.
        torrents = paginator.page(paginator.num_pages)

    context = {
        'form': form,
        'torrent_list': torrents
    }
    return render(request, 'torrent/index.html', context)

def category_list(request):
    categories = Category.objects.filter(category_parent_id__isnull=True)
    return render(request, 'torrent/category_list.html', {'categories': categories})

def manage_torrents(request):
    user_torrents = Torrent.objects.filter(uploader=request.user)
    return render(request, 'torrent/manage_torrents.html', {'torrents': user_torrents})


def file_upload(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            filename = fs.save(file.name, file)
            messages.success(request, "Upload succeed")
            return redirect('manage_torrents')
    else:
        form = FileUploadForm()
    return render(request, 'torrent/upload.html', {'form': form})



def file_upload_success(request):
    return render(request, 'torrent/upload_success.html')
