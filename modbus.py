import socket, struct, threading

def recv_exact(sock, n):
    data = b''
    while len(data) < n:
        chunk = sock.recv(n-len(data))
        if not chunk:
            raise ConnectionError('Modbus connection closed')
        data += chunk
    return data

class Gateway:
    def __init__(self, host, port=502):
        self.host, self.port = host, port
        self.lock = threading.Lock()
        self.tid = 0

    def request(self, unit, function, address, value):
        with self.lock:
            self.tid = (self.tid + 1) & 65535
            pdu = struct.pack('>BHH', function, address, value)
            with socket.create_connection((self.host, self.port), timeout=2) as s:
                s.sendall(struct.pack('>HHHB', self.tid, 0, 6, unit)+pdu)
                tid, proto, length, uid = struct.unpack('>HHHB', recv_exact(s, 7))
                if (tid, proto, uid) != (self.tid, 0, unit) or not 2 <= length <= 254:
                    raise ValueError('Invalid MBAP')
                reply = recv_exact(s, length-1)
            if reply[0] != function:
                raise ValueError('Modbus exception: '+reply.hex())
            if function == 3:
                if reply[1] != value*2 or len(reply) != 2+value*2:
                    raise ValueError('Invalid register reply')
                return list(struct.unpack('>'+('H'*value), reply[2:]))
            if reply != pdu:
                raise ValueError('Write echo mismatch')
            return True

    def read(self, unit):
        return self.request(unit, 3, 0, 8)

    def write(self, unit, address, value):
        return self.request(unit, 6, address, value)
