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

if __name__ == '__main__':
    # Prompt the user for a trimix description
    trimix_input = input("Enter the trimix description (e.g., '18/35' or '50'): ")
    
    # Parse the input and get the gas percentages
    o2_percentage, he_percentage, n2_percentage = parse_trimix(trimix_input)
    
    # Output the results
    print(f"Oxygen: {o2_percentage}%, Helium: {he_percentage}%, Nitrogen: {n2_percentage}%")
