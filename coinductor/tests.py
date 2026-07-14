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
        # Velocity bar should show "ahead" status
        self.assertEqual(response.context["velocity_status"], "ahead")
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
        # Velocity bar should show "behind" status
        self.assertEqual(response.context["velocity_status"], "behind")
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

    def test_budget_setup_post_creates_custom_category(self):
        categories = list(Category.objects.filter(user=self.user, is_deleted=False))
        data = {
            "action": "add-category",
            "name": "Pets",
        }
        for category in categories:
            data[f"category_{category.id}"] = "0.00"

        self.client.login(username=self.user.username, password=self.password)
        response = self.client.post(reverse("home"), data, follow=False)

        self.assertRedirects(response, reverse("home"))
        pets_category = Category.objects.get(user=self.user, name="Pets", is_deleted=False)
        self.assertIsNotNone(pets_category)

    def test_budget_setup_post_rejects_duplicate_custom_category_name(self):
        Category.objects.create(user=self.user, name="Pets")
        categories = list(Category.objects.filter(user=self.user, is_deleted=False))
        data = {"action": "add-category", "name": "Pets"}
        for i, category in enumerate(categories):
            data[f"category_{category.id}"] = "100.00" if i == 0 else "0.00"

        self.client.login(username=self.user.username, password=self.password)
        response = self.client.post(reverse("home"), data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("custom_category_form", response.context)
        self.assertContains(response, "You already have a category named")

    def test_budget_setup_post_rejects_custom_amount_without_name(self):
        categories = list(Category.objects.filter(user=self.user, is_deleted=False))
        data = {"action": "add-category", "name": ""}
        for i, category in enumerate(categories):
            data[f"category_{category.id}"] = "100.00" if i == 0 else "0.00"

        self.client.login(username=self.user.username, password=self.password)
        response = self.client.post(reverse("home"), data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Category name cannot be empty.")

    def test_no_budget_state_renders_budget_setup_form(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Set up your monthly budget")
        self.assertContains(response, "budget-setup")
        self.assertIn("budget_form", response.context)
        self.assertIn("custom_category_form", response.context)
        self.assertContains(response, "Manage categories")

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

    def test_soft_deleted_custom_category_can_be_recreated(self):
        """
        Regression test: Soft-deleted custom categories should not block recreation
        due to unique constraint. The constraint is now conditional on is_deleted=False.
        """
        self.client.login(username=self.user.username, password=self.password)

        # Step 1: Create 'Pets' custom category
        categories = list(Category.objects.filter(user=self.user, is_deleted=False))
        data = {"action": "add-category", "name": "Pets"}
        for cat in categories:
            data[f"category_{cat.id}"] = "0.00"

        response = self.client.post(reverse("home"), data)
        self.assertEqual(response.status_code, 302)

        # Verify Pets was created
        pets = Category.objects.get(user=self.user, name="Pets", is_deleted=False)
        self.assertIsNotNone(pets)

        # Step 2: Soft-delete Pets
        pets.is_deleted = True
        pets.save()

        # Step 3: Create 'Pets' again (should succeed due to conditional constraint)
        categories = list(Category.objects.filter(user=self.user, is_deleted=False))
        data = {"action": "add-category", "name": "Pets"}
        for cat in categories:
            data[f"category_{cat.id}"] = "0.00"

        response = self.client.post(reverse("home"), data)
        self.assertEqual(response.status_code, 302)

        # Verify new Pets was created
        active_pets = Category.objects.filter(user=self.user, name="Pets", is_deleted=False)
        self.assertEqual(active_pets.count(), 1)

        # Verify old deleted Pets still exists
        all_pets = Category.objects.filter(user=self.user, name="Pets")
        self.assertEqual(all_pets.count(), 2)

        # Verify app remains functional
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_expense_quick_add_post_creates_expense_and_redirects(self):
        """Valid POST to add-expense creates expense and redirects to home."""
        category = Category.objects.get(user=self.user, name="Food")
        month_start = timezone.localdate().replace(day=1)
        Budget.objects.create(
            user=self.user,
            category=category,
            month=month_start,
            amount=Decimal("400.00"),
        )

        self.client.login(username=self.user.username, password=self.password)
        
        data = {
            "action": "add-expense",
            "amount": "25.50",
            "category": category.id,
            "date": "2026-07-01",
            "description": "Lunch",
        }
        response = self.client.post(reverse("home"), data)
        
        self.assertRedirects(response, reverse("home"))
        
        # Verify expense was created
        expense = Expense.objects.get(user=self.user, category=category)
        self.assertEqual(expense.amount, Decimal("25.50"))
        self.assertEqual(expense.description, "Lunch")

    def test_expense_quick_add_post_updates_dashboard_metrics(self):
        """After successful expense POST, dashboard shows updated metrics."""
        category = Category.objects.get(user=self.user, name="Food")
        month_start = timezone.localdate().replace(day=1)
        Budget.objects.create(
            user=self.user,
            category=category,
            month=month_start,
            amount=Decimal("400.00"),
        )

        self.client.login(username=self.user.username, password=self.password)
        
        # Get initial metrics
        response_before = self.client.get(reverse("home"))
        metrics_before = response_before.context["dashboard"]
        
        # Add expense
        data = {
            "action": "add-expense",
            "amount": "50.00",
            "category": category.id,
            "date": timezone.localdate().isoformat(),
        }
        self.client.post(reverse("home"), data)
        
        # Get updated metrics
        response_after = self.client.get(reverse("home"))
        metrics_after = response_after.context["dashboard"]
        
        # Verify metrics changed
        self.assertLess(
            metrics_after["remaining_budget"],
            metrics_before["remaining_budget"]
        )
        self.assertEqual(
            metrics_after["total_spent"],
            Decimal("50.00")
        )

    def test_expense_quick_add_invalid_post_shows_inline_errors(self):
        """Invalid POST preserves form data and shows errors."""
        category = Category.objects.get(user=self.user, name="Food")
        
        self.client.login(username=self.user.username, password=self.password)
        
        # Submit without required amount
        data = {
            "action": "add-expense",
            "category": category.id,
            "date": "2026-07-01",
        }
        response = self.client.post(reverse("home"), data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("expense_form", response.context)
        self.assertFalse(response.context["expense_form"].is_valid())
        self.assertIn("amount", response.context["expense_form"].errors)

    def test_expense_quick_add_negative_amount_shows_inline_errors(self):
        """Negative amount POST is rejected and renders inline errors."""
        category = Category.objects.get(user=self.user, name="Food")

        self.client.force_login(self.user)

        data = {
            "action": "add-expense",
            "amount": "-25.50",
            "category": category.id,
            "date": "2026-07-01",
        }
        response = self.client.post(reverse("home"), data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("expense_form", response.context)
        self.assertFalse(response.context["expense_form"].is_valid())
        self.assertIn("amount", response.context["expense_form"].errors)
        self.assertEqual(Expense.objects.count(), 0)

    def test_anonymous_user_cannot_post_expense(self):
        """Anonymous POST to add-expense redirects to login."""
        category = Category.objects.get(user=self.user, name="Food")
        
        data = {
            "action": "add-expense",
            "amount": "25.50",
            "category": category.id,
            "date": "2026-07-01",
        }
        response = self.client.post(reverse("home"), data)
        
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('home')}")
        self.assertEqual(Expense.objects.count(), 0)

    def test_anonymous_user_cannot_post_add_category(self):
        response = self.client.post(
            reverse("home"),
            {"action": "add-category", "name": "Pets"},
        )

        self.assertRedirects(response, f"{reverse('login')}?next={reverse('home')}")
        self.assertFalse(
            Category.objects.filter(user=self.user, name="Pets", is_deleted=False).exists()
        )

    def test_anonymous_user_cannot_post_delete_category(self):
        category = Category.objects.get(user=self.user, name="Food")
        response = self.client.post(
            reverse("home"),
            {"action": "delete-category", "category_id": category.id},
        )

        self.assertRedirects(response, f"{reverse('login')}?next={reverse('home')}")
        category.refresh_from_db()
        self.assertFalse(category.is_deleted)

    def test_anonymous_user_cannot_post_budget_setup(self):
        category = Category.objects.get(user=self.user, name="Food")
        response = self.client.post(
            reverse("home"),
            {"action": "budget-setup", f"category_{category.id}": "100.00"},
        )

        self.assertRedirects(response, f"{reverse('login')}?next={reverse('home')}")
        self.assertEqual(Budget.objects.filter(user=self.user).count(), 0)

    def test_cross_user_category_is_rejected_in_add_expense_post(self):
        other_user = User.objects.create_user(
            username="cross-user-expense@example.com",
            password="Pass12345!",
        )
        other_category = Category.objects.get(user=other_user, name="Food")
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("home"),
            {
                "action": "add-expense",
                "amount": "10.00",
                "category": other_category.id,
                "date": timezone.localdate().isoformat(),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("expense_form", response.context)
        self.assertIn("category", response.context["expense_form"].errors)
        self.assertEqual(Expense.objects.filter(user=self.user).count(), 0)
        self.assertEqual(Expense.objects.filter(user=other_user).count(), 0)

    def test_cross_user_category_cannot_be_soft_deleted(self):
        other_user = User.objects.create_user(
            username="cross-user-delete@example.com",
            password="Pass12345!",
        )
        other_category = Category.objects.get(user=other_user, name="Food")
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("home"),
            {"action": "delete-category", "category_id": other_category.id},
        )

        self.assertRedirects(response, reverse("home"))
        other_category.refresh_from_db()
        self.assertFalse(other_category.is_deleted)

    def test_cross_user_category_is_ignored_in_budget_setup_post(self):
        other_user = User.objects.create_user(
            username="cross-user-budget@example.com",
            password="Pass12345!",
        )
        other_category = Category.objects.get(user=other_user, name="Food")
        month_start = timezone.localdate().replace(day=1)
        Budget.objects.create(
            user=other_user,
            category=other_category,
            month=month_start,
            amount=Decimal("500.00"),
        )
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("home"),
            {
                "action": "budget-setup",
                f"category_{other_category.id}": "999.00",
            },
            follow=False,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("budget_form", response.context)
        self.assertTrue(response.context["budget_form"].errors)
        other_budget = Budget.objects.get(
            user=other_user,
            category=other_category,
            month=month_start,
            is_deleted=False,
        )
        self.assertEqual(other_budget.amount, Decimal("500.00"))
        self.assertEqual(Budget.objects.filter(user=self.user, month=month_start).count(), 0)

    def test_add_expense_post_with_invalid_date_shows_inline_errors(self):
        category = Category.objects.get(user=self.user, name="Food")
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("home"),
            {
                "action": "add-expense",
                "amount": "20.00",
                "category": category.id,
                "date": "not-a-date",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("expense_form", response.context)
        self.assertIn("date", response.context["expense_form"].errors)
        self.assertEqual(Expense.objects.filter(user=self.user).count(), 0)

    def test_add_expense_post_with_invalid_category_type_shows_inline_errors(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("home"),
            {
                "action": "add-expense",
                "amount": "20.00",
                "category": "abc",
                "date": timezone.localdate().isoformat(),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("expense_form", response.context)
        self.assertIn("category", response.context["expense_form"].errors)
        self.assertEqual(Expense.objects.filter(user=self.user).count(), 0)

    def test_add_category_post_with_overlong_name_shows_inline_errors(self):
        self.client.force_login(self.user)
        overlong_name = "X" * 101

        response = self.client.post(
            reverse("home"),
            {"action": "add-category", "name": overlong_name},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("custom_category_form", response.context)
        self.assertIn("name", response.context["custom_category_form"].errors)
        self.assertFalse(
            Category.objects.filter(user=self.user, name=overlong_name, is_deleted=False).exists()
        )

    def test_delete_category_post_without_category_id_is_noop(self):
        category = Category.objects.get(user=self.user, name="Food")
        self.client.force_login(self.user)

        response = self.client.post(reverse("home"), {"action": "delete-category"})

        self.assertRedirects(response, reverse("home"))
        category.refresh_from_db()
        self.assertFalse(category.is_deleted)

    def test_budget_setup_post_with_non_decimal_amount_shows_inline_errors(self):
        category = Category.objects.get(user=self.user, name="Food")
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("home"),
            {
                "action": "budget-setup",
                f"category_{category.id}": "abc",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("budget_form", response.context)
        self.assertTrue(response.context["budget_form"].errors)
        self.assertEqual(Budget.objects.filter(user=self.user).count(), 0)

    def test_dashboard_shows_quick_add_form_when_budget_exists(self):
        """Dashboard renders quick-add expense form when budget is set."""
        category = Category.objects.get(user=self.user, name="Food")
        month_start = timezone.localdate().replace(day=1)
        Budget.objects.create(
            user=self.user,
            category=category,
            month=month_start,
            amount=Decimal("400.00"),
        )

        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add expense")
        self.assertContains(response, 'name="action" value="add-expense"')
        self.assertIn("expense_form", response.context)

    def test_dashboard_shows_quick_add_form_in_no_budget_state(self):
        """Dashboard renders quick-add expense form even without budget."""
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add expense")
        self.assertContains(response, 'name="action" value="add-expense"')
        self.assertContains(response, "You can track expenses even without a budget")
        self.assertIn("expense_form", response.context)

    def test_quick_add_form_preserves_on_track_status_rendering(self):
        """Quick-add form presence doesn't break on-track/off-track display."""
        category = Category.objects.get(user=self.user, name="Food")
        month_start = timezone.localdate().replace(day=1)
        Budget.objects.create(
            user=self.user,
            category=category,
            month=month_start,
            amount=Decimal("400.00"),
        )

        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        # Should still show on-track badge
        self.assertTrue(response.context["on_track"])
        # And quick-add form
        self.assertIn("expense_form", response.context)
