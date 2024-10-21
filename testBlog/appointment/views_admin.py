from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from .decorators import require_user_authenticated, require_superuser, require_staff_or_superuser
from .forms import ServiceForm, StaffMemberForm
from .models import Service, StaffMember
from .services import handle_service_management_request, prepare_user_profile_data
from .utils.json_context import get_generic_context_with_extra


@require_user_authenticated
@require_superuser
def add_or_update_service(request, service_id=None):
    if service_id:
        service = get_object_or_404(Service, pk=service_id)
        page_title = "Просмотр услуги"
        btn_text = "Сохранить"
    else:
        service = None
        page_title = "Добавление услуги"
        btn_text = "Добавить"
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            if service:
                messages.success(request, "Услуга успешно сохранена")
            else:
                messages.success(request, "Услуга успешно добавлена")
            return redirect('get_service_list' if service else 'add_service')
    else:
        form = ServiceForm(instance=service)
    context = {
        'page_title': page_title,
        'btn_text': btn_text,
        'form': form,
    }
    return render(request, 'administration/manage_service.html', context)


@require_user_authenticated
@require_superuser
def get_service_list(request):
    services = Service.objects.all()
    context = {'services': services}
    return render(request, 'administration/service_list.html', context=context)


@require_user_authenticated
@require_superuser
def show_abilities(request):
    return render(request, 'administration/manege_all.html')


@require_user_authenticated
@require_superuser
def delete_service(request, service_id):
    service = get_object_or_404(Service, pk=service_id)
    service.delete()
    messages.success(request, "Услуга удалена")
    return redirect('get_service_list')


@require_user_authenticated
@require_superuser
def add_staff_member_info(request):
    if request.method == 'POST':
        form = StaffMemberForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = StaffMemberForm()

    context = get_generic_context_with_extra(request=request, extra={'form': form})
    return render(request, 'administration/manage_staff.html', context)


@require_user_authenticated
@require_superuser
def get_staff_list(request):
    staff_members = StaffMember.objects.all()
    context = {'staff_members': staff_members}
    return render(request, 'administration/staff_list.html', context=context)
