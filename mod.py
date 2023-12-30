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


def find_depth_for_30m_end(n2_percentage):
    """
    Calculate the depth at which the Equivalent Narcotic Depth (END) is 30 meters for a given nitrogen percentage in the gas mix.

    Parameters:
    n2_percentage (float): Percentage of nitrogen in the gas mix.

    Returns:
    float: Depth in meters at which the END is 30 meters.
    """
    frac_n2_mix = n2_percentage / 100  # Fraction of N2 in the mix
    target_ppn2_air_30m = 0.79 * 4  # PPN2 when breathing air at 30 meters

    depth = (target_ppn2_air_30m / frac_n2_mix - 1) * 10
    return depth


def calculate_depth_for_gas_density(o2_percentage, he_percentage, target_density):
    """
    Calculate the depth at which a given target gas density is reached for a specific gas mix.
    Corroborated by https://gue.com/blog/density-discords-understanding-and-applying-gas-density-research/

    Parameters:
    o2_percentage (float): Percentage of oxygen in the gas mix.
    he_percentage (float): Percentage of helium in the gas mix.
    target_density (float): Target gas density in g/l.

    Returns:
    float: Depth in meters at which the target gas density is reached.
    """
    # Specific gravities of gases at standard conditions (g/l)
    specific_gravity_o2 = 1.429
    specific_gravity_n2 = 1.2506
    specific_gravity_he = 0.1786

    # Convert percentages to fractions
    frac_o2 = o2_percentage / 100
    frac_he = he_percentage / 100
    frac_n2 = 1 - frac_o2 - frac_he

    # Initialize depth
    depth = 0

    # Increment depth until the target density is reached or exceeded
    while True:
        total_pressure = 1 + depth / 10  # Total pressure at depth (in ATA)
        density = total_pressure * (
                    frac_o2 * specific_gravity_o2 + frac_n2 * specific_gravity_n2 + frac_he * specific_gravity_he)

        if density >= target_density:
            break
        depth += 1

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

    depth_for_30m_end = find_depth_for_30m_end(n2_percentage)
    print(f"With {n2_percentage}% N2 in the mix, the depth at which END is 30 meters is {depth_for_30m_end:.2f} meters.")

    target_densities = [5.2, 6.2]  # Limits in g/l
    for target_density in target_densities:
        depth_for_soft_limit = calculate_depth_for_gas_density(o2_percentage, he_percentage, target_density)
        print(
            f"With {o2_percentage}% O2 and {he_percentage}% He, the depth for {target_density} g/l gas density is {depth_for_soft_limit} meters.")
