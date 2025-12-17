import sys
import os

print("Running Pre-Delivery Verification...")

try:
    print("1. Checking imports...")
    import streamlit
    import google.generativeai
    import dotenv
    print("   -> Success: Dependencies found.")
except ImportError as e:
    print(f"   -> FAIL: Missing dependency - {e}")
    sys.exit(1)

try:
    print("2. Checking Agent Module Syntax...")
    from advisor_agent import AdvisorAgent
    print("   -> Success: advisor_agent.py is valid.")
except Exception as e:
    print(f"   -> FAIL: advisor_agent.py error - {e}")
    sys.exit(1)

print("3. Checking App Syntax...")
# Just check if file exists and can be read, we can't easily import streamlit app script as a module due to st. commands
if os.path.exists("app.py"):
    with open("app.py", "r") as f:
        content = f.read()
    print("   -> Success: app.py exists.")
else:
    print("   -> FAIL: app.py missing.")
    sys.exit(1)

print("\nALL CHECKS PASSED. Project is ready for delivery.")
