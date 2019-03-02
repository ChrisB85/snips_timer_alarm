def get_intent_question(x):
    return {
        "IWant": "Co chcesz robić?",
        "TurnOn" : "Co chcesz włączyć?",
        "TurnOff" : "Co chcesz wyłączyć?",
        "Mute" : "Co chcesz wyciszyć?",
        "Unmute" : "Czego dźwięk chcesz przywrócić?",
        "Play" : "Co chcesz odtworzyć?",
        "Pause" : "Co chcesz wstrzymać?",
        "Stop" : "Co chcesz zatrzymać?",
        "clear_room": "Które pomieszczenie?"
#        "command": "Co chcesz zrobić?"
    }.get(x, "")


def get_intent_slots(intent_message):
    slots_count = len(intent_message.slots.intent_slot)
    slots = []
    for x in range(slots_count):
        slots.append(intent_message.slots.intent_slot[x].slot_value.value.value)
    return slots
