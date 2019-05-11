from pprint import pprint
import json, time, os, io
from dateutil import tz
import datetime

global timers_file
timers_file = './timers.json'
alarms_file = './alarms.json'

def call_timer(site_id, total_amount, end_time, target):
    os.system('./timer.py ' + site_id + ' ' + str(int(total_amount)) + ' ' + str(end_time) + ' "' + str(target) + '" &')

def call_alarm(site_id, hour, target):
    os.system('./timer.py ' + site_id + ' alarm "' + str(hour) + '" "' + str(target) + '" &')

def handle_file(file_path):
    try:
        fp = open(file_path)
    except IOError:
        # If not exists, create the file
        fp = open(file_path, 'w+')
        data = []
        json.dump(data, fp)

def check_timers(call = False):
    handle_file(timers_file)
    with open(timers_file) as json_file:
        data = json.load(json_file)
        new_data = []
        for timer in data:
            if int(timer['end_time']) > int(time.time() * 1000):
                new_data.append(timer)
                if call:
                    call_timer(timer['site_id'], timer['amount'], timer['end_time'], timer['target'])
        with open(timers_file, 'w') as outfile:
            json.dump(new_data, outfile)

def check_alarms(call = False):
    handle_file(alarms_file)
    with open(alarms_file) as json_file:
        data = json.load(json_file)
        new_data = []
        for alarm in data:
            alarm_datetime = datetime.datetime.strptime(alarm['hour'], "%Y-%m-%d %H:%M")
            if time.mktime(alarm_datetime.timetuple()) > time.mktime(time.gmtime()):
                new_data.append(alarm)
                if call:
                    call_alarm(alarm['site_id'], alarm['hour'], alarm['target'])
        with open(alarms_file, 'w') as outfile:
            json.dump(new_data, outfile)

def add_timer(site_id, amount, end_time, target):
    handle_file(timers_file)
    with open(timers_file) as json_file:
        data = json.load(json_file)
    data_json = {}
    data_json["site_id"] = site_id
    data_json["amount"] = amount
    data_json["end_time"] = end_time
    data_json["target"] = target
    data.append(data_json)
    with open(timers_file, 'w') as outfile:
        json.dump(data, outfile)

def add_alarm(site_id, hour, target):
    handle_file(alarms_file)
    with open(alarms_file) as json_file:
        data = json.load(json_file)
    data_json = {}
    data_json["site_id"] = site_id
    data_json["hour"] = hour
    data_json["target"] = target
    data.append(data_json)
    with open(alarms_file, 'w') as outfile:
        json.dump(data, outfile)

def remove_timer(site_id, amount, end_time, target):
    handle_file(timers_file)
    with open(timers_file) as json_file:
        data = json.load(json_file)
        new_data = []
        for timer in data:
            if site_id != timer['site_id'] and amount != timer['amount'] and end_time != timer['end_time']:
                new_data.append(timer)
        with open(timers_file, 'w') as outfile:
            json.dump(new_data, outfile)

def get_intent_amount(x):
    if isinstance(x, int):
        return x
    else:
      try:
          return float(x.replace(" i pół", ".5"))
      except ValueError:
          return {
              "pół": 0.5,
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
    object = intent_message.slots
    object_methods = [method_name for method_name in dir(object)
                  if callable(getattr(object, method_name))]
#    pprint(object_methods)
#    pprint(intent_message.slots.items())
#    pprint(intent_message.slots.values())
    for x in range(slots_count):
        slots.append(intent_message.slots.location[x].slot_value.value.value)
    return slots

def get_hours(intent_message):
    slots = []
    if (intent_message.slots is None):
        return slots
    slots_count = len(intent_message.slots.hour)
    for x in range(slots_count):
        slots.append(intent_message.slots.hour[x].slot_value.value.value)
    return slots

def get_targets(intent_message):
    slots = []
    if (intent_message.slots is None):
        return slots
    slots_count = len(intent_message.slots.time_target)
    for x in range(slots_count):
        slots.append(intent_message.slots.time_target[x].slot_value.value.value)
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

def get_amount_say_string(amount):
    amount_say = get_amount_say(amount)
    text_all = ""
    for num, text in enumerate(amount_say, start=1):
        if num == 1:
            text_all = text_all + text
        elif num != len(amount_say):
            text_all = text_all + ", " + text
        else:
            text_all = text_all + ", " + text
    return text_all

def get_local_datetime(utc_time = None, format = "%Y-%m-%d %H:%M:%S"):
  if utc_time is None:
    utc_time = time.gmtime()
  utc_time_h_m = time.strftime("%Y-%m-%d %H:%M:%S+00:00", utc_time)
  from_zone = tz.tzutc()
  to_zone = tz.tzlocal()
  utc = datetime.datetime.strptime(utc_time_h_m, "%Y-%m-%d %H:%M:%S+00:00")
  utc = utc.replace(tzinfo=from_zone)
  local = utc.astimezone(to_zone)
  return_time = local.strftime(format)
#  print(return_time)
  return return_time
