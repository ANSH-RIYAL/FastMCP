#!/usr/bin/env python3
"""
Simple test script to demonstrate FastMCP Supply Chain Optimizer
"""

import asyncio
import json
from fastmcp_server import start_server, stop_server, process_event

async def test_demo():
    print("🧪 Testing FastMCP Supply Chain Optimizer")
    print("=" * 50)
    
    # Start server
    print("1. Starting FastMCP Server...")
    await start_server()
    print("✅ Server started successfully!")
    
    # Test events
    test_events = [
        {
            "event_type": "DEMAND_SPIKE",
            "product_id": "P001",
            "value": "40 units"
        },
        {
            "event_type": "DELAY",
            "product_id": "P002",
            "value": "2 days"
        },
        {
            "event_type": "COST_INCREASE",
            "product_id": "P003",
            "value": "8.50"
        }
    ]
    
    print("\n2. Processing test events...")
    for i, event in enumerate(test_events, 1):
        print(f"\n--- Event {i}: {event['event_type']} ---")
        print(f"Product: {event['product_id']}, Value: {event['value']}")
        
        result = await process_event(event)
        print(f"AI Response:\n{result}")
        print("-" * 40)
    
    # Stop server
    print("\n3. Stopping server...")
    await stop_server()
    print("✅ Server stopped successfully!")
    
    print("\n🎉 Demo completed! Open http://localhost:5000 for the web interface.")

if __name__ == "__main__":
    asyncio.run(test_demo()) 