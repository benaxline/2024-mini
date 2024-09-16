"""
Response time - single-threaded
"""

from machine import Pin
import time
import random
import json
import network
import urequests


N: int = 10
sample_ms = 10.0
on_ms = 500


def random_time_interval(tmin: float, tmax: float) -> float:
    """return a random time interval between max and min"""
    return random.uniform(tmin, tmax)


def blinker(N: int, led: Pin) -> None:
    # %% let user know game started / is over

    for _ in range(N):
        led.high()
        time.sleep(0.1)
        led.low()
        time.sleep(0.1)


def write_json(json_filename: str, data: dict) -> None:
    """Writes data to a JSON file.

    Parameters
    ----------

    json_filename: str
        The name of the file to write to. This will overwrite any existing file.

    data: dict
        Dictionary data to write to the file.
    """

    with open(json_filename, "w") as f:
        json.dump(data, f)


def scorer(t: list[int | None]) -> None:
    # %% collate results
    misses = t.count(None)
    print(f"You missed the light {misses} / {len(t)} times")
    t_good = [x for x in t if x is not None]
    if t_good:
        average_time = sum(t_good) / len(t_good)
        min_time = min(t_good)
        max_time = max(t_good)
    else:
        min_time = average_time = max_time = None
    
    print(f"Response times - Min: {min_time}ms, Max: {max_time}ms, Avg: {average_time}ms")
    # add key, value to this dict to store the minimum, maximum, average response time
    # and score (non-misses / total flashes) i.e. the score a floating point number
    # is in range [0..1]
    data = {
        "misses" : misses,
        "total flashes" : len(t),
        "minimum time" : min_time,
        "maximum time" : max_time,
        "average time" : average_time
        }

    # %% make dynamic filename and write JSON

    now: tuple[int] = time.localtime()

    now_str = "-".join(map(str, now[:3])) + "T" + "_".join(map(str, now[3:6]))
    filename = f"score-{now_str}.json"

    print("write", filename)

    write_json(filename, data)

    send_data_to_server(data)


def scan_wifi():
    # Initialize the Wi-Fi interface in station mode
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    print("Scanning for available networks...")
    networks = wlan.scan()  # Scans for available Wi-Fi networks

    if not networks:
        print("No networks found.")
        return

    # Display the list of available networks
    for network_info in networks:
        ssid = network_info[0].decode()  # SSID (network name)
        bssid = network_info[1]  # MAC address of the AP
        channel = network_info[2]  # Channel number
        RSSI = network_info[3]  # Signal strength
        authmode = network_info[4]  # Authentication mode
        
        print(f"SSID: {ssid}, RSSI: {RSSI}, Channel: {channel}, Auth Mode: {authmode}")

def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    # Wait for connection
    while not wlan.isconnected():
        print("Connecting to WiFi...")
        time.sleep(1)
    print("Connected to WiFi:", wlan.ifconfig())

def send_data_to_server(data):
    """Sends the data to the server via HTTP POST."""
    headers = {"Content-Type": "application/json"}
    try:
        response = urequests.post(API_URL, headers=headers, data=json.dumps(data))
        print("Data uploaded:", response.text)
        response.close()
    except Exception as e:
        print("Failed to send data:", e)

if __name__ == "__main__":
    # using "if __name__" allows us to reuse functions in other script files

    # make this 'secret'
    SSID = "Ben"
    PASSWORD = "Password"

    API_URL = "https://ben-mini-default-rtdb.firebaseio.com/data.json"

    connect_to_wifi(SSID, PASSWORD)


    led = Pin("LED", Pin.OUT)
    button = Pin(16, Pin.IN, Pin.PULL_UP)

    t: list[int | None] = []

    blinker(3, led)

    for i in range(N):
        time.sleep(random_time_interval(0.5, 5.0))

        led.high()

        tic = time.ticks_ms()
        t0 = None
        while time.ticks_diff(time.ticks_ms(), tic) < on_ms:
            if button.value() == 0:
                t0 = time.ticks_diff(time.ticks_ms(), tic)
                led.low()
                break
        t.append(t0)

        led.low()

    blinker(5, led)

    scorer(t)

    # scan_wifi()
   

