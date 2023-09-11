#!/usr/bin/env python
from socket import socket, AF_PACKET, SOCK_RAW
import struct

s = socket(AF_PACKET, SOCK_RAW)
s.bind(("eth0", 0))

payload = "TESTEEEEE"

#! =============================================================
#? Ethernet header

src_addr = "\x00\x15\x5d\x57\x95\x09"
dst_addr = "\x00\x15\x5d\x57\x95\x09"
ethertype = "\x80\x00"

header_ethernet = struct.pack('!6s6s2s', dst_addr.encode(), src_addr.encode(), ethertype.encode())
#! =============================================================
#? IP header

vers_ihl = "\x45" 
type = "\x00"
total_length = "\x00\x54" # 84 bytes
identification = "\x00\x00"
flags_fo = "\x00\x00"
ttl = "\x40" # 64
protocol = "\x11" # UDP
header_checksum = "\x00\x00" # will be filled later
src_addr = "\xac\x14\x2d\x30" # 172.20.45.48
dst_addr = "\xac\x14\x2d\x30"

header_ip = struct.pack(
    '!1s1s2s2s2s1s1s2s4s4s',
    vers_ihl.encode(),
    type.encode(),
    total_length.encode(),
    identification.encode(),
    flags_fo.encode(),
    ttl.encode(),
    protocol.encode(),
    header_checksum.encode(),
    src_addr.encode(),
    dst_addr.encode()
    )
#! =============================================================
#? UDP header

# port = 12000
src_port = "\x2e\xe0" # 12000
dst_port = "\x2e\xe0" # 12000
length = "\x00\x34" # 52 bytes
checksum = "\x00\x00" # will be filled later

header_udp = struct.pack(
    '!2s2s2s2s',
    src_port.encode(),
    dst_port.encode(),
    length.encode(),
    checksum.encode()
    )
#! =============================================================


s.send(header_ethernet + header_ip + header_udp + payload.encode())