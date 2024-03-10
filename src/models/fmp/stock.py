#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-09

@author: Roland VANDE MAELE

@abstract: this ORM (Object-Relational Mapping) model represents the FMP stock
tables in the PostgreSQL database.

"""

from sqlalchemy import Column, Integer, String, Float
from src.models.base import Base

class StockSymbol(Base):
    """
    Represents a stock symbol entity within the database.
    
    Attributes:
        id (int): The unique identifier for the stock symbol. This is the 
        primary key in the database.
        symbol (str): The ticker symbol of the stock, e.g., 'AAPL' for Apple 
        Inc. This field is required, unique and cannot be null.
        exchange (str): The name of the stock exchange where the stock is 
        traded, e.g., 'NASDAQ'.
        exchangeShortName (str): A shorter or abbreviated name for the 
        exchange, e.g., 'NYSE' for New York Stock Exchange.
        price (float): The current price of the stock. This field can store 
        floating-point numbers to accommodate stock prices with cents.
        name (str): The official name of the company that the stock symbol 
        represents. This field is required and cannot be null.
        type_ (str): Stock, ETF or Trust
        
    The `__tablename__` attribute specifies the name of the database table to 
    which this class is mapped.

    FMP comments: 
        Find symbols for traded and non-traded stocks with our Symbol List. 
        This comprehensive list includes over 25,000 stocks, making it the 
        perfect resource for investors and traders of all levels.

    """
    __tablename__ = 'stocksymbol'
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), unique=True, nullable=False)
    exchange = Column(String(35))
    exchangeshortname = Column(String(10))
    price = Column(Float)
    name = Column(String(180))
    type_ = Column(String(5))
