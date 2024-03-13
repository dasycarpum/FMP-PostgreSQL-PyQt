#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-09

@author: Roland VANDE MAELE

@abstract: this ORM (Object-Relational Mapping) model represents the FMP stock
tables in the PostgreSQL database.

"""

from sqlalchemy import (Column, Integer, BigInteger, String, Float, Boolean,
                        Date, ForeignKey, UniqueConstraint)
from sqlalchemy.orm import relationship
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

    company = relationship("CompanyProfile", back_populates="stocksymbol")
    daily_charts = relationship("DailyChartEOD", back_populates="stocksymbol")
    

class CompanyProfile(Base):
    """
    Represents the profile of a company associated with a stock symbol.

    Attributes:
        id (int): Primary key.
        stock_id (int): Foreign key linking to the StockSymbol table, ensuring
         a one-to-one relationship.
        currency (str): The currency in which the company operates.
        cik (str): The Central Index Key (CIK) assigned by the SEC.
        isin (str): The International Securities Identification Number.
        cusip (str): The Committee on Uniform Securities Identification Procedures number.
        industry (str): The industry sector the company belongs to.
        website (str): The official website of the company.
        description (str): A brief description of the company's operations.
        sector (str): The sector of the economy to which the company contributes.
        country (str): The country where the company is headquartered.
        image (str): A URL to an image or logo of the company.
        ipo_date (datetime.date): The initial public offering date for the company's stock.
        is_etf (bool): Indicates whether the company is an ETF (Exchange-Traded Fund).
        is_actively_trading (bool): Indicates whether the company's stock is
         currently being actively traded.
        is_adr (bool): Indicates whether the company is an ADR (American Depository Receipt).
        isf_und (bool): Indicates whether the company is a fund.

    The CompanyProfile model is designed to hold detailed information about 
    companies associated with stock symbols. It has a one-to-one relationship 
    with the StockSymbol model, allowing for easy access to stock-related data 
    alongside company profiles.

    """
    __tablename__ = 'companyprofile'

    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey(StockSymbol.id), unique=True, nullable=False)
    currency = Column(String(3))
    cik = Column(String(10))
    isin = Column(String(12))
    cusip = Column(String(9))
    industry = Column(String(60))
    website = Column(String(255))
    description = Column(String)
    sector = Column(String(60))
    country = Column(String(5))
    image = Column(String(255))
    ipo_date = Column(Date)
    is_etf = Column(Boolean)
    is_actively_trading = Column(Boolean)
    is_adr = Column(Boolean)
    is_fund = Column(Boolean)

    stocksymbol = relationship("StockSymbol", back_populates="company")

class DailyChartEOD(Base):
    """
    Represents daily quote data for a stock symbol.

    Each instance of this class corresponds to a single daily quotation record
    for a specific stock symbol, including information such as opening price
    opening price, closing price, volume, etc.

    Attributes:
        id (BigInteger): Unique record identifier.
        stock_id (Integer): Foreign key to the associated stock symbol.
        date (Date): Date of quotation.
        open (Float): Quotation opening price.
        high (Float): Highest price reached during the day.
        low (Float): Lowest price reached during the day.
        close (Float): Quotation closing price.
        adjclose (Float): Adjusted closing price, taking into account corporate
            such as splits.
        volume (BigInteger): Total volume of shares traded during the day.
        unadjusted_volume (BigInteger): Total volume of shares traded without adjustments.
        change (Float): Change in price from previous day.
        change_percent (Float): Percentage change in price from previous day.
        vwap (Float): Volume-weighted average price.
    
    Relationships:
        stocksymbol (relationship): SQLAlchemy `relationship` to the 
        corresponding `StockSymbol` instance, providing access to the stock 
        symbol associated with this quotation.
    
    Constraints:
        __table_args__: A unique constraint (`_stockid_date_uc`) ensuring that 
        there can be only one quotation entry per stock per day, combining 
        `stock_id` and `date`.

    """
    __tablename__ = 'dailychart'

    id = Column(BigInteger, primary_key=True)
    stock_id = Column(Integer, ForeignKey(StockSymbol.id), nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    adj_close = Column(Float)
    volume = Column(BigInteger)
    unadjusted_volume = Column(BigInteger)
    change = Column(Float)
    change_percent = Column(Float)
    vwap = Column(Float)

    stocksymbol = relationship("StockSymbol", back_populates="daily_charts")

    # Add a unique constraint for stock_id and date
    __table_args__ = (UniqueConstraint('stock_id', 'date',
                      name='_stockid_date_uc'),)
