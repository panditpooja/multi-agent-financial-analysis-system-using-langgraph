#!/usr/bin/env python
"""
Verification script to check if Django setup is correct.
"""
import os
import sys

def check_file_exists(filepath):
    """Check if a file exists."""
    if os.path.exists(filepath):
        print(f"✅ {filepath}")
        return True
    else:
        print(f"❌ {filepath} - NOT FOUND")
        return False

def check_import(module_name):
    """Check if a module can be imported."""
    try:
        __import__(module_name)
        print(f"✅ {module_name} - Import successful")
        return True
    except ImportError as e:
        print(f"❌ {module_name} - Import failed: {e}")
        return False

def main():
    print("🔍 Verifying Django Setup...\n")
    
    all_ok = True
    
    # Check required files
    print("📁 Checking required files:")
    files_to_check = [
        'agentic_ai_multi_gent_financial_analysis.py',
        'manage.py',
        'financial_ai/settings.py',
        'financial_ai/urls.py',
        'financial_ai/views.py',
        'templates/financial_ai/index.html',
        'requirements.txt'
    ]
    
    for filepath in files_to_check:
        if not check_file_exists(filepath):
            all_ok = False
    
    print("\n📦 Checking Python imports:")
    
    # Check Django
    if not check_import('django'):
        print("   💡 Run: pip install Django>=4.2.0")
        all_ok = False
    
    # Check other dependencies
    dependencies = [
        'langchain_openai',
        'langchain_tavily',
        'langchain_community',
        'langchain_experimental',
        'langgraph',
        'dotenv'
    ]
    
    for dep in dependencies:
        if not check_import(dep):
            print(f"   💡 Run: pip install -r requirements.txt")
            all_ok = False
    
    # Check core module
    print("\n🔧 Checking core module:")
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from agentic_ai_multi_gent_financial_analysis import process_query, build_graph
        print("✅ agentic_ai_multi_gent_financial_analysis - Import successful")
    except Exception as e:
        print(f"❌ agentic_ai_multi_gent_financial_analysis - Import failed: {e}")
        all_ok = False
    
    # Check environment variables
    print("\n🔐 Checking environment variables:")
    from dotenv import load_dotenv
    load_dotenv()
    
    env_vars = {
        'OPENROUTER_API_KEY': 'OpenRouter API key',
        'ALPHAVANTAGE_API_KEY': 'Alpha Vantage API key',
        'TAVILY_API_KEY': 'Tavily API key (optional)'
    }
    
    for var, desc in env_vars.items():
        value = os.getenv(var)
        if value:
            masked = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
            print(f"✅ {var}: {masked}")
        else:
            print(f"⚠️  {var}: NOT SET ({desc})")
            if var != 'TAVILY_API_KEY':
                all_ok = False
    
    print("\n" + "="*60)
    if all_ok:
        print("✅ All checks passed! You're ready to run the Django server.")
        print("\n🚀 Next steps:")
        print("   1. python manage.py migrate")
        print("   2. python manage.py runserver")
        print("   3. Open http://127.0.0.1:8000/ in your browser")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
    print("="*60)

if __name__ == "__main__":
    main()

