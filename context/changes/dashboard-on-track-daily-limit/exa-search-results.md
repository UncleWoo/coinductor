# Exa-Search Results: S-01 Compatible Libraries

**Date:** 2026-06-29  
**Change ID:** dashboard-on-track-daily-limit  
**Stack:** Django 6.0.6, Python 3.13, SQLite, uv

---

## Search 1: Django Dashboard Libraries (Real-time Budget Tracking)

**Query:** `"Django Python dashboard library real-time data visualization budget tracking 2024 2025"`

| Name | URL | Published |
|------|-----|-----------|
| ARWA044/finance-tracker | https://github.com/ARWA044/finance-tracker | 2025-07-27 |
| usmanhalalit/DjangoRealtime | https://github.com/usmanhalalit/DjangoRealtime | 2025-11-03 |
| Kzu0-afk/ledgerly-web | https://github.com/Kzu0-afk/ledgerly-web | — |
| Anonym0usWork1221/hassan-traders | https://github.com/anonym0uswork1221/hassan-traders | 2025-06-20 |
| 48Naveenkumar/Personal-Finance-Tracker-with-AI-Expense-Prediction | https://github.com/48Naveenkumar/Personal-Finance-Tracker-with-AI-Expense-Prediction | 2025-02-21 |

---

## Search 2: Django Admin Dashboard & Charts

**Query:** `"Django admin dashboard library Python charts graphs 2024 2025"`

| Name | URL | Notes |
|------|-----|-------|
| **django-admin-charts** | https://pypi.org/project/django-admin-charts/ | Charts for Django admin |
| **django-unfold** | https://github.com/unfoldadmin/django-unfold | Modern Django admin theme |
| **django-dashub** | https://github.com/klixsoft/django-dashub | Dashboard library |
| **Unfold Admin** | https://unfoldadmin.com/ | Commercial admin modernization |
| **wildfish/django-dashboards** | https://github.com/wildfish/django-dashboards | Dashboard components |

---

## Search 3: Python Charting Libraries

**Query:** `"python charting library web django compatible chart.js plotly 2024 2025"`

| Name | URL | Notes |
|------|-----|-------|
| **Chartkick.py** | https://chartkick.com/python | Create charts with one line of Python |
| **Plotly** (v6.8.0) | https://pypi.org/project/plotly/ | Interactive graphing |
| **Plotly Python Docs** | https://plotly.com/python/ | Full documentation |
| **django-plotly-dash** | https://django-plotly-dash.readthedocs.io/ | Plotly Dash integration with Django |
| **ankane/chartkick.py** | https://github.com/ankane/chartkick.py | GitHub repo |

---

## Search 4: HTMX + Django Integration

**Query:** `"HTMX Django real-time updates dynamic content 2024 2025"`

| Name | URL | Published |
|------|-----|-----------|
| Dynamic web apps with HTMX, Python, Django (InfoWorld) | https://www.infoworld.com/article/3802689/dynamic-web-apps-with-htmx-python-and-django.html | 2025-01-15 |
| Real-time notifications with Django-channels, HTMX and SSE | https://www.techblog.moebius.space/posts/2024-04-20-sse-with-django-channels-and-htmx/ | 2024-04-20 |
| Django + HTMX: Build Dynamic Web Apps (sparrow.so) | https://blog.sparrow.so/the-ultimate-django-htmx-guide-building-modern-dynamic-web-applications-in-2025/ | 2025-12-03 |
| HTMX 2.0 × Django 2025 Guide (Tasuke Hub) | https://tasukehub.com/articles/htmx-2-django-spa-guide-2025 | 2025-11-26 |
| Django + HTMX Interactive Apps (CODERCOPS) | https://www.codercops.com/blog/django-htmx-interactive-apps-without-javascript | 2026-02-24 |

---

## Search 5: Django UI Components (Cotton, Components)

**Query:** `"django-components django-cotton Tailwind CSS Django integration 2024 2025"`

| Name | URL | Published |
|------|-----|-----------|
| **Django Cotton** | https://django-cotton.com/ | Modern UI composition |
| **django-cotton (GitHub)** | https://github.com/wrabit/django-cotton | 2024-06-08 |
| Django Cotton UI Installation | https://django-cotton.com/ui/installation | — |
| ReThinking Django Templates (Forum) | https://forum.djangoproject.com/t/blog-rethinking-django-template-4-server-side-component/43607 | 2025-12-03 |
| django-components vs django-cotton | https://github.com/django-components/django-components/discussions/552 | — |

---

## Library Compatibility Matrix for S-01

