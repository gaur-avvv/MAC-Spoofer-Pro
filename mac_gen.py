import random

import os
os.system('clear')
os.system('toilet -f slant --gay "mac-spoofer-pro"')
print("Tool by: @gaur-avvv")



def generate_random_mac():
    """Generate a random MAC address with locally administered address prefix."""
    return "02:%02x:%02x:%02x:%02x:%02x" % (
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff)
    )

# Example usage:
new_mac = generate_random_mac()
print(f"Generated random MAC address: {new_mac}")