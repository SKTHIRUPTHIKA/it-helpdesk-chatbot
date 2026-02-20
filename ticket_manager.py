import json
import os
from datetime import datetime

TICKET_FILE = "tickets/tickets.json"

def create_ticket(issue):
    os.makedirs("tickets", exist_ok=True)

    if os.path.exists(TICKET_FILE):
        with open(TICKET_FILE, "r") as f:
            tickets = json.load(f)
    else:
        tickets = []

    ticket_id = f"TICKET-{len(tickets) + 1}"

    ticket = {
        "ticket_id": ticket_id,
        "issue": issue,
        "status": "OPEN",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    tickets.append(ticket)

    with open(TICKET_FILE, "w") as f:
        json.dump(tickets, f, indent=4)

    return ticket_id
