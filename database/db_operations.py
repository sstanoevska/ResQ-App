# import hashlib
# import os
# import re
# import secrets
# import random
# import bcrypt
# from cryptography.fernet import Fernet
# from help_sms import send_sms
# from normalize_phone import normalize_phone
# from .db_test import get_db_connection
# from dotenv import load_dotenv
#
# load_dotenv()
# fernet = Fernet(os.getenv("SECRET_KEY"))
#
# pw_regex = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@#$%^&*!]).{8,}$"
#
# def sha256_hash(egn):
#     return hashlib.sha256(egn.encode()).hexdigest()
#
# def encrypt_egn(egn):
#     return fernet.encrypt(egn.encode()).decode()
#
# def decrypt_egn(encrypted):
#     return fernet.decrypt(encrypted.encode()).decode()
#
# def store_egn_mapping(plain_egn):
#     hashed = sha256_hash(plain_egn)
#     encrypted = encrypt_egn(plain_egn)
#
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT 1 FROM egn_lookup WHERE hashed_egn = %s", (hashed,))
#     if not cursor.fetchone():
#         cursor.execute("INSERT INTO egn_lookup (hashed_egn, EGN_encrypted) VALUES (%s, %s)", (hashed, encrypted))
#         conn.commit()
#     conn.close()
#     return hashed
#
# def hash_password(pw):
#     return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
#
# def check_password(stored, entered):
#     return bcrypt.checkpw(entered.encode(), stored.encode())
#
# def register_patient(egn, name, username, password, dob, address, phone, allergies=None, diagnosis=None, medications=None):
#     if not (egn.isdigit() and len(egn) == 10):
#         return "Invalid EGN format"
#     if not re.match(pw_regex, password):
#         return "Weak password! Use letters, numbers and special characters."
#     if not all([egn, name, phone, password]):
#         return "Missing required fields"
#
#     hashed = store_egn_mapping(egn)
#     hashed_pw = hash_password(password)
#     conn = get_db_connection()
#     cursor = conn.cursor()
#
#     cursor.execute("SELECT 1 FROM app_users WHERE EGN=%s", (hashed,))
#     if cursor.fetchone():
#         return "A user with this EGN already exists."
#
#     cursor.execute("SELECT 1 FROM app_users WHERE username=%s", (username,))
#     if cursor.fetchone():
#         return "A user with this username already exists."
#
#
#
#     cursor.execute("INSERT INTO app_users (EGN, name, username, password, role, phone) VALUES (%s,%s,%s,%s,%s,%s)",
#                    (hashed, name, username, hashed_pw,'patient', phone))
#     cursor.execute("""INSERT INTO patient_info (EGN, date_of_birth, address, allergies, diagnosis, medications)
#                       VALUES (%s,%s,%s,%s,%s,%s)""",
#                    (hashed, dob, address, allergies, diagnosis, medications))
#
#     conn.commit()
#     conn.close()
#     return "Patient registered successfully!"
#
# def register_doctor(egn, name, username, password, phone, role='doctor'):
#     if not (egn.isdigit() and len(egn) == 10):
#         return "Invalid EGN format"
#     if not re.match(pw_regex, password):
#         return "Weak password! Use letters, numbers and special characters."
#     if not all([egn, name, phone, password]):
#         return "Missing fields"
#
#     hashed = store_egn_mapping(egn)
#     hashed_pw = hash_password(password)
#     conn = get_db_connection()
#     cursor = conn.cursor()
#
#     cursor.execute("SELECT 1 FROM app_users WHERE username=%s", (username,))
#     if cursor.fetchone():
#         return "A user with this username already exists."
#     cursor.execute("SELECT 1 FROM app_users WHERE EGN=%s", (hashed,))
#     if cursor.fetchone():
#         return "A user with this EGN already exists!"
#
#
#     cursor.execute("INSERT INTO app_users (EGN, name, username, password, role, phone) VALUES (%s,%s,%s,%s,%s,%s)",
#                    (hashed, name, username, hashed_pw, role, phone))
#
#     conn.commit()
#     conn.close()
#     return "Doctor registered successfully!"
#
# def login_user(username, password, remember_me=False):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#
#     cursor.execute("SELECT EGN, password, role FROM app_users WHERE BINARY username = %s", (username,))
#     user = cursor.fetchone()
#
#     if not user:
#         conn.close()
#         return "User not found."
#
#     # Verify password
#     if not check_password(user['password'], password):
#         conn.close()
#         return "Invalid credentials."
#
#
#
#     token = None
#     if remember_me:
#         token = secrets.token_hex(16)
#         cursor.execute("UPDATE app_users SET remember_me_token = %s WHERE username = %s", (token, username))
#         conn.commit()
#
#     conn.close()
#
#     return {
#         "message": f"Login successful. Role: {user['role']}",
#         "token": token,
#         "role": user['role'],
#         "egn": user['EGN']  # 🆕 Also return EGN directly here
#     }
#
#
# def add_contact(user_egn, name, phone, email, contact_type):
#     phone = normalize_phone(phone)
#     hashed_egn = user_egn
#
#     conn = get_db_connection()
#     cursor = conn.cursor()
#
#     cursor.execute("""
#         INSERT INTO emergency_contacts(user_egn, name, phone, email, contact_type)
#         VALUES (%s, %s, %s, %s, %s)
#     """, (hashed_egn, name, phone, email, contact_type.lower()))
#
#     conn.commit()
#     conn.close()
#
#     return "Contact added."
#
#
# def assign_patient(doctor_egn, patient_egn):
#     hashed_doctor = doctor_egn
#     hashed_patient = sha256_hash(patient_egn)
#
#     conn = get_db_connection()
#     cursor = conn.cursor()
#
#
#     cursor.execute("SELECT 1 FROM app_users WHERE EGN = %s AND role = 'patient'", (hashed_patient,))
#     if not cursor.fetchone():
#         conn.close()
#         return "Patient not found"
#
#     # ✅ Insert relationship
#     try:
#         cursor.execute("INSERT INTO doctor_patient(doctor_egn, patient_egn) VALUES (%s, %s)",
#                        (hashed_doctor, hashed_patient))
#         conn.commit()
#         print(f"✅ Assigned: Doctor {hashed_doctor} → Patient {hashed_patient}")
#     except Exception as e:
#         print(f"❌ ERROR assigning patient: {e}")
#         conn.rollback()
#         raise
#
#     conn.close()
#     return "Patient assigned."
#
#
#
# def get_doctor_patients(doctor_egn):
#     hashed = doctor_egn
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("""
#        SELECT u.name, el.EGN_encrypted, p.date_of_birth, u.phone, p.address,
#               p.allergies, p.diagnosis, p.medications
#         FROM doctor_patient dp
#         JOIN app_users u ON dp.patient_egn = u.EGN
#         JOIN egn_lookup el ON u.EGN = el.hashed_egn
#         JOIN patient_info p ON dp.patient_egn = p.EGN
#         WHERE dp.doctor_egn = %s
#     """, (hashed,))
#     results = cursor.fetchall()
#
#     for row in results:
#         row['EGN'] = decrypt_egn(row.pop('EGN_encrypted'))
#
#     conn.close()
#
#     # ✅ Always return a list (even if empty)
#     return results
#
#
# def get_assigned_doctor(patient_egn):
#     hashed = sha256_hash(patient_egn)
#     conn = get_db_connection()
#     cursor = conn.cursor()
#
#     # Debug: Print the hashed EGN
#     print(f"Fetching doctor for patient EGN: {hashed}")
#
#     # Check the raw query with the parameter
#     cursor.execute("""
#         SELECT u.name, u.username, u.phone
#         FROM emergency_contacts ec
#         JOIN app_users u ON ec.user_egn = u.EGN
#         WHERE ec.user_egn = %s AND ec.contact_type = 'doctor'
#     """, (hashed,))
#
#     doctor = cursor.fetchone()
#
#     # Debug: Log the query and result
#     print(
#         f"SQL Query executed: SELECT u.name, u.username, u.phone FROM emergency_contacts ec JOIN app_users u ON ec.user_egn = u.EGN WHERE ec.user_egn = {hashed} AND ec.contact_type = 'doctor'")
#     print(f"Fetched Doctor: {doctor}")
#
#     conn.close()
#
#     if not doctor:
#         return "No doctor assigned!"
#
#     return doctor
#
#
# def get_patient_contacts(hashed_egn):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("""
#         SELECT id, name, phone, email, contact_type
#         FROM emergency_contacts
#         WHERE user_egn = %s
#     """, (hashed_egn,))
#     contacts = cursor.fetchall()
#     conn.close()
#
#     print(f"Fetched contacts from database for EGN {hashed_egn}: {contacts}")
#
#     return contacts if contacts else []
#
#
# def edit_patient_info(egn, updates):
#     hashed = sha256_hash(egn)
#     conn = get_db_connection()
#     cursor = conn.cursor()
#
#     if "name" in updates or "phone" in updates:
#         fields = []
#         values = []
#         if "name" in updates:
#             fields.append("name = %s")
#             values.append(updates["name"])
#         if "phone" in updates:
#             fields.append("phone = %s")
#             values.append(updates["phone"])
#         values.append(hashed)
#         cursor.execute(f"UPDATE app_users SET {', '.join(fields)} WHERE EGN = %s", values)
#
#     if "address" in updates or "diagnosis" in updates:
#         fields = []
#         values = []
#         if "address" in updates:
#             fields.append("address = %s")
#             values.append(updates["address"])
#         if "diagnosis" in updates:
#             fields.append("diagnosis = %s")
#             values.append(updates["diagnosis"])
#         values.append(hashed)
#         cursor.execute(f"UPDATE patient_info SET {', '.join(fields)} WHERE EGN = %s", values)
#
#     conn.commit()
#     conn.close()
#     return "Profile updated successfully!"
#
#
# def send_reset_code_sms(phone):
#     phone = normalize_phone(phone)
#     conn = get_db_connection()
#     cursor = conn.cursor()
#
#     cursor.execute("""
#         SELECT 1 FROM app_users
#         WHERE phone = %s
#     """, (phone,))
#
#     if not cursor.fetchone():
#         conn.close()
#         return "User not found!"
#
#     code = str(random.randint(100000, 999999))
#
#     cursor.execute("""
#         UPDATE app_users
#         SET reset_codes = %s, reset_attempts = 0
#         WHERE phone = %s
#     """, (code, phone))
#     conn.commit()
#     conn.close()
#
#     msg = f"Your reset code is {code}"
#     return send_sms(phone, msg)
#
# def reset_password_with_sms(phone, code_entered, new_password):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#
#     cursor.execute("""
#         SELECT reset_codes, reset_attempts
#         FROM app_users
#         WHERE phone = %s
#     """, (phone,))
#     result = cursor.fetchone()
#
#     if not result:
#         conn.close()
#         return {"message": "User not found.", "success": False}
#
#     stored_code = result["reset_codes"]
#     attempts = result["reset_attempts"] or 0
#
#     if attempts >= 3:
#         conn.close()
#         return {
#             "message": "Maximum reset attempts reached. Please try again later.",
#             "success": False,
#             "locked_out": True
#         }
#
#     if stored_code != code_entered:
#         cursor.execute("""
#             UPDATE app_users
#             SET reset_attempts = reset_attempts + 1
#             WHERE phone = %s
#         """, (phone,))
#         conn.commit()
#
#         remaining = 2 - attempts  # 3 attempts total
#         conn.close()
#         return {
#             "message": f"Incorrect reset code. You have {remaining} attempts left.",
#             "success": False,
#             "locked_out": attempts + 1 >= 3
#         }
#     # Success
#     hashed_pw = hash_password(new_password)
#     cursor.execute("""
#         UPDATE app_users
#         SET password = %s, reset_codes = NULL, reset_attempts = 0
#         WHERE phone = %s
#     """, (hashed_pw, phone))
#     conn.commit()
#     conn.close()
#
#     return {
#         "message": "Password reset successful!",
#         "success": True
#     }
#
#
#
#
# def edit_profile_info(egn, updates):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#
#     hashed_egn = egn
#     app_users_fields = {k: updates[k] for k in ['name', 'username', 'phone'] if updates.get(k)}
#
#     if app_users_fields:
#         set_clause_users = ", ".join([f"{field} = %s" for field in app_users_fields])
#         values_users = list(app_users_fields.values())
#         values_users.append(hashed_egn)
#
#         cursor.execute(f"UPDATE app_users SET {set_clause_users} WHERE EGN = %s", values_users)
#
#     # Only update patient_info if address is present
#     if "address" in updates:
#         cursor.execute("""
#             UPDATE patient_info SET address = %s WHERE EGN = %s
#         """, (updates["address"], hashed_egn))
#
#     conn.commit()
#     conn.close()
#     return "Profile updated!"
#
#
# def show_success_message(self, message):
#     self.ids.message_label.text = message
#     self.ids.message_label.text_color = (0, 0.6, 0, 1)
#
# def show_error_message(self, message):
#     self.ids.message_label.text = message
#     self.ids.message_label.text_color = (1, 0, 0, 1)
#
# def go_back(self):
#     self.manager.current = "patient_dashboard"
#
#
# def update_emergency_contact(contact_id, updates):
#     conn= get_db_connection()
#
#     try:
#         with conn.cursor() as cursor:
#             update_fields = []
#             values = []
#
#
#             for field, value in updates.items():
#
#                 if field == "phone" and value:
#                     value = normalize_phone(value)
#
#                 if value:
#                     update_fields.append(f"{field} = %s")
#                     values.append(value)
#
#             if not update_fields:
#                 return "No fields to update."
#
#
#             update_query = f"UPDATE emergency_contacts SET {', '.join(update_fields)} WHERE id = %s"
#             values.append(contact_id)
#
#             cursor.execute(update_query, tuple(values))
#             conn.commit()
#
#             return "Contact updated successfully."
#     finally:
#         conn.close()
#
#
# def edit_doctor_profile(egn, updates):
#     hashed = sha256_hash(egn)
#     conn = get_db_connection()
#     cursor = conn.cursor()
#
#     cursor.execute("SELECT role FROM app_users WHERE EGN = %s", (hashed,))
#     user = cursor.fetchone()
#     if not user:
#         conn.close()
#         return {"message": "User not found."}
#
#     if user["role"] != "doctor":
#         conn.close()
#         return {"message": "Unauthorized access."}
#
#     fields = []
#     values = []
#
#     if "name" in updates:
#         fields.append("name = %s")
#         values.append(updates["name"])
#
#     if "phone" in updates:
#         fields.append("phone = %s")
#         values.append(updates["phone"])
#
#     if not fields:
#         conn.close()
#         return "Nothing was updated."
#
#     values.append(hashed)
#     cursor.execute(
#         f"UPDATE app_users SET {', '.join(fields)} WHERE EGN = %s", tuple(values)
#     )
#
#     conn.commit()
#     conn.close()
#     return "Profile updated successfully!"
#
# def delete_doctor_patient(doctor_egn, patient_egn):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     try:
#         cursor.execute("""
#             DELETE FROM doctor_patient
#             WHERE doctor_egn = %s AND patient_egn = %s
#         """, (doctor_egn, patient_egn))
#         conn.commit()
#
#         if cursor.rowcount > 0:
#             return "Patient removed"
#         else:
#             return "No matching patient to delete"
#     except Exception as e:
#         conn.rollback()
#         return f"Error: {str(e)}"
#     finally:
#         cursor.close()
#         conn.close()
#
import hashlib
import os
import re
import secrets
import random
from datetime import datetime

