import os
import json
from datetime import datetime

METRICS_FILE = "metrics.json"


def load_metrics():
    if not os.path.exists(METRICS_FILE):
        return {"total_tickets": 0, "auto_resolved": 0, "escalated": 0}

    with open(METRICS_FILE, "r") as f:
        return json.load(f)


def save_metrics(metrics):
    with open(METRICS_FILE, "w") as f:
        json.dump(metrics, f, indent=4)


def create_ticket(user, issue):
    ticket_id = datetime.now().strftime("%Y%m%d%H%M%S")
    return {
        "ticket_id": ticket_id,
        "user": user,
        "issue": issue,
        "status": "Open",
        "created_at": datetime.now().isoformat()
    }


def find_solution(issue):
    issue = issue.lower()
    kb_map = {
        "password": "password_reset.txt",
        "wifi": "wifi_issue.txt",
        "software": "software_install.txt"
    }

    for keyword, filename in kb_map.items():
        if keyword in issue:
            path = os.path.join("kb", filename)
            if os.path.exists(path):
                with open(path, "r") as f:
                    return f.read()
    return None


def save_ticket(ticket):
    if not os.path.exists("tickets"):
        os.mkdir("tickets")

    with open(f"tickets/{ticket['ticket_id']}.json", "w") as f:
        json.dump(ticket, f, indent=4)


def raise_ticket():
    metrics = load_metrics()

    user = input("Enter your employee ID: ")
    issue = input("Describe your issue: ")

    ticket = create_ticket(user, issue)
    solution = find_solution(issue)

    metrics["total_tickets"] += 1

    if solution:
        ticket["status"] = "Resolved"
        ticket["resolution"] = solution
        metrics["auto_resolved"] += 1
        print("\n✅ ISSUE AUTO-RESOLVED\n")
        print(solution)
    else:
        ticket["status"] = "Escalated"
        metrics["escalated"] += 1
        print("\n🚨 Issue escalated to IT team")

    save_ticket(ticket)
    save_metrics(metrics)

    print(f"\n🎫 Ticket ID: {ticket['ticket_id']}")


def show_metrics():
    metrics = load_metrics()

    print("\n📊 HELP DESK METRICS")
    print("------------------")
    print(f"Total Tickets   : {metrics['total_tickets']}")
    print(f"Auto-Resolved   : {metrics['auto_resolved']}")
    print(f"Escalated       : {metrics['escalated']}")

    if metrics["total_tickets"] > 0:
        rate = (metrics["auto_resolved"] / metrics["total_tickets"]) * 100
        print(f"Auto-Resolution : {rate:.2f}%")


def check_status():
    ticket_id = input("Enter Ticket ID: ")
    path = f"tickets/{ticket_id}.json"

    if not os.path.exists(path):
        print("❌ Ticket not found")
        return

    with open(path, "r") as f:
        ticket = json.load(f)

    print("\n🎫 TICKET DETAILS")
    print("-----------------")
    for k, v in ticket.items():
        print(f"{k}: {v}")


def main_menu():
    while True:
        print("\n🧑‍💻 Enterprise IT Helpdesk Bot")
        print("1. Raise a new ticket")
        print("2. Check ticket status")
        print("3. View metrics")
        print("4. Exit")

        choice = input("Choose (1/2/3/4): ")

        if choice == "1":
            raise_ticket()
        elif choice == "2":
            check_status()
        elif choice == "3":
            show_metrics()
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice")


if __name__ == "__main__":
    main_menu()


