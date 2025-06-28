import random
from typing import List, Dict, Any, Optional, Tuple

INITIAL_DATA = [
    {
        "LAYOUT_ID": "LAY001",
        "SELL_ID": "SELL001",
        "PRODUCT_NAME": "Coles Brand Milk 2L",
        "LOYALTY_GROUP": "Core",
        "SEGMENT_1": "High Value",
        "SEGMENT_2": "Regular Shopper",
        "ORIGIN": "AU",
        "CATEGORY_NAME": "Dairy",
        "SUBCATEGORY_NAME": "Milk",
        "ITEM_CLASS_NAME": "Full Cream",
        "SUPPLIER": "Coles Dairy",
        "BRAND": "Coles",
        "PACK_SIZE": "2L",
        "SHELF_SPACE_CM": 12.5,  # 2L milk carton width
    },
    {
        "LAYOUT_ID": "LAY002",
        "SELL_ID": "SELL002",
        "PRODUCT_NAME": "Woolworths Bread White",
        "LOYALTY_GROUP": "Core",
        "SEGMENT_1": "Regular Shopper",
        "SEGMENT_2": "Family",
        "ORIGIN": "AU",
        "CATEGORY_NAME": "Bakery",
        "SUBCATEGORY_NAME": "Bread",
        "ITEM_CLASS_NAME": "White",
        "SUPPLIER": "Woolworths Bakery",
        "BRAND": "Woolworths",
        "PACK_SIZE": "650g",
        "SHELF_SPACE_CM": 15.0,  # Standard bread loaf width
    },
    {
        "LAYOUT_ID": "LAY003",
        "SELL_ID": "SELL003",
        "PRODUCT_NAME": "Arnott's Tim Tams",
        "LOYALTY_GROUP": "Premium",
        "SEGMENT_1": "High Value",
        "SEGMENT_2": "Regular Shopper",
        "ORIGIN": "AU",
        "CATEGORY_NAME": "Confectionery",
        "SUBCATEGORY_NAME": "Biscuits",
        "ITEM_CLASS_NAME": "Chocolate",
        "SUPPLIER": "Arnott's",
        "BRAND": "Arnott's",
        "PACK_SIZE": "200g",
        "SHELF_SPACE_CM": 8.5,  # Standard biscuit packet width
    },
    {
        "LAYOUT_ID": "LAY004",
        "SELL_ID": "SELL004",
        "PRODUCT_NAME": "Vegemite 380g",
        "LOYALTY_GROUP": "Core",
        "SEGMENT_1": "Family",
        "SEGMENT_2": "Regular Shopper",
        "ORIGIN": "AU",
        "CATEGORY_NAME": "Pantry",
        "SUBCATEGORY_NAME": "Spreads",
        "ITEM_CLASS_NAME": "Yeast Extract",
        "SUPPLIER": "Bega",
        "BRAND": "Vegemite",
        "PACK_SIZE": "380g",
        "SHELF_SPACE_CM": 7.0,  # Standard jar width
    },
    {
        "LAYOUT_ID": "LAY005",
        "SELL_ID": "SELL005",
        "PRODUCT_NAME": "Kangaroo Steak",
        "LOYALTY_GROUP": "Premium",
        "SEGMENT_1": "Health Conscious",
        "SEGMENT_2": "High Value",
        "ORIGIN": "AU",
        "CATEGORY_NAME": "Meat",
        "SUBCATEGORY_NAME": "Game",
        "ITEM_CLASS_NAME": "Steak",
        "SUPPLIER": "Macro Meats",
        "BRAND": "Macro",
        "PACK_SIZE": "500g",
        "SHELF_SPACE_CM": 18.0,  # Meat tray width
    },
    {
        "LAYOUT_ID": "LAY006",
        "SELL_ID": "SELL006",
        "PRODUCT_NAME": "Tim Tam Slam Kit",
        "LOYALTY_GROUP": "Premium",
        "SEGMENT_1": "Impulse Buyer",
        "SEGMENT_2": "High Value",
        "ORIGIN": "AU",
        "CATEGORY_NAME": "Confectionery",
        "SUBCATEGORY_NAME": "Biscuits",
        "ITEM_CLASS_NAME": "Gift Set",
        "SUPPLIER": "Arnott's",
        "BRAND": "Arnott's",
        "PACK_SIZE": "400g",
        "SHELF_SPACE_CM": 22.0,  # Gift set box width
    },
]


