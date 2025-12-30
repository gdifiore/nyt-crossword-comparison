"""
Shared configuration constants for the application.
"""

# Application version
VERSION = "0.0.1"

# Database configuration
TABLE_NAME = "puzzle_completion"
DB_POOL_MIN_CONN = 1
DB_POOL_MAX_CONN = 10

# Histogram configuration
MIN_BINS = 3
MAX_BINS = 15
DEFAULT_BIN_SIZE = 10  # seconds

# Time validation (in seconds)
MIN_COMPLETION_TIME = 10  # 10 seconds minimum
MAX_COMPLETION_TIME = 900  # 15 minutes maximum
