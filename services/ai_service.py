def understand_request(message):

    text = message.lower()

    if any(word in text for word in [
        "towel", "clean", "cleaning", "toiletries",
        "soap", "shampoo", "blanket", "pillow"
    ]):
        return {
            "department": "Housekeeping",
            "priority": "Normal",
            "intent": "Housekeeping Request"
        }

    if any(word in text for word in [
        "taxi", "cab", "airport", "pickup",
        "transport", "drop"
    ]):
        return {
            "department": "Transport",
            "priority": "Normal",
            "intent": "Transportation Request"
        }

    if any(word in text for word in [
        "food", "breakfast", "dinner", "lunch",
        "restaurant", "meal"
    ]):
        return {
            "department": "Food Service",
            "priority": "Normal",
            "intent": "Food Service Request"
        }

    if any(word in text for word in [
        "ac", "air conditioner", "light", "water",
        "plumbing", "leak", "heater", "electricity"
    ]):
        return {
            "department": "Maintenance",
            "priority": "High",
            "intent": "Maintenance Issue"
        }

    if any(word in text for word in [
        "checkout", "check out", "checkin", "check-in",
        "reception", "room", "booking", "late arrival"
    ]):
        return {
            "department": "Reception",
            "priority": "Normal",
            "intent": "Reception Request"
        }

    if "emergency" in text or "urgent" in text:
        return {
            "department": "Reception",
            "priority": "Critical",
            "intent": "Emergency Request"
        }

    return {
        "department": "Reception",
        "priority": "Normal",
        "intent": "General Hotel Request"
    }