import bcrypt
from cryptography.fernet import Fernet
from dateutil.relativedelta import relativedelta

from help_sms import send_sms
from normalize_phone import normalize_phone
from .db_test import get_db_connection
from dotenv import load_dotenv

conn = get_db_connection()
cursor = conn.cursor()


# Create history table query
create_table_query = """
CREATE TABLE IF NOT EXISTS patient_history (
    EGN VARCHAR(255) NOT NULL,
    edate DATE NULL,
    visit_type VARCHAR(100) NULL,
    symptom TEXT NULL,
    description TEXT NULL
)
# """

cursor.execute(create_table_query)
conn.commit()

load_dotenv()
fernet = Fernet(os.getenv("SECRET_KEY"))

pw_regex = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@#$%^&*!]).{8,}$"


def sha256_hash(egn):
    return hashlib.sha256(egn.encode()).hexdigest()


def encrypt_egn(egn):
    return fernet.encrypt(egn.encode()).decode()


def decrypt_egn(encrypted):
    return fernet.decrypt(encrypted.encode()).decode()


def store_egn_mapping(plain_egn):
    hashed = sha256_hash(plain_egn)
    encrypted = encrypt_egn(plain_egn)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM egn_lookup WHERE hashed_egn = %s", (hashed,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO egn_lookup (hashed_egn, EGN_encrypted) VALUES (%s, %s)", (hashed, encrypted))
        conn.commit()
    conn.close()
    return hashed


