import os
import requests
from .models import Torrent, Project, Category
from django.http import HttpResponse
from django.core.management import call_command
from django.shortcuts import render, get_object_or_404, redirect
from .forms import SearchForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .ratelimit import RateLimit, RateLimitExceeded
from .forms import URLDownloadForm, FileUploadForm
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomAuthenticationForm, TorrentActionForm, RegisterForm
from torf import Torrent as Torrenttorf, BdecodeError
from torrent.models import Torrent, Tracker
from django.core.files.base import ContentFile
from urllib.parse import urlparse

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

def logout_view(request):
    logout(request)
    return redirect('login')

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'torrent/register.html', {'form': form})

@login_required
def dashboard(request):
    user = request.user
    torrents = Torrent.objects.filter(uploader=user)
    torrent_count = torrents.count()
    categories = Category.objects.all()
    projects = Project.objects.all()

    if request.method == 'POST':
        torrent_ids = request.POST.getlist('torrent_ids')
        if 'delete' in request.POST:
            if torrent_ids:
                Torrent.objects.filter(id__in=torrent_ids, uploader=request.user).delete()
                messages.success(request, "Selected torrents have been deleted.")
            else:
                messages.warning(request, "No torrents were selected for deletion.")
        elif 'set_category' in request.POST:
            category_id = request.POST.get('category')
            if category_id and torrent_ids:
                category = Category.objects.get(id=category_id)
                Torrent.objects.filter(id__in=torrent_ids).update(category=category)
                messages.success(request, "Category set successfully.")
            else:
                messages.warning(request, "No torrents or category were selected.")
        elif 'set_project' in request.POST:
            project_id = request.POST.get('project')
            if project_id and torrent_ids:
                project = Project.objects.get(id=project_id)
                Torrent.objects.filter(id__in=torrent_ids).update(project=project)
                messages.success(request, "Project set successfully.")
            else:
                messages.warning(request, "No torrents or project were selected.")
        elif 'activate' in request.POST:
            if torrent_ids:
                Torrent.objects.filter(id__in=torrent_ids, uploader=request.user).update(is_active=True)
                messages.success(request, "Selected torrents have been activated.")
            else:
                messages.warning(request, "No torrents were selected for activation.")
        elif 'deactivate' in request.POST:
            if torrent_ids:
                Torrent.objects.filter(id__in=torrent_ids, uploader=request.user).update(is_active=False)
                messages.success(request, "Selected torrents have been deactivated.")
            else:
                messages.warning(request, "No torrents were selected for deactivation.")
        return redirect('dashboard')


    form = FileUploadForm()
    url_form = URLDownloadForm()

    return render(request, 'torrent/dashboard.html', {
        'torrents': torrents,
        'torrent_count': torrent_count,
        'form': form,
        'url_form': url_form,
        'categories': categories,
        'projects': projects
    })

@login_required
def delete_torrents(request):
    if request.method == 'POST':
        torrent_ids = request.POST.getlist('torrent_ids')
        if torrent_ids:
            Torrent.objects.filter(id__in=torrent_ids, uploader=request.user).delete()
            messages.success(request, "Selected torrents have been deleted.")
        else:
            messages.warning(request, "No torrents were selected for deletion.")
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
                        metainfo_file='torrent/' + (t.name + '.torrent')[:128],
                        # Truncate to fit the database field length
                        file_list=file_list[:2048],  # Truncate to fit the database field length
                        file_nbr=len(t.files),
                        uploader=request.user,
                        comment="Default comment"[:256],  # Truncate to fit the database field length
                        slug=t.name[:50],  # Truncate to fit the database field length
                        category=None,
                        is_active=True,
                        description="Default description"[:2000],  # Truncate to fit the database field length
                        website_url="",  # Leave empty
                        website_url_download="",  # Leave empty
                        website_url_repo="",  # Leave empty
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


@login_required
def download_torrent(request):
    if request.method == 'POST':
        form = URLDownloadForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            try:
                response = requests.get(url)
                response.raise_for_status()  # Vérifie si la requête a réussi
                print(f"Successfully downloaded content from {url}")

                # Télécharger le fichier en mémoire
                content = ContentFile(response.content)

                # Obtenir le nom du fichier à partir de l'URL
                parsed_url = urlparse(url)
                filename = parsed_url.path.split('/')[-1]
                print(f"Filename obtained: {filename}")

                # Sauvegarder le fichier temporairement pour l'importation
                fs = FileSystemStorage(location=settings.MEDIA_ROOT)
                temp_file_path = fs.save(filename, content)
                print(f"File saved temporarily at {temp_file_path}")

                # Lancer l'importation du fichier torrent dans la base de données
                torrent_file_path = os.path.join(settings.MEDIA_ROOT, temp_file_path)
                t = Torrenttorf.read(torrent_file_path)

                if Torrent.objects.filter(info_hash=t.infohash).exists():
                    messages.warning(request, f"Info hash {t.infohash} already exists in the database.")
                else:
                    t.trackers.append([settings.TRACKER_ANNOUNCE])
                    file_list = ''.join([f"{file.name};{file.size}\n" for file in t.files])
                    magnet_uri = str(t.magnet())  # Ensure magnet URI is a string

                    torrent_name_with_extension = (t.name + '.torrent')[:128]  # Truncate to fit the database field length

                    # Écrire le fichier torrent dans media/torrent
                    torrent_dir = os.path.join(settings.MEDIA_ROOT, 'torrent')
                    if not os.path.exists(torrent_dir):
                        os.makedirs(torrent_dir)

                    torrent_file_path = os.path.join(torrent_dir, torrent_name_with_extension)

                    if os.path.exists(torrent_file_path):
                        print("Le fichier existe déjà. Remove")
                        os.remove(torrent_file_path)
                    else:
                        print("Le fichier n'existe pas.")

                    t.write(torrent_file_path)
                    print("Fichier torrent " + torrent_file_path + " écrit avec succès.")


                    obj = Torrent(
                        info_hash=t.infohash[:40],  # Truncate to fit the database field length
                        name=t.name[:128],  # Truncate to fit the database field length
                        size=t.size,
                        pieces=t.pieces,
                        piece_size=t.piece_size,
                        magnet=magnet_uri[:2048],  # Truncate to fit the database field length
                        torrent_filename=(t.name + '.torrent')[:128],  # Truncate to fit the database field length
                        is_bitiso=False,
                        metainfo_file='torrent/' + (t.name + '.torrent')[:128],
                        # Truncate to fit the database field length
                        file_list=file_list[:2048],  # Truncate to fit the database field length
                        file_nbr=len(t.files),
                        uploader=request.user,
                        comment="Default comment"[:256],  # Truncate to fit the database field length
                        slug=t.name[:50],  # Truncate to fit the database field length
                        category=None,
                        is_active=False,
                        description="Default description"[:2000],  # Truncate to fit the database field length
                        website_url="",  # Leave empty
                        website_url_download=url[:2000],  # Store the download URL
                        website_url_repo="",  # Leave empty
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
                    print(f"Torrent {obj.name} with hash {obj.info_hash} saved to database.")

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

                    messages.success(request, "Download, upload, and import succeeded.")
            except requests.exceptions.RequestException as e:
                print(f"Error downloading file: {e}")
                messages.error(request, f'Error downloading file: {e}')
            except PermissionError as e:
                print(f"Permission error: {e}")
                messages.error(request, f'Permission error: {e}')
            except BdecodeError:
                print("Invalid torrent file format.")
                messages.error(request, "Invalid torrent file format.")
            return redirect('dashboard')
    return redirect('dashboard')