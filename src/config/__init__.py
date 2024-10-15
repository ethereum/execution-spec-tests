"""
This module initializes the config package.

The config package is responsible for loading and managing application-wide
environment configurations, making them accessible throughout the application.
"""

# This import is done to facilitate cleaner imports in the project
# `from config import env` instead of `from config.env import env`
from .env import env  # noqa401
