import random
import os

DEVICE_PREFIXES = {
    "smartwatch": "00:1A:7D",  # Example prefix (e.g., Apple)
    "earbuds": "40:4E:36",     # Example prefix (e.g., ASUSTek)
    "desktop": "00:1B:63",     # Example prefix (e.g., Cisco)
    "phone": "8C:2D:AA",       # Example prefix (e.g., Apple)
}

def generate_random_mac(device_type=None):
    """
    Generate a random MAC address.
    If device_type is provided and known, use its specific prefix.
    Otherwise, generate a MAC address with a locally administered prefix.
    """
    if device_type and device_type in DEVICE_PREFIXES:
        prefix_parts = DEVICE_PREFIXES[device_type].split(':')
        if len(prefix_parts) == 3:
            return "%s:%s:%s:%02x:%02x:%02x" % (
                prefix_parts[0],
                prefix_parts[1],
                prefix_parts[2],
                random.randint(0x00, 0xff),
                random.randint(0x00, 0xff),
                random.randint(0x00, 0xff)
            )
        else:
            # This print will only show if generate_random_mac is called with a known but malformed device_type
            # and mac_gen.py is run directly. If imported, the caller (mac_spoof.py) won't see this print.
            print(f"Warning: Malformed prefix for device type '{device_type}'. Falling back to default.")

    return "02:%02x:%02x:%02x:%02x:%02x" % (
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff)
    )

if __name__ == "__main__":
    os.system('clear')
    os.system('toilet --gay "MAC-Sp00fer-Pr0"') # This will still run if toilet is not installed, showing an error
    print("Tool by: https://github.com/gaur-avvv")
    print("\n--- Generating MAC Addresses (Examples from mac_gen.py) ---")

    new_mac_random = generate_random_mac()
    print(f"Generated random MAC address (default): {new_mac_random}")

    new_mac_phone = generate_random_mac("phone")
    print(f"Generated phone MAC address: {new_mac_phone}")

    new_mac_smartwatch = generate_random_mac("smartwatch")
    print(f"Generated smartwatch MAC address: {new_mac_smartwatch}")

    new_mac_earbuds = generate_random_mac("earbuds")
    print(f"Generated earbuds MAC address: {new_mac_earbuds}")

    new_mac_desktop = generate_random_mac("desktop")
    print(f"Generated desktop MAC address: {new_mac_desktop}")

    new_mac_unknown = generate_random_mac("unknown_device_type")
    print(f"Generated MAC for unknown device type: {new_mac_unknown}")

    # Test for malformed prefix handling
    # Temporarily add a malformed prefix to test the warning and fallback
    # Note: The warning in generate_random_mac for malformed prefixes will be printed here.
    DEVICE_PREFIXES["test_malformed"] = "XX:YY"
    new_mac_malformed = generate_random_mac("test_malformed")
    print(f"Generated MAC for malformed prefix test: {new_mac_malformed}")
    # Clean up by removing the test entry
    if "test_malformed" in DEVICE_PREFIXES:
        del DEVICE_PREFIXES["test_malformed"]

    print("--------------------------------\n")
