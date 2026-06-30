from decimal import Decimal
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
import calendar

from budget.models import Budget, Category


class BudgetSetupForm(forms.Form):
    """Form for setting current-month category budgets with optional custom category creation."""

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        month_start = timezone.localdate().replace(day=1)
        self.month_start = month_start

        # Build fields for each user category (predefined + any custom)
        user_categories = Category.objects.filter(user=user, is_deleted=False).order_by("name")
        for category in user_categories:
            field_name = f"category_{category.id}"
            initial_amount = Decimal("0.00")

            existing_budget = Budget.objects.filter(
                user=user,
                category=category,
                month=month_start,
                is_deleted=False,
            ).first()
            if existing_budget:
                initial_amount = existing_budget.amount

            self.fields[field_name] = forms.DecimalField(
                label=category.name,
                min_value=Decimal("0.00"),
                decimal_places=2,
                initial=initial_amount,
                required=False,
            )

    def clean(self):
        cleaned = super().clean()

        # Extract budget amounts
        amounts = []
        for key, value in cleaned.items():
            if key.startswith("category_"):
                if value is None:
                    value = Decimal("0.00")
                amounts.append(value)

        # Validate: at least one amount > 0
        if amounts and not any(amt > Decimal("0.00") for amt in amounts):
            raise ValidationError(
                "At least one category must have a budget amount greater than 0."
            )

        return cleaned

    def save(self):
        """Upsert budgets for current month."""
        saved_budgets = []
        month_start = self.month_start

        for key, value in self.cleaned_data.items():
            if key.startswith("category_"):
                category_id = int(key.split("_")[1])
                amount = value if value is not None else Decimal("0.00")

                category = Category.objects.get(id=category_id, user=self.user)

                budget, created = Budget.objects.update_or_create(
                    user=self.user,
                    category=category,
                    month=month_start,
                    defaults={"amount": amount, "is_deleted": False},
                )
                saved_budgets.append(budget)

        return saved_budgets


class CustomCategoryForm(forms.ModelForm):
    """Form for creating new user-owned categories during budget setup."""

    class Meta:
        model = Category
        fields = ["name"]

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["name"].required = False

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()

        if not name:
            raise ValidationError("Category name cannot be empty.")

        # Check uniqueness within user scope
        existing = Category.objects.filter(user=self.user, name=name, is_deleted=False).exists()
        if existing:
            raise ValidationError(f"You already have a category named '{name}'.")

        return name

    def save(self, commit=True):
        category = super().save(commit=False)
        category.user = self.user
        if commit:
            category.save()
        return category