| Library | Django 6.0 | Python 3.13 | S-01 Relevance | Install Priority |
|---------|------------|-------------|----------------|------------------|
| django-unfold | ✅ | ✅ | Low (admin theme, not user dashboard) | Skip |
| django-dashboards | ✅ | ✅ | Medium (dashboard components) | Evaluate |
| django-admin-charts | ✅ | ✅ | Low (admin only) | Skip |
| Chartkick.py | ✅ | ✅ | Medium (simple charts) | Optional for S-01 |
| Plotly | ✅ | ✅ | Low (overkill for S-01) | Skip |
| django-plotly-dash | ✅ | ⚠️ Check | Low (overkill) | Skip |
| HTMX + django-htmx | ✅ | ✅ | **High for S-02** | Defer to S-02 |
| Django Cotton | ✅ | ✅ | Medium (component-based templates) | Optional |
| TailwindCSS (CDN) | ✅ | N/A | **High** | Use CDN |

---

## Recommendations for S-01

### Zero-Install Approach (Recommended)

For S-01 dashboard showing on-track status + daily limit:

1. **Dashboard display**: Django views + templates (built-in)
2. **Styling**: TailwindCSS via CDN
3. **Date calculation**: Python `calendar` module (built-in)
4. **Charts**: Not needed for S-01 (just numbers + status indicator)

### Libraries to Consider for Future Slices

**For S-02 (expense entry with instant recalc):**
- **HTMX** + **django-htmx** for dynamic updates without full page reloads
- **Django Cotton** or **django-components** for reusable UI components

**For enhanced dashboards (post-MVP):**
- **Chartkick.py** for simple spending charts
- **django-dashboards** for structured dashboard components

---

## Raw JSON Responses

<details>
<summary>Search 1 Raw Response</summary>

```json
{"requestId":"d51b62ce634da959b5a1a807ebf4647a","resolvedSearchType":"","results":[{"id":"https://github.com/ARWA044/finance-tracker","title":"ARWA044/finance-tracker","url":"https://github.com/ARWA044/finance-tracker","publishedDate":"2025-07-27T20:51:04.000Z"},{"id":"5069289990","title":"usmanhalalit/DjangoRealtime","url":"https://github.com/usmanhalalit/DjangoRealtime","publishedDate":"2025-11-03T00:00:00.000Z"},{"id":"https://github.com/Kzu0-afk/ledgerly-web","title":"Kzu0-afk/ledgerly-web","url":"https://github.com/Kzu0-afk/ledgerly-web"},{"id":"https://github.com/anonym0uswork1221/hassan-traders","title":"Anonym0usWork1221/hassan-traders","url":"https://github.com/anonym0uswork1221/hassan-traders","publishedDate":"2025-06-20T12:35:13.000Z"},{"id":"https://github.com/48Naveenkumar/Personal-Finance-Tracker-with-AI-Expense-Prediction","title":"48Naveenkumar/Personal-Finance-Tracker-with-AI-Expense-Prediction","url":"https://github.com/48Naveenkumar/Personal-Finance-Tracker-with-AI-Expense-Prediction","publishedDate":"2025-02-21T11:17:09.000Z"}],"searchTime":1137.1,"costDollars":{"total":0.007,"search":{"neural":0.007}}}
```
</details>

<details>
<summary>Search 2 Raw Response</summary>

```json
{"requestId":"aa4b9ea8f52598003aa234cb29cab1cc","resolvedSearchType":"","results":[{"id":"https://pypi.org/project/django-admin-charts/","title":"django-admin-charts · PyPI","url":"https://pypi.org/project/django-admin-charts/","image":"https://pypi.org/static/images/twitter.abaf4b19.webp"},{"id":"https://github.com/unfoldadmin/django-unfold?tab=readme-ov-file","title":"unfoldadmin/django-unfold","url":"https://github.com/unfoldadmin/django-unfold?tab=readme-ov-file","publishedDate":"2022-08-19T07:00:41.000Z"},{"id":"https://github.com/klixsoft/django-dashub","title":"klixsoft/django-dashub","url":"https://github.com/klixsoft/django-dashub"},{"id":"https://unfoldadmin.com/","title":"Modern Django Admin - Unfold","url":"https://unfoldadmin.com/","image":"https://unfoldadmin.com/static/img/opengraph.jpg"},{"id":"https://github.com/wildfish/django-dashboards","title":"wildfish/django-dashboards","url":"https://github.com/wildfish/django-dashboards"}],"searchTime":1083.2,"costDollars":{"total":0.007,"search":{"neural":0.007}}}
```
</details>

<details>
<summary>Search 3 Raw Response</summary>

