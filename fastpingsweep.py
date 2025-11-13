import socket
import struct
import ipaddress
import sys
import threading

def ping(host):
    with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP) as s:
        try:
            s.settimeout(2)

            pre_checksum_header = struct.pack('!BBHHH', 8, 0, 0, 1234, 1)
            payload = b'ping'
            pre_checksum_packet = pre_checksum_header + payload

            checksum = calculate_checksum(pre_checksum_packet)
            header = struct.pack('!BBHHH', 8, 0, checksum, 1234, 1)
            packet = header + payload

            s.sendto(packet, (host, 0))

            while True:
                resp, addr = s.recvfrom(128)
                src_ip = addr[0]

                if src_ip != host:
                    continue

                icmp_header = resp[20:28]
                icmp_type, code, recv_checksum, recv_id, recv_seq = struct.unpack('!BBHHH', icmp_header)

                if icmp_type == 0 and code == 0 and recv_id == 1234:
                    print(host)
                    break

        except:
            pass

def calculate_checksum(packet):
    checksum = 0
    count_to = (len(packet) // 2) * 2
    for i in range(0, count_to, 2):
        checksum += (packet[i] << 8) + packet[i+1]
    if count_to < len(packet):
        checksum += packet[len(packet) - 1]
    checksum &= 0xffffffff
    checksum = (checksum >> 16) + (checksum & 0xffff)
    checksum += (checksum >> 16)
    return ~checksum & 0xffff

network = ipaddress.ip_network(sys.argv[1])

threads = []
for host in network.hosts():
    t = threading.Thread(target=ping, args=[str(host)])
    threads.append(t)
    t.start()

for t in threads:
    t.join()
