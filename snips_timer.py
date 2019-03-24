def get_intent_amount(x):
#    print(type(x))
    if isinstance(x, int):
        return x
    else:
      try:
          return float(x.replace(" i pół", ".5"))
      except ValueError:
          return {
              "jedną": 1,
              "dwie": 2,
              "półtorej": 1.5,
              "jedną i pół": 1.5,
              "dwie i pół" : 2.5,
              "trzy i pół" : 3.5,
              "cztery i pół" : 4.5,
              "pięć i pół" : 5.5,
              "sześć i pół" : 6.5,
              "siedem i pół" : 7.5,
              "osiem i pół" : 8.5,
              "dziewięć i pół": 9.5,
              "dziesięć i pół": 10.5
          }.get(x, x)

def get_intent_slots(intent_message):
    slots_count = len(intent_message.slots.intent_slot)
    slots = []
    for x in range(slots_count):
        slots.append(intent_message.slots.intent_slot[x].slot_value.value.value)
    return slots

def get_time_units(intent_message):
    slots_count = len(intent_message.slots.time_unit)
    slots = []
    for x in range(slots_count):
        slots.append(intent_message.slots.time_unit[x].slot_value.value.value)
    return slots

def get_locations(intent_message):
    slots = []
    if (intent_message.slots is None):
        return slots
    slots_count = len(intent_message.slots.location)
    for x in range(slots_count):
        slots.append(intent_message.slots.location[x].slot_value.value.value)
    return slots

def get_unit_multiplier(unit):
    return {
        "second": 1,
        "minute": 60,
        "hour": 3600,
        "day" : 86400
    }.get(unit, 1)

def format_unit_days(amount):
    return {
        1: "dzień"
    }.get(amount, "dni")

def format_unit_hour(amount):
    return {
        1: "godzina",
        2: "godziny",
        3: "godziny",
        4: "godziny"
    }.get(amount, "godzin")

def format_unit_minutes(amount):
    return {
        1: "minuta",
        2: "minuty",
        3: "minuty",
        4: "minuty"
    }.get(amount, "minut")

def format_unit_seconds(amount):
    return {
        1: "sekunda",
        2: "sekundy",
        3: "sekundy",
        4: "sekundy"
    }.get(amount, "sekund")

def format_amount(amount):
    return {
        1: "jedna",
        2: "dwie"
    }.get(amount, str(amount))

def get_amount_say(amount):
    days = int(amount // 86400)
    amount = amount % 86400
    hours = int(amount // 3600)
    amount = amount % 3600
    minutes = int(amount // 60)
    amount = amount % 60
    seconds = int(amount)
#        print(days)
#        print(hours)
#        print(minutes)
#        print(seconds)
    amount_say = []
    if days > 0:
        amount_say.append(str(days) + " " + format_unit_days(days))
    if hours > 0:
        amount_say.append(format_amount(hours) + " " + format_unit_hour(hours))
    if minutes > 0:
        amount_say.append(format_amount(minutes) + " " + format_unit_minutes(minutes))
    if seconds > 0:
        amount_say.append(format_amount(seconds) + " " + format_unit_seconds(seconds))
    return amount_say
