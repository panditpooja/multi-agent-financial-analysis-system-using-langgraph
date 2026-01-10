# Django Web Interface for Financial AI Multi-Agent System

A beautiful, modern Django web interface for the Multi-Agent Financial Analysis System.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Database

```bash
python manage.py migrate
```

### 3. Run the Server

```bash
python manage.py runserver
```

Or use the helper script:

```bash
python run_django_server.py
```

### 4. Open in Browser

Navigate to: `http://127.0.0.1:8000/`

## 📋 Features

- ✅ **Modern Chat Interface**: Beautiful, responsive UI
- ✅ **Real-time Query Processing**: Instant responses
- ✅ **Session Management**: Maintains conversation context
- ✅ **Error Handling**: Graceful error messages
- ✅ **Markdown Support**: Rich text formatting in responses

## 🎯 Usage Examples

Once the server is running, you can ask questions like:

- "What was the last closing stock price of AAPL?"
- "Summarize the latest news about Tesla's stock performance."
- "Draw a plot of the closing stock prices of AAPL over the last week."

## 📁 Project Structure

```
.
├── agentic_ai_multi_gent_financial_analysis.py  # Core multi-agent system
├── financial_ai/                                 # Django application
│   ├── settings.py                               # Django configuration
│   ├── urls.py                                  # URL routing
│   ├── views.py                                 # View handlers
│   └── ...
├── templates/                                    # HTML templates
│   └── financial_ai/
│       └── index.html                            # Main chat UI
├── manage.py                                     # Django management
└── requirements.txt                              # Dependencies
```

## ⚙️ Configuration

Make sure your `.env` file contains all required API keys:

```env
OPENROUTER_API_KEY=your_key_here
ALPHAVANTAGE_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
```

## 🔧 Troubleshooting

### Django Not Found
```bash
pip install Django>=4.2.0
```

### Database Errors
```bash
python manage.py migrate
```

### Import Errors
Make sure `agentic_ai_multi_gent_financial_analysis.py` is in the project root.

## 📚 Documentation

See `DJANGO_SETUP.md` for detailed setup instructions.

