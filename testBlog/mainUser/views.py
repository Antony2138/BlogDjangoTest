from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .services import handle_user_registration

# Create your views here.


def registration(request):
    return handle_user_registration(request)
    # form = UserRegisterForm()
    # context = {
    #     "today": timezone.now(),
    #     "register_form": form
    # }
    # template = "mainUser/registration.html"
    #
    # if request.method == "POST":
    #     register_form = UserRegisterForm(request.POST)
    #     if register_form.is_valid():
    #         user = register_form.save(commit=False)
    #         user.set_password(register_form.cleaned_data["password"])
    #         user.save()
    #         messages.success(request, "Ваш аккаунт создан. Можно войти на сайт.")
    #         return redirect("login")
    #     else:
    #         print("cheac")
    #         return render(request, template, context)
    # else:
    #     return render(request, template, context)


@login_required
def profile(request):
    return render(request, "mainUser/profile.html")
