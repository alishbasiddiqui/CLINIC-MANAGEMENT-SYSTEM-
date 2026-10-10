import json
from pathlib import Path
from datetime import datetime


# Safely resolve path in standard Python scripts as well as REPL / interactive environments
try:
    DATA_FILE = Path(__file__).with_name("clinic_data.json")
except NameError:
    DATA_FILE = Path.cwd() / "clinic_data.json"


def create_sample_patients():
    """Create fictional patients for testing."""
    return [
        {
            "token": 101,
            "patient_id": "P001",
            "name": "Ali Khan",
            "age": 25,
            "gender": "Male",
            "problem": "Fever and headache",
            "priority": "Normal",
            "doctor": "Dr. Ahmed",
            "status": "Waiting",
            "examination": "",
            "prescription": [],
            "visits": []
        },
        {
            "token": 102,
            "patient_id": "P002",
            "name": "Sara Malik",
            "age": 32,
            "gender": "Female",
            "problem": "Difficulty breathing",
            "priority": "Emergency",
            "doctor": "Dr. Ahmed",
            "status": "Waiting",
            "examination": "",
            "prescription": [],
            "visits": []
        },
        {
            "token": 103,
            "patient_id": "P003",
            "name": "Usman Ali",
            "age": 40,
            "gender": "Male",
            "problem": "Stomach pain",
            "priority": "Normal",
            "doctor": "Dr. Ahmed",
            "status": "Waiting",
            "examination": "",
            "prescription": [],
            "visits": []
        },
        {
            "token": 104,
            "patient_id": "P004",
            "name": "Ayesha Noor",
            "age": 28,
            "gender": "Female",
            "problem": "Cough",
            "priority": "Normal",
            "doctor": "Dr. Usman",
            "status": "Waiting",
            "examination": "",
            "prescription": [],
            "visits": []
        }
    ]


def save_patients(patients):
    """Save patient records to the JSON file."""
    try:
        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump(patients, file, indent=4, ensure_ascii=False)
        return True
    except OSError as error:
        print("Could not save records:", error)
        return False


def load_patients():
    """Load existing data or create sample data on first run / empty file."""
    if not DATA_FILE.exists():
        patients = create_sample_patients()
        if save_patients(patients):
            print("Sample patient records created.")
        return patients

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            content = file.read().strip()
            
            # File exists but contains no data (0 bytes or blank spaces)
            if not content:
                patients = create_sample_patients()
                save_patients(patients)
                print("Empty data file detected. Sample patient records created.")
                return patients
                
            patients = json.loads(content)

        if not isinstance(patients, list):
            raise ValueError("The data must contain a list of patients.")

        for patient in patients:
            if not isinstance(patient, dict):
                raise ValueError("A patient record is invalid.")

        return patients

    except (OSError, json.JSONDecodeError, ValueError) as error:
        print("Could not read saved patient records:", error)
        print("The existing file has not been overwritten.")
        return None


def get_doctor_patients(patients, doctor_name):
    """Return patients assigned to the selected doctor."""
    return [
        patient for patient in patients
        if patient.get("doctor", "").casefold() == doctor_name.casefold()
    ]


def get_integer(prompt, minimum=1):
    """Get a valid whole number from the user."""
    while True:
        try:
            number = int(input(prompt).strip())

            if number < minimum:
                print("Enter a number greater than or equal to", minimum)
                continue

            return number

        except ValueError:
            print("Invalid input. Please enter a whole number.")


def find_patient(patients, doctor_name):
    """Find a patient assigned to this doctor using their token."""
    token = get_integer("Enter patient token number: ")

    for patient in get_doctor_patients(patients, doctor_name):
        if patient.get("token") == token:
            return patient

    print("Patient not found in your assigned patient list.")
    return None


def display_patient(patient):
    """Display basic patient information."""
    print("\n" + "=" * 45)
    print("TOKEN:", patient.get("token"))
    print("PATIENT ID:", patient.get("patient_id"))
    print("NAME:", patient.get("name"))
    print("AGE:", patient.get("age"))
    print("GENDER:", patient.get("gender"))
    print("REPORTED PROBLEM:", patient.get("problem"))
    print("PRIORITY:", patient.get("priority"))
    print("DOCTOR:", patient.get("doctor"))
    print("CONSULTATION STATUS:", patient.get("status"))
    print("=" * 45)


def view_waiting_patients(patients, doctor_name):
    """Display waiting patients, with emergency cases first."""
    waiting = [
        patient for patient in get_doctor_patients(
            patients, doctor_name
        )
        if patient.get("status") == "Waiting"
    ]

    waiting.sort(
        key=lambda patient: (
            patient.get("priority", "").casefold() != "emergency",
            patient.get("token", 0)
        )
    )

    if not waiting:
        print("\nThere are no waiting patients assigned to you.")
        return

    print("\nWAITING PATIENTS")
    print("-" * 65)

    for patient in waiting:
        print(
            "Token:", patient.get("token"),
            "| Name:", patient.get("name"),
            "| Problem:", patient.get("problem"),
            "| Priority:", patient.get("priority")
        )


def view_patient_details(patients, doctor_name):
    """View the details of an assigned patient."""
    patient = find_patient(patients, doctor_name)

    if patient is None:
        return

    display_patient(patient)

    if patient.get("examination"):
        print("EXAMINATION FINDINGS:", patient["examination"])

    prescription = patient.get("prescription", [])

    if prescription:
        print("\nCURRENT PRESCRIPTION")

        for item in prescription:
            print("Medicine:", item.get("medicine"))
            print("Dosage:", item.get("dosage"))
            print("Instructions:", item.get("instructions"))
            print("-" * 25)


