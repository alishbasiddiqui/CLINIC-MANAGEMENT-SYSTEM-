"""Module 3: On-the-spot Token & Emergency Priority Management."""

from datetime import datetime

patients = []
next_token_number = 1

def find_patient(patient_id):
    for patient in patients:
        if patient["patient_id"].lower() == patient_id.strip().lower():
            return patient
    return None

def generate_token(patient, is_emergency=False):
    global next_token_number

    if patient is None:
        print("Patient not found.")
        return

    if patient["token_number"] is not None:
        print(f"{patient['name']}'s token number is already {patient['token_number']}.")
        return

    if is_emergency:
        for p in patients:
            if p["token_number"] is not None:
                num = int(p["token_number"][1:]) + 1
                p["token_number"] = f"T{num:03d}"
        
        patient["token_number"] = "T001"
        next_token_number += 1
        print(f"EMERGENCY! {patient['name']} ko priority token diya gaya: T001")
    else:
        patient["token_number"] = f"T{next_token_number:03d}"
        next_token_number += 1
        print(f"{patient['name']}'s token number is {patient['token_number']}.")

def manage_tokens():
    if not patients:
        print("There are no registered patients.")
        return

    patient_id = input("Patient ID: ")
    patient = find_patient(patient_id)
    
    if patient is None:
        print("Patient not found.")
        return

    is_emergency_input = input("Kya yeh Emergency patient hai? (yes/no): ").strip().lower()
    is_emergency = True if is_emergency_input == 'yes' or is_emergency_input == 'y' else False
    
    generate_token(patient, is_emergency)

if __name__ == "__main__":
    print("--- Module 3: Token & Emergency Priority Test ---")
    
    p1 = {"patient_id": "P001", "name": "Ali", "token_number": None}
    patients.append(p1)
    print("\nTest 1: Normal Patient (Ali)")
    manage_tokens()
    
    p2 = {"patient_id": "P002", "name": "Sara", "token_number": None}
    patients.append(p2)
    print("\nTest 2: Emergency Patient (Sara)")
    manage_tokens()
    
    print("\n--- Final Tokens ---")
    for p in patients:
        print(f"{p['name']}: {p['token_number']}")