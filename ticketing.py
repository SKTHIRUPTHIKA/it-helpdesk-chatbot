import json
import uuid
from datetime import datetime

TICKET_FILE = "tickets/open_tickets.json"

def create_ticket(user, issue):
    ticket = {
        "ticket_id": str(uuid.uuid4())[:8],
        "user": user,
        "issue": issue,
        "status": "OPEN",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(TICKET_FILE, "r") as f:
        tickets = json.load(f)

    tickets.append(ticket)

    with open(TICKET_FILE, "w") as f:
        json.dump(tickets, f, indent=2)

    return ticket["ticket_id"]
