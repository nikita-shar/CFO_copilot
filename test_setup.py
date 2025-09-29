#!/usr/bin/env python3
"""
Simple test script to verify your setup before running the full app.
"""

import os
import sys

print("=" * 60)
print("CFO AI Assistant - Setup Test")
print("=" * 60)

# Test 1: Check Python version
print("\n1. Checking Python version...")
version = sys.version_info
if version.major >= 3 and version.minor >= 8:
    print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} (OK)")
else:
    print(f"   ❌ Python {version.major}.{version.minor} (Need 3.8+)")
    sys.exit(1)

# Test 2: Check if agent/__init__.py exists
print("\n2. Checking agent/__init__.py...")
if os.path.exists("agent/__init__.py"):
    print("   ✅ agent/__init__.py exists")
else:
    print("   ❌ agent/__init__.py missing")
    print("   Fix: touch agent/__init__.py")
    sys.exit(1)

# Test 3: Check required files
print("\n3. Checking required files...")
required_files = [
    "openai_cfo_agent.py",
    "streamlit_app.py",
    "agent/cfo_functions.py",
    "agent/data_loader.py"
]

all_files_exist = True
for file in required_files:
    if os.path.exists(file):
        print(f"   ✅ {file}")
    else:
        print(f"   ❌ {file} missing")
        all_files_exist = False

if not all_files_exist:
    print("\n   Some files are missing!")
    sys.exit(1)

# Test 4: Check API key
print("\n4. Checking OPENAI_API_KEY...")
api_key = os.getenv('OPENAI_API_KEY')
if api_key:
    # Mask the key for security
    masked = api_key[:10] + "..." + api_key[-4:] if len(api_key) > 14 else "***"
    print(f"   ✅ API key found: {masked}")
else:
    print("   ❌ OPENAI_API_KEY not set")
    print("   Fix: export OPENAI_API_KEY='sk-proj-...'")
    sys.exit(1)

# Test 5: Check if openai package is installed
print("\n5. Checking dependencies...")
try:
    import openai
    print(f"   ✅ openai package installed (v{openai.__version__})")
except ImportError:
    print("   ❌ openai package not installed")
    print("   Fix: pip install -r requirements.txt")
    sys.exit(1)

try:
    import streamlit
    print(f"   ✅ streamlit package installed (v{streamlit.__version__})")
except ImportError:
    print("   ❌ streamlit package not installed")
    print("   Fix: pip install -r requirements.txt")
    sys.exit(1)

try:
    import plotly
    print(f"   ✅ plotly package installed (v{plotly.__version__})")
except ImportError:
    print("   ❌ plotly package not installed")
    print("   Fix: pip install -r requirements.txt")
    sys.exit(1)

# Test 6: Check if import works
print("\n6. Testing imports...")
try:
    from openai_cfo_agent import OpenAICFOAgent
    print("   ✅ OpenAICFOAgent import successful")
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

# Test 7: Check if data loader works
print("\n7. Testing data loader...")
try:
    from agent.data_loader import load_data
    print("   ✅ data_loader import successful")
    
    # Try to load data
    actuals, budget, cash, fx = load_data()
    print(f"   ✅ Data loaded: {len(actuals)} actuals, {len(budget)} budget records")
except Exception as e:
    print(f"   ❌ Data loading failed: {e}")
    print("   This might be OK if you haven't set up data files yet")

# Test 8: Initialize agent (without calling API)
print("\n8. Testing agent initialization...")
try:
    from openai_cfo_agent import OpenAICFOAgent
    agent = OpenAICFOAgent(api_key)
    print("   ✅ Agent initialized successfully")
    print(f"   ✅ Current year: {agent.current_year}")
    print(f"   ✅ Current month: {agent.current_month}")
    print(f"   ✅ Available tools: {len(agent.tools)}")
except Exception as e:
    print(f"   ❌ Agent initialization failed: {e}")
    sys.exit(1)

# Success!
print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print("\nYou're ready to run the app:")
print("  streamlit run streamlit_app.py")
print("\nOr test with a real query:")
print("  python test_agent_query.py")
print("=" * 60)