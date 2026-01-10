# Django Setup Guide for Financial AI Multi-Agent System

This guide will help you set up and run the Django web interface for the Financial AI Multi-Agent System.

## Prerequisites

- Python 3.8 or higher
- All API keys set in `.env` file (see main README.md)

## Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install Django along with all other required packages.

### 2. Set Up Django

Run the following commands to set up the Django database:

```bash
# Create database migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create a superuser (optional, for admin access)
python manage.py createsuperuser
```

### 3. Collect Static Files (if needed)

```bash
python manage.py collectstatic --noinput
```

### 4. Run the Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## Usage

1. Open your browser and navigate to `http://127.0.0.1:8000/`
2. You'll see a beautiful chat interface
3. Type your financial queries in the input field
4. Examples:
   - "What was the last closing stock price of AAPL?"
   - "Summarize the latest news about Tesla's stock performance."
   - "Draw a plot of the closing stock prices of AAPL over the last week."

## Features

- **Modern UI**: Beautiful, responsive chat interface
- **Real-time Processing**: Queries are processed in real-time
- **Session Management**: Maintains conversation context using thread IDs
- **Error Handling**: Graceful error messages for failed queries
- **Markdown Support**: Responses support markdown formatting

## Project Structure

```
.
├── agentic_ai_multi_gent_financial_analysis.py  # Core multi-agent system
├── financial_ai/                                 # Django app
│   ├── settings.py                               # Django settings
│   ├── urls.py                                  # URL routing
│   ├── views.py                                 # View handlers
│   ├── wsgi.py                                  # WSGI config
│   └── asgi.py                                  # ASGI config
├── templates/                                    # HTML templates
│   └── financial_ai/
│       ├── index.html                           # Main chat interface
│       └── history.html                         # Query history (placeholder)
├── manage.py                                     # Django management script
└── requirements.txt                              # Python dependencies
```

## Configuration

### Environment Variables

Make sure your `.env` file contains:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
ALPHAVANTAGE_API_KEY=your_alpha_vantage_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
DJANGO_SECRET_KEY=your-secret-key-here  # Optional, auto-generated if not set
DEBUG=True  # Set to False in production
```

### Django Settings

Key settings in `financial_ai/settings.py`:

- `DEBUG`: Set to `False` in production
- `ALLOWED_HOSTS`: Configure for your domain in production
- `SECRET_KEY`: Use a strong secret key in production

## Production Deployment

For production deployment:

1. Set `DEBUG = False` in settings
2. Configure `ALLOWED_HOSTS` with your domain
3. Set a strong `SECRET_KEY`
4. Use a production database (PostgreSQL recommended)
5. Set up proper static file serving
6. Use a production WSGI server (e.g., Gunicorn)
7. Set up reverse proxy (e.g., Nginx)

## Troubleshooting

### Import Errors

If you see import errors, make sure:
- All dependencies are installed: `pip install -r requirements.txt`
- The `agentic_ai_multi_gent_financial_analysis.py` file is in the project root
- Python path is set correctly

### CSRF Token Errors

The application uses Django's CSRF protection. The template includes CSRF token handling automatically.

### Session Issues

Sessions are stored in the database. Make sure migrations are applied:
```bash
python manage.py migrate
```

## API Endpoints

- `GET /` - Main chat interface
- `POST /query/` - Process a financial query (returns JSON)
- `GET /history/` - Query history (placeholder)

## Next Steps

- Add query history storage
- Implement user authentication
- Add metrics dashboard integration
- Add export functionality for responses

