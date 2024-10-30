from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404

from .decorators import require_user_authenticated, require_superuser, require_staff_or_superuser
from .forms import ServiceForm, StaffMemberForm, PersonalInformationForm, StaffAppointmentInformationForm, \
    StaffDaysOffForm
from .models import Service, StaffMember, DayOff, WorkingHours
from .services import handle_service_management_request, prepare_user_profile_data, update_personal_info_service, \
    handle_entity_management_request
from .utils.error_codes import ErrorCode
from .utils.json_context import get_generic_context_with_extra, json_response, get_generic_context, \
    handle_unauthorized_response
from .utils.permissions import check_permissions


@require_user_authenticated
@require_staff_or_superuser
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
        # is it necessary instance??
        form = ServiceForm(instance=service)
    context = {
        'page_title': page_title,
        'btn_text': btn_text,
        'form': form,
    }
    return render(request, 'administration/manage_service.html', context)


@require_user_authenticated
@require_staff_or_superuser
def get_service_list(request):
    services = Service.objects.all()
    context = {'services': services}
    return render(request, 'administration/service_list.html', context=context)


@require_user_authenticated
@require_staff_or_superuser
def show_abilities(request):
    return render(request, 'administration/manege_all.html')


@require_user_authenticated
@require_staff_or_superuser
def delete_service(request, service_id):
    service = get_object_or_404(Service, pk=service_id)
    service.delete()
    messages.success(request, "Услуга удалена")
    return redirect('get_service_list')


@require_user_authenticated
@require_staff_or_superuser
def add_staff_member_info(request):
    if request.method == 'POST':
        form = StaffMemberForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            user.is_staff = True
            user.save()
            form.save()
            messages.success(request, "Работник успешно создан!")
            return redirect('get_staff_list')
    else:
        form = StaffMemberForm()
    context = {
        'page_title': 'Создание сотрудника',
        'btn_text': 'Добавить',
        'form': form,
    }
    return render(request, 'administration/manage_staff.html', context=context)


@require_user_authenticated
@require_staff_or_superuser
def update_personal_info(request, staff_user_id=None, response_type='html'):

    if not check_permissions(staff_user_id=staff_user_id, user=request.user):
        message = "Вы можете изменять только собственную персональную информацию"
        return handle_unauthorized_response(request, message, response_type)

    if request.method == 'POST':
        user, is_valid, error_message = update_personal_info_service(staff_user_id, request.POST, request.user)
        if is_valid:
            return redirect('user_profile')
        else:
            messages.error(request, error_message)
            return redirect('update_personal_info')

    if staff_user_id:
        user = get_user_model().objects.get(pk=staff_user_id)
    else:
        user = request.user

    form = PersonalInformationForm(initial={
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
    }, user=user)

    context = get_generic_context_with_extra(request=request, extra={'form': form, 'btn_text': "Сохранить"})
    return render(request, 'administration/manage_staff_personal_info.html', context)


@require_user_authenticated
@require_staff_or_superuser
def get_staff_list(request):
    staff_members = StaffMember.objects.all()
    context = {'staff_members': staff_members}
    return render(request, 'administration/staff_list.html', context=context)


@require_user_authenticated
@require_staff_or_superuser
def remove_staff_member(request, staff_user_id, response_type='html'):

    if not check_permissions(staff_user_id, request.user):
        message = "Вы не можете удалить чужой профиль"
        return handle_unauthorized_response(request, message, response_type)

    staff_member = get_object_or_404(StaffMember, user_id=staff_user_id)
    staff_member.delete()
    user = User.objects.get(pk=staff_user_id)
    user.is_staff = False
    user.save()
    messages.success(request, "Работник успешно удален!")
    return redirect('get_staff_list')


@require_user_authenticated
@require_staff_or_superuser
def user_profile(request, staff_user_id=None):
    data = prepare_user_profile_data(request.user, staff_user_id)
    context = get_generic_context_with_extra(request=request, extra=data['extra_context'])
    template = data['template']
    return render(request, template, context)


