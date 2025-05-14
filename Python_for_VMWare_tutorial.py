#
#   Intention here is to introduce REST API to VMWare experts.
#   The best way to learn Python, REST and AI code generating capabilities
#   is to paste this script into ChatGPT after typing the question:  what does
#   this code do and how do I use it?  
#   The AI will explain it to you and tell you how to setup a Python environment
#   so you can run this script on your vCenter.
#
#   You will need to install Python and an IDE to use the code.  IDLE is an
#   excellent IDE and often installs with Python.
#
#   The code makes a REST call to vCenter and gets the vmids, machine names and
#   network card type and prints them to a csv.  The functionality does not 
#   compete with Aria.  REST allows VMWare to connect to complimentary prodcuts
#   like Team Dynamix Asset Managers.  Power users can write programs that
#   interface with Cisco, Oracle and other products.  
#
#   Output goes to a csv file and contains three columns:  vm_id,vm_name,nic_type
#   
#   This will give you tools and some insight into using Python, REST and VMWare!!
#

import requests
import urllib3
import json
import csv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://your.vcenter.org/api"    #  <<-- your VMWare REST endpoint
USERNAME = "username"    # <<-- your VMWare user name
PASSWORD = "password"

def get_session_id():
    url = f"{BASE_URL}/session"
    response = requests.post(url, auth=(USERNAME, PASSWORD), verify=False)
    response.raise_for_status()
    return response.json()

def get_powered_on_vms(session_id):
    url = f"{BASE_URL}/vcenter/vm"
    headers = {"vmware-api-session-id": session_id}
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    vms = response.json()
    return [vm for vm in vms if vm.get("power_state") == "POWERED_ON"]

def get_vm_nics(session_id, vm_id):
    url = f"{BASE_URL}/vcenter/vm/{vm_id}/hardware/ethernet"
    headers = {"vmware-api-session-id": session_id}
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    return response.json()

def get_vm_nic_type(session_id, vm_id, nic_id):
    url = f"{BASE_URL}/vcenter/vm/{vm_id}/hardware/ethernet/{nic_id}"
    headers = {"vmware-api-session-id": session_id}
    response = requests.get(url, headers=headers, verify=False)
    if response.status_code == 200:
        return response.json().get("type", "UNKNOWN")
    return "UNKNOWN"

def main():
    session_id = get_session_id()
    powered_on_vms = get_powered_on_vms(session_id)
    results = []

    for vm in powered_on_vms:
        vm_id = vm.get("vm")
        vm_name = vm.get("name")

        try:
            nic_list = get_vm_nics(session_id, vm_id)
            for nic in nic_list:
                nic_id = nic.get("nic")
                nic_type = get_vm_nic_type(session_id, vm_id, nic_id)
                results.append({
                    "vm_id": vm_id,
                    "vm_name": vm_name,
                    "nic_type": nic_type
                })
        except Exception as e:
            print(f"Failed to get NICs for {vm_name} ({vm_id}): {e}")
            results.append({
                "vm_id": vm_id,
                "vm_name": vm_name,
                "nic_type": "UNKNOWN"
            })

    # Write to CSV
    with open("nic_report.csv", mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["vm_id", "vm_name", "nic_type"])
        writer.writeheader()
        writer.writerows(results)

    print("nic_report.csv written successfully.")

if __name__ == "__main__":
    main()
