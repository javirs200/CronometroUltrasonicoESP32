import struct
import bluetooth


def advertising_payload(limited_disc=False, br_edr=False, name=None, services=None):
    """Create BLE advertising payload"""
    payload = bytearray()

    def _append(adv_type, value):
        nonlocal payload
        payload += struct.pack("BB", len(value) + 1, adv_type) + value

    _append(
        0x01, struct.pack("B", (0x02 if limited_disc else 0x06) + (0x18 if br_edr else 0x00))
    )

    if name:
        _append(0x09, name.encode("utf-8"))

    if services:
        for uuid in services:
            b = bytes(uuid)
            if len(b) == 2:
                _append(0x03, b)
            elif len(b) == 4:
                _append(0x05, b)
            elif len(b) == 16:
                _append(0x07, b)

    return payload
