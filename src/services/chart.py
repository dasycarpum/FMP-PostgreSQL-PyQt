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
    return [result[0] for result in results_n[:3]]

def calculate_optimal_standard_deviation(prices: pd.DataFrame, window_size: int) -> float:
    """Calculate the optimal standard deviation multiplier for Bollinger Bands.

    This function iterates over a range of potential standard deviation 
    multipliers to determine which multiplier results in Bollinger Bands that 
    best fit a given strategy. The strategy aims to minimize the number of 
    times the stock price closes outside the bands while maximizing the number 
    of times the stock price touches the bands.

    Args:
        prices (pd.DataFrame): DataFrame containing the price data with columns 
        including 'close', 'high', and 'low'.
        window_size (int): The number of periods over which to calculate the 
        moving average and moving standard deviation.

    Returns:
        float: The optimal standard deviation multiplier that results in the 
        best scoring Bollinger Bands according to the specified criteria.

    Raises:
        ValueError: If 'prices' does not contain the required columns.

    """
    # Define a range of potential standard deviations
    std_devs = np.arange(1.5, 3.1, 0.1)
    best_std = None
    best_score = float('inf')  # Lower scores are better

    # Iterate over possible standard deviations
    for std in std_devs:
        # Calculate moving average and moving standard deviation
        moving_avg = prices['close'].rolling(window=window_size).mean()
        moving_std = prices['close'].rolling(window=window_size).std()

        # Calculate Bollinger Bands
        upper_band = moving_avg + (moving_std * std)
        lower_band = moving_avg - (moving_std * std)

        # Calculate criteria
        # Count how many times the close is above the upper band or below the lower band
        above_upper = (prices['close'] > upper_band).sum()
        below_lower = (prices['close'] < lower_band).sum()
        touches_high = ((prices['high'] >= upper_band) & (prices['close'] <= upper_band)).sum()
        touches_low = ((prices['low'] <= lower_band) & (prices['close'] >= lower_band)).sum()

        # Define a scoring function: minimize the bad closures and maximize the touches
        score = (above_upper + below_lower) - (touches_high + touches_low)

        # Update the best standard deviation found so far
        if score < best_score:
            best_score = score
            best_std = std

    return round(best_std, 2)

def calculate_optimal_stds(prices: pd.DataFrame, days: list) -> list:
    """Calculate the optimal standard deviation multipliers for Bollinger Bands 
    over various window sizes.

    This function utilizes `calculate_optimal_standard_deviation` to find the 
    best standard deviation multiplier for Bollinger Bands for multiple window 
    sizes specified in the `days` list. It iterates over each window size, 
    calculates the optimal standard deviation multiplier for that window size, 
    and compiles the results into a list.

    Args:
        prices (pd.DataFrame): DataFrame containing the price data with columns 
        including 'close', 'high', and 'low'.
        days (list of int): A list of integers representing the window sizes 
        (in days) over which to calculate the moving average and moving 
        standard deviation for the Bollinger Bands.

    Returns:
        list of float: A list of optimal standard deviation multipliers for 
        each window size specified in `days`.

    Raises:
        ValueError: If 'prices' does not contain the required columns.

    """
    results = []

    for day in days:
        results.append(calculate_optimal_standard_deviation(prices, day))

    return results
