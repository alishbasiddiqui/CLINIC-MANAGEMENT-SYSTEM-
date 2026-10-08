"""Console-based clinic receptionist login and management system."""

from datetime import datetime
from getpass import getpass

# Demonstration credentials only. Do not store real passwords in source code.
RECEPTIONIST_USERNAME = "receptionist"
RECEPTIONIST_PASSWORD = "clinic123"
MAX_LOGIN_ATTEMPTS = 3

# These records remain available while the program is running.
patients = []
doctors = ["Dr. Ahmed", "Dr. Sara", "Dr. John"]
activities = []
logged_in = False
next_patient_number = 1
next_token_number = 1


def record_activity(description):
    """Add an activity with its current date and time."""
    activities.append({
        "date": datetime.now().date(),
        "time": datetime.now().strftime("%H:%M:%S"),
        "description": description,
    })


def require_login():
    """Return True only when a receptionist is currently authenticated."""
    if not logged_in:
        print("Access denied. Please log in to use clinic functions.")
        return False
    return True


def login():
    """Prompt for credentials, allowing at most three attempts."""
    global logged_in

    for attempt in range(1, MAX_LOGIN_ATTEMPTS + 1):
        print("\n=== Receptionist Login ===")
        username = input("Username: ").strip()
        password = getpass("Password: ").strip()

        if username == RECEPTIONIST_USERNAME and password == RECEPTIONIST_PASSWORD:
            logged_in = True
            print("\nLogin successful. Welcome to the clinic dashboard.")
            record_activity("Receptionist logged in")
            return True

        remaining = MAX_LOGIN_ATTEMPTS - attempt
        if remaining:
            print(f"Incorrect username or password. {remaining} attempt(s) remaining.")
        else:
            print("Incorrect username or password. Maximum attempts reached.")

    logged_in = False
    return False


def logout():
    """End the authenticated session."""
    global logged_in

    if not require_login():
        return
    record_activity("Receptionist logged out")
    logged_in = False
    print("You have been logged out.")


def find_patient(patient_id):
    """Return a patient record by ID, or None if it does not exist."""
    if patient_id is None:
        return None

    normalized_id = str(patient_id).strip().lower()
    if not normalized_id:
        return None

    for patient in patients:
        if str(patient["patient_id"]).strip().lower() == normalized_id:
            return patient
    return None


def generate_token(patient):
    """Assign the next token if needed and display the patient's token."""
    global next_token_number

    if not require_login():
        return
    if patient is None:
        print("Patient not found.")
        return

    if patient["token_number"] is None:
        patient["token_number"] = f"T{next_token_number:03d}"
        next_token_number += 1
        record_activity(f"Generated token for {patient['patient_id']}")

    print(f"{patient['name']}'s token number is {patient['token_number']}.")


def register_patient():
    """Collect patient details and create a patient record."""
    global next_patient_number

    if not require_login():
        return

    name = input("Patient name: ").strip()
    if not name:
        print("Patient name cannot be empty.")
        return

    while True:
        try:
            age = int(input("Age: "))
            if age < 0:
                print("Age cannot be negative.")
                continue
            break
        except ValueError:
            print("Please enter a whole number for age.")

    gender = input("Gender: ").strip()
    contact = input("Contact number: ").strip()

    patient_id = f"P{next_patient_number:03d}"
    next_patient_number += 1
    patient = {
        "patient_id": patient_id,
        "name": name,
        "age": age,
        "gender": gender,
        "contact": contact,
        "doctor": None,
        "token_number": None,
        "payment_amount": 0.0,
        "payment_status": "Pending",
        "registered_at": datetime.now(),
    }
    patients.append(patient)
    record_activity(f"Registered patient {patient_id} ({name})")

    print(f"Patient registered successfully. Patient ID: {patient_id}")
    # Every new registration receives a token automatically.
    generate_token(patient)


