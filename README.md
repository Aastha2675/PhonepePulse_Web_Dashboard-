# PeepIntoPe - PhonePe Pulse Web Dashboard 

An interactive full-stack web application designed to visualize and analyze PhonePe’s transaction and user data across India. This platform transforms raw JSON data into actionable business insights through an automated ETL pipeline and a dynamic geographical interface.

## 🚀 Features

- **Interactive Map Visualization:** Integrated **Leaflet.js** for an intuitive Choropleth map, allowing users to select states and view region-specific data.
- **Dynamic Data Filtering:** Filter insights by **Year (2018-2024)**, **Quarter**, and **Transaction Category**.
- **Business Intelligence Dashboards:** Real-time generation of state-wise rankings, total transaction values, and count distributions using **Chart.js**.
- **Automated ETL Pipeline:** A robust Python-based pipeline that extracts nested JSON metadata, transforms it for analytical readiness, and loads it into a structured **MySQL** relational database.
- **High-Performance Backend:** Built with **Flask**, featuring optimized SQL queries, database indexing, and connection pooling to ensure low-latency responses.

## 🛠️ Tech Stack

- **Frontend:** HTML5, CSS3, JavaScript, Leaflet.js (Maps), Chart.js (Graphs)
- **Backend:** Flask (Python)
- **Database:** MySQL
- **Data Processing:** Python (Pandas, SQLAlchemy, JSON)
- **API:** RESTful Architecture

## 📋 Database Schema & ETL

The project processes large-scale data points involving:
1. **Aggregated Insurance:** Transaction trends in the insurance sector.
2. **Aggregated Transactions:** Category-wise (Peer-to-peer, Merchant payments, etc.) breakdowns.
3. **Aggregated Users:** Device-wise and brand-wise user distribution.
4. **Map/Top Tables:** Regional and district-level granularity for deep-dive analysis.

## ⚙️ Installation & Setup

1. **Clone the Repository:**
   ```bash
   git clone [https://github.com/Aastha2675/PhonepePulse_Web_Dashboard-.git](https://github.com/Aastha2675/PhonepePulse_Web_Dashboard-.git)
   cd PhonepePulse_Web_Dashboard
   ```

2. **Install Dependencies:**
  ```
  pip install -r requirements.txt
  ```

3. **Database Configuration:**
```text
 - Create a MySQL database.
 - Update the connection string in the backend configuration file with your credentials.
 - Run the ETL script to migrate data from the JSON source to MySQL.
 ```

4. **Run the Application:**
```bash
python app.py
```

---

## 📈 Optimization Highlights
Query Latency: Reduced data retrieval time by implementing strategic indexing on frequently filtered columns (Year, Quarter, State).

Scalability: Utilized connection pooling to manage concurrent user requests effectively, preventing database bottlenecks during intensive analytical queries.


---

## 👤 Author
Aastha Mhatre | Full Stack AI/ML Developer