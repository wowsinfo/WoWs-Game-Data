'''
This is used to calculate AP Penetration in World of Warships

original matlab code from https://pastebin.com/1NEwkf7R,
converted to python using http://www.ompclib.appspot.com/m2py,
used https://github.com/EdibleBug/WoWSFT-Kotlin/blob/5d4ce2d4ffb722c010b265ce3c39417eddd009c7/WoWSFT-Data/src/main/kotlin/WoWSFT/utils/PenetrationUtils.kt as a reference,
modified by me.
'''

from math import *
import matplotlib.pyplot as plt


def get_ap_penetration(ap, output=False):
    penetration_value = 0.5561613  # PENETRATION
    G = 9.81  # GRAVITY
    sea_level_temperature = 288  # TEMPERATURE AT SEA LEVEL
    temperature_lapse_rate = 0.0065  # TEMPERATURE LAPSE RATE
    sea_level_pressure = 101325  # PRESSURE AT SEA LEVEL
    univ_gas_constant = 8.31447  # UNIV GAS CONSTANT
    mass_air = 0.0289644  # MOLAR MASS OF AIR

    shell_weight = ap['weight']
    shell_diameter = ap['diameter']
    shell_drag = ap['drag']
    shell_velocity = ap['velocity']
    shell_krupp = ap['krupp']

    cw_quadratic = 1  # QUADRATIC DRAG COEFFICIENT
    cw_linear = 100 + 1000 / 3 * shell_diameter  # LINEAR DRAG COEFFICIENT

    penetration_value = penetration_value * shell_krupp / 2400  # KRUPP INCLUSION
    drag_constant = 0.5 * shell_drag * \
        (shell_diameter / 2) ** 2 * pi / \
        shell_weight  # CONSTANTS TERMS OF DRAG

    alpha = []
    # ELEV. ANGLES 0...15,
    # 150 is used here because step cannot be 0.1, the point here is to have lots of angles
    # 150 should be replace because it is different for every ship
    for i in range(0, 150, 1):
        alpha.append(i / 10 * pi / 180)

    armour = []
    distance = []
    time = []
    dt = 0.1  # TIME STEP

    # for each alpha angle do:
    for i in range(1, len(alpha)):
        v_x = cos(alpha[i]) * shell_velocity
        v_y = sin(alpha[i]) * shell_velocity
        x = 0
        y = 0
        time_taken = 0

        # follow flight path until shell hits ground again
        while y >= 0:

            x = x + dt * v_x
            y = y + dt * v_y

            temperature = sea_level_temperature - temperature_lapse_rate * y
            pressure = sea_level_pressure * (1 - temperature_lapse_rate * y / sea_level_temperature) ** (
                G * mass_air / (univ_gas_constant * temperature_lapse_rate))
            rho = pressure * mass_air / (univ_gas_constant * temperature)

            v_x = v_x - dt * drag_constant * rho * \
                (cw_quadratic * v_x ** 2 + cw_linear * v_x)
            # copysign when x = 1, it is the same as sign
            v_y = v_y - dt * G - dt * drag_constant * rho * \
                (cw_quadratic * v_y ** 2 + cw_linear * abs(v_y)) * copysign(1, v_y)

            time_taken = time_taken + dt

        v_total = (v_y ** 2 + v_x ** 2) ** 0.5
        # PENETRATION FORMULA
        ap_pen = penetration_value * v_total ** 1.1 * \
            shell_weight ** 0.55 / (shell_diameter * 1000) ** 0.65
        # IMPACT ANGLE ON BELT ARMOR
        impact_angle = atan(abs(v_y) / abs(v_x))

        armour.append(cos(impact_angle) * ap_pen)
        distance.append(x / 1000)
        # no idea why it needs to be divide by 3, followed wowft code
        time.append(time_taken / 3.0)

    # print(armour)
    # print(distance)

    if output:
        for i, v in enumerate(armour):
            print('{:2f}km - {:2f}mm ({:2f}s)'.format(distance[i], v, time[i]))

    fig, ax = plt.subplots()
    plt.title('AP Penetration / Shell travel time')
    # pen
    ax.set_xlabel('Distance (km)')
    ax.set_ylabel('Armour (mm)')
    ax.plot(distance, armour)
    # time
    ax2 = ax.twinx()
    ax2.set_ylabel('Time (s)')
    ax2.plot(distance, time)
    plt.show()


# testing only
if __name__ == '__main__':
    get_ap_penetration({'weight': 55, 'drag': 0.321,
                       'velocity': 950, 'diameter': 0.152, 'krupp': 2216})
