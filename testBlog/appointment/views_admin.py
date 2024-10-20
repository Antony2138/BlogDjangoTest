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
    if request.method == 'POST':
        if service_id:
            service = Service.objects.get(pk=service_id)
            form = ServiceForm(request.POST, request.FILES, instance=service)
            if form.is_valid():
                form.save()
                messages.success(request, "Услуга успешно сохранена")
                return redirect('get_service_list')
        else:
            form = ServiceForm(request.POST)
            if form.is_valid:
                form.save()
                messages.success(request, "Услуга успешно добавлена")
                return redirect('add_service')
    context = {
        'page_title': " Добавление услуги",
        'bnt_text': "Добавить",
    }
    if service_id:
        service = get_object_or_404(Service, pk=service_id)
        form = ServiceForm(instance=service)
        context = {
            'page_title': " Просмотр услуги ",
            'bnt_text': "Сохранить",
        }
    else:
        form = ServiceForm()
    context['form'] = form

    return render(request, 'administration/manage_service.html', context)
# @require_user_authenticated
# @require_superuser
# def add_or_update_service(request, service_id=None, view=0):
#     if request.method == 'POST':
#         service, is_valid, error_message = handle_service_management_request(request.POST, request.FILES, service_id)
#         if is_valid:
#             messages.success(request, "Service saved successfully!")
#             return redirect('add_service')
#         else:
#             messages.error(request, error_message)
#
#     extra_context = {
#         "btn_text": "Save",
#         "page_title": "Add Service",
#     }
#     if service_id:
#         service = get_object_or_404(Service, pk=service_id)
#         form = ServiceForm(instance=service)
#         if view != 1:
#             extra_context['btn_text'] = "Update"
#             extra_context['page_title'] = "Update Service"
#         else:
#             for field in form.fields.values():
#                 field.disabled = True
#             extra_context['btn_text'] = None
#             extra_context['page_title'] = "View Service"
#             extra_context['service'] = service
#     else:
#         form = ServiceForm()
#     extra_context['form'] = form
#     context = get_generic_context_with_extra(request=request, extra=extra_context)
#     return render(request, 'administration/manage_service.html', context=context)


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


# @require_user_authenticated
# @require_staff_or_superuser
# def user_profile(request, staff_user_id=None):
#     data = prepare_user_profile_data(request.user, staff_user_id)
#     error = data.get('error')
#     status_code = data.get('status_code', 400)
#     context = get_generic_context_with_extra(request=request, extra=data['extra_context'])
#     error_template = 'error_pages/403_forbidden.html' if status_code == 403 else 'error_pages/404_not_found.html'
#     template = data['template'] if not error else error_template
#     return render(request, template, context)