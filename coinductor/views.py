from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.shortcuts import redirect, render

from budget.services import get_dashboard_metrics


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            email_validator = EmailValidator()
            username_value = form.cleaned_data["username"]
            try:
                email_validator(username_value)
            except ValidationError:
                form.add_error("username", "Enter a valid email address.")
            else:
                user = form.save()
                login(request, user)
                return redirect("home")
    else:
        form = UserCreationForm()

    return render(request, "registration/signup.html", {"form": form})


def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("login")

    return render(request, "registration/logged_out.html")


@login_required
def home(request):
    dashboard = get_dashboard_metrics(request.user)
    show_budget_setup_placeholder = request.GET.get("setup-budget") == "1"
    return render(
        request,
        "home.html",
        {
            "dashboard": dashboard,
            "empty_state": dashboard["empty_state"],
            "on_track": dashboard["on_track"],
            "show_budget_setup_placeholder": show_budget_setup_placeholder,
        },
    )
