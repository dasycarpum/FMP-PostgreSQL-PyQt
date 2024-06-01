#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-05-29

@author: Roland VANDE MAELE

@abstract: this file is intended for functions processing technical indicators

"""

import numpy as np
import pandas as pd
from src.services.various import safe_divide

def calculate_optimal_moving_averages(prices: pd.Series) -> list:
    """
    Calculate optimal moving averages for a given series of prices.
    
    This function iteratively calculates moving averages over a range of window 
    sizes, measures the sum of the absolute distances between the prices and 
    their corresponding moving averages, and counts the number of intersections 
    with a standard moving average. Results are normalized and scored to 
    identify the most optimal window sizes.
    
    Args:
        prices (pd.Series): A pandas Series of prices, dates as index.

    Returns:
        list: A list of strings, where each string is the window size of one of 
        the top three most optimal moving averages. The optimal moving averages 
        are determined by combining scores based on the sum of distances and the
        number of intersections after normalization.

    """
    n = len(prices)
    min_days, max_days, step = 15, 60, 3
    results = []

    for days in range(min_days, min(max_days + 1, n), step):
        # Calculate moving average
        moving_avg = prices.rolling(window=days).mean().dropna()

        # Calculate sum of distances
        sum_distance = np.sum(np.abs(prices - moving_avg))

        # Calculate intersections
        difference = moving_avg - prices
        sign_changes = difference.shift(1) * difference < 0
        number_of_intersections = sign_changes.sum()

        results.append((days, number_of_intersections, sum_distance))

    # Sort results based on a score
    intersection = [t[1] for t in results]
    distance = [t[2] for t in results]

    # -> calculate min and max for each column
    min_i, max_i = min(intersection), max(intersection)
    min_d, max_d = min(distance), max(distance)

    # -> min-max normalisation by column and score
    results_n = [
        (
            t[0],
            safe_divide(t[1] - min_i, max_i - min_i) + safe_divide(t[2] - min_d, max_d - min_d)
        )
        for t in results
    ]

    results_n.sort(key=lambda x: (x[1]))

    # Return the days of the three best moving averages
    return [str(result[0]) for result in results_n[:3]]