def hash_password(pw):
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()


def check_password(stored, entered):
    return bcrypt.checkpw(entered.encode(), stored.encode())


def register_patient(egn, name, username, password, dob, address, phone, allergies=None, diagnosis=None,
                     medications=None):
    if not (egn.isdigit() and len(egn) == 10):
        return "Invalid EGN format"
    if not re.match(pw_regex, password):
        return "Weak password! Use letters, numbers and special characters."
    if not all([egn, name, phone, password]):
        return "Missing required fields"

    hashed = store_egn_mapping(egn)
    hashed_pw = hash_password(password)
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM app_users WHERE EGN=%s", (hashed,))
    if cursor.fetchone():
        return "A user with this EGN already exists."

    cursor.execute("SELECT 1 FROM app_users WHERE username=%s", (username,))
    if cursor.fetchone():
        return "A user with this username already exists."

    cursor.execute("INSERT INTO app_users (EGN, name, username, password, role, phone) VALUES (%s,%s,%s,%s,%s,%s)",
                   (hashed, name, username, hashed_pw, 'patient', phone))
    cursor.execute("""INSERT INTO patient_info (EGN, date_of_birth, address, allergies, diagnosis, medications)
                      VALUES (%s,%s,%s,%s,%s,%s)""",
                   (hashed, dob, address, allergies, diagnosis, medications))

    conn.commit()
    conn.close()
    return "Patient registered successfully!"


