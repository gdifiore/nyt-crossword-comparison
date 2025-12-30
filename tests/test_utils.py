"""Tests for utils.py functions."""
import pytest
import utils


class TestCalculateNumBins:
    """Tests for calculate_num_bins function."""

    def test_basic_calculation(self):
        """Test basic bin calculation."""
        data = [10, 20, 30, 40, 50]  # Range of 40 seconds
        num_bins = utils.calculate_num_bins(data)
        # Range is 40, bin_size is 10, so 40/10 = 4, max(3, 4) = 4
        assert num_bins == 4

    def test_minimum_bins(self):
        """Test that minimum number of bins is returned when range is small."""
        data = [10, 12, 15]  # Range of 5 seconds
        num_bins = utils.calculate_num_bins(data)
        # Range is 5, bin_size is 10, so 5/10 = 0, max(3, 0) = 3
        assert num_bins == 3

    def test_maximum_bins_cap(self):
        """Test that bins are capped at MAX_BINS."""
        import config

        # Create data with range > MAX_BINS * bin_size
        data = [0, 200]  # Range of 200 seconds
        num_bins = utils.calculate_num_bins(data)
        # Range is 200, bin_size is 10, so 200/10 = 20, but max is 15
        assert num_bins == config.MAX_BINS

    def test_empty_data_raises_error(self):
        """Test that empty data raises ValueError."""
        with pytest.raises(ValueError, match="Data cannot be empty"):
            utils.calculate_num_bins([])

    def test_single_value(self):
        """Test with single value (range = 0)."""
        data = [50]
        num_bins = utils.calculate_num_bins(data)
        # Range is 0, so should return min_bins
        assert num_bins == 3

    def test_custom_min_bins(self):
        """Test custom minimum bins parameter."""
        data = [10, 12]
        num_bins = utils.calculate_num_bins(data, min_bins=5)
        # Range is 2, which is less than bin_size, so should return min_bins
        assert num_bins == 5

    def test_custom_bin_size(self):
        """Test custom bin size parameter."""
        data = [10, 60]  # Range of 50 seconds
        num_bins = utils.calculate_num_bins(data, bin_size=5)
        # Range is 50, bin_size is 5, so 50/5 = 10
        assert num_bins == 10

    def test_all_same_values(self):
        """Test when all values are identical."""
        data = [42, 42, 42, 42]
        num_bins = utils.calculate_num_bins(data)
        # Range is 0, should return min_bins
        assert num_bins == 3
