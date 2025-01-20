# Minimal Viable Product (MVP) Requirements

## Overview
The goal of this MVP is to create an end-to-end data pipeline that extracts financial data from the Twelve Data API, processes it, and provides real-time visualization using Streamlit. The transformed data will be stored in a PostgreSQL database (Pagila schema) for future scalability and analysis.

---

## Requirements

### 1. **Data Extraction (OLTP-Style Data)**
- **Source:** Twelve Data API (Cryptocurrency & Sales Data)
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

### 5. **Automation**
- **Scheduling:** Automate data extraction and transformation process.
- **Tools:** AWS Lambda or cron jobs for periodic updates.
- **Goal:** Ensure continuous data refresh without manual intervention.

---

## Goals of the MVP

1. **Establish a Basic Data Pipeline:**  
   - Successfully extract, transform, and store financial data.
   - Ensure end-to