def register_doctor(egn, name, username, password, phone, role='doctor'):
    if not (egn.isdigit() and len(egn) == 10):
        return "Invalid EGN format"
    if not re.match(pw_regex, password):
        return "Weak password! Use letters, numbers and special characters."
    if not all([egn, name, phone, password]):
        return "Missing fields"

    hashed = store_egn_mapping(egn)
    hashed_pw = hash_password(password)
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM app_users WHERE username=%s", (username,))
    if cursor.fetchone():
        return "A user with this username already exists."
    cursor.execute("SELECT 1 FROM app_users WHERE EGN=%s", (hashed,))
    if cursor.fetchone():
        return "A user with this EGN already exists!"

    cursor.execute("INSERT INTO app_users (EGN, name, username, password, role, phone) VALUES (%s,%s,%s,%s,%s,%s)",
                   (hashed, name, username, hashed_pw, role, phone))

    conn.commit()
    conn.close()
    return "Doctor registered successfully!"


def login_user(username, password, remember_me=False):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT EGN, password, role FROM app_users WHERE BINARY username = %s", (username,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return "User not found."

    # Verify password
    if not check_password(user['password'], password):
        conn.close()
        return "Invalid credentials."

    token = None
    if remember_me:
        token = secrets.token_hex(16)
        cursor.execute("UPDATE app_users SET remember_me_token = %s WHERE username = %s", (token, username))
        conn.commit()

    conn.close()

    return {
        "message": f"Login successful. Role: {user['role']}",
        "token": token,
        "role": user['role'],
        "egn": user['EGN']  # 🆕 Also return EGN directly here
    }


