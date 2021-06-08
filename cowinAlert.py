import requests
import json
import time
import os
import datetime
import beepy

# urls and headers
state_url = "https://cdn-api.co-vin.in/api/v2/admin/location/states"
district_url = "https://cdn-api.co-vin.in/api/v2/admin/location/districts/"
generate_otp_url = "https://cdn-api.co-vin.in/api/v2/auth/generateMobileOTP"
validate_otp_url = "https://cdn-api.co-vin.in/api/v2/auth/generateMobileOTP"
header = {
    "accept": "application/json",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
}


def read_variables():
    f = open(
        "variables.json",
    )
    data = json.load(f)
    state = data["state"]
    district = data["district"]
    date = data["date"]
    age = data["age"]
    alert_duration= data['sound_duration']
    polling_duration = data['polling_duration']
    vaccine = data['vaccine']
    dose = data['dose_number']
    f.close()
    return state, district, date, age, alert_duration, polling_duration, vaccine, dose


def get_otp(phone_number, secret):
    """
    generates otp and returns a tranxaction id
    """
    body_content = {"mobile": phone_number, "secret": secret}
    res = requests.post(generate_otp_url, data=body_content, headers=header)
    if res.status_code == 200:
        print("OTP HAS BEEN SENT")
        return res.json()["txnId"]


def validate_otp(txnid, encrypted_otp):
    """
    use txnid to confirm otp and return auth token
    """
    res = int(input("Please Enter the OTP : "))
    body_content = {"otp": encrypted_otp, "txnId": txnid}
    res = requests.post(validate_otp_url, data=body_content, headers=header)
    if res.status_code == 200:
        print("TOKEN HAS BEEN GENERATED")
        return res.json()["token"]


def make_sound_loop(alert_duration: 10):
    print("Found a SPOT")
    try:
        for i in range(alert_duration):
            beepy.beep(sound=1)
    except KeyboardInterrupt:
        print("interrupted!")


def print_states(state_nave_var: None):
    res = requests.get(state_url, headers=header)
    if res.status_code == 200:
        state_list = res.json()["states"]
        try:
            if state_nave_var is not None:
                for state in state_list:
                    if state["state_name"] == state_nave_var:
                        return state["state_id"]
            else:
                print("Select State -- ")
                count = 1
                for state in state_list:
                    state_name = state["state_name"]
                    print(f"{count} : {state_name}")
                    count += 1
                sec = int(input("\nSelect an option: "))
                return state_list[sec - 1]["state_id"]
        except IndexError as e:
            print("Incorrect option selected, try again!!\n")
            return print_states()
        except KeyError as e:
            print("Incorrect option selected, try again!!\n")
            return print_states()


def print_district(state_id, district_name_var: None):
    url = district_url + str(state_id)
    res = requests.get(url, headers=header)
    try:
        if res.status_code == 200:
            district_list = res.json()["districts"]
            if district_name_var is not None:
                for district in district_list:
                    if district_name_var == district["district_name"]:
                        return district["district_id"]
            else:
                print("Select District -- ")
                count = 1
                for district in district_list:
                    district_name = district["district_name"]
                    print(f"{count} : {district_name}")
                    count += 1
                sec = int(input("\nSelect an option : "))
                return district_list[sec - 1]["district_id"]
    except IndexError as e:
        print("Incorrect option selected, try again!!\n")
        return print_states()
    except KeyError as e:
        print("Incorrect option selected, try again!!\n")
        return print_states()


def print_date(input_date: None):
    format = "%d-%m-%Y"
    if input_date is None:
        input_date = input("Select Date(DD-MM-YYYY) : ")
    try:
        datetime.datetime.strptime(input_date, format)
        return input_date
    except ValueError:
        print("This is the incorrect date string format. It should be YYYY-MM-DD")
        return print_date()


def print_age(age: None):
    if age is not None and age == 18 or age == 45:
        return age
    age_dict = {1: 18, 2: 45}
    print("Select Age - \n 1 : Above 18\n 2 : Above 45")
    input_age = int(input("\nSelect an option : "))
    age = age_dict.get(input_age)
    if age is None:
        print("Incorrect option selected, try again!!\n")
        return print_age()
    return age


def run():
    print(">>>>>> WELCOME TO COWIN ALERT APP <<<<<<<<\n")
    print("Use variables.json file?")
    use_var = str(input("Choose Y/N : "))
    state = district = age = date = alert_duration = polling_duration = None
    if use_var.lower() == "y":
        state, district, date, age , alert_duration, polling_duration, vaccine, dose = read_variables()
    state_id = print_states(state)
    district_id = print_district(state_id, district)
    date = print_date(date)
    age = print_age(age)
    url = f"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict?district_id={district_id}&date={date}"
    etag = None
    print("Now Sit back and relax, we will play a sound when slot opens up, cheers!!")
    print("Note - Press CTRL+C to stop the program")
    output_str = []
    found_flag = False
    try:
        while True:
            header["If-None-Match"] = etag
            r = requests.get(url, headers=header)
            if r.status_code == 200:
                etag = r.headers["etag"]
                data = r.json()
                count = 1
                for point in data["sessions"]:
                    if (point["min_age_limit"] == age and point["available_capacity"] > 0 and vaccine == point['vaccine'] and point[f'available_capacity_dose{dose}'] > 0):
                        found_flag = True
                        point_name = point["name"]
                        point_address = point["address"]
                        dose_slot = point[f'available_capacity_dose{dose}']
                        fee = point["fee"]
                        vaccine = point["vaccine"]
                        output_str.append(
                            f"{count}. \nName: {point_name}\nAddress: {point_address}\nDose-{dose} Capacity: {dose_slot}\nFee: {fee}\nVaccine: {vaccine}"
                        )
                        count += 1
            if found_flag:
                found_flag = False
                print(".....................................")
                print("location names with Open slots -")
                for slot in output_str:
                    print(slot)
                print(".....................................")
                make_sound_loop(alert_duration)
            time.sleep(5 if polling_duration is None else polling_duration)
    except KeyboardInterrupt:
        print("interrupted!")


if __name__ == "__main__":
    run()
