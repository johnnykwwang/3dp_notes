from requests import get, post
from statistics import stdev
from time import sleep

HE_TEMPERATURE = 240                # extruder temperature for measurements.  Should be normal printing temp.
BASE_URL = "http://127.0.0.1:7125"
N_SAMPLES = 5  # number of CALIBRATE_Z to execute.  Must >= 2
OOZING_MINUTES=1
CLEAN_NOZZLE_BEFORE_CALIBRATE_Z = True

def send_gcode(cmd='', retries=1):
    url = BASE_URL + "/printer/gcode/script?script=%s" % cmd
    resp = post(url)
    success = None
    for i in range(retries):
        try:
            success = 'ok' in resp.json()['result']
        except KeyError:
            print("G-code command '%s', failed. Retry %i/%i" % (cmd,
                                                                i+1,
                                                                retries))
        else:
            return True
    return False

def set_bedtemp(t=0):
    temp_set = False
    cmd = 'SET_HEATER_TEMPERATURE HEATER=heater_bed TARGET=%.1f' % t
    temp_set = send_gcode(cmd, retries=3)
    if not temp_set:
        raise RuntimeError("Bed temp could not be set.")


def set_hetemp(t=0):
    temp_set = False
    cmd = 'SET_HEATER_TEMPERATURE HEATER=extruder TARGET=%.1f' % t
    temp_set = send_gcode(cmd, retries=3)
    if not temp_set:
        raise RuntimeError("HE temp could not be set.")

def query_he_temp():
    url = BASE_URL + '/printer/objects/query?extruder'
    temp = get(url).json()['result']['status']['extruder']['temperature']
    return temp

def wait_for_hetemp():
    print('Heating started')
    while(1):
        temp = query_he_temp()
        if temp >= HE_TEMPERATURE-0.5:
            print("Reached hotend temp")
            break

def intentional_oozing(minute=2):
    sleep(minute*60)

def clear_bed_mesh():
    mesh_cleared = False
    cmd = 'BED_MESH_CLEAR'
    mesh_cleared = send_gcode(cmd, retries=3)
    if not mesh_cleared:
        raise RuntimeError("Could not clear mesh.")

def get_gcode_offset():
    url = BASE_URL + '/printer/objects/query?gcode_move'
    offset = get(url).json()['result']['status']['gcode_move']['homing_origin'][2]
    return offset

def main():
    # Home all
    if send_gcode('G28'):
        print("HomDONE")
    else:
        raise RuntimeError("Failed to home. Aborted.")
    clear_bed_mesh()
    
    set_hetemp(HE_TEMPERATURE)
    wait_for_hetemp()

    send_gcode('SET_GCODE_OFFSET Z=0.0')

    gcode_offsets = []

    for i in range(N_SAMPLES):
        if CLEAN_NOZZLE_BEFORE_CALIBRATE_Z:
            send_gcode('CLEAN_NOZZLE')
        send_gcode('CALIBRATE_Z')
        offset = get_gcode_offset()
        gcode_offsets.append(offset)
        send_gcode('SET_GCODE_OFFSET Z=0.0')
        print(f"Auto Z Calibration trial {i}, gcode_offset: {offset}")
        intentional_oozing(minute=OOZING_MINUTES)

    deviation = stdev(gcode_offsets)
    print(f"Standard Deviation = {deviation}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        set_bedtemp()
        set_hetemp()
        send_gcode('SET_FRAME_COMP enable=1')
        print("\nAborted by user!")
