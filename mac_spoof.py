#!/usr/bin/env python3
import subprocess
import re
import argparse
import os
import sys # For sys.exit

# Attempt to import from mac_gen.py
try:
    from mac_gen import generate_random_mac, DEVICE_PREFIXES
except ImportError as e:
    print(f"Error: Could not import from mac_gen.py. Make sure it's in the same directory. Details: {e}")
    sys.exit(1)

ORIGINAL_MAC_FILE_TEMPLATE = ".original_mac_{}.txt"

def get_original_mac_filepath(interface):
    """Generates the filepath for storing the original MAC address."""
    if not re.match(r"^[a-zA-Z0-9_-]+$", interface):
        print(f"Error: Invalid interface name format '{interface}'.")
        return None
    return ORIGINAL_MAC_FILE_TEMPLATE.format(interface)

def save_original_mac(interface, original_mac):
    """Saves the original MAC address to a file."""
    filepath = get_original_mac_filepath(interface)
    if not filepath:
        return False
    try:
        with open(filepath, "w") as f:
            f.write(original_mac)
        print(f"Original MAC address {original_mac} for {interface} saved to {filepath}")
        return True
    except IOError as e:
        print(f"Error: Could not save original MAC address to {filepath}. {e}")
        return False

def read_original_mac(interface):
    """Reads the original MAC address from a file."""
    filepath = get_original_mac_filepath(interface)
    if not filepath:
        return None
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, "r") as f:
            mac = f.read().strip()
            if not mac:
                print(f"Warning: Original MAC file {filepath} is empty.")
                return None
            return mac
    except IOError as e:
        print(f"Error: Could not read original MAC address from {filepath}. {e}")
        return None

def get_current_mac(interface):
    """Gets the current MAC address of the specified interface."""
    try:
        ifconfig_result = subprocess.check_output(["ifconfig", interface], stderr=subprocess.STDOUT).decode('utf-8')
        mac_address_search = re.search(r"(\w\w:\w\w:\w\w:\w\w:\w\w:\w\w)", ifconfig_result)
        if mac_address_search:
            return mac_address_search.group(0)
        else:
            print(f"Could not read MAC address from ifconfig output for {interface}. Check if the interface has a MAC address configured.")
            return None
    except subprocess.CalledProcessError as e:
        output_str = e.output.decode('utf-8', errors='ignore') if e.output else "No output captured."
        print(f"Error: Failed to get MAC for {interface}. Command 'ifconfig {interface}' failed. Output: {output_str}")
        return None
    except FileNotFoundError:
        print("Error: 'ifconfig' command not found. Please ensure it's installed and in your PATH.")
        return None

def change_mac(interface, new_mac):
    """Changes the MAC address for the given interface."""
    print(f"Attempting to change MAC for {interface} to {new_mac}...")
    try:
        print(f"Disabling {interface}...")
        subprocess.check_call(["sudo", "ifconfig", interface, "down"], stderr=subprocess.STDOUT)
        print(f"Changing MAC address for {interface} to {new_mac}...")
        subprocess.check_call(["sudo", "ifconfig", interface, "hw", "ether", new_mac], stderr=subprocess.STDOUT)
        print(f"Enabling {interface}...")
        subprocess.check_call(["sudo", "ifconfig", interface, "up"], stderr=subprocess.STDOUT)
        print(f"MAC address for {interface} should now be changed to {new_mac}.")
        return True
    except subprocess.CalledProcessError as e:
        error_message = f"Error: Failed to change MAC for {interface}. Command '{' '.join(e.cmd)}' returned non-zero exit status {e.returncode}."
        print(error_message)
        print("Make sure you have 'sudo' permissions, the interface exists, and the MAC format is correct.")
        return False
    except FileNotFoundError:
        print("Error: 'sudo' or 'ifconfig' command not found. Please ensure they are installed and in your PATH.")
        return False

def verify_mac_change(interface, expected_mac):
    """Verifies if the MAC address was changed successfully."""
    print(f"Verifying MAC change for {interface}...")
    current_mac = get_current_mac(interface)
    if current_mac and current_mac.lower() == expected_mac.lower():
        print(f"SUCCESS: MAC address for {interface} is now {current_mac}.")
        return True
    else:
        print(f"FAILURE: MAC address change for {interface} failed or not yet effective.")
        print(f"Expected: {expected_mac}, Current: {current_mac if current_mac else 'Not found'}")
        return False

