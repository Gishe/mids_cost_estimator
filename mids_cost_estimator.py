import json
import yaml
import os

def load_prices():
    """Load enhancement prices from prices.yaml file"""
    prices_file = "prices.yaml"
    
    if not os.path.exists(prices_file):
        print(f"Warning: {prices_file} not found. Using default prices.")
        return {}, {}
    
    try:
        with open(prices_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
            
        # Flatten the structured data into a simple enhancement -> price mapping
        flat_prices = {}
        enhancement_categories = {}  # Map enhancement names to their categories
        
        # Get defaults
        defaults = data.get('defaults', {})
        
        # Process each category
        for category, enhancements in data.items():
            if category == 'defaults':
                continue
                
            # Skip if enhancements is None or not a dict
            if not enhancements or not isinstance(enhancements, dict):
                continue
                
            default_price = defaults.get(category, 0.05)  # fallback to 0.05M
            
            for enhancement, price in enhancements.items():
                # Skip dummy entries
                if enhancement == 'dummy_entry':
                    continue
                    
                # If price is None or not set, use the default for this category
                if price is None:
                    flat_prices[enhancement] = default_price
                else:
                    flat_prices[enhancement] = price
                
                # Store the category for this enhancement
                enhancement_categories[enhancement] = category
        
        return flat_prices, enhancement_categories
        
    except Exception as e:
        print(f"Error loading {prices_file}: {e}")
        import traceback
        traceback.print_exc()
        return {}, {}

def load_mbd(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_enhancements(data):
    enhancements = []
    for power in data.get("PowerEntries", []):
        for slot in power.get("SlotEntries", []):
            enh = slot.get("Enhancement")
            if enh is not None:
                name = enh.get("Uid", "Unknown")
                level = enh.get("IoLevel", 50)
                enhancements.append((name, int(level)))
    return enhancements

def estimate_total_cost(enhancements, enhancement_costs):
    total_cost = 0
    breakdown = {}
    unknown_enhancements = set()
    
    for name, level in enhancements:
        # Convert millions to full inf amount
        base_cost_millions = enhancement_costs.get(name, 1.05)  # fallback estimate in millions
        base_cost = int(base_cost_millions * 1_000_000)  # convert to full inf amount
        total_cost += base_cost
        breakdown[name] = breakdown.get(name, 0) + base_cost
        
        if name not in enhancement_costs:
            unknown_enhancements.add(name)
    
    return total_cost, breakdown, unknown_enhancements

def format_millions(value):
    return f"{value/1_000_000:.2f}M"

def group_enhancements_by_category(breakdown, enhancement_categories, enhancement_costs):
    """Group enhancements by their categories and calculate totals per category"""
    grouped = {}
    category_totals = {}
    
    for name, cost in breakdown.items():
        category = enhancement_categories.get(name, "Unknown")
        
        if category not in grouped:
            grouped[category] = []
            category_totals[category] = 0
        
        # Calculate count using the millions value from YAML
        base_cost_millions = enhancement_costs.get(name, 1.05)
        base_cost_full = int(base_cost_millions * 1_000_000)
        count = cost // base_cost_full
        
        grouped[category].append((name, cost, count))
        category_totals[category] += cost
    
    return grouped, category_totals

def format_category_name(category):
    """Convert category name to a more readable format"""
    return category.replace('_', ' ').title()

def main(file_path):
    # Load prices from YAML file
    enhancement_costs, enhancement_categories = load_prices()
    
    data = load_mbd(file_path)
    enhancements = extract_enhancements(data)
    total, breakdown, unknown = estimate_total_cost(enhancements, enhancement_costs)

    print(f"\nBuild: {data.get('Name', 'Unnamed')}")
    print(f"Level: {data.get('Level', 'Unknown')}")
    print(f"Class: {data.get('Class', 'Unknown')}")
    print(f"Total Enhancements: {len(enhancements)}")
    
    print("\nEnhancement Cost Breakdown by Set:")
    print("=" * 60)
    
    # Group enhancements by category
    grouped, category_totals = group_enhancements_by_category(breakdown, enhancement_categories, enhancement_costs)
    
    # Sort categories by total cost (highest first)
    sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
    
    for category, category_total in sorted_categories:
        if category_total > 0:  # Only show categories with enhancements
            print(f"\n{format_category_name(category)}:")
            print("-" * 40)
            
            # Sort enhancements within category by name
            sorted_enhancements = sorted(grouped[category], key=lambda x: x[0])
            
            for name, cost, count in sorted_enhancements:
                print(f"  {name}: {format_millions(cost)} inf ({count}x)")
            
            print(f"  Category Total: {format_millions(category_total)} inf")
    
    print("\n" + "=" * 60)
    print(f"Total Estimated Cost: {format_millions(total)} inf")
    
    if unknown:
        print(f"\nUnknown Enhancements (using 1.05M estimate):")
        for name in sorted(unknown):
            print(f"  {name}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python mids_cost_estimator.py <path_to_build.mbd>")
    else:
        main(sys.argv[1])
