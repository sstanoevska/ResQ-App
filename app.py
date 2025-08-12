import hashlib

import pymysql
from hashlib import sha256
import os
from flask import Flask, request, jsonify, session
from database.db_operations import (
    register_doctor, register_patient, login_user,
    add_contact, assign_patient, get_patient_contacts,
    get_doctor_patients,
    get_assigned_doctor, reset_password_with_sms, send_reset_code_sms, sha256_hash, edit_profile_info,
    update_emergency_contact, edit_doctor_profile, edit_patient_info, delete_doctor_patient, add_patient_history,
    get_patient_history, patient_visit_report, patient_symptoms_report
)
from database.db_test import get_db_connection
from help_sms import send_sms
from normalize_phone import normalize_phone

app = Flask(__name__)
app.secret_key = "V87sa7l1fbq2l0cf-iC5JHAPEDnigqCBXUkjGSzV4qo="  # required for sessions

@app.route('/')
def home():
    return jsonify({"message": "Welcome!"})

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    role = data.get('role')

    required_fields = ["EGN", "name", "username", "password", "phone"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"message": f"The field '{field}' is required."}), 400

    data["phone"] = normalize_phone(data["phone"])

    if not role:
        return jsonify({"message": "Role is required."}), 400

    if role == 'patient':
        result = register_patient(
            data.get('EGN'),
            data.get('name'),
            data.get('username'),
            data.get('password'),
            data.get('date_of_birth'),
            data.get('address'),
            data.get('phone'),
            data.get('allergies'),
            data.get('diagnosis'),
            data.get('medications'),
        )
    elif role == 'doctor':
        result = register_doctor(
            data.get("EGN"),
            data.get("name"),
            data.get("username"),
            data.get("password"),
            data.get("phone"),
            "doctor",
        )
    else:
        return jsonify({"message": "Invalid role!"})

    if isinstance(result, tuple):
        return jsonify({"message": result[0]}), result[1]


    return jsonify({"message": result}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    remember_me = data.get('remember_me', False)

    if not username or not password:
        return jsonify({"message": "Username and password are required."}), 400

    result = login_user(username, password, remember_me)

    if isinstance(result, dict):
        # ✅ Fetch the EGN when login is successful
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT EGN FROM app_users WHERE BINARY username = %s", (username,))
        user = cursor.fetchone()
        conn.close()

        if user:
            result["username"] = username
            result["egn"] = user["EGN"]
            return jsonify(result), 200
        else:
            return jsonify({"message": "User not found."}), 400
    else:
        return jsonify({"message": result}), 400




@app.route('/send-sms-reset', methods=['POST'])
def send_sms_reset():
    data = request.json
    phone = data.get("phone")


    if not phone:
        return jsonify({"message": "Invalid phone number."}), 400

    phone = normalize_phone(phone)
    result = send_reset_code_sms(phone)
    return jsonify({"message": result})

@app.route('/reset-password-sms', methods=['POST'])
def reset_pw_sms():
    data = request.json
    phone = data.get("phone")
    code = data.get("code")
    new_pw = data.get("new_password")

    if not all([phone, code, new_pw]):
        return jsonify({"message": "Invalid data", "success": False}), 400

    result = reset_password_with_sms(phone, code, new_pw)
    return jsonify(result)


#Temporary change to trigger git
@app.route('/add-emergency-contact', methods=['POST'])
def add_emergency_contact():
    data = request.json
    print("[DEBUG] Incoming data:", data)

    user_egn = data.get("user_egn")
    name = data.get("name")
    phone = data.get("phone")
    contact_type = data.get("contact_type")
    email = data.get("email") or None

    if not all([user_egn, name, phone, contact_type]):
        return jsonify({"message": "Invalid data"}), 400

    print("[DEBUG] Raw user EGN from app:", user_egn)

    try:
        result = add_contact(user_egn, name, phone, email, contact_type)
        return jsonify({"message": result}), 200

    except Exception as e:
        import traceback
        print("Error in add-emergency-contact:")
        traceback.print_exc()
        return jsonify({"message": "Internal server error", "error": str(e)}), 500

@app.route("/assign-patient", methods=["POST"])
def assign_patient():
    data = request.get_json()
    doctor_egn = data.get("doctor_egn")
    patient_egn = data.get("patient_egn")

    if not doctor_egn or not patient_egn:
        return jsonify({"message": "Missing data"}), 400

    hashed_patient_egn = hashlib.sha256(patient_egn.encode()).hexdigest()

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if patient exists
    cursor.execute("SELECT 1 FROM app_users WHERE EGN = %s AND role = 'patient'", (hashed_patient_egn,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"message": "Patient not found"}), 404

    # Check if already assigned
    cursor.execute("""
        SELECT 1 FROM doctor_patient 
        WHERE doctor_egn = %s AND patient_egn = %s
    """, (doctor_egn, hashed_patient_egn))
    if cursor.fetchone():
        conn.close()
        return jsonify({"message": "Patient is already added to your list."}), 400

    # Assign patient
    try:
        cursor.execute("""
            INSERT INTO doctor_patient (doctor_egn, patient_egn)
            VALUES (%s, %s)
        """, (doctor_egn, hashed_patient_egn))
        conn.commit()
        return jsonify({"message": "Patient successfully assigned"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"Error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/doctor-dashboard', methods=['GET'])
def doctor_dashboard():
    username = request.args.get("doctor_egn")  # this is actually the username

    if not username:
        return jsonify({"message": "Missing username."}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get doctor user info from app_users
    cursor.execute("SELECT name, role, EGN, phone FROM app_users WHERE username = %s", (username,))
    user = cursor.fetchone()

    if not user:
        return jsonify({"message": "User not found."}), 404

    if user["role"] != "doctor":
        return jsonify({"message": "Unauthorized access.", "role": user["role"]}), 403

    hashed_egn = user["EGN"]

    # Build doctor info from app_users only
    doctor_info = {
        "name": user["name"],
        "phone": user["phone"]
    }

    # Get patients using the EGN (doctor_egn) as argument
    patients = get_doctor_patients(hashed_egn)

    conn.close()

    return jsonify({
        "role": "doctor",
        "doctor_info": doctor_info,
        "patients": patients
    })

@app.route("/add_history-patient", methods=["POST"])
def patient_history():
    data = request.json
    egn = data.get("EGN")

    allowed = ["edate", "visit_type", "symptoms", "description"]
    insert = {k: v for k, v in data.items() if k in allowed and v}
    #
    print(egn)
    print(insert, 'line 249')
    if not egn or not insert:
        return jsonify({"message": "Invalid data."}), 400
    print(insert)
    result = add_patient_history(egn, insert['edate'], insert['visit_type'], insert['symptoms'], insert['description'])
    return jsonify({"message": result})
@app.route("/get-history-patient", methods=["POST"])
def view_patient_history():
    data = request.json
    print(data, 'line 259')
    egn = data.get("EGN")
    if not egn:
        return jsonify({"message": "Invalid data."}), 400

    result = get_patient_history(egn)
    return jsonify({"message": result})
@app.route("/patient-visits-report", methods=["GET"])
def patient_visits():
    egn = request.args.get("EGN")
    months = request.args.get("months", type=int)

    if not egn and request.is_json:
        body = request.get_json(silent=True) or {}
        egn = body.get("EGN")
        months = months or body.get("months")

    if not egn:
        return jsonify({"message": "Invalid data."}), 400

    try:
        result = patient_visit_report(egn, months)
    except TypeError:
        result = patient_visit_report(egn)

    return jsonify({"message": result})

# @app.route("/patient-symptoms-report", methods=["GET"])
# def patient_symptoms():
#     data = request.json
#     egn = data.get("EGN")
#     if not egn:
#         return jsonify({"message": "Invalid data."}), 400
#     result = patient_symptoms_report(egn)
#     return jsonify({"message": result})

@app.route("/edit-patient", methods=["POST"])
def edit_patient():
    data = request.json
    egn = data.get("egn")

    allowed = ["name", "phone", "address", "diagnosis"]
    updates = {k: v for k, v in data.items() if k in allowed and v}

    if not egn or not updates:
        return jsonify({"message": "Invalid data."}), 400

    result = edit_patient_info(egn, updates)
    return jsonify({"message": result})

@app.route('/patient-dashboard', methods=['GET'])
def patient_dashboard():
    username = request.args.get("username")

    if not username:
        return jsonify({"message": "Missing username."}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name, role, EGN, phone FROM app_users WHERE username = %s", (username,))
    user = cursor.fetchone()

    if not user:
        return jsonify({"message": "User not found."}), 404

    print(">>> Found user:", user)

    if user["role"] != "patient":
        return jsonify({"message": "Unauthorized access.", "role": user["role"]}), 403

    hashed_egn = user["EGN"]
    print(">>> Hashed EGN from user:", hashed_egn)

    cursor.execute("SELECT * FROM patient_info")
    rows = cursor.fetchall()
    print(">>> All patient_info EGNs:", [r["EGN"] for r in rows])

    cursor.execute("""
        SELECT date_of_birth, address, allergies, diagnosis, medications
        FROM patient_info WHERE EGN = %s
    """, (hashed_egn,))
    row = cursor.fetchone()

    if not row:
        print(">>> NO MATCH in patient_info for EGN:", hashed_egn)
        return jsonify({"message": "Patient info not found."}), 404

    print(">>> MATCHED patient_info:", row)

    patient_info = {
        "name": user["name"],
        "date_of_birth": str(row["date_of_birth"]) if row["date_of_birth"] else "",
        "address": row["address"],
        "allergies": row["allergies"],
        "diagnosis": row["diagnosis"],
        "medications": row["medications"],
        "phone": user["phone"]
    }

    contacts = get_patient_contacts(hashed_egn)

    return jsonify({
        "role": "patient",
        "patient_info": patient_info,
        "emergency_contacts": contacts
    })


@app.route('/send-alert', methods=['POST'])
def send_alert():
    try:
        data = request.get_json(force=True)
        egn = data.get("patient_egn")
        alert_type = data.get("alert_type", "").lower()  # doctor or others

        # Fetch patient name using their EGN

        print(f"Received EGN: {egn}")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, phone FROM app_users WHERE EGN=%s", (egn,))
        result = cursor.fetchone()

        # Debugging: Check if patient name is fetched correctly
        print(f"Fetched result: {result}")

        patient_name = result["name"] if result else "the patient"
        patient_phone = result["phone"] if result else None

        print(f"Patient name: {patient_name}, Patient phone: {patient_phone}")

        conn.close()

        if not egn or alert_type not in ["doctor", "others"]:
            return jsonify({"message": "Invalid alert data."}), 400

        contacts = get_patient_contacts(egn)
        messages = []

        if alert_type == "doctor":
            for c in contacts:
                if c["contact_type"] == "doctor":
                    msg = (f"ПОМОЩ!🚨 Вашият пациент {patient_name} се нуждае от вашата помощ! Моля, обадете се веднага на {patient_phone}!"
                           
                           f"\n\nHELP!🚨 Your patient {patient_name} needs your help! Please call them immediately at {patient_phone}!")

                    send_sms(c["phone"], msg)
                    messages.append(f"Message sent to {c['name']} (Doctor)")

        elif alert_type == "others":
            for c in contacts:
                if c["contact_type"] != "doctor":  # Only send to non-doctors
                    text = (f"{c['name']}, {patient_name} се нуждае от вашата помощ! 🚨 Моля, обадете се веднага на {patient_phone}!"
                            f"\n\n {c['name']}, {patient_name} needs your help!🚨 Please contact them immediately at : {patient_phone}!")


                    send_sms(c["phone"], text)
                    messages.append(f"Message sent to {c['name']} (Other)")

        return jsonify({"messages": messages})

    except Exception as e:
        import traceback
        print("Error in /send-alert:", traceback.format_exc())
        return jsonify({"message": str(e)}), 500


@app.route('/edit-profile', methods=['PUT'])
def edit_profile():
    data = request.get_json()
    egn = data.get("EGN")

    if not egn:
        return jsonify({"message": "Invalid data."}), 400


    updates = {
        "name": data.get("name"),
        "username": data.get("username"),
        "phone": data.get("phone"),
        "address": data.get("address")
    }

    if not any(updates.values()):
        return jsonify({"message": "No changes made."}), 400

    result = edit_profile_info(egn, updates)
    return jsonify({"message": result}), 200

@app.route('/edit-emergency-contact', methods=['PUT'])
def edit_emergency_contact():
    data = request.get_json()
    contact_id = data.get("contact_id")

    if not contact_id:
        return jsonify({"message": "Invalid data."}), 400

    updates = {
        "name": data.get("name"),
        "phone": data.get("phone"),
        "email": data.get("email"),
        "contact_type": data.get("contact_type")
    }

    if "phone" in updates and updates["phone"]:
        updates["phone"] = normalize_phone(updates["phone"])

    if not any(updates.values()):
        return jsonify({"message": "No changes made."}), 400

    result = update_emergency_contact(contact_id, updates)

    return jsonify({"message": result}), 200



@app.route("/edit-doctor-profile", methods=["PUT"])
def edit_doctor_profile_route():
    data = request.get_json()
    egn = data.get("EGN")

    updates = {
        "name": data.get("name"),
        "phone": data.get("phone")
    }

    updates = {k: v for k, v in updates.items() if v is not None}

    return jsonify(edit_doctor_profile(egn, updates))


@app.route('/delete-contact', methods=['DELETE'])
def delete_contact():
    data = request.get_json()
    egn = data.get("EGN")
    id = data.get("id")

    if not (egn and id):
        return jsonify({"message": "Invalid data."}), 400

    hashed = egn  # 🛠️ No re-hashing!

    print(f"🛠️ Attempting to delete contact where user_egn={hashed} and id={id}")  # 🔥 DEBUG

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM emergency_contacts
        WHERE user_egn = %s AND id = %s
    """, (hashed, id))

    affected_rows = cursor.rowcount
    print(f"🛠️ Deleted {affected_rows} row(s)")

    conn.commit()
    conn.close()

    if affected_rows == 0:
        return jsonify({"message": "Nothing deleted. Maybe invalid EGN or ID."}), 400

    return jsonify({"message": "Contact deleted successfully."}), 200

import hashlib

@app.route("/delete-patient", methods=["POST"])
def delete_patient():
    data = request.get_json()
    doctor_egn = data.get("doctor_egn")
    patient_egn = data.get("patient_egn")

    print("🟠 DELETE doctor_egn:", doctor_egn)
    print("🟠 DELETE patient_egn (raw):", patient_egn)

    if not doctor_egn or not patient_egn:
        return jsonify({"message": "Invalid data"}), 400

    # ✅ Hash the patient_egn so it matches what is stored in doctor_patient table
    hashed_patient_egn = hashlib.sha256(patient_egn.encode()).hexdigest()
    print("🟠 DELETE patient_egn (hashed):", hashed_patient_egn)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM doctor_patient
        WHERE doctor_egn = %s AND patient_egn = %s
    """, (doctor_egn, hashed_patient_egn))

    affected_rows = cursor.rowcount
    conn.commit()
    conn.close()

    if affected_rows == 0:
        return jsonify({"message": "No matching patient to delete"}), 400

    return jsonify({"message": "Patient removed"}), 200



@app.route('/verify-contact', methods=['POST'])
def verify_contact():
    data = request.get_json()
    contact_id = data.get("contact_id")
    code_entered = data.get("code")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT verification_code FROM emergency_contacts WHERE id = %s", (contact_id,))
    result = cursor.fetchone()

    if not result:
        conn.close()
        return jsonify({"message": "Contact not found"}), 404

    if result["verification_code"] == code_entered:
        cursor.execute("UPDATE emergency_contacts SET verified = 1 WHERE id = %s", (contact_id,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Contact verified successfully"}), 200
    else:
        conn.close()
        return jsonify({"message": "Incorrect code"}), 400


@app.route('/auto-login', methods=['POST'])
def auto_login():
    data = request.json
    token = data.get("token")
    if not token:
        return jsonify({"message": "Token missing"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, role, EGN FROM app_users WHERE remember_me_token = %s", (token,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({
            "message": "Auto-login success",
            "role": user["role"],
            "username": user["username"],
            "EGN": user["EGN"]  # ✅ Now included
        })
    else:
        return jsonify({"message": "Invalid token"}), 401



if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port)