def examine_patient(patients, doctor_name):
    """Record examination findings and update consultation status."""
    patient = find_patient(patients, doctor_name)

    if patient is None:
        return

    if patient.get("status") == "Completed":
        print("This token is already completed.")
        return

    display_patient(patient)

    if patient.get("priority", "").casefold() == "emergency":
        print("EMERGENCY PRIORITY: Arrange immediate clinical assessment.")

    findings = input("Enter examination findings: ").strip()

    if not findings:
        print("Examination findings cannot be empty.")
        return

    old_findings = patient.get("examination", "")
    old_status = patient.get("status", "Waiting")

    patient["examination"] = findings
    patient["status"] = "In Consultation"

    if save_patients(patients):
        print("Examination findings saved.")
        print("Status updated to In Consultation.")
    else:
        patient["examination"] = old_findings
        patient["status"] = old_status
        print("Changes were not saved. Please try again.")


def provide_prescription(patients, doctor_name):
    """Save a prescription for a patient who has been examined."""
    patient = find_patient(patients, doctor_name)

    if patient is None:
        return

    if patient.get("status") == "Completed":
        print("This token is already completed.")
        return

    if not patient.get("examination", "").strip():
        print("Record examination findings before providing a prescription.")
        return

    print("\nPRESCRIPTION")
    medicine = input("Medicine name: ").strip()
    dosage = input("Dosage: ").strip()
    instructions = input("Instructions: ").strip()

    if not medicine or not dosage or not instructions:
        print("All prescription fields are required.")
        return

    prescription_item = {
        "medicine": medicine,
        "dosage": dosage,
        "instructions": instructions
    }

    patient.setdefault("prescription", []).append(prescription_item)

    if save_patients(patients):
        print("Prescription saved successfully.")
    else:
        patient["prescription"].pop()
        print("Prescription could not be saved.")


def complete_token(patients, doctor_name):
    """Complete the token and save a visit history record."""
    patient = find_patient(patients, doctor_name)

    if patient is None:
        return

    if patient.get("status") == "Completed":
        print("This token is already completed.")
        return

    if not patient.get("examination", "").strip():
        print("Examine the patient before completing the token.")
        return

    visit = {
        "date_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "token": patient.get("token"),
        "problem": patient.get("problem", ""),
        "priority": patient.get("priority", "Normal"),
        "examination": patient.get("examination", ""),
        "prescription": [
            item.copy() for item in patient.get("prescription", [])
        ],
        "status": "Completed",
        "doctor": doctor_name
    }

    patient.setdefault("visits", []).append(visit)
    patient["status"] = "Completed"

    if save_patients(patients):
        print("Token marked as completed.")
        print("Consultation history saved.")
    else:
        patient["visits"].pop()
        patient["status"] = "In Consultation"
        print("Could not save completion. Please try again.")


def view_visit_history(patients, doctor_name):
    """Display completed visit records for an assigned patient."""
    patient = find_patient(patients, doctor_name)

    if patient is None:
        return

    visits = patient.get("visits", [])

    if not visits:
        print("No completed consultation records found.")
        return

    print("\nCONSULTATION HISTORY")
    print("-" * 45)
    print("Patient:", patient.get("name"))

    for number, visit in enumerate(visits, start=1):
        print("\nVisit number:", number)
        print("Date and time:", visit.get("date_time"))
        print("Doctor:", visit.get("doctor"))
        print("Problem:", visit.get("problem"))
        print("Priority:", visit.get("priority"))
        print("Examination:", visit.get("examination"))
        print("Status:", visit.get("status"))

        print("Prescription:")

        prescription = visit.get("prescription", [])

        if not prescription:
            print("No prescription recorded.")

        for item in prescription:
            print(
                item.get("medicine"),
                "| Dosage:", item.get("dosage"),
                "| Instructions:", item.get("instructions")
            )


def main():
    """Start the doctor module."""
    patients = load_patients()

    if patients is None:
        print("Program stopped to protect existing patient data.")
        return

    print("\nCLINIC MANAGEMENT SYSTEM")
    print("DOCTOR MODULE")
    print("-" * 30)

    doctor_name = input(
        "Enter doctor name (Dr. Ahmed or Dr. Usman): "
    ).strip()

    if not doctor_name:
        print("Doctor name cannot be empty.")
        return

    if not get_doctor_patients(patients, doctor_name):
        print("No patients are assigned to this doctor.")
        return

    while True:
        print("\nLogged in as:", doctor_name)
        print("\n1. View waiting patients")
        print("2. View patient details")
        print("3. Examine patient")
        print("4. Provide prescription")
        print("5. Complete patient token")
        print("6. View consultation history")
        print("7. Exit")

        choice = input("Select an option from 1 to 7: ").strip()

        if choice == "1":
            view_waiting_patients(patients, doctor_name)

        elif choice == "2":
            view_patient_details(patients, doctor_name)

        elif choice == "3":
            examine_patient(patients, doctor_name)

        elif choice == "4":
            provide_prescription(patients, doctor_name)

        elif choice == "5":
            complete_token(patients, doctor_name)

        elif choice == "6":
            view_visit_history(patients, doctor_name)

        elif choice == "7":
            print("Doctor module closed.")
            break

        else:
            print("Invalid choice. Enter a number from 1 to 7.")


if __name__ == "__main__":
    main()
    