from django.core.exceptions import ValidationError
from django.db import models

DEFAULT_CATEGORIES = [
    "Food",
    "Transport",
    "Entertainment",
    "Shopping",
    "Bills",
    "Health",
    "Other",
]


def validate_first_day_of_month(value):
    if value.day != 1:
        raise ValidationError("Month must be set to the first day of the month.")


class OwnedSoftDeleteModel(models.Model):
    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="%(class)ss",
    )
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(OwnedSoftDeleteModel):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"],
                name="category_unique_user_name",
            )
        ]

    def __str__(self):
        return self.name


class Budget(OwnedSoftDeleteModel):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="budgets",
    )
    month = models.DateField(validators=[validate_first_day_of_month])
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "category", "month"],
                name="budget_unique_user_category_month",
            )
        ]
        ordering = ["-month", "category__name"]

    def clean(self):
        super().clean()
        if self.category_id and self.user_id and self.category.user_id != self.user_id:
            raise ValidationError(
                {"category": "Category must belong to the same user as the budget."}
            )

    def __str__(self):
        return f"{self.category} - {self.month:%Y-%m}"


class Expense(OwnedSoftDeleteModel):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="expenses",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def clean(self):
        super().clean()
        if self.category_id and self.user_id and self.category.user_id != self.user_id:
            raise ValidationError(
                {"category": "Category must belong to the same user as the expense."}
            )

    def __str__(self):
        return f"{self.category} - {self.amount} on {self.date}"
