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
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomAuthenticationForm, TorrentActionForm, RegisterForm, ProjectForm
from torf import Torrent as Torrenttorf, BdecodeError,  ReadError, WriteError
from torrent.models import Torrent, Tracker
from django.core.files.base import ContentFile
from urllib.parse import urlparse
from django.db.models import ProtectedError


import uuid

# def project_detail(request, project_id):
#     project = get_object_or_404(Project, pk=project_id)
#     return render(request, 'path_to_your_template.html', {'project': project})

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

#
def project_detail(request, identifier):
    if identifier.isdigit():
        project = get_object_or_404(Project, id=identifier)
    else:
        project = get_object_or_404(Project, slug=identifier)

    torrents = project.torrents.all()  # Utiliser le nom de la relation définie dans related_name

    return render(request, 'torrent/project_detail.html', {
        'project': project,
        'torrents': torrents,
    })

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

    # Get the top 10 torrents with the most seeds
    top_seeded_torrents = Torrent.objects.filter(is_active=True).order_by('-seed')[:10]

    if form.is_valid() and form.cleaned_data['query']:
        query = form.cleaned_data['query']
        torrents = torrents.filter(name__icontains=query)

    # Pagination
    paginator = Paginator(torrents, 40)  # 10 torrents par page, ajustez si nécessaire

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
        'torrent_list': torrents,
        'top_seeded_torrent_list': top_seeded_torrents, 
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
    torrents = Torrent.objects.filter(uploader=user).order_by('-creation')
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
def dashboard_project(request):
    user = request.user
    projects = Project.objects.filter(user=user)
    project_count = projects.count()

    if request.method == 'POST':
        if 'create' in request.POST:
            project_form = ProjectForm(request.POST, request.FILES)
            if project_form.is_valid():
                new_project = project_form.save(commit=False)
                new_project.user = user
                new_project.save()
                messages.success(request, "New project has been created.")
                return redirect('dashboard_project')
        else:
            project_ids = request.POST.getlist('project_ids')
            if 'delete' in request.POST:
                if project_ids:
                    for project_id in project_ids:
                        project = get_object_or_404(Project, id=project_id, user=user)
                        try:
                            project.delete()
                            messages.success(request, f"Project '{project.name}' has been deleted.")
                        except ProtectedError:
                            torrent_count = project.torrents.count()
                            messages.error(request, f"Cannot delete the project '{project.name}' because it is referenced by {torrent_count} torrents.")
                else:
                    messages.warning(request, "No projects were selected for deletion.")
            elif 'activate' in request.POST:
                if project_ids:
                    Project.objects.filter(id__in=project_ids, user=user).update(is_active=True)
                    messages.success(request, "Selected projects have been activated.")
                else:
                    messages.warning(request, "No projects were selected for activation.")
            elif 'deactivate' in request.POST:
                if project_ids:
                    Project.objects.filter(id__in=project_ids, user=user).update(is_active=False)
                    messages.success(request, "Selected projects have been deactivated.")
                else:
                    messages.warning(request, "No projects were selected for deactivation.")
            return redirect('dashboard_project')
    else:
        project_form = ProjectForm()

    project_torrents = [(project, project.torrents.count()) for project in projects]

    return render(request, 'torrent/dashboard_project.html', {
        'projects': project_torrents,
        'project_count': project_count,
        'project_form': project_form,
    })

