import random
import string

# In-memory database replacement for now
registered_businesses = {}
packages = {}

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def register_business(name, address):
    if not name or not address:
        return "Error: Business name and address required."
    code = generate_code()
    registered_businesses[code] = {"name": name, "address": address}
    return f"Registered '{name}' with code: {code}"

def notify_dropoff(tracking, business_code, recipient):
    if business_code not in registered_businesses:
        return "Error: Business location code not recognized."
    if not tracking or not recipient:
        return "Error: Tracking number and recipient name are required."
    
    pickup_code = generate_code(8)
    packages[pickup_code] = {
        "tracking": tracking,
        "recipient": recipient,
        "business_code": business_code,
        "picked_up": False
    }
    return f"Drop-off recorded. Pickup Code for recipient: {pickup_code}"

def verify_pickup(pickup_code):
    package = packages.get(pickup_code)
    if not package:
        return "Error: Invalid pickup code."
    if package["picked_up"]:
        return "This package has already been picked up."
    
    package["picked_up"] = True
    return f"Pickup verified for {package['recipient']} (Tracking: {package['tracking']})."