def add_contact(user_egn, name, phone, email, contact_type):
    phone = normalize_phone(phone)
    hashed_egn = user_egn

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO emergency_contacts(user_egn, name, phone, email, contact_type)
        VALUES (%s, %s, %s, %s, %s)
    """, (hashed_egn, name, phone, email, contact_type.lower()))

    conn.commit()
    conn.close()

    return "Contact added."


def assign_patient(doctor_egn, patient_egn):
    hashed_doctor = doctor_egn
    hashed_patient = sha256_hash(patient_egn)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM app_users WHERE EGN = %s AND role = 'patient'", (hashed_patient,))
    if not cursor.fetchone():
        conn.close()
        return "Patient not found"

    # ✅ Insert relationship
    try:
        cursor.execute("INSERT INTO doctor_patient(doctor_egn, patient_egn) VALUES (%s, %s)",
                       (hashed_doctor, hashed_patient))
        conn.commit()
        print(f"✅ Assigned: Doctor {hashed_doctor} → Patient {hashed_patient}")
    except Exception as e:
        print(f"❌ ERROR assigning patient: {e}")
        conn.rollback()
        raise

    conn.close()
    return "Patient assigned."


def get_doctor_patients(doctor_egn):
    hashed = doctor_egn
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
       SELECT u.name, el.EGN_encrypted, p.date_of_birth, u.phone, p.address, 
              p.allergies, p.diagnosis, p.medications
        FROM doctor_patient dp
        JOIN app_users u ON dp.patient_egn = u.EGN
        JOIN egn_lookup el ON u.EGN = el.hashed_egn
        JOIN patient_info p ON dp.patient_egn = p.EGN
        WHERE dp.doctor_egn = %s
    """, (hashed,))
    results = cursor.fetchall()

    for row in results:
        row['EGN'] = decrypt_egn(row.pop('EGN_encrypted'))

    conn.close()

    # ✅ Always return a list (even if empty)
    return results


