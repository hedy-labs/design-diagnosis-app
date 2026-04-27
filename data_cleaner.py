"""
Data Cleaner — Convert internal keys to human-readable format

Converts system keys like 'face_cloths' to 'Face Cloths' for display in emails/PDFs.
"""

import logging

logger = logging.getLogger(__name__)


# Mapping of internal keys to human-readable names
ITEM_NAME_MAPPING = {
    # Tier 1 items
    'bedside_lamps': 'Bedside Lamps',
    'bedside_tables': 'Bedside Tables',
    'two_towels_per_guest': 'Two Towels Per Guest',
    'two_pillows_per_guest': 'Two Pillows Per Guest',
    'plunger': 'Plunger',
    'soap_dispenser': 'Soap Dispenser',
    'mattress_protectors': 'Mattress Protectors',
    
    # Tier 2 items
    'hangers': 'Hangers',
    'power_bars': 'Power Bars',
    'dish_drying_rack': 'Dish Drying Rack',
    'pillow_protectors': 'Pillow Protectors',
    
    # Tier 3 items
    'shower_hooks': 'Shower Hooks',
    'towel_hooks': 'Towel Hooks',
    'face_cloths': 'Face Cloths',
    'extra_blanket': 'Extra Blanket',
    'full_length_mirror': 'Full Length Mirror',
    'entry_hooks': 'Entry Hooks',
    'shoe_rack': 'Shoe Rack',
    'welcome_basket': 'Welcome Basket',
    'bathroom_caddy': 'Bathroom Caddy',
    'desk_chair': 'Desk Chair',
    'workspace': 'Workspace',
    'coffee_maker': 'Coffee Maker',
    'can_opener': 'Can Opener',
    'sofa_side_tables': 'Sofa Side Tables',
    'two_pillows': 'Two Pillows',
    'mattress_protector': 'Mattress Protector',
    'pillow_protector': 'Pillow Protector',
    'hot_water_in_bathroom': 'Hot Water in Bathroom',
    'top_sheet': 'Top Sheet',
    'drain_catcher': 'Drain Catcher',
    'squeegee': 'Squeegee',
    'sharp_knives': 'Sharp Knives',
    'scissors': 'Scissors',
    'peeler': 'Peeler',
    'potable_water': 'Potable Water',
    'laundry_supplies': 'Laundry Supplies',
    'extra_toilet_paper': 'Extra Toilet Paper',
    'guest_closet': 'Guest Closet',
}


def clean_item_name(item_key: str) -> str:
    """
    Convert internal item key to human-readable name.
    
    Args:
        item_key: Internal key (e.g., 'bedside_lamps')
    
    Returns: Human-readable name (e.g., 'Bedside Lamps')
    """
    return ITEM_NAME_MAPPING.get(item_key, item_key.replace('_', ' ').title())


def clean_recommendation_title(title: str) -> str:
    """
    Clean recommendation title by converting underscores to spaces.
    """
    return title.replace('_', ' ').title()


def clean_missing_items_list(missing_items: list) -> list:
    """
    Convert list of internal keys to human-readable names.
    
    Args:
        missing_items: List of internal keys
    
    Returns: List of human-readable names
    """
    return [clean_item_name(item) for item in missing_items]


def clean_comfort_checklist(checklist: list) -> list:
    """
    Clean comfort checklist items.
    """
    return [clean_item_name(item) for item in checklist]
