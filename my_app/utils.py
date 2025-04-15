import random
import string

# In-memory database replacement for now
registered_businesses = {}
packages = {}
test_pickup_codes = set()

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

def generate_test_pickup_code():
    code = generate_code(8)
    test_pickup_codes.add(code)
    return code

def validate_test_pickup_code(entered_code, correct_code):
    return entered_code == correct_code

def get_local_businesses():
    """Returns a list of 25 local businesses."""
    businesses = [
        "McDonald's", "Walmart", "Target", "Starbucks", "Subway",
        "Panda Express", "Dollar Tree", "Kroger", "Best Buy", "Home Depot",
        "Joe's Pizza", "Sunny's Chinese Takeout", "QuickMart", "Green Grocers",
        "Happy Donuts", "Big Al's Discount Store", "FreshMart", "Burger Barn",
        "Tech Haven", "Books & More", "The Coffee Spot", "Taco Fiesta",
        "Urban Outfitters", "Gadget Galaxy", "The Local Deli"
    ]
    return businesses

def get_random_businesses_with_distances(businesses, count=10):
    """Randomly selects businesses and assigns random distances."""
    selected = random.sample(businesses, count)
    return [f"{business} [{random.uniform(0.5, 10):.1f} miles away]" for business in selected]