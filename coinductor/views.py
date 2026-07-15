from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.crypto import get_random_string

from budget.forms import BudgetSetupForm, CustomCategoryForm, ExpenseQuickAddForm
from budget.models import Budget, Category
from budget.services import get_dashboard_metrics

EXPENSE_IDEMPOTENCY_SESSION_KEY = "expense_idempotency_tokens"
EXPENSE_IDEMPOTENCY_WINDOW = 20


def _issue_expense_idempotency_token(request):
    token = get_random_string(32)
    tokens = request.session.get(EXPENSE_IDEMPOTENCY_SESSION_KEY, [])
    tokens.append(token)
    request.session[EXPENSE_IDEMPOTENCY_SESSION_KEY] = tokens[-EXPENSE_IDEMPOTENCY_WINDOW:]
    return token


def _consume_expense_idempotency_token(request, token):
    if not token:
        return False
    tokens = request.session.get(EXPENSE_IDEMPOTENCY_SESSION_KEY, [])
    if token not in tokens:
        return False
    tokens.remove(token)
    request.session[EXPENSE_IDEMPOTENCY_SESSION_KEY] = tokens
    return True


def _render_home(
    request,
    dashboard,
    budget_form,
    custom_category_form,
    expense_form,
    user_categories,
):
    return render(
        request,
        "home.html",
        {
            "dashboard": dashboard,
            "empty_state": dashboard["empty_state"],
            "on_track": dashboard["on_track"],
            "velocity_status": dashboard["velocity_status"],
            "budget_form": budget_form,
            "custom_category_form": custom_category_form,
            "user_categories": user_categories,
            "expense_form": expense_form,
            "expense_idempotency_token": _issue_expense_idempotency_token(request),
        },
    )


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

        if action == "add-expense":
            if not _consume_expense_idempotency_token(
                request, request.POST.get("idempotency_token")
            ):
                return redirect("home")
            expense_form = ExpenseQuickAddForm(
                user=request.user, data=request.POST
            )
            if expense_form.is_valid():
                expense_form.save()
                return redirect("home")
            else:
                # Re-render with errors
                dashboard = get_dashboard_metrics(request.user)
                budget_form = BudgetSetupForm(user=request.user)
                custom_category_form = CustomCategoryForm(user=request.user)
                user_categories = Category.objects.filter(
                    user=request.user, is_deleted=False
                ).order_by("name")
                return _render_home(
                    request,
                    dashboard,
                    budget_form,
                    custom_category_form,
                    expense_form,
                    user_categories,
                )

        elif action == "add-category":
            custom_category_form = CustomCategoryForm(
                user=request.user, data=request.POST
            )
            if custom_category_form.is_valid():
                try:
                    custom_category_form.save()
                    return redirect("home")
                except IntegrityError:
                    custom_category_form.add_error(
                        "name", "A category with this name already exists."
                    )
            # Re-render with errors
            dashboard = get_dashboard_metrics(request.user)
            budget_form = BudgetSetupForm(user=request.user)
            expense_form = ExpenseQuickAddForm(user=request.user)
            user_categories = Category.objects.filter(
                user=request.user, is_deleted=False
            ).order_by("name")
            return _render_home(
                request,
                dashboard,
                budget_form,
                custom_category_form,
                expense_form,
                user_categories,
            )

        elif action == "delete-category":
            category_id = request.POST.get("category_id")
            if category_id:
                category = Category.objects.filter(
                    id=category_id, user=request.user, is_deleted=False
                ).first()
                if category:
                    category.is_deleted = True
                    category.save()
            return redirect("home")

        elif action == "budget-setup":
            budget_form = BudgetSetupForm(user=request.user, data=request.POST)
            if budget_form.is_valid():
                try:
                    budget_form.save()
                    return redirect("home")
                except IntegrityError:
                    budget_form.add_error(
                        None, "A budget for this category and month already exists."
                    )
                    dashboard = get_dashboard_metrics(request.user)
                    custom_category_form = CustomCategoryForm(user=request.user)
                    expense_form = ExpenseQuickAddForm(user=request.user)
                    user_categories = Category.objects.filter(
                        user=request.user, is_deleted=False
                    ).order_by("name")
                    return _render_home(
                        request,
                        dashboard,
                        budget_form,
                        custom_category_form,
                        expense_form,
                        user_categories,
                    )
            else:
                # Re-render with errors
                dashboard = get_dashboard_metrics(request.user)
                custom_category_form = CustomCategoryForm(user=request.user)
                expense_form = ExpenseQuickAddForm(user=request.user)
                user_categories = Category.objects.filter(
                    user=request.user, is_deleted=False
                ).order_by("name")
                return _render_home(
                    request,
                    dashboard,
                    budget_form,
                    custom_category_form,
                    expense_form,
                    user_categories,
                )

        # Unknown action — redirect to home
        return redirect("home")

    # GET request
    dashboard = get_dashboard_metrics(request.user)
    user_categories = Category.objects.filter(
        user=request.user, is_deleted=False
    ).order_by("name")

    return _render_home(
        request,
        dashboard,
        BudgetSetupForm(user=request.user),
        CustomCategoryForm(user=request.user),
        ExpenseQuickAddForm(user=request.user),
        user_categories,
    )
