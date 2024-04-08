def build_passkey(ble_mac):
    mac = ble_mac  # Read Beacon BLE MAC 00:8C:10:30:00:00
    lst_mac = mac.split(":")  # Split BLE MAC 00, 8C, 10, 30, 00, 00

    if len(lst_mac) != 6:  # Validate BLE MAC Length
        return 0

    # Convert to String to HEX (Base 16)
    addr = [int(i, 16) for i in lst_mac]

    # Passkey generation
    passkey = 0
    for i in range(6):
        passkey += (addr[i] << 8)  # 8bit Left shift (Final passkey)

    # If passkey length is >=7 digit then consider first 6 digit as passkey
    if len(str(passkey)) >= 7:
        passkey = int(str(passkey)[:6])

    return passkey


print(build_passkey("00:8C:10:30:02:59"))