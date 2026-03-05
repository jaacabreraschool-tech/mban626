import csv
import random
from datetime import datetime, timedelta

# Headers matching your app
HEADERS = [
    "Ticket Number",
    "Name",
    "Priority",
    "Assigned To",
    "Product Purchased",
    "Date of Purchase",
    "Type",
    "Short Description",
    "Detailed Description",
]

# Sample data for random generation
FIRST_NAMES = ["John", "Jane", "Mike", "Sarah", "Tom", "Emily", "Robert", "Jessica", "James", "Lisa", "David", "Mary", "Richard", "Patricia", "Charles", "Jennifer", "Joseph", "Linda", "Thomas", "Barbara", "Christopher", "Susan", "Daniel", "Margaret", "Matthew", "Karen", "Anthony", "Nancy", "Mark", "Betty", "Donald", "Sandra", "Steven", "Ashley", "Paul", "Kimberly", "Andrew", "Donna", "Franklin", "Carol", "George"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Peterson", "Phillips", "Campbell", "Parker"]
PRIORITIES = ["P1 - Critical", "P2 - High", "P3 - Medium", "P4 - Low"]
ASSIGNED_TO = ["Tier 1 Support", "Tier 2 Support"]
PRODUCTS = [
    "Adobe Photoshop", "Amazon Echo", "Amazon Kindle", "Apple AirPods", "Asus ROG",
    "Autodesk AutoCAD", "Bose QuietComfort", "Bose SoundLink Speaker", "Canon DSLR Camera",
    "Canon EOS", "Dell XPS", "Dyson Vacuum Cleaner", "Fitbit Charge", "Fitbit Versa Smartwatch",
    "Garmin Forerunner", "Google Nest", "Google Pixel", "GoPro Action Camera", "GoPro Hero",
    "HP Pavilion", "iPhone", "Lenovo ThinkPad", "LG OLED", "LG Smart TV", "LG Washing Machine",
    "MacBook Pro", "Microsoft Office", "Microsoft Surface", "Microsoft Xbox Controller",
    "Nest Thermostat", "Nikon D", "Nintendo Switch", "Nintendo Switch Pro Controller",
    "Philips Hue Lights", "PlayStation", "Roomba Robot Vacuum", "Samsung Galaxy",
    "Samsung Soundbar", "Sony 4K HDR TV", "Sony PlayStation"
]
TYPES = ["Incident", "Problem", "Inquiry"]
SHORT_DESC = [
    "Product not working",
    "Need support",
    "Technical issue",
    "Shipping question",
    "Billing inquiry",
    "Feature request",
    "Bug report",
    "General question"
]
DETAILED_DESC_TEMPLATES = [
    "Customer reported issue with the product.",
    "Unable to resolve the issue through standard troubleshooting.",
    "Product arrived damaged or defective.",
    "Customer needs urgent assistance.",
    "Follow-up required from previous ticket.",
    "Escalation needed for resolution.",
]

def generate_random_date(days_back=365):
    """Generate a random date within the last N days"""
    today = datetime.now()
    random_days = random.randint(0, days_back)
    return (today - timedelta(days=random_days)).strftime("%Y-%m-%d")

def generate_tickets(num_tickets=1000):
    """Generate random tickets and write to CSV"""
    # Create unique names by combining first and last names
    unique_names = []
    for first in FIRST_NAMES:
        for last in LAST_NAMES:
            unique_names.append(f"{first} {last}")
    
    # Shuffle to randomize order
    random.shuffle(unique_names)
    
    # Ensure we have enough unique names
    if num_tickets > len(unique_names):
        raise ValueError(f"Need {num_tickets} unique names but only have {len(unique_names)} combinations")
    
    # Use only the first num_tickets unique names to avoid duplicates
    selected_names = unique_names[:num_tickets]
    
    # Track ticket numbers by type
    ticket_counts = {"Problem": 0, "Incident": 0, "Inquiry": 0}
    prefix_map = {"Problem": "PRB", "Incident": "INC", "Inquiry": "INQ"}
    
    with open("tickets.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        
        for i in range(num_tickets):
            ticket_type = random.choice(TYPES)
            ticket_counts[ticket_type] += 1
            prefix = prefix_map[ticket_type]
            
            ticket = {
                "Ticket Number": f"{prefix}-{ticket_counts[ticket_type]:05d}",
                "Name": selected_names[i],
                "Priority": random.choice(PRIORITIES),
                "Assigned To": random.choice(ASSIGNED_TO),
                "Product Purchased": random.choice(PRODUCTS),
                "Date of Purchase": generate_random_date(),
                "Type": ticket_type,
                "Short Description": random.choice(SHORT_DESC),
                "Detailed Description": random.choice(DETAILED_DESC_TEMPLATES),
            }
            writer.writerow(ticket)
        
        print(f"✓ Successfully generated {num_tickets} random tickets!")
        print(f"  - Problem (PRB): {ticket_counts['Problem']}")
        print(f"  - Incident (INC): {ticket_counts['Incident']}")
        print(f"  - Inquiry (INQ): {ticket_counts['Inquiry']}")

if __name__ == "__main__":
    generate_tickets(1000)
