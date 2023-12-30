# Objectives:
# Calculate PO2 for different SPs so I can set dil and BOs based on conditions (target 1.1 for dil, 1.4 or 1.6 for BO)
# Compute END limits on OC and CC
# Compute soft limit on gas density (5.2g/l) and hard limit (6.2g/l) for OC, and then for CC with different SPs

import sys


def parse_trimix(trimix):
    """
    Parses a trimix string and returns the percentages of O2, He, and N2.

    Parameters:
    trimix (str): A string representing the trimix, e.g., '18/35' or '50'.

    Returns:
    tuple: Percentages of O2, He, and N2.
    """
    if '/' in trimix:
        o2, he = map(int, trimix.split('/'))
        n2 = 100 - o2 - he
    else:
        o2 = int(trimix)
        he = 0
        n2 = 100 - o2

    return o2, he, n2

def calculate_depth_for_po2(target_po2, oxygen_percentage):
    """
    Calculate the depth at which a given target PO2 is achieved with a specific oxygen percentage in the gas mix.

    Parameters:
    target_po2 (float): Target partial pressure of oxygen (PO2) in bar.
    oxygen_percentage (float): Percentage of oxygen in the gas mix.

    Returns:
    float: Depth in meters at which the target PO2 is achieved.
    """
    frac_o2 = oxygen_percentage / 100
    depth = (target_po2 / frac_o2 - 1) * 10
    return depth


if __name__ == '__main__':
    # Check if the trimix specification is provided as a command line argument
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <trimix>")
        sys.exit(1)

    # Get the trimix specification from command line argument
    trimix_input = sys.argv[1]

    # Parse the input and get the gas percentages
    o2_percentage, he_percentage, n2_percentage = parse_trimix(trimix_input)

    # Output the results
    print(f"Oxygen: {o2_percentage}%, Helium: {he_percentage}%, Nitrogen: {n2_percentage}%")

    targets_po2 = [1.1, 1.4, 1.6]  # PO2 targets in bar
    for po2 in targets_po2:
        depth = calculate_depth_for_po2(po2, o2_percentage)
        print(
            f"With a {o2_percentage}% O2 mix, a PO2 of {po2} bar is achieved at a depth of {depth:.2f} meters.")
