import pandas as pd
import json
from typing import Dict, Any

class SupplyChainTools:
    def __init__(self, inventory_file: str = "data/inventory.csv"):
        self.inventory_file = inventory_file
        self.inventory_df = pd.read_csv(inventory_file)
        self.actions_log = []
    
    def get_inventory_status(self, product_id: str = None) -> Dict[str, Any]:
        """Get current inventory status for a product or all products"""
        if product_id:
            product_data = self.inventory_df[self.inventory_df['product_id'] == product_id]
            if product_data.empty:
                return {"error": f"Product {product_id} not found"}
            return product_data.to_dict('records')[0]
        else:
            return self.inventory_df.to_dict('records')
    
    def update_inventory(self, product_id: str, warehouse: str, quantity: int) -> Dict[str, Any]:
        """Update inventory for a specific product and warehouse"""
        if warehouse not in ['warehouse_A', 'warehouse_B', 'warehouse_C']:
            return {"error": f"Invalid warehouse: {warehouse}"}
        
        mask = self.inventory_df['product_id'] == product_id
        if not mask.any():
            return {"error": f"Product {product_id} not found"}
        
        current_qty = self.inventory_df.loc[mask, warehouse].iloc[0]
        new_qty = max(0, current_qty + quantity)  # Prevent negative inventory
        self.inventory_df.loc[mask, warehouse] = new_qty
        
        action = f"Updated {product_id} in {warehouse}: {current_qty} -> {new_qty}"
        self.actions_log.append(action)
        
        return {
            "success": True,
            "product_id": product_id,
            "warehouse": warehouse,
            "old_quantity": current_qty,
            "new_quantity": new_qty,
            "action": action
        }
    
    def calculate_transfer(self, product_id: str, from_warehouse: str, to_warehouse: str, quantity: int) -> Dict[str, Any]:
        """Calculate and execute inventory transfer between warehouses"""
        # First reduce from source warehouse
        result1 = self.update_inventory(product_id, from_warehouse, -quantity)
        if "error" in result1:
            return result1
        
        # Then add to destination warehouse
        result2 = self.update_inventory(product_id, to_warehouse, quantity)
        if "error" in result2:
            # Rollback if destination update fails
            self.update_inventory(product_id, from_warehouse, quantity)
            return result2
        
        action = f"TRANSFER: {quantity} units of {product_id} from {from_warehouse} to {to_warehouse}"
        self.actions_log.append(action)
        
        return {
            "success": True,
            "action": action,
            "from_warehouse": from_warehouse,
            "to_warehouse": to_warehouse,
            "quantity": quantity,
            "product_id": product_id
        }
    
    def predict_stockout(self, product_id: str, warehouse: str) -> Dict[str, Any]:
        """Simple prediction of when a product might run out of stock"""
        product_data = self.inventory_df[self.inventory_df['product_id'] == product_id]
        if product_data.empty:
            return {"error": f"Product {product_id} not found"}
        
        current_stock = product_data[warehouse].iloc[0]
        
        # Simple heuristic: if stock is low, predict stockout soon
        if current_stock <= 20:
            days_to_stockout = "1-2 days"
        elif current_stock <= 50:
            days_to_stockout = "3-5 days"
        elif current_stock <= 100:
            days_to_stockout = "1-2 weeks"
        else:
            days_to_stockout = "More than 2 weeks"
        
        return {
            "product_id": product_id,
            "warehouse": warehouse,
            "current_stock": current_stock,
            "predicted_stockout": days_to_stockout,
            "risk_level": "HIGH" if current_stock <= 20 else "MEDIUM" if current_stock <= 50 else "LOW"
        }
    
    def recommend_reorder(self, product_id: str, quantity: int) -> Dict[str, Any]:
        """Recommend reorder action for a product"""
        product_data = self.inventory_df[self.inventory_df['product_id'] == product_id]
        if product_data.empty:
            return {"error": f"Product {product_id} not found"}
        
        supplier = product_data['supplier'].iloc[0]
        cost_per_unit = product_data['cost_per_unit'].iloc[0]
        total_cost = quantity * cost_per_unit
        
        action = f"ORDER: {quantity} units of {product_id} from {supplier} at ${cost_per_unit}/unit (Total: ${total_cost:.2f})"
        self.actions_log.append(action)
        
        return {
            "success": True,
            "action": action,
            "product_id": product_id,
            "quantity": quantity,
            "supplier": supplier,
            "cost_per_unit": cost_per_unit,
            "total_cost": total_cost
        }
    
    def save_inventory(self):
        """Save current inventory state back to file"""
        self.inventory_df.to_csv(self.inventory_file, index=False)
    
    def get_actions_log(self):
        """Get all recorded actions"""
        return self.actions_log 