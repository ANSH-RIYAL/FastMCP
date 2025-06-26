# FastMCP Supply Chain Optimizer

A **custom implementation** of **FastMCP** (Model Context Protocol) for real-time supply chain optimization using Gemini AI. This project demonstrates low-latency, multi-tool orchestration inspired by Anthropic's internal FastMCP system.

## 🎯 What This Demonstrates

- **Custom FastMCP Implementation**: Multi-tool calling at every LLM processing step (not sequential)
- **Real-time Event Processing**: Stream of supply chain events with live AI responses
- **Intelligent Recommendations**: AI-powered inventory optimization with actionable insights
- **Live Web Interface**: Real-time monitoring and control with beautiful UI
- **Modular Tool Architecture**: Easy to extend and modify for different use cases

## 🔧 About FastMCP vs MCP

**FastMCP is not open source** - it's Anthropic's internal implementation. This project is a **minimal simulation** of FastMCP's key innovation:

### Core Difference: Parallel Tool Calling
- **Standard MCP**: Sequential alternating between 1 LLM call → 1 tool call → 1 LLM call
- **FastMCP**: Multiple tools called at every step of LLM processing
- **This Implementation**: Simulates FastMCP's approach with multiple tool execution per event

> *"FastMCP isn't open source, so I built a minimal simulation of a low-latency multi-tool orchestration stack inspired by it — showcasing how an LLM agent can respond to real-time supply chain updates with actionable suggestions via routed tools."*

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python3 flask_app.py
```

### 3. Open Browser

Navigate to `http://localhost:5000`

### 4. Alternative: Use Local LLM

