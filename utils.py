def calculate_num_bins(data, min_bins=3, bin_size=10):
    """
    Calculate the number of bins for a histogram.

    The function calculates the number of bins based on the range of the data.
    The number of bins is determined as the range of the data divided by the bin size,
    but it will be at least the minimum number of bins specified.

    Parameters:
    data (list of int/float): The data to be binned. Must not be empty.
    min_bins (int, optional): The minimum number of bins. Default is 3.
    bin_size (int, optional): The size of each bin in seconds. Default is 10.

    Returns:
    num_bins (int): The number of bins (between min_bins and 15).

    Raises:
    ValueError: If data is empty.

    Edge cases:
    - If range of data is less than bin_size, returns min_bins
    - Maximum bins is capped at 15 to prevent overcrowding
    """
    if not data:
        raise ValueError("Data cannot be empty")

    range_of_data = max(data) - min(data)
    num_bins = max(min_bins, range_of_data // bin_size)

    max_bins = 15
    num_bins = min(max_bins, num_bins)  # Ensure num_bins does not exceed max_bins

    return num_bins
