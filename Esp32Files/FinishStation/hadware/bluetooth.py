import bluetooth
from ble_advertising import advertising_payload
from micropython import const

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_READ_REQUEST = const(4)
_IRQ_GATTS_WRITE = const(3)

_FLAG_READ = const(0x0002)
_FLAG_WRITE = const(0x0004)
_FLAG_NOTIFY = const(0x0010)

_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (
    bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"),
    _FLAG_READ | _FLAG_NOTIFY,
)
_UART_RX = (
    bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"),
    _FLAG_WRITE,
)


class BLE:
    def __init__(self, name="ESP32-BLE", rx_callback=None):
        self.name = name
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        self.ble.irq(self._irq)
        self.register_services()
        self.rx_callback = rx_callback
        self._connect_callback = None
        self._disconnect_callback = None
        self.is_connected = False
        self.start_advertising()

    def register_services(self):
        """Register UART service"""
        ((self.tx, self.rx),) = self.ble.gatts_register_services(
            (
                (
                    _UART_UUID,
                    (_UART_TX, _UART_RX),
                ),
            )
        )

    def start_advertising(self):
        """Start BLE advertising"""
        self.ble.gap_advertise(
            100, advertising_payload(name=self.name, services=[_UART_UUID])
        )
        print(f"BLE advertising started: {self.name}")

    def stop_advertising(self):
        """Stop BLE advertising"""
        self.ble.gap_advertise(None)

    def _irq(self, event, data):
        """Handle BLE events"""
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, addr_type, addr = data
            self.is_connected = True
            addr_str = ":".join("{:02X}".format(b) for b in addr)
            print(f"Central connected: {addr_str}")
            if self._connect_callback:
                self._connect_callback()

        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, addr_type, addr = data
            self.is_connected = False
            print("Central disconnected")
            self.start_advertising()
            if self._disconnect_callback:
                self._disconnect_callback()

        elif event == _IRQ_GATTS_WRITE:
            conn_handle, attr_handle = data
            data_received = self.ble.gatts_read(self.rx)
            if self.rx_callback:
                self.rx_callback(data_received)

    def send(self, data):
        """Send data to connected central"""
        if self.is_connected:
            if isinstance(data, str):
                data = data.encode()
            self.ble.gatts_notify(0, self.tx, data)

    def on_connect(self, callback):
        """Set connect callback"""
        self._connect_callback = callback

    def on_disconnect(self, callback):
        """Set disconnect callback"""
        self._disconnect_callback = callback

    def close(self):
        """Close BLE connection"""
        self.ble.active(False)
        print("BLE closed")
