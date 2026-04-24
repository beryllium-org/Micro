from ipaddress import ip_address
import wifi
from socketpool import SocketPool
from ssl import create_default_context
from adafruit_requests import Session
from cptoml import fetch


class driver_wifi:
    """
    Beryllium OS network driver for the built in wifi module
    Usage: modprobe driver_wifi as network
    """

    def __init__(self):
        # internal use only
        self._pool = None
        self._session = None
        self._tz = None
        self._ntp = None
        self._ssid = None

        # public
        self.error = False
        self.hw_name = "wifi"
        self.interface_type = "wifi"

        if wifi.radio.connected or wifi.radio.ap_active:
            # We need to inherit connection
            self._pool = SocketPool(wifi.radio)
            self._session = Session(self._pool, create_default_context())

    @property
    def enabled(self) -> bool:
        return wifi.radio.enabled

    @property
    def connected(self) -> bool:
        return wifi.radio.connected

    @property
    def ap_connected(self) -> bool:
        return wifi.radio.ap_active

    @property
    def mode(self) -> None:
        if wifi.radio.ap_active:
            if wifi.radio.connected:
                return "both"
            else:
                return "hotspot"
        elif wifi.radio.connected:
            return "station"
        else:
            return "disconnected"

    def _update(self) -> None:
        if (not wifi.radio.connected) and self._ssid:
            self._ssid = None
            self.disconnect()

    def connect(self, ssid: str, passwd=None, retries: int = 3) -> bool:
        """
        Connect to a wifi access point
        """

        if retries < 1:
            retries = 1
        fails = 0
        while fails is not retries:
            self.disconnect_ap()
            self.disconnect()

            try:
                if passwd:
                    wifi.radio.connect(ssid=ssid, password=passwd)
                else:
                    wifi.radio.connect(ssid=ssid)
                break
            except:
                fails += 1
        if fails is retries:
            self.disconnect()
            return False
        self._pool = SocketPool(wifi.radio)
        self._session = Session(self._pool, create_default_context())
        self._ssid = ssid
        return True

    def connect_ap(self, ssid: str, passwd=None) -> bool:
        """
        Create an AP.
        """

        self.disconnect_ap()
        try:
            if passwd:
                wifi.radio.start_ap(ssid=ssid, password=passwd)
            else:
                wifi.radio.start_ap(ssid=ssid)
        except:
            return False
        self._pool = SocketPool(wifi.radio)
        self._session = Session(self._pool, create_default_context())
        return True

    def hostname(self, name=None) -> str:
        if name is not None:
            wifi.radio.hostname = name
        return wifi.radio.hostname

    def ping(self, host=str):
        """
        ICMP Ping
        """
        return wifi.radio.ping(self.resolve(host))

    def get(self, host: str, timeout: int = 6):
        """
        HTTP Get
        """
        if self._session is not None:
            if not ((host.startswith("http://") or host.startswith("https://"))):
                host = "http://" + host

            return self._session.get(host, timeout=timeout)
        else:
            return None

    def resolve(self, host: str):
        """
        Resolve ip string, to something usable
        No domain resolves just yet
        """
        if host.startswith("https://"):
            host = host[8:]
        elif host.startswith("http://"):
            host = host[7:]
        try:
            return ip_address(self._pool.getaddrinfo(host, 0)[0][4][0])
        except OSError:
            raise ConnectionError

    def scan(self) -> dict:
        """
        scan and store all nearby networks
        """
        if wifi.radio.enabled:
            net = {}
            for network in wifi.radio.start_scanning_networks():
                sec = None
                if len(network.authmode) is 3:
                    sec = str(network.authmode[0])
                    sec = sec[sec.rfind(".") + 1 :]
                else:
                    sec = "Unknown"
                net.update({network.ssid: [sec, network.rssi]})
                del sec
            wifi.radio.stop_scanning_networks()
            return net

        return list()

    def get_ipconf(self) -> dict:
        """
        A getter for all of the wifi data
        iwconfig will need this
        """
        data = {
            "ssid": None,
            "bssid": None,
            "channel": None,
            "country": None,
            "ip": wifi.radio.ipv4_address,
            "ip_ap": wifi.radio.ipv4_address_ap,
            "power": str(wifi.radio.enabled),
            "gateway": (
                wifi.radio.ipv4_gateway
                if not wifi.radio.ap_active
                else wifi.radio.ipv4_gateway_ap
            ),
            "mode": self.mode,
            "ssid": self._ssid,
            "dns": wifi.radio.ipv4_dns,
            "subnet": wifi.radio.ipv4_subnet,
            "subnet_ap": wifi.radio.ipv4_subnet_ap,
            "mac": wifi.radio.mac_address,
            "mac_ap": wifi.radio.mac_address_ap,
            "mac_pretty": ":".join(
                "{:02x}".format(byte) for byte in wifi.radio.mac_address
            ),
            "mac_pretty_ap": ":".join(
                "{:02x}".format(byte) for byte in wifi.radio.mac_address_ap
            ),
            "hostname": wifi.radio.hostname,
        }

        try:
            data["bssid"] = wifi.radio.ap_info.bssid
            data["channel"] = wifi.radio.ap_info.channel
            data["country"] = wifi.radio.ap_info.country
        except:
            data["bssid"] = None
            data["channel"] = None
            data["country"] = None

        return data

    def reset(self) -> None:
        self.disconnect()
        self.disconnect_ap()

    def disconnect(self) -> None:
        """
        Disconnect from the wifi
        """
        while wifi.radio.connected:
            wifi.radio.stop_station()
        wifi.radio.stop_scanning_networks()

        if wifi.radio.ap_active:
            return

        try:
            wifi.radio.enabled = False
        except:
            pass

        from time import sleep

        sleep(0.5)

        try:
            wifi.radio.enabled = True
        except:
            pass

        del self._pool, self._session
        self._pool = None
        self._session = None

    def disconnect_ap(self) -> None:
        """
        Disconnect from the wifi ap
        """
        while wifi.radio.ap_active:
            wifi.radio.stop_ap()
        wifi.radio.stop_scanning_networks()

        if wifi.radio.connected:
            return

        try:
            wifi.radio.enabled = False
        except:
            pass

        from time import sleep

        sleep(0.5)

        try:
            wifi.radio.enabled = True
        except:
            pass

        del self._pool, self._session
        self._pool = None
        self._session = None

    def start(self) -> None:
        """
        Power on the wifi
        """
        try:
            wifi.radio.enabled = True
        except:
            pass
        self.disconnect()
        self.disconnect_ap()

    def stop(self) -> None:
        """
        Stop all wifi transactions
        Disconnect
        Power it off
        """
        self.disconnect()
        self.disconnect_ap()
        try:
            wifi.radio.enabled = False
        except:
            pass

    def timeset(self, tz=None) -> bool:
        """
        Fetch network time and set it into the current rtc object
        set timezone by passing a tz
        """
        from adafruit_ntp import NTP
        from rtc import RTC
        from time import struct_time

        if tz is None:
            tz = fetch("tz_offset", "BERYLLIUM")

        if tz is None:
            tz = 2

        if tz != self._tz:
            self._tz = tz

        if self.connected:
            if self._ntp is None:
                try:
                    self._ntp = NTP(self._pool, tz_offset=self._tz)
                except:
                    return False
            RTC().datetime = self._ntp.datetime
            return True
        return False

    def reset_session(self) -> None:
        del self._session
        self._session = Session(self._pool, create_default_context())

    def enter(self, args=None) -> int:
        print("This driver holds no executable")
        return 0
