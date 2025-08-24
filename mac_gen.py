import random

import os
os.system('clear')
os.system('toilet --gay "MAC-Sp00fer-Pr0"')
print("Tool by: https://github.com/gaur-avvv")



def generate_random_mac():
    """Generate a random MAC address with locally administered address prefix."""
    return "02:%02x:%02x:%02x:%02x:%02x" % (
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff)
    )

#example usage:
new_mac = generate_random_mac()
print(f"Generated random MAC address: {new_mac}")