@require_user_authenticated
@require_staff_or_superuser
def update_staff_info(request, user_id=None, response_type='html'):

    if not check_permissions(staff_user_id=user_id, user=request.user):
        message = "Вы можете изменять только собственную информацию приема"
        return handle_unauthorized_response(request, message, response_type)


    staff_member = StaffMember.objects.get(user=user_id)

    if request.method == 'POST':
        form = StaffAppointmentInformationForm(request.POST, instance=staff_member)
        if form.is_valid():
            form.save()
            if user_id:
                return redirect('user_profile', staff_user_id=user_id)
            return redirect('user_profile')
    else:
        form = StaffAppointmentInformationForm(instance=staff_member)
    context = {
        'page_title': 'Персональная информация',
        'btn_text': 'Сохранить',
        'form': form,
    }
    return render(request, 'administration/manage_staff.html', context=context)


@require_user_authenticated
@require_staff_or_superuser
def add_day_off(request, staff_user_id=None, response_type='html'):
    if not check_permissions(staff_user_id, request.user):
        message = "Вы можете добавлять только свои собственные выходные дни."
        return handle_unauthorized_response(request, message, response_type)

    staff_member = StaffMember.objects.get(user_id=staff_user_id)
    return handle_entity_management_request(request, staff_member, entity_type='day_off')


@require_user_authenticated
@require_staff_or_superuser
def update_day_off(request, day_off_id, staff_user_id=None, response_type='html'):

    if not check_permissions(staff_user_id=staff_user_id, user=request.user):
        message = "Вы можете изменять только собственные выходные дни"
        return handle_unauthorized_response(request, message, response_type)

    day_off = DayOff.objects.get(pk=day_off_id)
    if not day_off:
        if response_type == 'json':
            return json_response("Day off does not exist.", status=404, success=False,
                                 error_code=ErrorCode.DAY_OFF_NOT_FOUND)
        else:
            context = get_generic_context(request=request)
            return render(request, 'error_pages/404_not_found.html', context=context, status=404)

    staff_user_id = staff_user_id or request.user.pk
    staff_member = StaffMember.objects.get(user_id=staff_user_id)
    return handle_entity_management_request(request, staff_member, entity_type='day_off', instance=day_off)


@require_user_authenticated
@require_staff_or_superuser
def delete_day_off(request, day_off_id):
    day_off = get_object_or_404(DayOff, pk=day_off_id)
    day_off.delete()
    messages.success(request, "Выходные успешно удалены!")
    return redirect('user_profile', staff_user_id=request.user.id)


@require_user_authenticated
@require_staff_or_superuser
def add_working_hours(request, staff_user_id=None):
    staff_user_id = staff_user_id or request.user.pk
    staff_user_id = staff_user_id if staff_user_id else request.user.pk
    staff_member = StaffMember.objects.get(user_id=staff_user_id)
    return handle_entity_management_request(request=request, staff_member=staff_member, staff_user_id=staff_user_id,
                                            entity_type='working_hours')


@require_user_authenticated
@require_staff_or_superuser
def update_working_hours(request, working_hours_id, staff_user_id=None, response_type='html'):
    working_hours = WorkingHours.objects.get(pk=working_hours_id)
    if not working_hours:
        if response_type == 'json':
            return json_response("Working hours does not exist.", status=404, success=False,
                                 error_code=ErrorCode.WORKING_HOURS_NOT_FOUND)
        else:
            context = get_generic_context(request=request)
            return render(request, 'error_pages/404_not_found.html', context=context)

    staff_user_id = staff_user_id or request.user.pk
    staff_member = get_object_or_404(StaffMember, user_id=staff_user_id or request.user.id)
    return handle_entity_management_request(request=request, staff_member=staff_member, add=False,
                                            instance_id=working_hours_id, staff_user_id=staff_user_id,
                                            entity_type='working_hours', instance=working_hours)


@require_user_authenticated
@require_staff_or_superuser
def delete_working_hours(request, working_hours_id):
    working_hours = get_object_or_404(WorkingHours, pk=working_hours_id)
    working_hours.delete()
    messages.success(request, "Рабочие часы успешно удалены!")
    return redirect('user_profile', staff_user_id=request.user.id)


