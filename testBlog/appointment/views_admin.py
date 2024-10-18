from django.contrib import messages
from django.shortcuts import render, redirect

from .decorators import require_user_authenticated, require_superuser
from .forms import ServiceForm


def add_or_update_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid:
            form.save()
            messages.success(request, "Service saved successfully!")
            return redirect('/add-service')
    form = ServiceForm()
    data = {
        'form': form,
        "btn_text": "Save",
    }
    return render(request, 'administration/manage_service.html', data)


@require_user_authenticated
@require_superuser
def show_abilities(request):
    return render(request, 'administration/manege_all.html')

    # extra_context = {
    #     "btn_text": "Save",
    #     "page_title": "Add Service",
    # }
    # if service_id:
    #     service = get_object_or_404(Service, pk=service_id)
    #     form = ServiceForm(instance=service)
    #     if view != 1:
    #         extra_context['btn_text'] = _("Update")
    #         extra_context['page_title'] = _("Update Service")
    #     else:
    #         for field in form.fields.values():
    #             field.disabled = True
    #         extra_context['btn_text'] = None
    #         extra_context['page_title'] = _("View Service")
    #         extra_context['service'] = service
    # else:
    #     form = ServiceForm()
    # extra_context['form'] = form
    # context = get_generic_context_with_extra(request=request, extra=extra_context)
    # return render(request, 'administration/manage_service.html', context=context)
