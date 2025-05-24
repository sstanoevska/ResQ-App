def normalize_phone(phone):
    phone = phone.strip()
    if phone.startswith("0") and len(phone) == 10:
        return "+359" + phone[1:]
    elif not phone.startswith("+"):
        return "+359" + phone
    return phone