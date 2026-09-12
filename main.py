import socket
import struct
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# 1. THE HEADER — every single UDP packet starts with this, 29 bytes, always.
#    It tells us which packet type follows, so we can route accordingly.
# ---------------------------------------------------------------------------
HEADER_FORMAT = "<HBBBBBQfIIBB"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)  # 29 bytes

PACKET_IDS = {
    0: "Motion",
    1: "Session",
    2: "LapData",
    3: "Event",
    4: "Participants",
    5: "CarSetups",
    6: "CarTelemetry",
    7: "CarStatus",
    8: "FinalClassification",
    9: "LobbyInfo",
    10: "CarDamage",
    11: "SessionHistory",
    12: "TyreSets",
    13: "MotionEx",
    14: "TimeTrial",
    15: "Lap Positions",
    16: "Car Telemetry 2"
}

# dataclass decorator used here to provide __init__ , __repr__, __eq__ functions easily
@dataclass
class PacketHeader:
    packet_format: int
    game_year: int
    game_major_version: int
    game_minor_version: int
    packet_version: int
    packet_id: int
    session_uid: int
    session_time: float
    frame_identifier: int
    overall_frame_identifier: int
    player_car_index: int
    secondary_player_car_index: int


def parse_header(data: bytes) -> PacketHeader:
    fields = struct.unpack(HEADER_FORMAT, data[:HEADER_SIZE])

    # fields is by default tuple, so asterisk sends it as indivisual arguments
    # return PacketHeader(*fields) to return value in a pretty printing format
    return PacketHeader(*fields)


# 2. CAR TELEMETRY PACKET (packet_id == 6)
#    Contains, per car: speed, throttle/brake/steer, RPM, DRS, brake temps,
#    tyre surface + inner temps, engine temp, tyre pressures, surface type.
#    Format string below decodes ONE car's block (60 bytes).
# ---------------------------------------------------------------------------

CAR_TELEMETRY_FORMAT = "<HfffBbHBBH4H4B4BH4f4B"
CAR_TELEMETRY_SIZE = struct.calcsize(CAR_TELEMETRY_FORMAT)  # 60 bytes
NUM_CARS = 20


@dataclass
class CarTelemetryData:
    speed: int
    throttle: float
    steer: float
    brake: float
    clutch: int
    gear: int
    engine_rpm: int
    drs: int
    rev_lights_percent: int
    rev_lights_bit_value: int
    brakes_temperature: tuple      # 4 values: RL, RR, FL, FR
    tyres_surface_temperature: tuple
    tyres_inner_temperature: tuple
    engine_temperature: int
    tyres_pressure: tuple
    surface_type: tuple

def parse_car_telemetry_pkt(data: bytes) -> list:
    offset = HEADER_SIZE
    cars = []

    for i in range(NUM_CARS):
        chunk = data[offset: offset + CAR_TELEMETRY_SIZE]
        vals = struct.unpack(CAR_TELEMETRY_FORMAT, chunk)

        cars.append(CarTelemetryData(
            speed=vals[0],
            throttle=vals[1],
            steer=vals[2],
            brake=vals[3],
            clutch=vals[4],
            gear=vals[5],
            engine_rpm=vals[6],
            drs=vals[7],
            rev_lights_percent=vals[8],
            rev_lights_bit_value=vals[9],
            brakes_temperature=vals[10:14],
            tyres_surface_temperature=vals[14:18],
            tyres_inner_temperature=vals[18:22],
            engine_temperature=vals[22],
            tyres_pressure=vals[23:27],
            surface_type=vals[27:31],
        ))

        offset += CAR_TELEMETRY_SIZE    
    return cars

# ---------------------------------------------------------------------------
# 3. MAIN LOOP — listen, decode header, route by packet type
# ---------------------------------------------------------------------------
def main():

    # create a server type of internet and udp
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # bind the server to a ip
    # keep in mind it takes a tuple as input
    server.bind(("127.0.0.1", 20777))

    print("Listening for F1 25 telemetry...")

    while True:
        # in case of udp just recieve the message and addr in the form of a tuple
        data, addr = server.recvfrom(2048)
        # print("len of data: ", len(data))

        # too small pkt size = malformed packet
        if len(data) < HEADER_SIZE:
            continue  
        
        # print(parse_header(data))
        header = parse_header(data)
        if header.packet_id == 6:
            cars = parse_car_telemetry_pkt(data)
            my_car = cars[header.player_car_index]
            print(
                f"Speed: {my_car.speed:3d} km/h | "
                f"Gear: {my_car.gear:2d} | "
                f"RPM: {my_car.engine_rpm:5d} | "
                f"Tyre Pressures (PSI) RL/RR/FL/FR: "
                f"{my_car.tyres_pressure[0]:.1f} / {my_car.tyres_pressure[1]:.1f} / "
                f"{my_car.tyres_pressure[2]:.1f} / {my_car.tyres_pressure[3]:.1f} | "
                f"Tyre Surface Temp RL/RR/FL/FR: "
                f"{my_car.tyres_surface_temperature[0]} / {my_car.tyres_surface_temperature[1]} / "
                f"{my_car.tyres_surface_temperature[2]} / {my_car.tyres_surface_temperature[3]}"
            )

if __name__ == "__main__":
    main()
