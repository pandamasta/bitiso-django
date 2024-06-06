import os
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
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import CustomAuthenticationForm
from torf import Torrent as Torrenttorf, BdecodeError
from torrent.models import Torrent, Tracker

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



def file_upload_success(request):
    return render(request, 'torrent/upload_success.html')

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'torrent/login.html', {'form': form})

@login_required
def dashboard(request):
    user = request.user
    torrents = Torrent.objects.filter(uploader=user)
    torrent_count = torrents.count()
    form = FileUploadForm()
    return render(request, 'torrent/dashboard.html', {'torrents': torrents, 'torrent_count': torrent_count, 'form': form})

@login_required
def delete_torrents(request):
    if request.method == 'POST':
        torrent_ids = request.POST.getlist('torrent_ids')
        if torrent_ids:
            Torrent.objects.filter(id__in=torrent_ids, uploader=request.user).delete()
    return redirect('dashboard')

@login_required
def file_upload(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            filename = fs.save(file.name, file)
            try:
                torrent_file_path = os.path.join(settings.MEDIA_ROOT, filename)
                t = Torrenttorf.read(torrent_file_path)

                if Torrent.objects.filter(info_hash=t.infohash).exists():
                    messages.warning(request, "Info hash " + t.infohash + " already exists in the database.")
                else:
                    t.trackers.append([settings.TRACKER_ANNOUNCE])
                    file_list = ''.join([f"{file.name};{file.size}\n" for file in t.files])
                    magnet_uri = str(t.magnet())  # Ensure magnet URI is a string
                    obj = Torrent(
                        info_hash=t.infohash[:40],  # Truncate to fit the database field length
                        name=t.name[:128],  # Truncate to fit the database field length
                        size=t.size,
                        pieces=t.pieces,
                        piece_size=t.piece_size,
                        magnet=magnet_uri[:2048],  # Truncate to fit the database field length
                        torrent_filename=(t.name + '.torrent')[:128],  # Truncate to fit the database field length
                        is_bitiso=False,
                        metainfo_file='torrent/' + (t.name + '.torrent')[:128],  # Truncate to fit the database field length
                        file_list=file_list[:2048],  # Truncate to fit the database field length
                        file_nbr=len(t.files),
                        uploader=request.user,
                        comment="Default comment"[:256],  # Truncate to fit the database field length
                        slug=t.name[:50],  # Truncate to fit the database field length
                        category=None,
                        is_active=True,
                        description="Default description"[:2000],  # Truncate to fit the database field length
                        website_url=""[:2000],  # Truncate to fit the database field length
                        website_url_download=""[:2000],  # Truncate to fit the database field length
                        website_url_repo=""[:2000],  # Truncate to fit the database field length
                        version="1.0"[:16],  # Truncate to fit the database field length
                        gpg_signature=None,
                        hash_signature=""[:128],  # Truncate to fit the database field length
                        seed=0,
                        leech=0,
                        dl_number=0,
                        dl_completed=0,
                        project=None
                    )
                    obj.save()

                    list_of_tracker_id = []
                    for sublist in t.trackers:
                        level = t.trackers.index(sublist)
                        for tracker_url in sublist:
                            if not Tracker.objects.filter(url=tracker_url).exists():
                                tracker = Tracker(url=tracker_url)
                                tracker.save()
                                list_of_tracker_id.append([tracker.id, level])
                            else:
                                list_of_tracker_id.append([Tracker.objects.get(url=tracker_url).id, level])

                    for tracker_id in list_of_tracker_id:
                        obj.trackers.add(tracker_id[0])
                        tracker_stat = obj.trackerstat_set.get(tracker_id=tracker_id[0])
                        tracker_stat.level = tracker_id[1]
                        tracker_stat.save()

                    messages.success(request, "Upload and import succeeded.")
            except BdecodeError:
                messages.error(request, "Invalid torrent file format.")
            return redirect('dashboard')
    return redirect('dashboard')