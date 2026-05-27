# BDO Smart Tax Hub — Developer Guide

A Django web application for managing tax planning, client portfolios, and tax return workflows.

---

## Table of Contents

1. [Tech Stack](#tech-stack)
2. [Project Structure](#project-structure)
3. [Setup](#setup)
4. [How Django Works](#how-django-works)
5. [File by File Explanation](#file-by-file-explanation)
6. [How to Add a New View](#how-to-add-a-new-view)
7. [How to Create a Database Table](#how-to-create-a-database-table)
8. [How to Build CRUD Actions](#how-to-build-crud-actions)
9. [URL Reference](#url-reference)

---

## Tech Stack

| Layer    | Technology                  |
|----------|-----------------------------|
| Backend  | Django 4.2                  |
| Database | SQLite (development)        |
| Frontend | Django Templates + Ionicons |
| Charts   | Chart.js                    |

---

## Project Structure

```
BDO/
├── manage.py                   # CLI tool to run Django commands
├── requirements.txt            # Python dependencies
├── README.md
│
├── bdo_project/                # Project-level configuration
│   ├── settings.py             # Database, installed apps, timezone, etc.
│   ├── urls.py                 # Root URL routing
│   └── wsgi.py                 # Entry point for production servers
│
└── app/                        # The main application module
    ├── models.py               # Defines database tables as Python classes
    ├── views.py                # Functions that handle each HTTP request
    ├── urls.py                 # Maps URLs to view functions
    ├── migrations/             # Auto-generated files that update the database
    └── templates/              # HTML files rendered by the views
        ├── base.html           # Shared sidebar + layout (all pages inherit this)
        ├── login.html          # Standalone login page
        ├── index.html          # Dashboard
        ├── users.html          # User list + edit/delete modals
        ├── clients.html        # Client list
        ├── tax_returns.html    # All tax returns
        ├── my_returns.html     # Returns assigned to the logged-in user
        ├── planning.html       # Planning tasks with filters
        └── configuration.html  # Configuration tables
```

---

## Setup

```bash
# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create database tables
python manage.py makemigrations
python manage.py migrate

# 4. Create your admin user
python manage.py createsuperuser

# 5. Start the server
python manage.py runserver
```

Open http://127.0.0.1:8000/login/ in your browser.

---

## How Django Works

Django follows the **MTV pattern**: Model → Template → View.
Every HTTP request travels through these layers in order:

```
Browser Request
      │
      ▼
urls.py  ──────────────────────────────────────────────
  Compares the URL against its list of patterns.       │
  Calls the matching view function.                    │
      │                                                │
      ▼                                                │
views.py                                               │
  Receives the request object.                         │
  Queries the database through models if needed.       │
  Passes data to a template.                           │
  Returns an HTTP response (HTML, redirect, JSON).     │
      │                                                │
      ▼                                                │
models.py                                              │
  Each class = one database table.                     │
  Django translates Python queries into SQL.           │
      │                                                │
      ▼                                                │
templates/*.html                                       │
  Django fills the {{ variables }} with real data.     │
  Returns the final HTML string.                       │
      │                                                │
      ▼                                                │
Browser Response ◄─────────────────────────────────────
```

### The request lifecycle — concrete example

User visits `/planning/`:

```
1. bdo_project/urls.py  →  path('', include('app.urls'))
2. app/urls.py          →  path('planning/', views.planning)
3. app/views.py         →  def planning(request):
                               tasks = PlanningTask.objects.all()
                               return render(request, 'planning.html', {'tasks': tasks})
4. planning.html        →  {% for task in tasks %} ... {% endfor %}
5. Browser              ←  Receives the rendered HTML page
```

---

## File by File Explanation

### `manage.py`

The command-line interface for Django. You never edit this file.
It is always called with a subcommand:

```bash
python manage.py runserver        # Start development server
python manage.py makemigrations   # Detect model changes, generate migration files
python manage.py migrate          # Apply migrations to the database
python manage.py createsuperuser  # Create an admin user
python manage.py shell            # Open a Python shell with Django loaded
```

---

### `bdo_project/settings.py`

Global configuration for the entire project. Key sections:

```python
INSTALLED_APPS = [
    ...
    'app',   # ← Your app must be registered here for Django to find its models and templates
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',   # ← Database file location
    }
}

TEMPLATES = [{
    ...
    'APP_DIRS': True,   # ← Tells Django to look for templates inside each app's /templates/ folder
}]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Bogota'
```

---

### `bdo_project/urls.py`

The root URL dispatcher. It receives every request and decides which app handles it.

```python
urlpatterns = [
    path('admin/', admin.site.urls),   # Built-in Django admin panel
    path('', include('app.urls')),     # Everything else goes to app/urls.py
]
```

---

### `app/urls.py`

Maps specific URL paths to view functions inside this app.

```python
urlpatterns = [
    path('',             views.home,       name='home'),
    path('planning/',    views.planning,   name='planning'),
    path('users/',       views.users,      name='users'),
    # ...
]
```

The `name=` parameter lets you reference the URL in templates without hardcoding the path:
```html
<a href="{% url 'planning' %}">Planning</a>
```

---

### `app/views.py`

Each function handles one URL. It always receives `request` and must return a response.

```python
@login_required(login_url='/login/')   # Redirect to login if not authenticated
def planning(request):
    tasks = PlanningTask.objects.all()  # Query the database
    return render(request, 'planning.html', {'tasks': tasks})
    #              ↑ template file          ↑ data available in the template
```

**Common response types:**

```python
return render(request, 'page.html', context)   # Render HTML
return redirect('view_name')                    # Redirect to another URL
return redirect('/some/path/')                  # Redirect to a path
```

**Reading form data from a POST request:**

```python
def my_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')   # Read form field
    if request.method == 'GET':
        search = request.GET.get('q')     # Read query param (?q=...)
```

---

### `app/models.py`

Each class represents a database table. Each attribute is a column.

```python
class PlanningTask(models.Model):
    client    = models.CharField(max_length=200)   # TEXT column, max 200 chars
    due_date  = models.DateField()                 # DATE column
    status    = models.CharField(choices=STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Set automatically on insert
    updated_at = models.DateTimeField(auto_now=True)      # Set automatically on update
```

**Common field types:**

| Field type        | Database type | Use case                        |
|-------------------|---------------|---------------------------------|
| `CharField`       | VARCHAR       | Short text, requires max_length |
| `TextField`       | TEXT          | Long text, no length limit      |
| `IntegerField`    | INTEGER       | Whole numbers                   |
| `DecimalField`    | DECIMAL       | Money, precise decimals         |
| `BooleanField`    | BOOLEAN       | True / False                    |
| `DateField`       | DATE          | Date only                       |
| `DateTimeField`   | DATETIME      | Date + time                     |
| `ForeignKey`      | INTEGER (FK)  | Link to another table           |

---

### `app/migrations/`

Auto-generated files — **never edit them manually**.
Each file is a snapshot of your models at a point in time.

```
migrations/
├── __init__.py        # Makes it a Python package
├── 0001_initial.py    # First migration: creates tables from scratch
├── 0002_....py        # Second migration: adds a column, etc.
```

---

### `app/templates/base.html`

The shared layout every page inherits. It contains the sidebar and the main content area.

```html
<!-- base.html -->
<nav class="sidebar"> ... menu links ... </nav>

<main class="content">
    {% block content %}{% endblock %}   ← Each child page fills this block
</main>
```

Child templates inherit the sidebar by extending this file:

```html
<!-- planning.html -->
{% extends "base.html" %}

{% block content %}
  <h1>Planning</h1>
  ...
{% endblock %}
```

---

## How to Add a New View

Follow these 3 steps every time you add a new page.

### Step 1 — Create the template

Create `app/templates/reports.html`:

```html
{% extends "base.html" %}

{% block title %}Reports{% endblock %}

{% block content %}
<h1>Reports</h1>
<p>Content goes here.</p>
{% endblock %}
```

### Step 2 — Create the view function

In `app/views.py`, add:

```python
@login_required(login_url='/login/')
def reports(request):
    return render(request, 'reports.html')
```

### Step 3 — Register the URL

In `app/urls.py`, add one line:

```python
path('reports/', views.reports, name='reports'),
```

### Step 4 — Add it to the sidebar (optional)

In `app/templates/base.html`, add a `<li>` inside the `<nav>`:

```html
<li>
    <a href="{% url 'reports' %}"
       {% if request.resolver_match.url_name == 'reports' %}class="active"{% endif %}>
        <span class="icon"><ion-icon name="bar-chart-outline"></ion-icon></span>
        <span>Reports</span>
    </a>
</li>
```

The `class="active"` part highlights the current page in the sidebar automatically.

---

## How to Create a Database Table

### Step 1 — Define the model

In `app/models.py`:

```python
class Client(models.Model):
    STATUS_CHOICES = [
        ('active',   'Active'),
        ('inactive', 'Inactive'),
    ]

    name       = models.CharField(max_length=200)
    tax_id     = models.CharField(max_length=20, unique=True)
    contact    = models.CharField(max_length=200, blank=True)
    city       = models.CharField(max_length=100)
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']       # Default sort order
        verbose_name = 'Client'

    def __str__(self):
        return self.name          # Shown in Django admin and shell
```

### Step 2 — Generate the migration

```bash
python manage.py makemigrations
```

Django reads your model and creates a file like `migrations/0002_client.py`.

### Step 3 — Apply the migration

```bash
python manage.py migrate
```

Django executes the SQL and creates the `app_client` table in `db.sqlite3`.

### Step 4 — Use it in a view

```python
from .models import Client

def clients(request):
    all_clients = Client.objects.filter(status='active').order_by('name')
    return render(request, 'clients.html', {'clients': all_clients})
```

### Adding a column later

Just add the field to the model class and run `makemigrations` + `migrate` again.
Django detects the change and generates only the diff.

---

## How to Build CRUD Actions

### Create (POST form → save to database)

**Template** — a form that POSTs to the same URL:
```html
<form method="post" action="{% url 'clients' %}">
    {% csrf_token %}
    <input type="text" name="name" required>
    <input type="text" name="tax_id" required>
    <button type="submit">Save</button>
</form>
```

**View** — handle both GET (show form) and POST (save data):
```python
def clients(request):
    if request.method == 'POST':
        Client.objects.create(
            name   = request.POST.get('name'),
            tax_id = request.POST.get('tax_id'),
            city   = request.POST.get('city'),
        )
        return redirect('clients')   # Reload after saving

    all_clients = Client.objects.all()
    return render(request, 'clients.html', {'clients': all_clients})
```

---

### Read (query the database)

```python
# All records
Client.objects.all()

# Filter by a field
Client.objects.filter(status='active')

# Filter by multiple fields
Client.objects.filter(status='active', city='Bogotá')

# Get one record (raises 404 if not found)
client = get_object_or_404(Client, pk=pk)

# Order results
Client.objects.all().order_by('name')        # A → Z
Client.objects.all().order_by('-created_at') # Newest first

# Search (case-insensitive contains)
Client.objects.filter(name__icontains=search_term)
```

---

### Update (load existing record, save changes)

**URL:**
```python
path('clients/<int:pk>/edit/', views.client_edit, name='client_edit'),
```

**View:**
```python
def client_edit(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        client.name   = request.POST.get('name')
        client.tax_id = request.POST.get('tax_id')
        client.save()
        return redirect('clients')
    return render(request, 'clients.html', {'clients': Client.objects.all(), 'edit': client})
```

---

### Delete (confirm with POST, then delete)

**URL:**
```python
path('clients/<int:pk>/delete/', views.client_delete, name='client_delete'),
```

**View:**
```python
def client_delete(request, pk):
    if request.method == 'POST':
        client = get_object_or_404(Client, pk=pk)
        client.delete()
    return redirect('clients')
```

**Template** — always use POST for deletions (never a plain link):
```html
<form method="post" action="{% url 'client_delete' client.pk %}">
    {% csrf_token %}
    <button type="submit">Confirm Delete</button>
</form>
```

---

## URL Reference

| URL                   | View              | Description                      |
|-----------------------|-------------------|----------------------------------|
| `/`                   | `home`            | Dashboard                        |
| `/login/`             | `login_view`      | Login page                       |
| `/logout/`            | `logout_view`     | Logout                           |
| `/users/`             | `users`           | User list                        |
| `/users/<pk>/edit/`   | `user_edit`       | Edit a user                      |
| `/users/<pk>/delete/` | `user_delete`     | Delete a user                    |
| `/clients/`           | `clients`         | Client list                      |
| `/tax-returns/`       | `tax_returns`     | All tax returns                  |
| `/my-returns/`        | `my_returns`      | Returns assigned to current user |
| `/planning/`          | `planning`        | Planning tasks (filterable)      |
| `/configuration/`     | `configuration`   | Configuration tables             |
| `/admin/`             | Django Admin      | Built-in admin panel             |
