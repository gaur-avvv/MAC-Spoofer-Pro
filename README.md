# MAC-Spoofer-Pro
mac-spoofer-pro is a simple yet powerful Python tool designed to spoof (change) the MAC address of network interfaces on Linux-based systems. The tool allows you to set a custom MAC address, generate a random MAC address of a network interface.

# Requirement:
Install git
```
apt install git
```
Install toilet
```
sudo apt install toilet
```
Install python3
```
apt update && upgrade
```

# Installation:
Clone from Github
```
git clone https://github.com/gaur-avvv/MAC-Spoofer-Pro
cd MAC-Spoofer-Pro
python3 mac_gen.py
```
![Screenshot_2024-10-23_13_45_45](https://github.com/user-attachments/assets/a204fa74-c58b-490e-ad6f-3ea655c6756b)

Now A random mac address get generated copy that mac address
Now run this command

```
sudo python3 mac_spoof.py
```
![Screenshot_2024-10-23_13_47_50](https://github.com/user-attachments/assets/db1ab7b5-f423-4c57-ab99-d307e2aa4d41)

* if you are using kali-linux in vm then choose _eth0_
* else choose _wlan0_

If you want to check your original mac address run this command and copy original mac address if you want to restore it earlier
```
ifconfig | grep ether
```


