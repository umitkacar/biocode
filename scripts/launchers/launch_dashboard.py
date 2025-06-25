#!/usr/bin/env python3
"""
Launch BioCode Agent Colony Dashboard
"""
import sys
import os
import argparse
import webbrowser
import time
import subprocess
from pathlib import Path

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def check_dependencies():
    """Check if required packages are installed"""
    required = ['flask', 'flask-socketio', 'flask-cors']
    missing = []
    
    for package in required:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"⚠️  Missing dependencies: {', '.join(missing)}")
        print("\nInstalling required packages...")
        
        # Install missing packages
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install'] + missing
        )
        print("✅ Dependencies installed successfully!\n")

def main():
    parser = argparse.ArgumentParser(description='BioCode Agent Colony Dashboard')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--no-browser', action='store_true', help='Do not open browser')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    parser.add_argument('--demo', action='store_true', help='Launch demo agents')
    
    args = parser.parse_args()
    
    print("""
    🧬 BioCode Agent Colony Dashboard
    =================================
    
    Living code monitoring and analytics
    """)
    
    # Check dependencies
    check_dependencies()
    
    # Import dashboard after dependencies are installed
    from dashboard.biocode_dashboard import run_dashboard
    
    # Launch demo agents if requested
    if args.demo:
        print("🔬 Launching demo agents...")
        from agent.biocode_agent import BioCodeAgent, AgentDNA
        
        # Create a demo agent
        demo_path = Path.home() / "CLAUDE_PROJECT" / "Code-Snippet"
        if demo_path.exists():
            dna = AgentDNA(
                agent_id="demo_dashboard",
                scan_frequency=10.0,
                lifespan=600,  # 10 minutes
                can_replicate=False,
                can_evolve=True
            )
            
            agent = BioCodeAgent(str(demo_path), dna, sandbox_mode=True)
            agent.start()
            print(f"✅ Demo agent launched: {dna.agent_id}")
        else:
            print("⚠️  Demo path not found, skipping demo agent")
    
    # Open browser after a short delay
    if not args.no_browser:
        def open_browser():
            time.sleep(2)  # Wait for server to start
            webbrowser.open(f'http://{args.host}:{args.port}')
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
    
    # Run dashboard
    try:
        run_dashboard(host=args.host, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard stopped. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()