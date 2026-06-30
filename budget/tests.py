from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from budget.models import DEFAULT_CATEGORIES, Budget, Category, Expense
from budget.services import get_dashboard_metrics

User = get_user_model()


class OwnershipValidationTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner@example.com", password="Pass12345!"
        )
        self.other_user = User.objects.create_user(
            username="other@example.com", password="Pass12345!"
        )
        self.category = Category.objects.create(user=self.owner, name="Custom Food")

    def test_budget_rejects_category_from_another_user(self):
        budget = Budget(
            user=self.other_user,
            category=self.category,
            month=date(2026, 6, 1),
            amount=Decimal("100.00"),
        )

        with self.assertRaises(ValidationError):
            budget.full_clean()

    def test_expense_rejects_category_from_another_user(self):
        expense = Expense(
            user=self.other_user,
            category=self.category,
            amount=Decimal("10.00"),
            date=date(2026, 6, 15),
            description="Lunch",
        )

        with self.assertRaises(ValidationError):
            expense.full_clean()


class DefaultCategorySeedingTests(TestCase):
    def test_user_creation_seeds_default_categories_once(self):
        user = User.objects.create_user(
            username="seeded@example.com", password="Pass12345!"
        )

        categories = Category.objects.filter(user=user).values_list("name", flat=True)
        self.assertEqual(set(categories), set(DEFAULT_CATEGORIES))
        self.assertEqual(Category.objects.filter(user=user).count(), len(DEFAULT_CATEGORIES))

    def test_existing_user_update_does_not_duplicate_categories(self):
        user = User.objects.create_user(
            username="existing@example.com", password="Pass12345!"
        )
        initial_count = Category.objects.filter(user=user).count()

        user.first_name = "Updated"
        user.save()

        self.assertEqual(Category.objects.filter(user=user).count(), initial_count)


class DashboardMetricsServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="service-user@example.com", password="Pass12345!"
        )
        self.other_user = User.objects.create_user(
            username="other-service-user@example.com", password="Pass12345!"
        )
        self.user_category = Category.objects.create(user=self.user, name="Owner Category")
        self.other_category = Category.objects.create(
            user=self.other_user, name="Other Category"
        )
        self.as_of = date(2026, 6, 10)

    def test_returns_no_budget_empty_state_when_month_has_no_budget(self):
        metrics = get_dashboard_metrics(self.user, as_of=self.as_of)

        self.assertEqual(metrics["empty_state"], "no_budget")
        self.assertFalse(metrics["has_budget"])
        self.assertFalse(metrics["on_track"])
        self.assertEqual(metrics["total_budget"], Decimal("0.00"))
        self.assertEqual(metrics["total_spent"], Decimal("0.00"))
        self.assertEqual(metrics["remaining_days"], 21)
        self.assertEqual(metrics["velocity_status"], "no_budget")

    def test_returns_no_expenses_state_when_budget_exists_without_expenses(self):
        Budget.objects.create(
            user=self.user,
            category=self.user_category,
            month=date(2026, 6, 1),
            amount=Decimal("300.00"),
        )

        metrics = get_dashboard_metrics(self.user, as_of=self.as_of)

        self.assertEqual(metrics["empty_state"], "no_expenses")
        self.assertTrue(metrics["has_budget"])
        self.assertFalse(metrics["has_expenses"])
        self.assertTrue(metrics["on_track"])
        self.assertEqual(metrics["remaining_budget"], Decimal("300.00"))
        self.assertEqual(metrics["daily_limit"], Decimal("14.29"))

    def test_filters_out_deleted_and_other_user_rows(self):
        Budget.objects.create(
            user=self.user,
            category=self.user_category,
            month=date(2026, 6, 1),
            amount=Decimal("400.00"),
        )
        Budget.objects.create(
            user=self.other_user,
            category=self.other_category,
            month=date(2026, 6, 1),
            amount=Decimal("900.00"),
        )
        Expense.objects.create(
            user=self.user,
            category=self.user_category,
            amount=Decimal("50.00"),
            date=date(2026, 6, 5),
        )
        Expense.objects.create(
            user=self.user,
            category=self.user_category,
            amount=Decimal("80.00"),
            date=date(2026, 6, 6),
            is_deleted=True,
        )
        Expense.objects.create(
            user=self.other_user,
            category=self.other_category,
            amount=Decimal("200.00"),
            date=date(2026, 6, 5),
        )

        metrics = get_dashboard_metrics(self.user, as_of=self.as_of)

        self.assertEqual(metrics["total_budget"], Decimal("400.00"))
        self.assertEqual(metrics["total_spent"], Decimal("50.00"))
        self.assertEqual(metrics["remaining_budget"], Decimal("350.00"))

    def test_pace_aware_on_track_turns_false_when_spending_is_too_fast(self):
        Budget.objects.create(
            user=self.user,
            category=self.user_category,
            month=date(2026, 6, 1),
            amount=Decimal("300.00"),
        )
        Expense.objects.create(
            user=self.user,
            category=self.user_category,
            amount=Decimal("120.00"),
            date=date(2026, 6, 9),
        )

        metrics = get_dashboard_metrics(self.user, as_of=self.as_of)

        self.assertFalse(metrics["on_track"])
        self.assertEqual(metrics["velocity_status"], "behind")
        self.assertEqual(metrics["daily_limit"], Decimal("8.57"))
        self.assertEqual(metrics["spent_per_day"], Decimal("12.00"))

    def test_overspending_produces_negative_remaining_budget_and_daily_limit(self):
        Budget.objects.create(
            user=self.user,
            category=self.user_category,
            month=date(2026, 6, 1),
            amount=Decimal("300.00"),
        )
        Expense.objects.create(
            user=self.user,
            category=self.user_category,
            amount=Decimal("360.00"),
            date=date(2026, 6, 8),
        )

        metrics = get_dashboard_metrics(self.user, as_of=self.as_of)

        self.assertEqual(metrics["remaining_budget"], Decimal("-60.00"))
        self.assertEqual(metrics["daily_limit"], Decimal("-2.86"))
        self.assertFalse(metrics["on_track"])

    def test_ignores_expenses_from_other_months(self):
        Budget.objects.create(
            user=self.user,
            category=self.user_category,
            month=date(2026, 6, 1),
            amount=Decimal("300.00"),
        )
        Expense.objects.create(
            user=self.user,
            category=self.user_category,
            amount=Decimal("90.00"),
            date=date(2026, 6, 9),
        )
        Expense.objects.create(
            user=self.user,
            category=self.user_category,
            amount=Decimal("200.00"),
            date=date(2026, 5, 31),
        )

        metrics = get_dashboard_metrics(self.user, as_of=self.as_of)

        self.assertEqual(metrics["total_spent"], Decimal("90.00"))
        self.assertTrue(metrics["on_track"])

    def test_service_output_contains_required_dashboard_keys(self):
        metrics = get_dashboard_metrics(self.user, as_of=self.as_of)

        expected_keys = {
            "month_start",
            "month_end",
            "days_in_month",
            "elapsed_days",
            "remaining_days",
            "total_budget",
            "total_spent",
            "remaining_budget",
            "daily_limit",
            "spent_per_day",
            "on_track",
            "velocity_status",
            "has_budget",
            "has_expenses",
            "empty_state",
        }

        self.assertSetEqual(set(metrics.keys()), expected_keys)

    def test_velocity_status_uses_five_percent_tolerance_boundary(self):
        Budget.objects.create(
            user=self.user,
            category=self.user_category,
            month=date(2026, 6, 1),
            amount=Decimal("630.00"),
        )
        Expense.objects.create(
            user=self.user,
            category=self.user_category,
            amount=Decimal("210.00"),
            date=date(2026, 6, 9),
        )

        at_boundary = get_dashboard_metrics(self.user, as_of=self.as_of)
        self.assertEqual(at_boundary["velocity_status"], "on_pace")

        Expense.objects.filter(user=self.user, category=self.user_category).delete()
        Expense.objects.create(
            user=self.user,
            category=self.user_category,
            amount=Decimal("210.10"),
            date=date(2026, 6, 9),
        )

        above_boundary = get_dashboard_metrics(self.user, as_of=self.as_of)
        self.assertEqual(above_boundary["velocity_status"], "behind")


class BudgetSetupFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="setup@example.com", password="Pass12345!"
        )
        # Create default categories for user
        Category.objects.filter(user=self.user).delete()
        for cat_name in DEFAULT_CATEGORIES:
            Category.objects.create(user=self.user, name=cat_name)

    def test_form_accepts_positive_amounts(self):
        from budget.forms import BudgetSetupForm

        categories = Category.objects.filter(user=self.user)
        data = {}
        for category in categories:
            data[f"category_{category.id}"] = "50.00"

        form = BudgetSetupForm(user=self.user, data=data)
        self.assertTrue(form.is_valid())

    def test_form_rejects_all_zero_amounts(self):
        from budget.forms import BudgetSetupForm

        categories = Category.objects.filter(user=self.user)
        data = {}
        for category in categories:
            data[f"category_{category.id}"] = "0.00"

        form = BudgetSetupForm(user=self.user, data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("At least one category", str(form.errors))

    def test_form_accepts_mixed_zero_and_positive(self):
        from budget.forms import BudgetSetupForm

        categories = list(Category.objects.filter(user=self.user))
        data = {}
        for i, category in enumerate(categories):
            if i == 0:
                data[f"category_{category.id}"] = "100.00"
            else:
                data[f"category_{category.id}"] = "0.00"

        form = BudgetSetupForm(user=self.user, data=data)
        self.assertTrue(form.is_valid())

    def test_form_rejects_negative_amounts(self):
        from budget.forms import BudgetSetupForm

        categories = Category.objects.filter(user=self.user)
        data = {}
        for category in categories:
            data[f"category_{category.id}"] = "-10.00"

        form = BudgetSetupForm(user=self.user, data=data)
        self.assertFalse(form.is_valid())

    def test_form_saves_budgets_as_upsert(self):
        from budget.forms import BudgetSetupForm
        from django.utils import timezone

        month_start = timezone.localdate().replace(day=1)
        categories = list(Category.objects.filter(user=self.user))

        # Create initial budget
        if len(categories) > 0:
            initial_cat = categories[0]
            Budget.objects.create(
                user=self.user, category=initial_cat, month=month_start, amount=Decimal("50.00")
            )

        # Submit form with updated amounts
        data = {}
        for i, category in enumerate(categories):
            data[f"category_{category.id}"] = "75.00"

        form = BudgetSetupForm(user=self.user, data=data)
        self.assertTrue(form.is_valid())
        saved = form.save()

        # Verify upsert: initial budget updated
        self.assertEqual(len(saved), len(categories))
        for budget in saved:
            self.assertEqual(budget.amount, Decimal("75.00"))
            self.assertEqual(budget.user, self.user)

    def test_form_preserves_existing_amounts_on_reopen(self):
        from budget.forms import BudgetSetupForm
        from django.utils import timezone

        month_start = timezone.localdate().replace(day=1)
        categories = list(Category.objects.filter(user=self.user))

        # Create initial budgets
        for i, cat in enumerate(categories):
            Budget.objects.create(
                user=self.user, category=cat, month=month_start, amount=Decimal(f"{100 + i}.00")
            )

        # Reopen form
        form = BudgetSetupForm(user=self.user)

        # Check initial values are loaded
        for i, cat in enumerate(categories):
            field_name = f"category_{cat.id}"
            self.assertEqual(form.fields[field_name].initial, Decimal(f"{100 + i}.00"))


class CustomCategoryFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="custom@example.com", password="Pass12345!"
        )
        self.other_user = User.objects.create_user(
            username="other_custom@example.com", password="Pass12345!"
        )

    def test_form_creates_new_custom_category(self):
        from budget.forms import CustomCategoryForm

        form = CustomCategoryForm(user=self.user, data={"name": "Custom Food"})
        self.assertTrue(form.is_valid())
        category = form.save()
        self.assertEqual(category.name, "Custom Food")
        self.assertEqual(category.user, self.user)

    def test_form_rejects_duplicate_user_category_name(self):
        from budget.forms import CustomCategoryForm

        Category.objects.create(user=self.user, name="Groceries")

        form = CustomCategoryForm(user=self.user, data={"name": "Groceries"})
        self.assertFalse(form.is_valid())
        self.assertIn("You already have a category named", str(form.errors))

    def test_form_allows_same_name_for_different_user(self):
        from budget.forms import CustomCategoryForm

        Category.objects.create(user=self.user, name="Groceries")

        form = CustomCategoryForm(user=self.other_user, data={"name": "Groceries"})
        self.assertTrue(form.is_valid())
        category = form.save()
        self.assertEqual(category.user, self.other_user)

    def test_form_rejects_empty_name(self):
        from budget.forms import CustomCategoryForm

        form = CustomCategoryForm(user=self.user, data={"name": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("Category name cannot be empty", str(form.errors))

    def test_form_ignores_deleted_categories_in_uniqueness_check(self):
        from budget.forms import CustomCategoryForm

        Category.objects.create(user=self.user, name="Old Food", is_deleted=True)

        form = CustomCategoryForm(user=self.user, data={"name": "Old Food"})
        self.assertTrue(form.is_valid())