def get_assigned_doctor(patient_egn):
    hashed = sha256_hash(patient_egn)
    conn = get_db_connection()
    cursor = conn.cursor()

    # Debug: Print the hashed EGN
    print(f"Fetching doctor for patient EGN: {hashed}")

    # Check the raw query with the parameter
    cursor.execute("""
        SELECT u.name, u.username, u.phone
        FROM emergency_contacts ec
        JOIN app_users u ON ec.user_egn = u.EGN
        WHERE ec.user_egn = %s AND ec.contact_type = 'doctor'
    """, (hashed,))

    doctor = cursor.fetchone()

    # Debug: Log the query and result
    print(
        f"SQL Query executed: SELECT u.name, u.username, u.phone FROM emergency_contacts ec JOIN app_users u ON ec.user_egn = u.EGN WHERE ec.user_egn = {hashed} AND ec.contact_type = 'doctor'")
    print(f"Fetched Doctor: {doctor}")

    conn.close()

    if not doctor:
        return "No doctor assigned!"

    return doctor


def get_patient_contacts(hashed_egn):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, phone, email, contact_type
        FROM emergency_contacts
        WHERE user_egn = %s
    """, (hashed_egn,))
    contacts = cursor.fetchall()
    conn.close()

    print(f"Fetched contacts from database for EGN {hashed_egn}: {contacts}")

    return contacts if contacts else []


def edit_patient_info(egn, updates):
    hashed = sha256_hash(egn)
    conn = get_db_connection()
    cursor = conn.cursor()

    if "name" in updates or "phone" in updates:
        fields = []
        values = []
        if "name" in updates:
            fields.append("name = %s")
            values.append(updates["name"])
        if "phone" in updates:
            fields.append("phone = %s")
            values.append(updates["phone"])
        values.append(hashed)
        cursor.execute(f"UPDATE app_users SET {', '.join(fields)} WHERE EGN = %s", values)

    if "address" in updates or "diagnosis" in updates:
        fields = []
        values = []
        if "address" in updates:
            fields.append("address = %s")
            values.append(updates["address"])
        if "diagnosis" in updates:
            fields.append("diagnosis = %s")
            values.append(updates["diagnosis"])
        values.append(hashed)
        cursor.execute(f"UPDATE patient_info SET {', '.join(fields)} WHERE EGN = %s", values)

    conn.commit()
    conn.close()
    return "Profile updated successfully!"


def send_reset_code_sms(phone):
    phone = normalize_phone(phone)
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 1 FROM app_users 
        WHERE phone = %s
    """, (phone,))

    if not cursor.fetchone():
        conn.close()
        return "User not found!"

    code = str(random.randint(100000, 999999))

    cursor.execute("""
        UPDATE app_users
        SET reset_codes = %s, reset_attempts = 0
        WHERE phone = %s
    """, (code, phone))
    conn.commit()
    conn.close()

    msg = f"Your reset code is {code}"
    return send_sms(phone, msg)


