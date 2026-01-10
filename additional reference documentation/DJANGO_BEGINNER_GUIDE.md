# Django Beginner's Guide - Where to Start

If you're new to Django, here's the **order** to read and understand the files:

## 🎯 Start Here (Essential Files)

### 1. **`manage.py`** ⭐ START HERE
**Why first?** This is Django's command-line utility - you'll use it constantly.

**What it does:**
- Runs the development server: `python manage.py runserver`
- Creates database tables: `python manage.py migrate`
- Creates admin users: `python manage.py createsuperuser`

**Key concept:** This file tells Django where your settings are located.

---

### 2. **`financial_ai/settings.py`** ⭐ VERY IMPORTANT
**Why second?** This is Django's configuration file - the "brain" of your app.

**What to look for:**
- `INSTALLED_APPS`: Lists all Django apps (including yours: `'financial_ai'`)
- `DATABASES`: Database configuration (SQLite by default)
- `TEMPLATES`: Where Django looks for HTML templates
- `STATIC_URL`: Where static files (CSS, JS) are served from

**Key concept:** This file configures how Django behaves.

---

### 3. **`financial_ai/urls.py`** ⭐ VERY IMPORTANT
**Why third?** This maps URLs to views (like a router).

**What it does:**
```python
path('', views.index, name='index')  # Homepage → index view
path('query/', views.process_query)   # /query/ → process_query view
path('metrics/', views.metrics_dashboard)  # /metrics/ → metrics_dashboard view
```

**Key concept:** 
- When user visits `/metrics/`, Django calls `views.metrics_dashboard()`
- URL patterns are checked in order (first match wins)

**Read this to understand:** How URLs connect to functions.

---

### 4. **`financial_ai/views.py`** ⭐ VERY IMPORTANT
**Why fourth?** This contains the actual logic that handles requests.

**What it does:**
- `index()`: Renders the chat interface HTML
- `process_query()`: Handles AJAX requests, processes queries
- `metrics_dashboard()`: Shows metrics in HTML
- `metrics_json()`: Returns metrics as JSON

**Key concept:**
- Views are Python functions that receive HTTP requests
- They return HTTP responses (HTML, JSON, etc.)

**Read this to understand:** What happens when a user makes a request.

---

### 5. **`templates/financial_ai/index.html`** ⭐ IMPORTANT
**Why fifth?** This is the HTML that users see in their browser.

**What it does:**
- Creates the chat interface UI
- Handles user input via JavaScript
- Sends AJAX requests to `/query/`
- Displays responses

**Key concept:** 
- Templates are HTML files with Django template syntax
- `{{ variable }}` displays variables
- `{% tag %}` executes template tags

**Read this to understand:** The user-facing interface.

---

## 📚 Next Steps (Understanding the Flow)

### 6. **`agentic_ai_multi_gent_financial_analysis.py`**
**What it does:** Contains the core multi-agent system logic (converted from notebook).

**Key functions:**
- `build_graph()`: Creates the LangGraph workflow
- `process_query()`: Processes a financial query

**Read this to understand:** How the AI system works behind the scenes.

---

### 7. **`templates/financial_ai/metrics.html`**
**What it does:** The metrics dashboard HTML template.

**Read this to understand:** How metrics are displayed.

---

## 🔄 How It All Works Together

Here's the **request flow** when a user asks a question:

```
1. User types query in browser
   ↓
2. JavaScript sends POST to /query/
   ↓
3. Django urls.py routes to views.process_query()
   ↓
4. views.py calls agentic_ai_multi_gent_financial_analysis.process_query()
   ↓
5. Multi-agent system processes query
   ↓
6. views.py returns JSON response
   ↓
7. JavaScript displays response in browser
```

## 📖 Reading Order Summary

**For absolute beginners, read in this order:**

1. ✅ **`manage.py`** - Understand how to run Django
2. ✅ **`financial_ai/settings.py`** - Understand configuration
3. ✅ **`financial_ai/urls.py`** - Understand URL routing
4. ✅ **`financial_ai/views.py`** - Understand request handling
5. ✅ **`templates/financial_ai/index.html`** - Understand the UI
6. ✅ **`agentic_ai_multi_gent_financial_analysis.py`** - Understand the AI system

## 🎓 Key Django Concepts (Quick Reference)

### URL → View → Template Pattern

```
URL (urls.py) → View (views.py) → Template (templates/)
```

**Example:**
- URL: `/metrics/`
- View: `metrics_dashboard(request)`
- Template: `templates/financial_ai/metrics.html`

### Request/Response Cycle

1. **Request**: User visits URL or sends data
2. **URL Routing**: `urls.py` finds matching pattern
3. **View Processing**: `views.py` function handles request
4. **Response**: View returns HTML, JSON, or redirect

### Template Variables

In templates, you can use:
- `{{ variable }}` - Display a variable
- `{% if condition %}` - Conditional logic
- `{% for item in list %}` - Loops

## 🚀 Quick Start Commands

Once you understand the files, use these commands:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create database tables
python manage.py migrate

# 3. Run the server
python manage.py runserver

# 4. Open browser
# Navigate to: http://127.0.0.1:8000/
```

## 💡 Pro Tips

1. **Start with `manage.py`** - It's the entry point
2. **Follow a request** - Pick a URL and trace it through urls.py → views.py → template
3. **Use Django's error pages** - They're very helpful for debugging
4. **Check the terminal** - Django prints useful debug information

## 🔍 File Purpose Quick Reference

| File | Purpose | When to Read |
|------|---------|--------------|
| `manage.py` | Django CLI tool | First - understand commands |
| `settings.py` | Configuration | Second - understand setup |
| `urls.py` | URL routing | Third - understand navigation |
| `views.py` | Request handlers | Fourth - understand logic |
| `index.html` | User interface | Fifth - understand UI |
| `metrics.html` | Metrics dashboard | Sixth - understand metrics UI |
| `wsgi.py` | Production server | Later - for deployment |
| `asgi.py` | Async server | Later - for async features |

## 📝 Next Steps After Reading

1. **Run the server**: `python manage.py runserver`
2. **Try the chat interface**: Ask a question
3. **View metrics**: Go to `/metrics/`
4. **Modify a view**: Change something in `views.py` and see what happens
5. **Modify a template**: Change something in `index.html` and refresh

## 🎯 Recommended Learning Path

1. **Day 1**: Read `manage.py`, `settings.py`, `urls.py`
2. **Day 2**: Read `views.py`, understand request/response
3. **Day 3**: Read `index.html`, understand templates
4. **Day 4**: Modify something and see what happens!

## ❓ Common Questions

**Q: Where do I add new features?**
A: Add new URLs in `urls.py`, new views in `views.py`, new templates in `templates/`

**Q: How do I change the homepage?**
A: Modify `views.index()` in `views.py` or `templates/financial_ai/index.html`

**Q: How do I add a new page?**
A: 
1. Add URL in `urls.py`
2. Add view function in `views.py`
3. Create template in `templates/financial_ai/`

**Q: Where is the database?**
A: SQLite database is `db.sqlite3` (created after `python manage.py migrate`)

---

**Start with `manage.py` and `settings.py` - they're the foundation!** 🚀

