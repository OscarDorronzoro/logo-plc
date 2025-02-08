from scapy.all import ARP, Ether, srp

def lookup_ip_address(mac_address):
    arp_request = ARP(pdst='192.168.6.0/24') # Network
    ether = Ether(dst='ff:ff:ff:ff:ff:ff')
    packet = ether/arp_request

    result = srp(packet, timeout=2, verbose=0)[0]

    for sent, received in result:
        if received.hwsrc.lower() == mac_address.lower():
            return received.psrc

    return None


default_ip = '192.168.6.2'
mac_phone = 'b6:e4:b1:c8:05:b1'

actual_ip = lookup_ip_address(mac_phone)
if actual_ip:
    print(actual_ip)
else:
    print(default_ip)