def reset_password_with_sms(phone, code_entered, new_password):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT reset_codes, reset_attempts
        FROM app_users
        WHERE phone = %s
    """, (phone,))
    result = cursor.fetchone()

    if not result:
        conn.close()
        return {"message": "User not found.", "success": False}

    stored_code = result["reset_codes"]
    attempts = result["reset_attempts"] or 0

    if attempts >= 3:
        conn.close()
        return {
            "message": "Maximum reset attempts reached. Please try again later.",
            "success": False,
            "locked_out": True
        }

    if stored_code != code_entered:
        cursor.execute("""
            UPDATE app_users
            SET reset_attempts = reset_attempts + 1
            WHERE phone = %s
        """, (phone,))
        conn.commit()

        remaining = 2 - attempts  # 3 attempts total
        conn.close()
        return {
            "message": f"Incorrect reset code. You have {remaining} attempts left.",
            "success": False,
            "locked_out": attempts + 1 >= 3
        }
    # Success
    hashed_pw = hash_password(new_password)
    cursor.execute("""
        UPDATE app_users
        SET password = %s, reset_codes = NULL, reset_attempts = 0
        WHERE phone = %s
    """, (hashed_pw, phone))
    conn.commit()
    conn.close()

    return {
        "message": "Password reset successful!",
        "success": True
    }


def edit_profile_info(egn, updates):
    conn = get_db_connection()
    cursor = conn.cursor()

    hashed_egn = egn
    app_users_fields = {k: updates[k] for k in ['name', 'username', 'phone'] if updates.get(k)}

    if app_users_fields:
        set_clause_users = ", ".join([f"{field} = %s" for field in app_users_fields])
        values_users = list(app_users_fields.values())
        values_users.append(hashed_egn)

        cursor.execute(f"UPDATE app_users SET {set_clause_users} WHERE EGN = %s", values_users)

    # Only update patient_info if address is present
    if "address" in updates:
        cursor.execute("""
            UPDATE patient_info SET address = %s WHERE EGN = %s
        """, (updates["address"], hashed_egn))

    conn.commit()
    conn.close()
    return "Profile updated!"


def show_success_message(self, message):
    self.ids.message_label.text = message
    self.ids.message_label.text_color = (0, 0.6, 0, 1)


def show_error_message(self, message):
    self.ids.message_label.text = message
    self.ids.message_label.text_color = (1, 0, 0, 1)


def go_back(self):
    self.manager.current = "patient_dashboard"


def update_emergency_contact(contact_id, updates):
    conn = get_db_connection()

    try:
        with conn.cursor() as cursor:
            update_fields = []
            values = []

            for field, value in updates.items():

                if field == "phone" and value:
                    value = normalize_phone(value)

                if value:
                    update_fields.append(f"{field} = %s")
                    values.append(value)

            if not update_fields:
                return "No fields to update."

            update_query = f"UPDATE emergency_contacts SET {', '.join(update_fields)} WHERE id = %s"
            values.append(contact_id)

            cursor.execute(update_query, tuple(values))
            conn.commit()

            return "Contact updated successfully."
    finally:
        conn.close()


def edit_doctor_profile(egn, updates):
    hashed = sha256_hash(egn)
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT role FROM app_users WHERE EGN = %s", (hashed,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return {"message": "User not found."}

    if user["role"] != "doctor":
        conn.close()
        return {"message": "Unauthorized access."}

    fields = []
    values = []

    if "name" in updates:
        fields.append("name = %s")
        values.append(updates["name"])

    if "phone" in updates:
        fields.append("phone = %s")
        values.append(updates["phone"])

    if not fields:
        conn.close()
        return "Nothing was updated."

    values.append(hashed)
    cursor.execute(
        f"UPDATE app_users SET {', '.join(fields)} WHERE EGN = %s", tuple(values)
    )

    conn.commit()
    conn.close()
    return "Profile updated successfully!"


def delete_doctor_patient(doctor_egn, patient_egn):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            DELETE FROM doctor_patient
            WHERE doctor_egn = %s AND patient_egn = %s
        """, (doctor_egn, patient_egn))
        conn.commit()

        if cursor.rowcount > 0:
            return "Patient removed"
        else:
            return "No matching patient to delete"
    except Exception as e:
        conn.rollback()
        return f"Error: {str(e)}"
    finally:
        cursor.close()
        conn.close()


