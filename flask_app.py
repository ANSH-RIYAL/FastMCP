from flask import Flask, render_template, jsonify, request
import asyncio
import pandas as pd
import time
import threading
from fastmcp_server import start_server, stop_server, process_event, get_actions_log

app = Flask(__name__)

# Global variables
server_running = False
event_stream_running = False
current_event_index = 0
events_df = None

def load_events():
    """Load events from CSV file"""
    global events_df
    try:
        events_df = pd.read_csv('data/events.csv')
        print(f"✅ Loaded {len(events_df)} events")
        return True
    except Exception as e:
        print(f"❌ Error loading events: {e}")
        return False

@app.route('/')
def index():
    """Main HTML page"""
    return render_template('index.html')

@app.route('/api/start_server', methods=['POST'])
def api_start_server():
    """Start the FastMCP server"""
    global server_running
    
    if server_running:
        return jsonify({"status": "error", "message": "Server already running"})
    
    try:
        # Run async function in thread
        def run_start_server():
            asyncio.run(start_server())
        
        thread = threading.Thread(target=run_start_server)
        thread.start()
        thread.join(timeout=5)  # Wait up to 5 seconds
        
        server_running = True
        return jsonify({"status": "success", "message": "FastMCP Server started successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to start server: {str(e)}"})

@app.route('/api/stop_server', methods=['POST'])
def api_stop_server():
    """Stop the FastMCP server"""
    global server_running, event_stream_running
    
    if not server_running:
        return jsonify({"status": "error", "message": "Server not running"})
    
    try:
        # Stop event stream if running
        event_stream_running = False
        
        # Run async function in thread
        def run_stop_server():
            asyncio.run(stop_server())
        
        thread = threading.Thread(target=run_stop_server)
        thread.start()
        thread.join(timeout=5)  # Wait up to 5 seconds
        
        server_running = False
        return jsonify({"status": "success", "message": "FastMCP Server stopped successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to stop server: {str(e)}"})

@app.route('/api/start_event_stream', methods=['POST'])
def api_start_event_stream():
    """Start the event stream"""
    global event_stream_running, current_event_index, events_df
    
    if not server_running:
        return jsonify({"status": "error", "message": "Server must be running first"})
    
    if event_stream_running:
        return jsonify({"status": "error", "message": "Event stream already running"})
    
    # Load events if not loaded
    if events_df is None:
        if not load_events():
            return jsonify({"status": "error", "message": "Failed to load events"})
    
    event_stream_running = True
    current_event_index = 0
    
    # Start event stream in background thread
    def run_event_stream():
        global current_event_index, event_stream_running
        
        while event_stream_running and current_event_index < len(events_df):
            try:
                # Get current event
                event_row = events_df.iloc[current_event_index]
                event = {
                    "timestamp": event_row['timestamp'],
                    "event_type": event_row['event_type'],
                    "product_id": event_row['product_id'],
                    "value": event_row['value']
                }
                
                # Process event
                def run_process_event():
                    return asyncio.run(process_event(event))
                
                thread = threading.Thread(target=run_process_event)
                thread.start()
                thread.join(timeout=10)  # Wait up to 10 seconds for processing
                
                current_event_index += 1
                
                # Random delay between events (1-3 seconds)
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ Error processing event: {e}")
                current_event_index += 1
                time.sleep(1)
        
        event_stream_running = False
    
    thread = threading.Thread(target=run_event_stream)
    thread.daemon = True
    thread.start()
    
    return jsonify({"status": "success", "message": "Event stream started"})

@app.route('/api/stop_event_stream', methods=['POST'])
def api_stop_event_stream():
    """Stop the event stream"""
    global event_stream_running
    
    event_stream_running = False
    return jsonify({"status": "success", "message": "Event stream stopped"})

@app.route('/api/get_status', methods=['GET'])
def api_get_status():
    """Get current status"""
    global server_running, event_stream_running, current_event_index, events_df
    
    return jsonify({
        "server_running": server_running,
        "event_stream_running": event_stream_running,
        "current_event_index": current_event_index,
        "total_events": len(events_df) if events_df is not None else 0,
        "actions_log": get_actions_log()
    })

@app.route('/api/get_next_event', methods=['GET'])
def api_get_next_event():
    """Get the next event to be processed"""
    global current_event_index, events_df
    
    if events_df is None or current_event_index >= len(events_df):
        return jsonify({"status": "error", "message": "No more events"})
    
    event_row = events_df.iloc[current_event_index]
    event = {
        "timestamp": event_row['timestamp'],
        "event_type": event_row['event_type'],
        "product_id": event_row['product_id'],
        "value": event_row['value']
    }
    
    return jsonify({"status": "success", "event": event})

if __name__ == '__main__':
    # Load events on startup
    load_events()
    
    print("🌐 Starting Flask server...")
    print("📱 Open http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000) 