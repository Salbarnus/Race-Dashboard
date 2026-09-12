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

        # appending object instance for each car with data in the list cars = []
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

def display_car_telemetry(data):
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


# 3. CAR STATUS PACKET (packet_id == 7)
#    Contains, per car: tc, antilock brakes, fuel mix, front brake bias, pit limiter,
#    fuel in tank, fuel capacity etc
#    Format string below decodes ONE car's block (57 bytes).
# ---------------------------------------------------------------------------
CAR_STATUS_FORMAT = "<BBBBBfffHHBBHBBBbfffBfffB"
CAR_STATUS_SIZE = struct.calcsize(CAR_STATUS_FORMAT) # 57 bytes


@dataclass
class CarStatusData:
    traction_control: int
    anti_lock_brakes: int
    fuel_mix: int
    front_brake_bias: int
    pit_limiter: int

    fuel_in_tank: float
    fuel_capacity: float
    fuel_remaining_laps: float

    max_rpm: int
    idle_rpm: int
    max_gears: int
    drs_allowed: int
    drs_activation_distance: int

    actual_tyre_compound: int
    visual_tyre_compound: int
    tyres_age_laps: int
    vehicle_fia_flags: int

    engine_power_ice: float
    engine_power_mguk: float
    ers_store_energy: float

    ers_deploy_mode: int

    ers_harvested_this_lap_mguk: float
    ers_harvested_this_lap_mguh: float
    ers_deployed_this_lap: float

    network_paused: int


def parse_car_status_pkt(data: bytes) -> list:
    offset = HEADER_SIZE
    cars_status = []

    for i in range(NUM_CARS):
        chunk = data[offset: offset + CAR_STATUS_SIZE]
        vals = struct.unpack(CAR_STATUS_FORMAT, chunk)

        cars_status.append(CarStatusData(*vals))

        offset += CAR_STATUS_SIZE
    return cars_status

def display_car_status(data):
    header = parse_header(data)
    if header.packet_id == 7:
        cars_status = parse_car_status_pkt(data)
        my_car_status = cars_status[header.player_car_index]
        print(my_car_status)


# 4. CAR DAMAGE PACKET (packet_id == 10)
#    Contains, per car: tyre wear, tyres damage, brakes damage, tyre blisters
#    front left wing damage, right wing damage etc
#    Format string below decodes ONE car's block (57 bytes).
# ---------------------------------------------------------------------------
CAR_DAMAGE_FORMAT = "<4f4B4B4B18B"
CAR_DAMAGE_SIZE = struct.calcsize(CAR_DAMAGE_FORMAT) # 46 bytes

@dataclass
class CarDamageData:
    tyres_wear: tuple
    tyres_damage: tuple
    brakes_damage: tuple
    tyre_blisters: tuple

    front_left_wing_damage: int
    front_right_wing_damage: int
    rear_wing_damage: int
    floor_damage: int
    diffuser_damage: int
    sidepod_damage: int
    drs_fault: int
    ers_fault: int
    gear_box_damage: int
    engine_damage: int
    engine_mguh_wear: int
    engine_es_wear: int
    engine_ce_wear: int
    engine_ice_wear: int
    engine_mguk_wear: int
    engine_tc_wear: int
    engine_blown: int
    engine_seized: int


def parse_car_damage_pkt(data: bytes) -> list:
    offset = HEADER_SIZE
    cars_damage = []

    for i in range(NUM_CARS):
        chunk = data[offset: offset + CAR_DAMAGE_SIZE]
        vals = struct.unpack(CAR_DAMAGE_FORMAT, chunk)

        cars_damage.append(CarDamageData(
            tyres_wear=vals[0:4],
            tyres_damage=vals[4:8],
            brakes_damage=vals[8:12],
            tyre_blisters=vals[12:16],
        
            front_left_wing_damage=vals[16],
            front_right_wing_damage=vals[17],
            rear_wing_damage=vals[18],
            floor_damage=vals[19],
            diffuser_damage=vals[20],
            sidepod_damage=vals[21],
            drs_fault=vals[22],
            ers_fault=vals[23],
            gear_box_damage=vals[24],
            engine_damage=vals[25],
            engine_mguh_wear=vals[26],
            engine_es_wear=vals[27],
            engine_ce_wear=vals[28],
            engine_ice_wear=vals[29],
            engine_mguk_wear=vals[30],
            engine_tc_wear=vals[31],
            engine_blown=vals[32],
            engine_seized=vals[33],
        ))

        offset += CAR_DAMAGE_SIZE    
    return cars_damage


def display_car_damage(data):
    header = parse_header(data)
    if header.packet_id == 10:
        cars_damage = parse_car_damage_pkt(data)
        my_car_damage = cars_damage[header.player_car_index]
        print(my_car_damage)

# ---------------------------------------------------------------------------
# 5. MAIN LOOP — listen, decode header, route by packet type
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
        # display_car_telemetry(data)
        display_car_status(data)
        # display_car_damage(data)

if __name__ == "__main__":
    main()
