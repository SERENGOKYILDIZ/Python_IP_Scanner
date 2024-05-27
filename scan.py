import os
import socket
import subprocess
import uuid
import re
import concurrent.futures


class IP_SCANNER:
    devices = []
    my_ip = ""
    my_mac = ""
    my_hostname = ""
    my_octets = ""

    def __init__(self):
        self.devices = []
        self.my_ip = ""
        self.my_mac = ""
        self.my_hostname = ""
        
        self.get_my_hostname()
        self.get_my_ip()
        self.get_my_mac()
        self.get_first_three_octets()
        
        self.print_me()

    def get_my_ip(self):
        ip_addresses = socket.getaddrinfo(self.my_hostname, None)

        # IPv4 adresini bul
        for addr in ip_addresses:
            if addr[0] == socket.AF_INET:
                self.my_ip = addr[4][0]
                break

    def get_my_mac(self):
        self.my_mac = ':'.join(
            ['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2 * 6, 2)][::-1])

    def get_my_hostname(self):
        self.my_hostname = socket.gethostname()

    def print_me(self):
        print(f"MY IP       : {self.my_ip}")
        print(f"MY MAC      : {self.my_mac}")
        print(f"MY HOSTNAME : {self.my_hostname}")
        print(f"MY Octets   : {self.my_octets}")

    def get_first_three_octets(self):
        match = re.match(r"(\d+\.\d+\.\d+)\.\d+", self.my_ip)
        if match:
            self.my_octets = match.group(1)

    def get_hostname(self, ip):
        try:
            host = socket.gethostbyaddr(ip)
            return host[0]
        except socket.herror:
            return "NULL"

    def ping_ip(self, ip):
        try:
            # Windows için
            completed_process = subprocess.run(
                ['ping', '-n', '1', ip],  # Linux/macOS için ['ping', '-c', '1', ip]
                capture_output=True,
                text=True
            )
            if completed_process.returncode == 0:
                return f"{ip} erişilebilir."
            else:
                return f"{ip} erişilemez. Hata: {completed_process.stderr.strip()}"
        except subprocess.CalledProcessError as e:
            return f"{ip} erişilemez. Hata: {str(e)}"

    # IP aralığını belirleyen fonksiyon
    def generate_ip_range(self, start, end):
        return [f"{self.my_octets}.{i}" for i in range(start, end + 1)]

    def get_ips(self):
        start_ip = 1  # Başlangıç IP (son oktet)
        end_ip = 254  # Bitiş IP (son oktet)

        ip_list = self.generate_ip_range(start_ip, end_ip)

        # Eşzamanlı olarak ping işlemi gerçekleştirme
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            results = list(executor.map(self.ping_ip, ip_list))

        self.get_devices()
        # # Sonuçları yazdır
        # for result in results:
        #     print(result)

    def get_devices(self):
        start_ip = 1  # Başlangıç IP (son oktet)
        end_ip = 254  # Bitiş IP (son oktet)
        ipler = []
        macler = []

        # arp -a komutunu çalıştır ve çıktıyı oku
        output = os.popen('arp -a').read()

        output = output.split()

        i = 0
        for i in range(len(output)):
            if output[i].startswith(self.my_ip):
                break
        print(f"İp adresimiz : {i} indexsinde")
        for k in range(i, len(output)):
            if output[k] == "dynamic":
                ipler.append(output[k - 2])
                macler.append(output[k - 1].replace("-",":"))

        ip_list = self.generate_ip_range(start_ip, end_ip)

        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            hostnameler = list(executor.map(self.get_hostname, ipler))

        ipler.insert(0, self.my_ip)
        macler.insert(0, self.my_mac)
        hostnameler.insert(0, self.my_hostname)

        print(f"İP adres     : {self.my_ip}")
        print(f"İP adresler  : {ipler}")
        print(f"MAC adresler : {macler}")
        print(f"Hostnameler   : {hostnameler}")

        for num in range(len(macler)):
            new_dict = {"ip": ipler[num], "mac": macler[num], "hostname": hostnameler[num]}
            self.devices.append(new_dict)

        print(self.devices)


ip = IP_SCANNER()
ip.get_ips()

input()
