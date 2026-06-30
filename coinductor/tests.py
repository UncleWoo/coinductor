from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from budget.models import Budget, Category, Expense

User = get_user_model()


class HomeDashboardViewTests(TestCase):
    def setUp(self):
        self.password = "Pass12345!"
        self.user = User.objects.create_user(
            username="dash-user@example.com",
            password=self.password,
        )

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse("home"))

        self.assertRedirects(response, f"{reverse('login')}?next={reverse('home')}")

    def test_authenticated_user_receives_dashboard_context(self):
        category = Category.objects.get(user=self.user, name="Food")
        month_start = timezone.localdate().replace(day=1)
        Budget.objects.create(
            user=self.user,
            category=category,
            month=month_start,
            amount=Decimal("400.00"),
        )
        Expense.objects.create(
            user=self.user,
            category=category,
            amount=Decimal("40.00"),
            date=timezone.localdate(),
        )

        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("dashboard", response.context)
        self.assertIn("daily_limit", response.context["dashboard"])
        self.assertIn("remaining_budget", response.context["dashboard"])
        self.assertIn("velocity_status", response.context["dashboard"])

    def test_dashboard_renders_no_budget_empty_state(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse("home"))

        self.assertContains(response, "Set up your monthly budget")
        self.assertContains(response, "Save budget")
        self.assertEqual(response.context["empty_state"], "no_budget")

    def test_dashboard_renders_no_expenses_guidance(self):
        category = Category.objects.get(user=self.user, name="Food")
        Budget.objects.create(
            user=self.user,
            category=category,
            month=timezone.localdate().replace(day=1),
            amount=Decimal("500.00"),
        )

        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse("home"))

        self.assertContains(response, "On track")
        self.assertContains(response, "No expenses yet for this month")
        self.assertContains(response, "Spending velocity")
        self.assertContains(response, "w-1/3")
        self.assertEqual(response.context["empty_state"], "no_expenses")

    def test_dashboard_renders_metrics_state(self):
        category = Category.objects.get(user=self.user, name="Food")
        Budget.objects.create(
            user=self.user,
            category=category,
            month=timezone.localdate().replace(day=1),
            amount=Decimal("500.00"),
        )
        Expense.objects.create(
            user=self.user,
            category=category,
            amount=Decimal("10000.00"),
            date=timezone.localdate(),
        )

        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse("home"))

        self.assertContains(response, "Remaining budget")
        self.assertContains(response, "Daily limit")
        self.assertContains(response, "Spending velocity")
        self.assertContains(response, "Off track")
        self.assertContains(response, "w-2/3")
        self.assertIsNone(response.context["empty_state"])

    def test_home_route_name_and_login_redirect_remain_home(self):
        self.assertEqual(reverse("home"), "/")
        self.assertEqual(self.client.get(reverse("home")).url.split("?")[0], reverse("login"))

    def test_budget_setup_post_with_valid_amounts_redirects_to_home(self):
        from decimal import Decimal

        month_start = timezone.localdate().replace(day=1)
        categories = list(Category.objects.filter(user=self.user, is_deleted=False))

        data = {"action": "budget-setup"}
        for i, category in enumerate(categories):
            if i == 0:
                data[f"category_{category.id}"] = "100.00"
            else:
                data[f"category_{category.id}"] = "0.00"

        self.client.login(username=self.user.username, password=self.password)
        response = self.client.post(reverse("home"), data, follow=False)

        self.assertRedirects(response, reverse("home"))

        # Verify budgets were saved
        saved_budgets = Budget.objects.filter(user=self.user, month=month_start)
        self.assertEqual(saved_budgets.count(), len(categories))
        self.assertTrue(any(b.amount == Decimal("100.00") for b in saved_budgets))

    def test_budget_setup_post_with_all_zeros_re_renders_with_errors(self):
        categories = list(Category.objects.filter(user=self.user, is_deleted=False))

        data = {"action": "budget-setup"}
        for category in categories:
            data[f"category_{category.id}"] = "0.00"

        self.client.login(username=self.user.username, password=self.password)
        response = self.client.post(reverse("home"), data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("budget_form", response.context)
        self.assertTrue(response.context["budget_form"].errors)
        self.assertIn("At least one category", str(response.context["budget_form"].errors))

    def test_budget_setup_post_with_negative_amounts_re_renders_with_errors(self):
        categories = list(Category.objects.filter(user=self.user, is_deleted=False))

        data = {"action": "budget-setup"}
        for category in categories:
            data[f"category_{category.id}"] = "-50.00"

        self.client.login(username=self.user.username, password=self.password)
        response = self.client.post(reverse("home"), data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("budget_form", response.context)
        self.assertTrue(response.context["budget_form"].errors)

    def test_budget_setup_post_unknown_action_redirects_to_home(self):
        categories = list(Category.objects.filter(user=self.user, is_deleted=False))

        data = {"action": "unknown-action"}
        for category in categories:
            data[f"category_{category.id}"] = "100.00"

        self.client.login(username=self.user.username, password=self.password)
        response = self.client.post(reverse("home"), data, follow=False)

        self.assertRedirects(response, reverse("home"))

    def test_budget_setup_post_upserts_existing_budgets(self):
        month_start = timezone.localdate().replace(day=1)
        category = Category.objects.get(user=self.user, name="Food")

        # Create initial budget
        Budget.objects.create(
            user=self.user,
            category=category,
            month=month_start,
            amount=Decimal("200.00"),
        )

        # Submit updated amount
        categories = list(Category.objects.filter(user=self.user, is_deleted=False))
        data = {"action": "budget-setup"}
        for cat in categories:
            data[f"category_{cat.id}"] = "300.00"

        self.client.login(username=self.user.username, password=self.password)
        response = self.client.post(reverse("home"), data, follow=False)

        self.assertRedirects(response, reverse("home"))

        # Verify no duplicate budgets, only one Food budget with updated amount
        food_budgets = Budget.objects.filter(user=self.user, category=category, month=month_start)
        self.assertEqual(food_budgets.count(), 1)
        self.assertEqual(food_budgets.first().amount, Decimal("300.00"))

    def test_budget_setup_post_clears_no_budget_empty_state(self):
        month_start = timezone.localdate().replace(day=1)
        categories = list(Category.objects.filter(user=self.user, is_deleted=False))

        # Verify no-budget state before setup
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse("home"))
        self.assertEqual(response.context["empty_state"], "no_budget")

        # Submit budget setup
        data = {"action": "budget-setup"}
        for i, category in enumerate(categories):
            if i == 0:
                data[f"category_{category.id}"] = "100.00"
            else:
                data[f"category_{category.id}"] = "0.00"

        response = self.client.post(reverse("home"), data, follow=True)
        self.assertEqual(response.context["empty_state"], "no_expenses")

    def test_no_budget_state_renders_budget_setup_form(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Set up your monthly budget")
        self.assertContains(response, "budget-setup")
        self.assertIn("budget_form", response.context)

    def test_budget_form_includes_all_user_categories(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse("home"))

        form = response.context["budget_form"]
        self.assertEqual(len(form.fields), 7)  # 7 default categories

    def test_metrics_state_renders_edit_form(self):
        category = Category.objects.get(user=self.user, name="Food")
        Budget.objects.create(
            user=self.user,
            category=category,
            month=timezone.localdate().replace(day=1),
            amount=Decimal("500.00"),
        )

        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse("home"))

        self.assertNotContains(response, "Set up your monthly budget")
        self.assertContains(response, "Edit monthly budget")
        self.assertIn("budget_form", response.context)

    def test_budget_form_error_display_inline(self):
        categories = list(Category.objects.filter(user=self.user, is_deleted=False))
        data = {"action": "budget-setup"}
        for cat in categories:
            data[f"category_{cat.id}"] = "0.00"

        self.client.login(username=self.user.username, password=self.password)
        response = self.client.post(reverse("home"), data)

        self.assertContains(response, "At least one category")
