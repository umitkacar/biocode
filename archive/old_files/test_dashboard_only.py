#!/usr/bin/env python3
"""
Test Dashboard without agents - just view reports
"""
import sys
import os
import webbrowser
import time

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from dashboard.biocode_dashboard import run_dashboard

print("""
🧬 BioCode Dashboard - Report Viewer Mode
========================================

Starting dashboard to view existing reports...
""")

# Open browser after delay
def open_browser():
    time.sleep(2)
    webbrowser.open('http://localhost:5000')
    print("\n✅ Dashboard opened in browser")
    print("📊 Go to 'View Reports' to see agent analysis results")

import threading
browser_thread = threading.Thread(target=open_browser)
browser_thread.daemon = True
browser_thread.start()

# Run dashboard
try:
    run_dashboard(host='127.0.0.1', port=5000, debug=False)
except KeyboardInterrupt:
    print("\n👋 Dashboard stopped")