def assign_doctor():
    """Assign an available doctor to a registered patient."""
    if not require_login():
        return
    if not patients:
        print("There are no registered patients to assign.")
        return

    print("\nAvailable doctors:")
    for number, doctor in enumerate(doctors, start=1):
        print(f"{number}. {doctor}")

    patient = find_patient(input("Patient ID: "))
    if patient is None:
        print("Patient not found.")
        return

    try:
        choice = int(input("Select doctor number: "))
        if choice < 1 or choice > len(doctors):
            raise ValueError
    except ValueError:
        print("Please select a valid doctor number.")
        return

    patient["doctor"] = doctors[choice - 1]
    record_activity(f"Assigned {patient['doctor']} to {patient['patient_id']}")
    print(f"{patient['doctor']} assigned to {patient['name']}.")


def view_today_patients():
    """Display patients registered during this program's current day."""
    if not require_login():
        return

    today = datetime.now().date()
    todays_patients = [
        patient for patient in patients
        if patient["registered_at"].date() == today
    ]
    if not todays_patients:
        print("No patients have been registered today.")
        return

    print("\n=== Today's Patients ===")
    print(f"{'ID':<8} {'Name':<22} {'Age':<5} {'Doctor':<18} {'Token':<8} {'Payment'}")
    print("-" * 78)
    for patient in todays_patients:
        print(
            f"{patient['patient_id']:<8} "
            f"{patient['name'][:21]:<22} "
            f"{patient['age']:<5} "
            f"{(patient['doctor'] or 'Not assigned')[:17]:<18} "
            f"{(patient['token_number'] or 'N/A'):<8} "
            f"{patient['payment_status']}"
        )


def manage_tokens():
    """Look up and display a patient's token number."""
    if not require_login():
        return
    if not patients:
        print("There are no registered patients.")
        return

    patient = find_patient(input("Patient ID: "))
    generate_token(patient)


def process_payment():
    """Record a payment amount and update the patient's payment status."""
    if not require_login():
        return
    if not patients:
        print("There are no registered patients.")
        return

    patient = find_patient(input("Patient ID: "))
    if patient is None:
        print("Patient not found.")
        return

    while True:
        try:
            amount = float(input("Payment amount (enter 0 if pending): "))
            if amount < 0:
                print("Payment amount cannot be negative.")
                continue
            break
        except ValueError:
            print("Please enter a valid amount, such as 25 or 25.50.")

    patient["payment_amount"] = amount
    patient["payment_status"] = "Paid" if amount > 0 else "Pending"
    record_activity(
        f"Payment updated for {patient['patient_id']}: "
        f"{patient['payment_status']} (${amount:.2f})"
    )
    print(
        f"Payment status: {patient['payment_status']} "
        f"(amount recorded: ${amount:.2f})."
    )


def view_today_activities():
    """Display activities recorded during this program session today."""
    if not require_login():
        return

    today = datetime.now().date()
    todays_activities = [
        activity for activity in activities
        if activity["date"] == today
    ]
    if not todays_activities:
        print("No clinic activities recorded today.")
        return

    print("\n=== Today's Clinic Activities ===")
    for activity in todays_activities:
        print(f"{activity['time']} - {activity['description']}")


def dashboard():
    """Show the protected clinic menu until the receptionist logs out."""
    if not require_login():
        return

    while logged_in:
        print("\n=== Clinic Dashboard ===")
        print("1. Today's Patients")
        print("2. Today's Clinic Activities")
        print("3. Patient Registration")
        print("4. Doctor Assignment")
        print("5. Token Management")
        print("6. Payment Management")
        print("7. Logout")
        choice = input("Select an option: ").strip()

        if choice == "1":
            view_today_patients()
        elif choice == "2":
            view_today_activities()
        elif choice == "3":
            register_patient()
        elif choice == "4":
            assign_doctor()
        elif choice == "5":
            manage_tokens()
        elif choice == "6":
            process_payment()
        elif choice == "7":
            logout()
        else:
            print("Invalid option. Please choose a number from 1 to 7.")


def main():
    """Require a fresh login before each dashboard session."""
    while True:
        if not login():
            print("Program ended after three failed login attempts.")
            break
        dashboard()
        print("Returning to the login screen.")


if __name__ == "__main__":
    main()