def restore_original_mac(interface):
    """Restores the original MAC address for the given interface."""
    print(f"Attempting to restore original MAC for {interface}...")
    original_mac = read_original_mac(interface)
    if original_mac:
        if change_mac(interface, original_mac):
            if verify_mac_change(interface, original_mac):
                print(f"Original MAC address successfully restored for {interface}.")
                filepath = get_original_mac_filepath(interface)
                if filepath and os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                        print(f"Cleaned up original MAC file: {filepath}")
                    except OSError as e:
                        print(f"Warning: Could not remove original MAC file {filepath}. {e}")
            else:
                print(f"Failed to verify restoration of original MAC for {interface}.")
        else:
            print(f"Failed to apply original MAC address for {interface}.")
    else:
        print(f"No original MAC address found saved for {interface}. Cannot restore.")

def main():
    parser = argparse.ArgumentParser(
        description="MAC Address Spoofer & Restorer. Allows setting a specific MAC, a random MAC based on device type, or restoring the original MAC.",
        formatter_class=argparse.RawTextHelpFormatter # To allow for better formatting of choices
    )
    parser.add_argument("interface", help="Network interface to manipulate (e.g., eth0, wlan0)")

    device_choices_help = "Choose a device type to generate a MAC address. Available types:\n" + \
                          "\n".join([f"  - {key}: {DEVICE_PREFIXES[key]}" for key in DEVICE_PREFIXES])

    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument("-m", "--new_mac", help="New MAC address to set (e.g., 00:11:22:33:44:55)")
    action_group.add_argument("-d", "--device_type", choices=DEVICE_PREFIXES.keys(),
                              help="Generate a MAC address for a specific device type.\n" + device_choices_help,
                              metavar="TYPE")
    action_group.add_argument("-r", "--restore", action="store_true", help="Restore the original MAC address")
    action_group.add_argument("-c", "--check", action="store_true", help="Check the current MAC address of the interface")

    args = parser.parse_args()

    if not args.interface: # Should be caught by argparse, but as a safeguard
        print("Error: Interface name is required.")
        parser.print_help()
        sys.exit(1)

    if not re.match(r"^[a-zA-Z0-9_-]+$", args.interface):
        print(f"Error: Invalid interface name format '{args.interface}'.")
        sys.exit(1)

    if args.check:
        print(f"Checking current MAC address for {args.interface}...")
        current_mac = get_current_mac(args.interface)
        if current_mac:
            print(f"Current MAC for {args.interface}: {current_mac}")
        else:
            print(f"Could not retrieve current MAC for {args.interface}.")

    elif args.new_mac or args.device_type:
        generated_new_mac = None
        if args.device_type:
            print(f"Preparing to spoof MAC for {args.interface} using device type: {args.device_type}...")
            if args.device_type not in DEVICE_PREFIXES: # Should be caught by choices, but good practice
                print(f"Error: Invalid device type '{args.device_type}'. Use --help to see available types.")
                sys.exit(1)
            generated_new_mac = generate_random_mac(args.device_type)
            print(f"Generated MAC for {args.device_type}: {generated_new_mac}")
        else: # args.new_mac must be set
            print(f"Preparing to spoof MAC for {args.interface} to {args.new_mac}...")
            # Validate explicit MAC address format
            if not re.match(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$", args.new_mac):
                print(f"Error: Invalid MAC address format: {args.new_mac}. Use XX:XX:XX:XX:XX:XX or XX-XX-XX-XX-XX-XX.")
                sys.exit(1)
            generated_new_mac = args.new_mac

        original_mac = get_current_mac(args.interface)
        if original_mac:
            print(f"Current (original) MAC for {args.interface}: {original_mac}")
            if original_mac.lower() == generated_new_mac.lower():
                print(f"Info: The new MAC address {generated_new_mac} is the same as the current MAC. No change needed.")
            else:
                if save_original_mac(args.interface, original_mac):
                    if change_mac(args.interface, generated_new_mac):
                        verify_mac_change(args.interface, generated_new_mac)
                else:
                    print(f"Halting spoofing process for {args.interface} due to failure saving original MAC.")
        else:
            print(f"Could not retrieve current MAC for {args.interface}. Cannot save original MAC. Proceeding with caution to change MAC to {generated_new_mac}.")
            if change_mac(args.interface, generated_new_mac):
                verify_mac_change(args.interface, generated_new_mac)

    elif args.restore:
        restore_original_mac(args.interface)

    else:
        print("Error: No action specified or invalid combination of arguments.")
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    if any(arg in sys.argv for arg in ["-m", "--new_mac", "-d", "--device_type", "-r", "--restore"]) and os.geteuid() != 0:
        print("Warning: This script requires sudo privileges to change MAC addresses.")
        print("You might be prompted for your password by 'sudo'.")
    main()