def list_torrents(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    torrents = project.torrents.all()
    return render(request, 'torrent/list_torrents.html', {
        'project': project,
        'torrents': torrents,
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
# Assurez-vous que le répertoire settings.MEDIA_TORRENT existe
os.makedirs(settings.MEDIA_TORRENT, exist_ok=True)

# Assurez-vous que le répertoire settings.MEDIA_TORRENT existe
os.makedirs(settings.MEDIA_TORRENT, exist_ok=True)


# Assurez-vous que le répertoire settings.MEDIA_TORRENT existe
os.makedirs(settings.MEDIA_TORRENT, exist_ok=True)

@login_required
def file_upload(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            fs = FileSystemStorage(location=settings.MEDIA_TORRENT)
            filename = file.name

            # Vérifiez si le fichier existe déjà
            if fs.exists(filename):
                messages.error(request, f"The file '{filename}' already exists. Please rename your file and try again.")
                return redirect('dashboard')

            # Enregistrez le fichier
            filename = fs.save(file.name, file)
            try:
                torrent_file_path = os.path.join(settings.MEDIA_TORRENT, filename)
                print(f"File saved temporarily at {torrent_file_path}")

                if not os.path.exists(torrent_file_path):
                    raise FileNotFoundError(f"File not found at {torrent_file_path}")

                t = Torrenttorf.read(torrent_file_path)

                # Ajouter les trackers Bitiso si nécessaire
                bitiso_trackers = [settings.TRACKER_ANNOUNCE]
                existing_trackers = [tracker for sublist in t.trackers for tracker in sublist]
                for tracker in bitiso_trackers:
                    if tracker not in existing_trackers:
                        t.trackers.append([tracker])

                print(f"Trackers after adding Bitiso: {t.trackers}")

                # Supprimez l'ancien fichier avant d'écrire le nouveau
                if os.path.exists(torrent_file_path):
                    os.remove(torrent_file_path)
                t.write(torrent_file_path)
                print(f"Torrent file with added trackers saved at {torrent_file_path}")

                if Torrent.objects.filter(info_hash=t.infohash).exists():
                    messages.warning(request, f"Info hash {t.infohash} already exists in the database.")
                else:
                    file_list = ''.join([f"{file.name};{file.size}\n" for file in t.files])
                    magnet_uri = str(t.magnet())
                    obj = Torrent(
                        info_hash=t.infohash[:40],
                        name=t.name[:128],
                        size=t.size,
                        pieces=t.pieces,
                        piece_size=t.piece_size,
                        magnet=magnet_uri[:2048],
                        torrent_filename=(t.name + '.torrent')[:128],
                        is_bitiso=False,
                        metainfo_file='torrent/' + os.path.basename(torrent_file_path),
                        file_list=file_list[:2048],
                        file_nbr=len(t.files),
                        uploader=request.user,
                        comment="Default comment"[:256],
                        slug=t.name[:50],
                        category=None,
                        is_active=False,
                        description="Default description"[:2000],
                        website_url="",
                        website_url_download="",
                        website_url_repo="",
                        version="1.0"[:16],
                        gpg_signature=None,
                        hash_signature=""[:128],
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
                                print(f"New tracker {tracker_url} added to the database.")
                            else:
                                list_of_tracker_id.append([Tracker.objects.get(url=tracker_url).id, level])
                                print(f"Existing tracker {tracker_url} found in the database.")

                    for tracker_id in list_of_tracker_id:
                        obj.trackers.add(tracker_id[0])
                        tracker_stat = obj.trackerstat_set.get(tracker_id=tracker_id[0])
                        tracker_stat.level = tracker_id[1]
                        tracker_stat.save()
                        print(f"Tracker {tracker_id[0]} linked to torrent {obj.name}.")

                    messages.success(request, "Upload and import succeeded.")
            except FileNotFoundError as e:
                print(f"File not found error: {e}")
                messages.error(request, f"File not found error: {e}")
            except ReadError as e:
                print(f"Read error: {e}")
                messages.error(request, f"Read error: {e}")
            except WriteError as e:
                print(f"Write error: {e}")
                messages.error(request, f"Write error: {e}")
            except BdecodeError as e:
                print(f"Invalid torrent file format: {e}")
                messages.error(request, "Invalid torrent file format.")
            return redirect('dashboard')
    return redirect('dashboard')


# Ajout d'un signal pour supprimer les fichiers torrent lorsque l'objet Torrent est supprimé
from django.db.models.signals import post_delete
from django.dispatch import receiver

@receiver(post_delete, sender=Torrent)
def delete_torrent_files_on_delete(sender, instance, **kwargs):
    if instance.metainfo_file:
        metainfo_file_path = str(instance.metainfo_file) if not isinstance(instance.metainfo_file, str) else instance.metainfo_file
        if metainfo_file_path:
            torrent_file_path = os.path.join(settings.MEDIA_ROOT, metainfo_file_path)
            if os.path.exists(torrent_file_path):
                os.remove(torrent_file_path)

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
                fs = FileSystemStorage(location=settings.MEDIA_TORRENT)
                temp_file_path = fs.save(filename, content)
                temp_file_full_path = os.path.join(settings.MEDIA_TORRENT, temp_file_path)
                print(f"File saved temporarily at {temp_file_full_path}")

                # Vérifier si le fichier existe réellement à ce chemin
                if not os.path.exists(temp_file_full_path):
                    raise FileNotFoundError(f"File not found at {temp_file_full_path}")

                # Lancer l'importation du fichier torrent dans la base de données
                t = Torrenttorf.read(temp_file_full_path)
                if Torrent.objects.filter(info_hash=t.infohash).exists():
                    messages.warning(request, f"Info hash {t.infohash} already exists in the database.")
                else:
                    t.trackers.append([settings.TRACKER_ANNOUNCE])
                    file_list = ''.join([f"{file.name};{file.size}\n" for file in t.files])
                    magnet_uri = str(t.magnet())  # Ensure magnet URI is a string

                    torrent_name_with_extension = (t.name + '.torrent')[:128]  # Truncate to fit the database field length

                    # Écrire le fichier torrent dans media/torrent
                    torrent_dir = os.path.join(settings.MEDIA_TORRENT)
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
                        metainfo_file='torrent/' + (t.name + '.torrent')[:128],  # Truncate to fit the database field length
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

@login_required
def delete_project(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
        project.delete()
        messages.success(request, f"The project '{project.name}' was successfully deleted.")
    except ProtectedError as e:
        referenced_objects = e.protected_objects
        num_referenced = referenced_objects.count()
        messages.error(request, f"Cannot delete the project '{project.name}' because it is referenced by {num_referenced} torrents.")
    except Project.DoesNotExist:
        messages.error(request, "The project you are trying to delete does not exist.")
    return redirect('project_list')  # Assurez-vous de rediriger vers la bonne vue
