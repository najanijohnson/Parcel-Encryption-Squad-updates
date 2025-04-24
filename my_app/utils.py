import random
import string
import datetime

# Set to store valid test pickup codes for customers
test_pickup_codes = set()

# Generates a random alphanumeric code of specified length
def generate_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# Generates and stores a test pickup code specifically for customer testing
def generate_test_pickup_code():
    code = generate_code(8)
    test_pickup_codes.add(code)
    return code

# Validates a customer's entered pickup code against the correct one
def validate_test_pickup_code(entered_code, correct_code):
    return entered_code.strip() == correct_code.strip()

# Returns a static list of 25 fictional/local business names
def get_local_businesses():
    businesses = [
        "McDonald's", "Walmart", "Target", "Starbucks", "Subway",
        "Panda Express", "Dollar Tree", "Kroger", "Best Buy", "Home Depot",
        "Joe's Pizza", "Sunny's Chinese Takeout", "QuickMart", "Green Grocers",
        "Happy Donuts", "Big Al's Discount Store", "FreshMart", "Burger Barn",
        "Tech Haven", "Books & More", "The Coffee Spot", "Taco Fiesta",
        "Urban Outfitters", "Gadget Galaxy", "The Local Deli"
    ]
    return businesses

# Randomly selects `count` businesses and assigns each a fake distance
def get_random_businesses_with_distances(businesses, count=10):
    selected = random.sample(businesses, count)
    return [f"{business} [{random.uniform(0.5, 10):.1f} miles away]" for business in selected]

# Returns the HTML content for the business contract used during signup
def get_fake_contract_text():
    return """
    <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 16px;">
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
    </div>
    """


# Simple validation for email format — checks for presence of '@', '.', and minimum length
def is_valid_email(email):
    email = email.strip()
    return "@" in email and "." in email and len(email) >= 5

# In-memory database for storing packages in 3 states: on the way, ready, and picked up
package_db = {
    "on_the_way": [],
    "ready_for_pickup": [],
    "picked_up": []
}

# Sample name pairs used to generate mock package data
sample_names = [
    ("Amari", "Thompson"), ("Jordan", "Nguyen"), ("Morgan", "Lee"),
    ("Skyler", "Diaz"), ("Devon", "Taylor"), ("Riley", "Carter"),
    ("Sasha", "Green"), ("Casey", "Brooks"), ("Avery", "Kim"),
    ("Blake", "Martinez"), ("Quinn", "Rivera"), ("Elliot", "Singh"),
    ("Peyton", "Walker"), ("Jamie", "Robinson"), ("Cameron", "Shah"),
    ("Kai", "Anderson"), ("Emery", "Nguyen"), ("Logan", "Brown"),
    ("Phoenix", "Sullivan"), ("Rowan", "Jackson"), ("Reese", "Johnson"),
    ("Alex", "Lopez"), ("Sage", "Thompson"), ("Charlie", "Bennett"),
    ("Tatum", "King"), ("Noel", "Foster"), ("Kendall", "Young"),
    ("Jules", "Wright"), ("Ari", "Ramirez"), ("Jaden", "Morgan")
]

# Creates a dictionary representing a fake package with random attributes
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

# Populates the package database with 6 mock packages in each status bucket
def initialize_mock_packages():
    for _ in range(6):
        package_db["on_the_way"].append(generate_mock_package())
    for _ in range(6):
        p = generate_mock_package()
        p["status"] = "ready_for_pickup"
        package_db["ready_for_pickup"].append(p)
    for _ in range(6):
        p = generate_mock_package()
        p["status"] = "picked_up"
        p["timestamp"] = datetime.datetime.now().strftime("%I:%M %p")
        package_db["picked_up"].append(p)

# Moves a package from one state list to another based on tracking ID
def move_package(tracking_id, from_state, to_state):
    for pkg in package_db[from_state]:
        if pkg["tracking_id"] == tracking_id:
            package_db[from_state].remove(pkg)
            pkg["status"] = to_state
            pkg["timestamp"] = datetime.datetime.now().strftime("%I:%M %p")
            package_db[to_state].append(pkg)
            return True
    return False

# Searches for a package across all states by name or tracking ID
def search_package(query):
    results = []
    query = query.lower().strip()
    for state in package_db:
        for pkg in package_db[state]:
            if query in pkg["tracking_id"].lower() or query in pkg["name"].lower():
                results.append(pkg)
    return results
