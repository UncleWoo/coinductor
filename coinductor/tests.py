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

        self.assertContains(response, "No budget set for this month")
        self.assertContains(response, "Set monthly budget")
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