```json
{"requestId":"51e7438456f967b0a04ccf4e311d3f8f","resolvedSearchType":"","results":[{"id":"https://chartkick.com/python","title":"Chartkick.py - Create beautiful JavaScript charts with one line of Python","url":"https://chartkick.com/python"},{"id":"https://pypi.org/project/plotly/","title":"plotly v6.8.0","url":"https://pypi.org/project/plotly/"},{"id":"https://plotly.com/python/","title":"Plotly Python Graphing Library","url":"https://plotly.com/python/","image":"https://help.plot.ly/images/twitter-default.png"},{"id":"https://django-plotly-dash.readthedocs.io/en/stable/index.html","title":"","url":"https://django-plotly-dash.readthedocs.io/en/stable/index.html"},{"id":"https://github.com/ankane/chartkick.py","title":"ankane/chartkick.py","url":"https://github.com/ankane/chartkick.py"}],"searchTime":1061.5,"costDollars":{"total":0.007,"search":{"neural":0.007}}}
```
</details>

<details>
<summary>Search 4 Raw Response</summary>

```json
{"requestId":"55a75d7917b09a57f1fb1d67e8baa61d","resolvedSearchType":"","results":[{"id":"https://www.infoworld.com/article/3802689/dynamic-web-apps-with-htmx-python-and-django.html","title":"Dynamic web apps with HTMX, Python, and Django | InfoWorld","url":"https://www.infoworld.com/article/3802689/dynamic-web-apps-with-htmx-python-and-django.html","publishedDate":"2025-01-15T05:41:02.000Z","author":"by Matthew Tyson","image":"https://www.infoworld.com/wp-content/uploads/2025/02/3802689-0-60355300-1739350885-shutterstock_2426683595.jpg?quality=50&strip=all&w=1024"},{"id":"23395038859","title":"Real-time notifications with Django-channels, HTMX and Server Sent Events","url":"https://www.techblog.moebius.space/posts/2024-04-20-sse-with-django-channels-and-htmx/","publishedDate":"2024-04-20T00:00:00.000Z"},{"id":"https://blog.sparrow.so/the-ultimate-django-htmx-guide-building-modern-dynamic-web-applications-in-2025/","title":"Django + HTMX: Build Dynamic Web Apps Without JavaScript","url":"https://blog.sparrow.so/the-ultimate-django-htmx-guide-building-modern-dynamic-web-applications-in-2025/","publishedDate":"2025-12-03T06:39:52.000Z"},{"id":"https://tasukehub.com/articles/htmx-2-django-spa-guide-2025?lang=en","title":"Ditch Complex SPAs! Lightning-Fast Web Development with HTMX 2.0 × Django [2025 Practical Guide]","url":"https://tasukehub.com/articles/htmx-2-django-spa-guide-2025?lang=en","publishedDate":"2025-11-26T12:20:00.000Z"},{"id":"https://www.codercops.com/blog/django-htmx-interactive-apps-without-javascript","title":"Django + HTMX -- Building Interactive Apps Without the JavaScript Bloat","url":"https://www.codercops.com/blog/django-htmx-interactive-apps-without-javascript","publishedDate":"2026-02-24T00:00:00.000Z"}],"searchTime":916.3,"costDollars":{"total":0.007,"search":{"neural":0.007}}}
```
</details>

<details>
<summary>Search 5 Raw Response</summary>

```json
{"requestId":"e1260989437f1807818df8470efe2598","resolvedSearchType":"","results":[{"id":"https://django-cotton.com/","title":"Django Cotton - Modern UI Composition for Django","url":"https://django-cotton.com/"},{"id":"https://github.com/wrabit/django-cotton","title":"GitHub - wrabit/django-cotton: Enabling Modern UI Composition in Django","url":"https://github.com/wrabit/django-cotton","publishedDate":"2024-06-08T13:30:49.000Z"},{"id":"https://django-cotton.com/ui/installation","title":"Installation - Django Cotton UI","url":"https://django-cotton.com/ui/installation"},{"id":"51817404390","title":"Blog: ReThinking Django Template #4: Server Side Component - Show & Tell - Django Forum","url":"https://forum.djangoproject.com/t/blog-rethinking-django-template-4-server-side-component/43607","publishedDate":"2025-12-03T00:00:00.000Z"},{"id":"https://github.com/django-components/django-components/discussions/552","title":"Comparision with django-cotton · django-components/django-components · Discussion #552","url":"https://github.com/django-components/django-components/discussions/552"}],"searchTime":1036.3,"costDollars":{"total":0.007,"search":{"neural":0.007}}}
```
</details>

---

**Total Search Cost:** $0.035 (5 searches × $0.007)
