import requests
import json
import time
import os
import datetime
import beepy

def make_sound_loop():
    print("Found a SPOT")
    try:
        while True:
            beepy.beep(sound=1)
    except KeyboardInterrupt:
        print('interrupted!')

def print_states():
    url = 'https://cdn-api.co-vin.in/api/v2/admin/location/states'
    header = {
            "accept": "application/json",
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        }
    res = requests.get(url, headers=header)
    if (res.status_code == 200):
        print("Select State -- ")
        count = 1
        state_list = res.json()['states']
        for state in state_list:
            state_name = state['state_name']
            print(f'{count} : {state_name}')
            count += 1
        sec = int(input("\nSelect an option: "))
        try:
            return state_list[sec-1]['state_id']
        except IndexError as e:
            print("Incorrect option selected, try again!!\n")
            return print_states()


def print_district(state_id):
    url = 'https://cdn-api.co-vin.in/api/v2/admin/location/districts/' + str(state_id)
    header = {
            "accept": "application/json",
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        }
    res = requests.get(url, headers=header)
    if (res.status_code == 200):
        print("Select District -- ")
        count = 1
        district_list = res.json()['districts']
        for district in district_list:
            district_name = district['district_name']
            print(f'{count} : {district_name}')
            count += 1
        sec = int(input("\nSelect an option : "))
        try:
            return district_list[sec-1]['district_id']
        except IndexError as e:
            print("Incorrect option selected, try again!!\n")
            return print_states()

def print_date():
    format = "%d-%m-%Y"
    input_date = input("Select Date(DD-MM-YYYY) : ")
    try:
        datetime.datetime.strptime(input_date, format)
        return input_date
    except ValueError:
        print("This is the incorrect date string format. It should be YYYY-MM-DD")
        return print_date()

def print_age():
    age_dict = {1:18, 2:45}
    print("Select Age - \n 1 : Above 18\n 2 : Above 45")
    input_age = int(input("\nSelect an option : "))
    age = age_dict.get(input_age)
    if age is None:
        print("Incorrect option selected, try again!!\n")
        return print_age()
    return age

def run():
    print(">>>>>> WELCOME TO COWIN ALERT BOT <<<<<<<<\n")
    state_id = print_states()
    district_id = print_district(state_id)
    date = print_date()
    age = print_age()
    url = f'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict?district_id={district_id}&date={date}'
    etag = None
    print("Now Sit back and relax, we will play a sound when slot opens up, cheers!!")
    print("Note - Press CTRL+C to stop the program")
    output_str = []
    found_flag = False
    try:
        while True:
            header = {
                "If-None-Match" : etag,
                "accept": "application/json",
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
            }
            r = requests.get(url, headers=header)
            if (r.status_code == 200):
                etag = r.headers['etag']
                data = r.json()
                for point in data['sessions']:
                    if point['min_age_limit'] == age and point['available_capacity'] > 0:
                        found_flag=True
                        point_name = point['name']
                        point_address = point['address']
                        dose1_slot = point['available_capacity_dose1']
                        dose2_slot = point['available_capacity_dose2']
                        fee = point['fee']
                        vaccine = point['vaccine']
                        output_str.append(f'1. \n name: {point_name}\naddress: {point_address}\ndose1 capacity: {dose1_slot}\ndose2 capacity: {dose2_slot}\nfee: {fee}\nvaccine: {vaccine}')
            if found_flag:
                break
            time.sleep(5)
    except KeyboardInterrupt:
        print('interrupted!')
    else:
        print("location names with Open slots -")
        for slot in output_str:
            print(slot)
        make_sound_loop()

run()