from django.shortcuts import redirect
from torrents.models import  Project
from django.contrib.auth.decorators import login_required

@login_required
def bulk_project_action(request):
    if request.method == 'POST':
        project_ids = request.POST.getlist('project_ids')
        projects = Project.objects.filter(id__in=project_ids)

        if 'activate' in request.POST:
            projects.update(is_active=True)
        elif 'deactivate' in request.POST:
            projects.update(is_active=False)
        elif 'delete' in request.POST:
            projects.delete()

        return redirect('project_list')
