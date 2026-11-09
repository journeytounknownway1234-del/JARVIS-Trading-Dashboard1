
# JARVIS Trading Dashboard

A market research dashboard using Yahoo Finance and TradingView.

## Features

- NIFTY 50 and BANK NIFTY overview
- Yahoo Finance market quotes
- TradingView interactive charts
- Custom watchlist
- SMA 20 and SMA 50 indicators
- RSI 14 technical signals
- Mobile responsive interface

## Installation

Install dependencies:

pip install -r requirements.txt

Start the server:

uvicorn backend.app:app --reload

Open:

http://127.0.0.1:8000

## Deployment

Designed for Railway deployment using railway.json.

## Disclaimer

Market data may be delayed or incomplete.
This application does not execute trades or connect to Zerodha.
Technical indicators are not investment advice.
