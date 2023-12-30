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
    Calculate the depth at which the Equivalent Narcotic Depth (END) is 30m for a given nitrogen percentage in the mix.

    Parameters:
    n2_percentage (float): Percentage of nitrogen in the gas mix.

    Returns:
    float: Depth in meters at which the END is 30 meters.
    """
    frac_n2_mix = n2_percentage / 100  # Fraction of N2 in the mix
    target_ppn2_air_30m = 0.79 * 4  # PPN2 when breathing air at 30 meters

    depth = (target_ppn2_air_30m / frac_n2_mix - 1) * 10
    return depth


# Specific gravities of gases at standard conditions (g/l)
SPECIFIC_GRAVITY_O2 = 1.429
SPECIFIC_GRAVITY_N2 = 1.2506
SPECIFIC_GRAVITY_HE = 0.1786


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
                frac_o2 * SPECIFIC_GRAVITY_O2 + frac_n2 * SPECIFIC_GRAVITY_N2 + frac_he * SPECIFIC_GRAVITY_HE)

        if density >= target_density:
            break
        depth += 1

    return depth


def calculate_depth_for_sp_and_density(initial_o2_percentage, initial_he_percentage, initial_n2_percentage, set_point,
                                       target_density):
    """
    Calculate the depth at which a given target gas density is reached for a specific mix adjusted to a set point (SP),
    starting from an initial depth of 10 meters.

    Parameters:
    initial_o2_percentage (float): Initial percentage of oxygen in the gas mix.
    initial_he_percentage (float): Initial percentage of helium in the gas mix.
    set_point (float): Target set point for PO2.
    target_density (float): Target gas density in g/l.

    Returns:
    float: Depth in meters at which the target gas density is reached for the adjusted mix.
    """
    # Start from an initial depth of 10 meters
    depth = 10

    while True:
        # Calculate ambient pressure at current depth
        ambient_pressure = 1 + depth / 10

        # Calculate the frac_o2 needed to reach the set point at this depth
        frac_o2 = set_point / ambient_pressure
        if frac_o2 >= 1.0:
            raise ValueError("Set point cannot be reached with the initial mix.")

        # Adjust He and N2 fractions based on the new O2 fraction
        total_he_n2 = 1 - frac_o2
        frac_he = initial_he_percentage / 100 * total_he_n2
        frac_n2 = initial_n2_percentage / 100 * total_he_n2

        # Calculate gas density of current gas composition
        density = ambient_pressure * (
                    frac_o2 * SPECIFIC_GRAVITY_O2 + frac_n2 * SPECIFIC_GRAVITY_N2 + frac_he * SPECIFIC_GRAVITY_HE)

        # Check if the gas density exceeds the target density
        if density >= target_density:
            return depth

        # Increase depth by 1 meter for next iteration
        depth += 1

    # Return the depth if the loop exits (which should not normally happen)
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
            f"PO2 of {po2} bar at {depth:.2f} meters.")

    depth_for_30m_end = find_depth_for_30m_end(n2_percentage)
    print(
        f"END is 30 meters at {depth_for_30m_end:.2f} meters.")

    target_densities = [5.2, 6.2]  # Hard nd soft limits in g/l
    for target_density in target_densities:
        depth_for_limit = calculate_depth_for_gas_density(o2_percentage, he_percentage, target_density)
        print(
            f"Depth for {target_density} g/l gas density is {depth_for_limit} meters on OC.")
        # Now for OC
        for setpoint in [1.0, 1.1, 1.2, 1.3]:
            depth_for_limit = calculate_depth_for_sp_and_density(o2_percentage, he_percentage, n2_percentage, setpoint,
                                                                 target_density)
            print(
                f"With SP {setpoint} the depth for {target_density} g/l is {depth_for_limit}."
            )
