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

def get_fake_contract_text():
    return """
    <h3>Business Registration Agreement</h3>
    <p>
    By registering your business with the Parcel Encryption Squad platform, you agree to the following terms:
    </p>
    <ul>
        <li>You will ensure the security and privacy of all packages held at your business for retrieval.</li>
        <li>You will not tamper with, open, or remove any items from any packages entrusted to your location.</li>
        <li>You will promptly notify customers of drop-offs using the provided tools on this platform.</li>
        <li>You agree to allow platform administrators to conduct virtual or in-person audits if necessary.</li>
        <li>You will not share login credentials or sensitive customer information with unauthorized individuals.</li>
        <li>You acknowledge that violations of this agreement may result in account suspension or removal.</li>
    </ul>
    <p>
    Please review and check the agreement box below before proceeding with your business registration.
    </p>
    """
#new def validating email address
def is_valid_email(email):
    """Basic email validation."""
    if "@" not in email and "." not in email and len(email) < 5: #basic check for @ and . and length
        return False
    return True

# Mock data to simulate packages in different states
package_db = {
    "on_the_way": [],
    "ready_for_pickup": [],
    "picked_up": []
}

# Sample names for generation
sample_names = [
    ("Amari", "Thompson"), ("Jordan", "Nguyen"), ("Morgan", "Lee"),
    ("Skyler", "Diaz"), ("Devon", "Taylor"), ("Riley", "Carter")
]

def generate_mock_package():
    first, last = random.choice(sample_names)
    tracking_id = f"PKG{random.randint(100000, 999999)}"
    size = random.choice(["Small", "Medium", "Large"])
    weight = f"{random.uniform(0.5, 10):.1f} lbs"
    status = "on_the_way"
    timestamp = datetime.datetime.now()

    return {
        "name": f"{first} {last}",
        "tracking_id": tracking_id,
        "size": size,
        "weight": weight,
        "status": status,
        "timestamp": timestamp.strftime("%I:%M %p")
    }

# Initialize with random data
def initialize_mock_packages(n=5):
    for _ in range(n):
        package_db["on_the_way"].append(generate_mock_package())

# Move package between states
def move_package(tracking_id, from_state, to_state):
    for pkg in package_db[from_state]:
        if pkg["tracking_id"] == tracking_id:
            package_db[from_state].remove(pkg)
            pkg["status"] = to_state
            pkg["timestamp"] = datetime.datetime.now().strftime("%I:%M %p")
            package_db[to_state].append(pkg)
            return True
    return False

# Search package
def search_package(query):
    results = []
    for state in package_db:
        for pkg in package_db[state]:
            if query.lower() in pkg["tracking_id"].lower() or query.lower() in pkg["name"].lower():
                results.append(pkg)
    return results