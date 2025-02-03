# Minimal Viable Product (MVP) Requirements

## Overview
The goal is to pull in data from the Twelve Data API to obtain some stocks and crypto data. I then transform them locally so and combine them to obtain a single source of truth (SSOT). I then load this into postgres pagila db, the code the update the db runs periodically (hourly). Finally I pull the data out and make some visualisations using streamlit.

---

## Requirements

### 1. **Data Extraction (OLTP-Style Data)**
- **Source:** Twelve Data API (Cryptocurrency & Stocks Data)
- **Frequency:** Hourly updates
- **Format:** JSON response converted to Pandas DataFrame
- **Storage:** Initially stored in Pandas for transformation
- **Why OLTP-Style?**  
  The data retrieved from the API is highly normalized, similar to an OLTP system, making it suitable for transactional operations but inefficient for analytical queries.

---

### 2. **Data Transformation (Denormalization for OLAP)**
- **Objective:** Convert normalized OLTP-style data into a denormalized OLAP table.
- **Operations:**
  - Join related data fields to create a flat, analysis-friendly table.
  - Calculate aggregate values such as averages, price changes, etc.
  - Format data for easier querying by analysts.
- **Why OLAP?**  
  The denormalization process helps improve query performance, reducing the need for complex joins and making data more accessible for analytics.

---

### 3. **Data Storage (PostgreSQL - Pagila Schema)**
- **Database:** PostgreSQL (using Pagila schema)
- **Tables:** Store denormalized data for efficient querying
- **Usage:** Data analysts can access structured data via SQL for reporting and insights.

---

### 4. **Visualization (Real-Time Updates with Streamlit)**
- **Visualization Tool:** Streamlit
- **Purpose:** Present real-time insights using dynamic charts and dashboards
- **Metrics Displayed:**
  - Stock/crypto trends
  - Comparative analysis
  - Moving averages and key indicators
- **Update Frequency:** Dashboard refreshes every minute (or configurable interval)

---

## Goals of the MVP

1. **Establish a Basic Data Pipeline:**  
   - Successfully extract, transform, and store financial data.
   - Ensure end-to-end data flow from API to PostgreSQL and visualization.

2. **Enable Data-Driven Insights:**  
   - Provide a single source of truth through the PostgreSQL database.
   - Ensure easy access for analysts to derive insights.

3. **Optimize Query Performance:**  
   - Transition from OLTP-style to OLAP structure for faster querying.
   - Ensure minimal response times in dashboards.

4. **Real-Time Visualization:**  
   - Deliver up-to-date metrics using Streamlit for financial insights.
   - Automate refresh intervals to avoid manual intervention.

---

## Data Flow Process

```mermaid
graph TD
    A[Twelve Data API] -->|API Call| B{New Data?}
    B -- Yes --> C[Pandas DataFrame]
    B -- No --> G[Wait for Next Interval]
    C --> D[Insert into PostgreSQL Table]
    D --> E[Pagila Database]
    E --> F[Retrieve Data from SQL]
    F --> H[Plots]
    H --> I[Streamlit Visualization]
    G -->|Check Again| A

