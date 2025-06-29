#!/usr/bin/env python3
"""
Run the Evolution Lab Realtime Dashboard
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.evolution_lab.dashboard_demo import main

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║            🧬 BioCode Evolution Lab Dashboard 🧬             ║
    ╠══════════════════════════════════════════════════════════════╣
    ║                                                              ║
    ║  This will start:                                            ║
    ║  • WebSocket server on ws://localhost:8765                   ║
    ║  • Dashboard UI on http://localhost:8080                     ║
    ║                                                              ║
    ║  The dashboard will:                                         ║
    ║  • Analyze Ear-segmentation-ai project                       ║
    ║  • Update metrics every 5 seconds                            ║
    ║  • Show 6 different analyzers in action                      ║
    ║  • Display real-time health scores                           ║
    ║                                                              ║
    ║  Press Ctrl+C to stop                                        ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    try:
        import websockets
        import aiohttp
        import aiohttp_cors
    except ImportError:
        print("\n❌ Missing required packages!")
        print("Please install with:")
        print("  pip install websockets aiohttp aiohttp-cors")
        print("\nOr install all dashboard dependencies:")
        print("  pip install -e '.[dashboard]'")
        sys.exit(1)
    
    asyncio.run(main())