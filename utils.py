import config


def calculate_num_bins(data, min_bins=None, bin_size=None):
    """
    Calculate the number of bins for a histogram.

    The function calculates the number of bins based on the range of the data.
    The number of bins is determined as the range of the data divided by the bin size,
    but it will be at least the minimum number of bins specified.

    Parameters:
    data (list of int/float): The data to be binned. Must not be empty.
    min_bins (int, optional): The minimum number of bins. Defaults to config.MIN_BINS (3).
    bin_size (int, optional): The size of each bin in seconds. Defaults to config.DEFAULT_BIN_SIZE (10).

    Returns:
    num_bins (int): The number of bins (between min_bins and MAX_BINS).

    Raises:
    ValueError: If data is empty.

    Edge cases:
    - If range of data is less than bin_size, returns min_bins
    - Maximum bins is capped at config.MAX_BINS to prevent overcrowding
    """
    if not data:
        raise ValueError("Data cannot be empty")

    # Use config defaults if not provided
    if min_bins is None:
        min_bins = config.MIN_BINS
    if bin_size is None:
        bin_size = config.DEFAULT_BIN_SIZE

    range_of_data = max(data) - min(data)
    num_bins = max(min_bins, range_of_data // bin_size)

    # Ensure num_bins does not exceed max_bins
    num_bins = min(config.MAX_BINS, num_bins)

    return num_bins
