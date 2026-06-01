def parse_market_hash_name(hash_name: str):
    """
    Parses a CS2 market hash name into components.
    Example: "★ AK-47 | Redline (Field-Tested)"
    Returns: (gun_name, skin, wear, is_stattrak)
    """
    is_stattrak = hash_name.startswith("★")
    
    # Remove the star if it exists for cleaner parsing
    clean_name = hash_name.replace("★ ", "").replace("★", "").strip()
    
    # Extract wear: everything inside the last set of parentheses
    wear = "Unknown"
    if "(" in clean_name and ")" in clean_name:
        wear = clean_name[clean_name.find("(")+1:clean_name.find(")")]
        # Remove the wear part from the name for gun/skin splitting
        clean_name = clean_name[:clean_name.find("(")].strip()
    
    # Split gun and skin
    if "|" in clean_name:
        parts = clean_name.split("|")
        gun_name = parts[0].strip()
        skin = parts[1].strip()
    else:
        gun_name = clean_name
        skin = "Default"
        
    return gun_name, skin, wear, is_stattrak
