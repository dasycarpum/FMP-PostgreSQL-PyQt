#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-10

@author: Roland VANDE MAELE

@abstract: this function retrieves and parses data from an external API.

"""

import json
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
import certifi


def get_jsonparsed_data(url):
    """
    Fetches and parses a JSON object from a given URL.

    Args:
        url (str): The URL from which to fetch the JSON data.

    Returns:
        dict/list: The parsed JSON data.

    Raises:
        RuntimeError: For general errors including network issues and data parsing errors.
    """
    try:
        response = urlopen(url, cafile=certifi.where())
        data = response.read().decode("utf-8")
        return json.loads(data)
    except HTTPError as e:
        # Handles HTTP errors, e.g., 404 Not Found, 500 Internal Server Error, etc.
        raise RuntimeError(f"HTTP error occurred: {e.code} - {e.reason}") from e
    except URLError as e:
        # Handles URL related errors, e.g., a malformed URL or unreachable domain.
        raise RuntimeError(f"URL error occurred: {e.reason}") from e
    except json.JSONDecodeError:
        # Handles errors thrown if the response body does not contain valid JSON.
        raise RuntimeError("Error parsing JSON data") from e
    except Exception as e:
        # General exception catch-all for unexpected issues.
        raise RuntimeError(f"An unexpected error occurred: {e}") from e
