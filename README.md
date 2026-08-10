# Coinductor

> **Daily budget tracker with dynamic spending limits**

Coinductor calculates how much you can spend *today* based on remaining budget and remaining days in the month. Instead of discovering overspend at month-end, you get real-time feedback after every expense.

## Core Concept

**Formula:** `daily_limit = remaining_budget / remaining_days_in_month`

- Set monthly budget per category (food: 2000 zł, transport: 500 zł)
- Add expenses as they happen
- Dashboard shows: on-track status (yes/no), remaining budget, daily limit

The daily limit recalculates after each expense, creating a feedback loop that changes behavior.

## Features

✅ **Implemented:**
- Email/password authentication
- Monthly budget setup (7 default categories: Food, Transport, Entertainment, Shopping, Bills, Health, Other)
- Custom categories (add/delete your own categories)
- Quick expense entry (≤3 taps/clicks from dashboard)
- Dynamic daily limit calculation
- On-track status with velocity tracking (ahead/on_pace/behind)
- Dashboard with empty state handling (no budget / no expenses)
- Ownership isolation (users can only see their own data)
- Duplicate submission protection (idempotency tokens)

🚧 **Planned:**
- AI-generated daily insights
- Historical spending charts
- Export/import budget data

## Tech Stack

- **Backend:** Django 6.0.6, Python 3.13
- **Database:** SQLite (development), PostgreSQL (production)
- **Package manager:** uv
- **Styling:** Tailwind CSS
- **Deployment:** Railway (or Fly.io)

## Quick Start

### Prerequisites
- Python 3.13+
- uv package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/UncleWoo/coinductor.git
cd coinductor

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser (optional, for admin access)
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

Open http://localhost:8000 in your browser.

### Testing

```bash
# Run all tests
python manage.py test

# Run specific test suite
python manage.py test budget.tests.AuthorizationBoundaryTests

# Run with verbose output
python manage.py test -v 2
```

## Usage

1. **Sign up** with email and password
2. **Set monthly budget** for categories (e.g., Food: 2000 zł, Transport: 500 zł)
3. **Add expenses** throughout the month
4. **Check dashboard** to see:
   - On-track status (green = ahead, yellow = on pace, red = behind)
   - Daily limit: "You can spend X zł/day"
   - Remaining budget and days left in month

## Project Structure

```
coinductor/
├── coinductor/          # Django project settings
│   ├── settings.py      # Configuration
│   ├── urls.py          # URL routing
│   └── views.py         # Main views (home, signup, logout)
├── budget/              # Budget app
│   ├── models.py        # Category, Budget, Expense models
│   ├── forms.py         # Budget setup, expense entry forms
│   ├── services.py      # Dashboard metrics calculation
│   ├── signals.py       # Default category seeding
│   └── tests.py         # Test suite (50+ tests)
├── context/             # Project documentation
│   ├── foundation/      # PRD, roadmap, tech stack
│   └── changes/         # Implementation plans
└── static/              # CSS, JavaScript
```

## Key Business Logic

**Daily limit calculation** (`budget/services.py`):
```python
remaining_budget = total_budget - total_spent
daily_limit = remaining_budget / remaining_days_in_month
```

**On-track status:**
- `spent_per_day = total_spent / elapsed_days`
- `on_track = (spent_per_day <= daily_limit)`

**Velocity status:**
- Ahead: spending slower than pace
- On pace: within 5% tolerance
- Behind: spending faster than pace

## Security & Authorization

- User-owned data isolation (all queries filter by `user=request.user`)
- Form validation prevents cross-user category manipulation
- Idempotency tokens protect against duplicate expense submission
- Signal handlers log errors gracefully without breaking user operations

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`python manage.py test`)
4. Commit changes (`git commit -m 'feat: add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

[License information]

## Contact

Project Link: https://github.com/UncleWoo/coinductor