def add_patient_history(EGN, edate, visit_type, symptom, description):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        edate = datetime.strptime(edate, "%Y-%m-%d").date()
        print(edate)  # Out
        cursor.execute("""
        INSERT INTO patient_history (EGN, edate, visit_type, symptom, description)
        VALUES (%s, %s, %s, %s, %s)
        """, (EGN, edate, visit_type, symptom, description))
        conn.commit()
        return "Record inserted successfully."
    except Exception as e:
        conn.rollback()
        return f"Error: {e}"
    finally:
        cursor.close()
        conn.close()


def get_patient_history(EGN):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        Select * from patient_history where EGN=%s order by edate;
        """, (EGN,))
        result = cursor.fetchall()
        if result:
            return {'message': "Records Found", 'data': result}
        else:
            return {'message': 'Record not Found', 'data': None}
    except Exception as e:
        return f"Error: {e}"
    finally:
        cursor.close()
        conn.close()


def patient_visit_report(egn, up_to_months=4):
    conn = get_db_connection()
    cursor = conn.cursor()
    # get date and months
    today = datetime.today().replace(day=1)
    start_date = (today - relativedelta(months=up_to_months - 1)).strftime("%Y-%m-%d")
    months = [(today - relativedelta(months=i)).strftime('%Y-%m') for i in reversed(range(up_to_months))]


    cursor.execute("""SELECT DATE_FORMAT(edate, '%%Y-%%m') AS month, COUNT(*) AS record_count FROM patient_history
        WHERE EGN = %s AND edate >= %s GROUP BY DATE_FORMAT(edate, '%%Y-%%m') ORDER BY DATE_FORMAT(edate, '%%Y-%%m')
    """, (egn, start_date))
    results = cursor.fetchall()
    db_results = {row["month"]: row["record_count"] for row in results}

    temp_results = [(datetime.strptime(month, "%Y-%m").strftime("%B"), db_results.get(month, 0)) for month in months]
    # Separate into two lists
    months = [item[0] for item in temp_results]
    counts = [item[1] for item in temp_results]
    # symptoms report query
    total_query = "SELECT COUNT(*) FROM patient_history WHERE EGN = %s"
    cursor.execute(total_query, (egn,))
    total_count = cursor.fetchone()['COUNT(*)']
    if total_count == 0:
        cursor.close()
        conn.close()
        symptom = []
        percent = []
    else:
        cursor.execute("""SELECT symptom, COUNT(*) AS count FROM patient_history WHERE EGN = %s GROUP BY symptom
                ORDER BY count DESC;""", (egn,))
        rows = cursor.fetchall()
        symptom_percentages = [(row['symptom'], round((row['count'] / total_count) * 100, 2)) for row in rows]

        symptom = [item[0] for item in symptom_percentages]
        percent = [item[1] for item in symptom_percentages]

    final_results = [months, counts, symptom, percent]
    cursor.close()
    conn.close()
    return final_results


def patient_symptoms_report(egn):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Step 1: Get total symptom count for the given EGN
    total_query = "SELECT COUNT(*) FROM patient_history WHERE EGN = %s"
    cursor.execute(total_query, (egn,))
    total_count = cursor.fetchone()['COUNT(*)']
    if total_count == 0:
        cursor.close()
        conn.close()
        return {"data": None}
    else:
        cursor.execute("""SELECT symptom, COUNT(*) AS count FROM patient_history WHERE EGN = %s GROUP BY symptom
            ORDER BY count DESC;""", (egn,))
        rows = cursor.fetchall()
        symptom_percentages = [(row['symptom'], round((row['count'] / total_count) * 100, 2)) for row in rows]

        symptom = [item[0] for item in symptom_percentages]
        percent = [item[1] for item in symptom_percentages]

        result = [symptom, percent]
        cursor.close()
        conn.close()
        return result