def generate_product_data(
    num_products: int = 3,
    categories: Optional[List[str]] = None,
    brands: Optional[List[str]] = None,
    suppliers: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Generate sample product data for testing and development.

    Args:
        num_products (int): Number of products to generate
        categories (list): List of possible category names
        brands (list): List of possible brand names
        suppliers (list): List of possible supplier names

    Returns:
        list: List of dictionaries containing product data
    """
    if categories is None:
        categories = ["Dairy", "Bakery", "Confectionery", "Skin Care"]
    if brands is None:
        brands = ["Coles", "Arnott's", "L'OREAL PARIS"]
    if suppliers is None:
        suppliers = ["Coles Dairy", "Arnott's", "L'Oréal"]

    # Shelf space ranges by category (in cm)
    shelf_space_ranges = {
        "Dairy": (8.0, 15.0),      # Milk cartons, yogurt tubs, cheese blocks
        "Bakery": (12.0, 18.0),    # Bread loaves, pastries, cakes
        "Confectionery": (6.0, 12.0),  # Chocolate bars, biscuits, candies
        "Skin Care": (4.0, 10.0),  # Small bottles, tubes, jars
        "Pantry": (6.0, 14.0),     # Cans, jars, packets
        "Meat": (15.0, 25.0),      # Meat trays, packages
        "Frozen": (10.0, 20.0),    # Frozen meals, ice cream
        "Beverages": (6.0, 12.0),  # Bottles, cans
        "Snacks": (8.0, 15.0),     # Chips, nuts, crackers
        "Household": (8.0, 20.0),  # Cleaning products, paper goods
    }

    products = []
    for i in range(num_products):
        category = random.choice(categories)
        pack_size_num = random.randint(1, 5)
        
        # Determine pack size unit based on category
        if category == "Dairy":
            pack_size_unit = "L" if random.choice([True, False]) else "g"
        elif category == "Beverages":
            pack_size_unit = "L" if random.choice([True, False]) else "ml"
        elif category == "Skin Care":
            pack_size_unit = "ml" if random.choice([True, False]) else "g"
        else:
            pack_size_unit = "g"
        
        pack_size = f"{pack_size_num}{pack_size_unit}"
        
        # Generate realistic shelf space based on category and pack size
        min_space, max_space = shelf_space_ranges.get(category, (6.0, 12.0))
        # Adjust based on pack size (larger packs = more shelf space)
        size_multiplier = 1.0 + (pack_size_num - 1) * 0.2
        shelf_space = round(random.uniform(min_space, max_space) * size_multiplier, 1)
        
        product = {
            "LAYOUT_ID": f"LAY{str(i+1).zfill(3)}",
            "SELL_ID": f"SELL{str(i+1).zfill(3)}",
            "PRODUCT_NAME": f"Sample Product {i+1}",
            "LOYALTY_GROUP": random.choice(["Core", "Premium", "Value"]),
            "SEGMENT_1": random.choice(["High Value", "Regular Shopper", "Family"]),
            "SEGMENT_2": random.choice(["Budget", "Premium", "Urban"]),
            "ORIGIN": "AU",
            "CATEGORY_NAME": category,
            "SUBCATEGORY_NAME": f"Subcategory {i+1}",
            "ITEM_CLASS_NAME": f"Item Class {i+1}",
            "SUPPLIER": random.choice(suppliers),
            "BRAND": random.choice(brands),
            "PACK_SIZE": pack_size,
            "SHELF_SPACE_CM": shelf_space,
        }
        products.append(product)

    return products
