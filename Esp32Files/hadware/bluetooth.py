import aioble
import asyncio
import bluetooth
from micropython import const

# UART Service UUID and Characteristics
_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX_UUID = bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_RX_UUID = bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")

# Advertising interval in microseconds (250ms)
_ADV_INTERVAL_US = const(250000)


class BLE:
    def __init__(self, name="ESP32-BLE", rx_callback=None):
        self.name = name
        self.rx_callback = rx_callback
        self._connect_callback = None
        self._disconnect_callback = None
        self.is_connected = False
        self.connection = None
        
        # Create UART service
        self.uart_service = aioble.Service(_UART_UUID)
        self.tx_char = aioble.Characteristic(
            self.uart_service,
            _UART_TX_UUID,
            read=True,
            notify=True,
        )
        self.rx_char = aioble.Characteristic(
            self.uart_service,
            _UART_RX_UUID,
            write=True,
            capture=True,
        )
        
        # Register the service
        aioble.register_services(self.uart_service)
        
        # Start the advertising task
        self._advertising_task = None
        self._rx_task = None
        self.start_advertising()

    def start_advertising(self):
        """Start BLE advertising"""
        print(f"Starting BLE advertising: {self.name}")
        self._advertising_task = asyncio.create_task(self._advertise())

    async def _advertise(self):
        """Advertise and handle connections"""
        while True:
            try:
                print(f"Waiting for connection: {self.name}")
                self.connection = await aioble.advertise(
                    _ADV_INTERVAL_US,
                    name=self.name,
                    services=[_UART_UUID],
                )
                print(f"Connection established: {self.name}")
                self.is_connected = True
                
                if self._connect_callback:
                    self._connect_callback()
                
                # Handle this connection
                await self._handle_connection()
                
            except asyncio.CancelledError:
                print(f"Advertising cancelled: {self.name}")
                break
            except Exception as e:
                print(f"Advertising error: {e}")
                await asyncio.sleep_ms(1000)

    async def _handle_connection(self):
        """Handle an active connection"""
        try:
            print(f"[CONN] Connection handler started")
            # Start listening for RX writes
            self._rx_task = asyncio.create_task(self._rx_listen())
            print(f"[CONN] RX listener task created")
            
            # Keep connection alive
            while self.is_connected:
                await asyncio.sleep_ms(100)
                
        except asyncio.CancelledError:
            print(f"[CONN] Connection handler cancelled")
            pass
        finally:
            if self._rx_task:
                self._rx_task.cancel()
            self.is_connected = False
            self.connection = None
            print(f"[CONN] Connection closed: {self.name}")
            
            if self._disconnect_callback:
                self._disconnect_callback()

    async def _rx_listen(self):
        """Listen for incoming data on RX characteristic"""
        try:
            while self.is_connected:
                try:
                    # Wait for write on RX characteristic
                    # written() returns (connection, data) when capture=True
                    conn, data = await self.rx_char.written(timeout_ms=5000)
                    print(f"[RX_LISTEN] Data received: {data}")
                    if self.rx_callback:
                        print(f"[RX_LISTEN] Calling callback with data: {data}")
                        self.rx_callback(data)
                except asyncio.TimeoutError:
                    # Timeouts are normal, just continue listening
                    print(f"[RX_LISTEN] Timeout waiting for data")
                    continue
                except Exception as e:
                    print(f"[RX_LISTEN] Error: {e}")
                    await asyncio.sleep_ms(100)
        except asyncio.CancelledError:
            print("[RX_LISTEN] Cancelled")
        except Exception as e:
            print(f"[RX_LISTEN] Fatal error: {e}")

    def send(self, data):
        """Send data to connected central"""
        if self.is_connected and self.connection:
            if isinstance(data, str):
                data = data.encode()
            try:
                # Update the TX characteristic and notify
                self.tx_char.write(data, send_update=True)
                print(f"Sent: {data}")
            except Exception as e:
                print(f"Send error: {e}")
        else:
            print("Not connected, cannot send")

    def on_connect(self, callback):
        """Set connect callback"""
        self._connect_callback = callback

    def on_disconnect(self, callback):
        """Set disconnect callback"""
        self._disconnect_callback = callback

    def stop_advertising(self):
        """Stop BLE advertising"""
        if self._advertising_task:
            self._advertising_task.cancel()
        print("BLE advertising stopped")

    def close(self):
        """Close BLE connection"""
        self.stop_advertising()
        if self.connection:
            self.connection.close()
        print("BLE closed")



