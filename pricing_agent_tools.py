class PricingAgentTools:
    def calculate_optimal_price(self, cost: float, margin: float, demand_factor: float) -> dict:
        """
        Calculate optimal price using a simple formula.
        """
        price = round((cost + margin) * demand_factor, 2)
        return {'price': price}

    def find_competitor_match(self, product_id: str) -> dict:
        """
        Find nearest competitor product (simulated lookup).
        """
        # Dummy competitor price for demonstration
        competitor_prices = {'P001': 22.99, 'P002': 18.50, 'P003': 25.00}
        price = competitor_prices.get(product_id, 19.99)
        return {'competitor_price': price}

    def generate_markdown_explanation(self, price_change: dict) -> dict:
        """
        Generate markdown explanation for price changes.
        """
        old = price_change.get('old_price', 'N/A')
        new = price_change.get('new_price', 'N/A')
        reason = price_change.get('reason', 'market adjustment')
        markdown = f"**Price Update**\nOld Price: ${old}\nNew Price: ${new}\nReason: {reason}"
        return {'markdown': markdown} 