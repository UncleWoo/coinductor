from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.utils import timezone

from budget.forms import BudgetSetupForm, CustomCategoryForm
from budget.models import Budget
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
    if request.method == "POST":
        action = request.POST.get("action", "")

        if action == "budget-setup":
            budget_form = BudgetSetupForm(user=request.user, data=request.POST)
            custom_category_name = request.POST.get("name", "").strip()
            custom_category_amount_raw = request.POST.get("custom_category_amount", "").strip()
            custom_category_form = CustomCategoryForm(
                user=request.user, data={"name": custom_category_name}
            )

            custom_category_valid = True
            if custom_category_name:
                custom_category_valid = custom_category_form.is_valid()
            elif custom_category_amount_raw not in {"", "0", "0.0", "0.00"}:
                custom_category_form.add_error(
                    "name", "Provide a category name when setting custom category amount."
                )
                custom_category_valid = False
            else:
                custom_category_form = CustomCategoryForm(user=request.user)

            if budget_form.is_valid() and custom_category_valid:
                custom_category = None
                if custom_category_name:
                    try:
                        custom_category = custom_category_form.save()
                    except IntegrityError:
                        # Should not happen with conditional constraint, but be defensive
                        custom_category_form.add_error(
                            "name", f"A category named '{custom_category_name}' already exists."
                        )
                        custom_category_valid = False
                        # Re-render with error
                        dashboard = get_dashboard_metrics(request.user)
                        return render(
                            request,
                            "home.html",
                            {
                                "dashboard": dashboard,
                                "empty_state": dashboard["empty_state"],
                                "on_track": dashboard["on_track"],
                                "budget_form": budget_form,
                                "custom_category_form": custom_category_form,
                            },
                        )
                budget_form.save()
                if custom_category:
                    custom_amount = budget_form.cleaned_data.get(
                        "custom_category_amount"
                    ) or 0
                    Budget.objects.update_or_create(
                        user=request.user,
                        category=custom_category,
                        month=timezone.localdate().replace(day=1),
                        defaults={"amount": custom_amount, "is_deleted": False},
                    )
                return redirect("home")
            else:
                # Re-render with errors
                dashboard = get_dashboard_metrics(request.user)
                return render(
                    request,
                    "home.html",
                    {
                        "dashboard": dashboard,
                        "empty_state": dashboard["empty_state"],
                        "on_track": dashboard["on_track"],
                        "budget_form": budget_form,
                        "custom_category_form": custom_category_form,
                    },
                )

        # Unknown action — redirect to home
        return redirect("home")

    # GET request
    dashboard = get_dashboard_metrics(request.user)

    context = {
        "dashboard": dashboard,
        "empty_state": dashboard["empty_state"],
        "on_track": dashboard["on_track"],
    }

    # Pass budget form for setup (no_budget) and editing (metrics states)
    context["budget_form"] = BudgetSetupForm(user=request.user)
    context["custom_category_form"] = CustomCategoryForm(user=request.user)

    return render(
        request,
        "home.html",
        context,
    )
