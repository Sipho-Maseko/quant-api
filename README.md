# 📈 Algorithmic Trading Risk Management & Backtesting API

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-316192?style=for-the-badge&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker)

A production-ready REST API that ingests live historical market data from Binance, executes vectorized quantitative backtests using Smart Money Concepts (SMC), and persists performance risk metrics to a relational database.

This project was built to demonstrate backend system design, efficient time-series data processing, and containerized deployment architecture.

## 🚀 Features

* **Live Market Data Integration:** Fetches historical klines (candlesticks) directly from the Binance Spot API.
* **Vectorized Backtesting Engine:** Replaces slow procedural loops with high-performance Pandas and NumPy vectorization to identify Bullish and Bearish Fair Value Gaps (FVG).
* **Automated Risk Metrics:** Calculates total return, maximum drawdown, Sharpe ratio, and win rate instantly.
* **Database Persistence:** Uses SQLAlchemy ORM to automatically store strategy parameters and execution results in PostgreSQL.
* **Containerized Infrastructure:** Fully isolated and reproducible environment using Docker and Docker Compose.

## 🏗️ System Architecture

1. **Client** sends a backtest request (Symbol, Timeframe, Capital, Risk %) via HTTP POST.
2. **FastAPI** validates the payload using Pydantic models.
3. The **Engine** fetches up to 1,000 live data points from Binance.
4. **Pandas** processes the data vector-style, computing trade entries, exits, and portfolio equity curves.
5. The results are committed to **PostgreSQL** via SQLAlchemy.
6. The risk metrics and database ID are returned to the client in a structured JSON response.

## ⚙️ Quick Start (Local Deployment)

Run this entire application locally in under 60 seconds using Docker.

**Prerequisites:** Docker Desktop installed and running.

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Sipho-Maseko/quant-api.git](https://github.com/Sipho-Maseko/quant-api.git)
   cd quant-api