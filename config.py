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

def get_unit_multiplier(unit):
    return {
        "second": 1,
        "minute": 60,
        "hour": 3600,
        "day" : 86400
    }.get(unit, 1)