For data privacy and internal tool usage, you can replace Gemini API with your own local LLM using [local-llm-api](https://github.com/ANSH-RIYAL/local-llm-api):

```bash
# Clone and setup local LLM API
git clone https://github.com/ANSH-RIYAL/local-llm-api.git
cd local-llm-api
./run_server.sh

# Modify fastmcp_server.py to use local API instead of Gemini
# Replace GEMINI_API_KEY with CUSTOM_API_URL = "http://localhost:8050"
```

## 🎮 How to Use

1. **Start FastMCP Server**: Click "Start FastMCP Server" to initialize the AI agent
2. **Start Event Stream**: Click "Start Event Stream" to begin processing supply chain events
3. **Monitor Results**: Watch the terminal output and action recommendations in real-time
4. **Stop When Done**: Use the stop buttons to gracefully shut down

## 🛠️ Tools Implemented

### Core Supply Chain Tools

#### 1. **get_inventory_status**
- **Purpose**: Check current inventory levels across all warehouses
- **Parameters**: `product_id` (optional)
- **Returns**: Complete inventory data for product or all products
- **Example**: `{"product_id": "P001"}` → Returns warehouse A/B/C stock levels

#### 2. **update_inventory**
- **Purpose**: Modify warehouse stock levels (add/subtract)
- **Parameters**: `product_id`, `warehouse`, `quantity`
- **Returns**: Success status and inventory change details
- **Example**: `{"product_id": "P001", "warehouse": "warehouse_A", "quantity": -10}`

#### 3. **calculate_transfer**
- **Purpose**: Move inventory between warehouses
- **Parameters**: `product_id`, `from_warehouse`, `to_warehouse`, `quantity`
- **Returns**: Transfer execution details and new inventory levels
- **Example**: `{"product_id": "P001", "from_warehouse": "warehouse_B", "to_warehouse": "warehouse_A", "quantity": 20}`

#### 4. **predict_stockout**
- **Purpose**: Forecast when products will run out of stock
- **Parameters**: `product_id`, `warehouse`
- **Returns**: Risk level and predicted stockout timeline
- **Example**: `{"product_id": "P001", "warehouse": "warehouse_A"}` → "HIGH risk, 1-2 days"

#### 5. **recommend_reorder**
- **Purpose**: Suggest reorder quantities and suppliers
- **Parameters**: `product_id`, `quantity`
- **Returns**: Order details with cost calculations
- **Example**: `{"product_id": "P001", "quantity": 50}` → "ORDER: 50 units from Supplier X at $5.50/unit"

### How to Modify Tools

#### Adding New Tools
1. **Add function to `supply_chain_tools.py`**:
```python
def new_tool_function(self, param1: str, param2: int) -> Dict[str, Any]:
    """Description of what this tool does"""
    # Implementation logic
    return {"success": True, "result": "tool output"}
```

2. **Register tool in `fastmcp_server.py`**:
```python
Tool(
    name="new_tool_function",
    description="Description of what this tool does",
    inputSchema={
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "Parameter 1"},
            "param2": {"type": "integer", "description": "Parameter 2"}
        },
        "required": ["param1", "param2"]
    }
)
```

3. **Add handler in `handle_call_tool`**:
```python
elif name == "new_tool_function":
    result = self.tools.new_tool_function(
        arguments["param1"],
        arguments["param2"]
    )
```

## 📊 What Happens

### Event Types Processed:
- **DEMAND_SPIKE**: Sudden increase in product demand
- **DELAY**: Supplier delivery delays  
- **COST_INCREASE**: Price changes from suppliers

### AI Actions:
- **Inventory Transfers**: Move stock between warehouses
- **Reorder Recommendations**: Suggest new orders with quantities
- **Stockout Predictions**: Forecast when products will run out
- **Cost Optimization**: Analyze supplier alternatives

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flask Web     │    │   Custom        │    │   Gemini AI     │
│   Interface     │◄──►│   FastMCP       │◄──►│   (or Local     │
│                 │    │   Server        │    │    LLM API)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   Event Stream  │    │   Supply Chain  │
│   (CSV Data)    │    │   Tools         │
└─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
FastMCP/
├── data/
│   ├── inventory.csv      # Product inventory data
│   └── events.csv         # Supply chain events stream
├── templates/
│   └── index.html         # Web interface
├── supply_chain_tools.py  # Core business logic
├── fastmcp_server.py      # Custom FastMCP implementation
├── flask_app.py          # Web server and API
├── test_demo.py          # Demo script
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🎯 Example Workflow

1. **Event**: `DEMAND_SPIKE for P001 - 40 units`
2. **Analysis**: AI checks current inventory across warehouses
3. **Prediction**: Identifies potential stockout risk
4. **Action**: Recommends transfer from warehouse B to A
5. **Execution**: Updates inventory and logs the action

### Sample Conversation Flow:
```
Event Stream → MCP Client: "DEMAND_SPIKE: P001, 40 units"
MCP Client → get_inventory_status: {"product_id": "P001"}
MCP Client → predict_stockout: {"product_id": "P001", "warehouse": "warehouse_A"}
MCP Client → calculate_transfer: {"product_id": "P001", "from_warehouse": "warehouse_B", "to_warehouse": "warehouse_A", "quantity": 20}
MCP Client → recommend_reorder: {"product_id": "P001", "quantity": 50}
MCP Client → User: "Transfer 20 units from B to A, reorder 50 units from Supplier X"
```

## 🔍 Monitoring

- **Terminal Output**: Real-time server logs and processing status
- **Action Log**: All AI recommendations and executed actions
- **Status Indicators**: Server and event stream status
- **Event Progress**: Current event being processed

## 🚀 Key Features

- **Real-time Processing**: Events processed as they arrive
- **Intelligent Recommendations**: AI-powered decision making
- **Live Updates**: Web interface updates in real-time
- **Simple Setup**: Minimal dependencies and configuration
- **Extensible**: Easy to add new tools and event types
- **Privacy Options**: Can use local LLM instead of cloud APIs

## 🎯 Use Cases

- **Supply Chain Optimization**: Real-time inventory management
- **Demand Forecasting**: AI-powered stock predictions
- **Cost Optimization**: Supplier and pricing analysis
- **Risk Management**: Stockout prevention and mitigation

## 🔄 Scenario Modifications

### 1. Real-Time Supply Chain Optimizer (Streaming Input + Live Agent Correction)

**Current Implementation**: ✅ **Partially Implemented**
- ✅ Streaming CSV events
- ✅ Real-time AI responses
- ✅ Basic inventory tools
- ❌ Fast correlation calculator
- ❌ Forecasting tool (ARIMA/exponential smoothing)
- ❌ Live agent correction

**What Can Be Added Soon**:
```python
# Add to supply_chain_tools.py
def calculate_correlation(self, product1: str, product2: str) -> Dict[str, Any]:
    """Calculate demand correlation between products"""
    # Implementation using pandas correlation

def forecast_demand(self, product_id: str, periods: int) -> Dict[str, Any]:
    """Forecast demand using simple exponential smoothing"""
    # Implementation using statsmodels

def recommend_reroute(self, from_supplier: str, to_supplier: str) -> Dict[str, Any]:
    """Recommend supply rerouting based on delays/costs"""
    # Implementation with cost analysis
```

**Example Conversation**:
```
Event: "SUPPLIER_DELAY: Supplier X, 3 days"
MCP Client: "Analyzing impact on P001, P002, P003..."
Tools Called: [get_inventory_status, calculate_correlation, forecast_demand, recommend_reroute]
Response: "Reroute P001 from Supplier X to Supplier Y. P002 and P003 show 0.8 correlation - adjust P002 orders accordingly."
```

### 2. Interactive Survey Analyzer (Multi-Agent & Multi-Tool)

**Modification Required**:
```python
# New tools in survey_tools.py
def extract_themes(self, responses: List[str]) -> Dict[str, Any]:
    """Extract common themes from survey responses"""

def compute_frequencies(self, data: pd.DataFrame) -> Dict[str, Any]:
    """Compute response frequencies and confidence intervals"""

def generate_summary_report(self, insights: Dict) -> Dict[str, Any]:
    """Generate client-facing summary reports"""
```

**Example Conversation**:
```
User: "Analyze 500 survey responses about Product X"
MCP Client: "Processing responses with multiple agents..."
Tools Called: [extract_themes, compute_frequencies, generate_summary_report]
Response: "Top themes: UI/UX (45%), Performance (32%), Price (23%). 78% satisfaction rate (±3% CI). Report generated."
```

### 3. Clinical Triage Assistant (Tool Selection with Tight Latency Loop)

**Modification Required**:
```python
# New tools in clinical_tools.py
def check_symptoms(self, symptoms: List[str]) -> Dict[str, Any]:
    """Check symptoms against medical database"""

def classify_risk(self, vitals: Dict) -> Dict[str, Any]:
    """Classify patient risk level"""

def score_triage_priority(self, risk: str, symptoms: List) -> Dict[str, Any]:
    """Score triage priority"""

def generate_doctor_note(self, patient_data: Dict) -> Dict[str, Any]:
    """Generate doctor notes"""
```

**Example Conversation**:
```
Patient Data: {"symptoms": ["chest pain", "shortness of breath"], "vitals": {"bp": "140/90"}}
MCP Client: "Analyzing patient data..."
Tools Called: [check_symptoms, classify_risk, score_triage_priority, generate_doctor_note]
Response: "HIGH RISK - Cardiac symptoms detected. Immediate triage required. Doctor note: 'Patient presents with chest pain and elevated BP...'"
```

### 4. E-Commerce Pricing Agent (Fast Feedback Loop)

**Modification Required**:
```python
# New tools in pricing_tools.py
def calculate_optimal_price(self, cost: float, margin: float, demand_factor: float) -> Dict[str, Any]:
    """Calculate optimal price using formula"""

def find_competitor_match(self, product_id: str) -> Dict[str, Any]:
    """Find nearest competitor product"""

def generate_markdown_explanation(self, price_change: Dict) -> Dict[str, Any]:
    """Generate markdown explanation for price changes"""
```

**Example Conversation**:
```
Event: "COMPETITOR_PRICE_CHANGE: Product X, $25.99 → $22.99"
MCP Client: "Analyzing competitive landscape..."
Tools Called: [find_competitor_match, calculate_optimal_price, generate_markdown_explanation]
Response: "Competitor reduced price by 12%. Recommended action: Reduce price to $23.99. Explanation: 'We've adjusted our pricing to remain competitive while maintaining healthy margins...'"
```

## 🔧 Development

### Adding New Tools
1. Add function to `supply_chain_tools.py`
2. Register tool in `fastmcp_server.py`
3. Update system prompts as needed

### Adding New Event Types
1. Add event to `data/events.csv`
2. Update event processing logic in `fastmcp_server.py`
3. Test with the web interface

### Switching to Local LLM
1. Set up [local-llm-api](https://github.com/ANSH-RIYAL/local-llm-api)
2. Modify `fastmcp_server.py` to use local API endpoint
3. Update prompts for local model compatibility

## 📝 Notes

- This is a **demonstration** using simulated data
- Inventory changes are saved back to CSV on server stop
- Uses Gemini API free tier (rate limits apply)
- Designed for simplicity and educational purposes
- **FastMCP is not open source** - this is a custom implementation
- Can be extended with local LLM for data privacy

## 🤝 Contributing

Feel free to extend this with:
- More sophisticated AI models
- Real database integration
- Additional supply chain tools
- Enhanced web interface features
- Parallel tool execution optimization
- Real-time data streaming

## 🔗 Related Projects

- **[local-llm-api](https://github.com/ANSH-RIYAL/local-llm-api)**: Local LLM API for data privacy
- **[MCP-RAG](https://github.com/ANSH-RIYAL/MCP-RAG)**: Reference MCP implementation

---

**Ready to optimize your supply chain with AI?** Start the server and watch the magic happen! 🚀

*This project demonstrates how to build a custom FastMCP-like system for real-time, multi-tool AI orchestration.* 