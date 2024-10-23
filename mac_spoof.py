import subprocess
import re

def get_current_mac(interface):
    try:
        # Get the result of the ifconfig command for the interface
        ifconfig_result = subprocess.check_output(["ifconfig", interface]).decode('utf-8')
        # Regex to match the MAC address pattern
        mac_address_search = re.search(r"(\w\w:\w\w:\w\w:\w\w:\w\w:\w\w)", ifconfig_result)
        if mac_address_search:
            return mac_address_search.group(0)
        else:
            print("Could not read MAC address.")
    except subprocess.CalledProcessError:
        print(f"Failed to get MAC address for {interface}. Make sure the interface exists.")

def change_mac(interface, new_mac):
    try:
        # Disable the network interface
        print(f"Disabling {interface}...")
        subprocess.call(["sudo", "ifconfig", interface, "down"])
        # Change the MAC address
        print(f"Changing MAC address for {interface} to {new_mac}...")
        subprocess.call(["sudo", "ifconfig", interface, "hw", "ether", new_mac])
        # Re-enable the network interface
        subprocess.call(["sudo", "ifconfig", interface, "up"])
        print(f"MAC address for {interface} changed successfully.")
    except subprocess.CalledProcessError:
        print(f"Failed to change MAC address for {interface}. Make sure you have proper permissions.")

def verify_mac_change(interface, new_mac):
    current_mac = get_current_mac(interface)
    if current_mac == new_mac:
        print(f"MAC address successfully changed to {new_mac}")
    else:
        print(f"Failed to change MAC address. Current MAC: {current_mac}")

# User input for network interface and desired MAC address
interface = input("Enter the network interface (e.g., eth0, wlan0): ")
new_mac = input("Enter the new MAC address (e.g., 00:11:22:33:44:55) : ")

# Display current MAC address
current_mac = get_current_mac(interface)
print(f"Current MAC address: {current_mac}")

# Change MAC address
change_mac(interface, new_mac)

# Verify if the MAC address has changed
verify_mac_change(interface, new_mac)


