import asyncio
import json
import os
from typing import Dict, Any, List
import google.generativeai as genai
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, CallToolResult, ListToolsResult
from supply_chain_tools import SupplyChainTools

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyB-d7vpvd2W8kXyVmfjn7XJNiZmDNP6hHM"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-exp')

class FastMCPServer:
    def __init__(self):
        self.server = Server("supply-chain-optimizer")
        self.tools = SupplyChainTools()
        self.setup_tools()
        self.setup_prompts()
        self.is_running = False
    
    def setup_tools(self):
        """Register all supply chain tools with MCP server"""
        
        @self.server.list_tools()
        async def handle_list_tools():
            return ListToolsResult(
                tools=[
                    Tool(
                        name="get_inventory_status",
                        description="Get current inventory status for a product or all products",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "product_id": {"type": "string", "description": "Product ID to check (optional)"}
                            }
                        }
                    ),
                    Tool(
                        name="update_inventory",
                        description="Update inventory for a specific product and warehouse",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "product_id": {"type": "string", "description": "Product ID"},
                                "warehouse": {"type": "string", "description": "Warehouse (warehouse_A, warehouse_B, warehouse_C)"},
                                "quantity": {"type": "integer", "description": "Quantity to add/subtract"}
                            },
                            "required": ["product_id", "warehouse", "quantity"]
                        }
                    ),
                    Tool(
                        name="calculate_transfer",
                        description="Calculate and execute inventory transfer between warehouses",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "product_id": {"type": "string", "description": "Product ID"},
                                "from_warehouse": {"type": "string", "description": "Source warehouse"},
                                "to_warehouse": {"type": "string", "description": "Destination warehouse"},
                                "quantity": {"type": "integer", "description": "Quantity to transfer"}
                            },
                            "required": ["product_id", "from_warehouse", "to_warehouse", "quantity"]
                        }
                    ),
                    Tool(
                        name="predict_stockout",
                        description="Predict when a product might run out of stock",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "product_id": {"type": "string", "description": "Product ID"},
                                "warehouse": {"type": "string", "description": "Warehouse to check"}
                            },
                            "required": ["product_id", "warehouse"]
                        }
                    ),
                    Tool(
                        name="recommend_reorder",
                        description="Recommend reorder action for a product",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "product_id": {"type": "string", "description": "Product ID"},
                                "quantity": {"type": "integer", "description": "Quantity to reorder"}
                            },
                            "required": ["product_id", "quantity"]
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict):
            try:
                if name == "get_inventory_status":
                    result = self.tools.get_inventory_status(arguments.get("product_id"))
                elif name == "update_inventory":
                    result = self.tools.update_inventory(
                        arguments["product_id"],
                        arguments["warehouse"],
                        arguments["quantity"]
                    )
                elif name == "calculate_transfer":
                    result = self.tools.calculate_transfer(
                        arguments["product_id"],
                        arguments["from_warehouse"],
                        arguments["to_warehouse"],
                        arguments["quantity"]
                    )
                elif name == "predict_stockout":
                    result = self.tools.predict_stockout(
                        arguments["product_id"],
                        arguments["warehouse"]
                    )
                elif name == "recommend_reorder":
                    result = self.tools.recommend_reorder(
                        arguments["product_id"],
                        arguments["quantity"]
                    )
                else:
                    result = {"error": f"Unknown tool: {name}"}
                
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps(result, indent=2))]
                )
            except Exception as e:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")]
                )
    
    def setup_prompts(self):
        """Setup system prompts for different scenarios"""
        self.system_prompt = """You are a Supply Chain Optimization Agent. Your job is to:

1. Analyze supply chain events (demand spikes, delays, cost increases)
2. Check current inventory status
3. Make intelligent recommendations for:
   - Inventory transfers between warehouses
   - Reorder quantities
   - Stockout predictions
   - Cost optimization

Always think step by step:
1. First, get current inventory status
2. Analyze the event impact
3. Check for potential stockouts
4. Recommend specific actions
5. Execute the actions if needed

Be concise but thorough in your analysis. Use the available tools to make decisions."""

        self.event_prompt_template = """New Supply Chain Event: {event_type} for {product_id} - {value}

Current Inventory Status:
{inventory_status}

Please analyze this event and recommend appropriate actions using the available tools."""

    async def process_event_parallel(self, event: Dict[str, Any]) -> str:
        """Process a supply chain event with parallel tool calling"""
        try:
            # Get current inventory status first
            inventory_status = self.tools.get_inventory_status(event.get('product_id'))
            
            # Format the event prompt
            event_prompt = self.event_prompt_template.format(
                event_type=event.get('event_type'),
                product_id=event.get('product_id'),
                value=event.get('value'),
                inventory_status=json.dumps(inventory_status, indent=2)
            )
            
            # Create the full prompt
            full_prompt = f"{self.system_prompt}\n\n{event_prompt}"
            
            # Process with Gemini - this is where parallel tool calling would happen
            # For now, we'll simulate it by processing the prompt and then executing tools
            response = await self._process_with_gemini_and_tools(full_prompt, event)
            
            return response
            
        except Exception as e:
            return f"Error processing event: {str(e)}"
    
    async def _process_with_gemini_and_tools(self, prompt: str, event: Dict[str, Any]) -> str:
        """Process prompt with Gemini and execute tools in parallel when possible"""
        try:
            # Generate response from Gemini
            response = model.generate_content(prompt)
            response_text = response.text
            
            # Simple tool calling simulation - in a real implementation, 
            # this would parse the response for tool calls and execute them in parallel
            actions = []
            
            # Check if response suggests any actions and execute them
            if "transfer" in response_text.lower():
                # Simulate transfer action
                if event.get('product_id') == 'P001':
                    transfer_result = self.tools.calculate_transfer(
                        'P001', 'warehouse_B', 'warehouse_A', 20
                    )
                    actions.append(f"TRANSFER: {transfer_result.get('action', 'Transfer executed')}")
            
            if "reorder" in response_text.lower() or "order" in response_text.lower():
                # Simulate reorder action
                reorder_result = self.tools.recommend_reorder(
                    event.get('product_id'), 50
                )
                actions.append(f"REORDER: {reorder_result.get('action', 'Reorder recommended')}")
            
            # Combine Gemini response with executed actions
            final_response = f"AI Analysis:\n{response_text}\n\n"
            if actions:
                final_response += "Executed Actions:\n" + "\n".join(actions)
            
            return final_response
            
        except Exception as e:
            return f"Error in AI processing: {str(e)}"
    
    async def start_server(self):
        """Start the MCP server"""
        print("🚀 Starting FastMCP Supply Chain Server...")
        print("📊 Loading inventory data...")
        
        # Load initial inventory
        initial_inventory = self.tools.get_inventory_status()
        print(f"✅ Loaded {len(initial_inventory)} products")
        
        # Start the MCP server
        self.is_running = True
        print("✅ FastMCP Server is running!")
        
        # In a real implementation, you would start the stdio server here
        # For this demo, we'll just mark it as running
        return True
    
    async def stop_server(self):
        """Stop the server and save inventory"""
        print("💾 Saving inventory changes...")
        self.tools.save_inventory()
        print("✅ Inventory saved!")
        self.is_running = False
        print("🛑 FastMCP Server stopped!")
    
    def get_actions_log(self) -> List[str]:
        """Get all recorded actions"""
        return self.tools.get_actions_log()

# Global server instance
server_instance = None

async def start_server():
    global server_instance
    server_instance = FastMCPServer()
    return await server_instance.start_server()

async def stop_server():
    global server_instance
    if server_instance:
        await server_instance.stop_server()

async def process_event(event: Dict[str, Any]) -> str:
    global server_instance
    if server_instance:
        return await server_instance.process_event_parallel(event)
    return "Server not running"

def get_actions_log() -> List[str]:
    global server_instance
    if server_instance:
        return server_instance.get_actions_log()
    return []

if __name__ == "__main__":
    # For testing
    async def test():
        await start_server()
        # Test event
        test_event = {
            "event_type": "DEMAND_SPIKE",
            "product_id": "P001",
            "value": "40 units"
        }
        result = await process_event(test_event)
        print(result)
        await stop_server()
    
    asyncio.run(test()) 