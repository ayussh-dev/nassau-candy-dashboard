# 🍬 Nassau Candy Distributor — Shipping Route Efficiency Dashboard

An interactive data analytics dashboard built with **Streamlit** and **Plotly** to analyze factory-to-customer shipping route efficiency for Nassau Candy Distributor.

---

## 📌 Project Overview

Nassau Candy Distributor ships products from **5 factories** across the US to customers in multiple regions. This project analyzes shipping performance data to identify:

- Which routes are most/least efficient
- Geographic bottlenecks causing delays
- Ship mode performance comparison
- State-level and order-level shipping insights

---

## 🏭 Factories

| Factory | Location |
|---|---|
| Lot's O' Nuts | Arizona |
| Wicked Choccy's | Georgia |
| Sugar Shack | Minnesota |
| Secret Factory | Iowa |
| The Other Factory | Tennessee |

---

## 📊 Dashboard Modules

1. **Route Efficiency Overview** — Top/Bottom 10 routes, lead time distribution, full route table
2. **Geographic Map** — US choropleth heatmap, factory locations, regional bottleneck detection
3. **Ship Mode Analysis** — Lead time by ship mode, delay rates, cost-time tradeoffs
4. **Route Drill-Down** — State-level insights, monthly timelines, order-level details

---

## 🚀 How to Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/nassau-candy-dashboard.git
cd nassau-candy-dashboard
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

---

## 📁 Project Structure

```
nassau-candy-dashboard/
├── app.py                          # Main Streamlit application
├── Nassau_Candy_Distributor.csv    # Dataset
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

---

## 🔑 Key KPIs

| KPI | Description |
|---|---|
| Shipping Lead Time | Ship Date − Order Date (days) |
| Average Lead Time | Mean shipping duration per route |
| Route Volume | Number of orders per route |
| Delay Frequency | % of shipments exceeding threshold |
| Efficiency Score | Normalized lead-time performance (0–100) |

---

## 🛠️ Tech Stack

- **Python 3.12**
- **Streamlit** — Web dashboard framework
- **Pandas** — Data processing
- **Plotly** — Interactive charts and maps

---

## 👤 Author

Internship Project — Unified Mentor  
Nassau Candy Distributor — Factory-to-Customer Shipping Route Efficiency Analysis
