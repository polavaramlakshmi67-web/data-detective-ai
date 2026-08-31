# Data Detective AI

## AI-Powered Business Analytics and Automated Data Investigation

Data Detective AI is an interactive business analytics application built with Python, Pandas, and Streamlit. It automatically investigates multiple business datasets, detects important patterns and anomalies, evaluates evidence, and produces actionable business recommendations.

The project simulates a real-world retail analytics environment using **RetailIQ**, a fictional e-commerce business.

---

## Project Overview

Business teams often have large amounts of data but need to quickly identify where the most important business problems are.

Data Detective AI addresses this by automatically examining business data and answering questions such as:

* Where is the strongest business signal?
* Are inventory levels becoming risky?
* Which customer issues occur most frequently?
* How are sales changing over time?
* Are there unusual sales values?
* How much is being spent on marketing?
* Which areas require further investigation?
* What action should the business consider?

The application goes beyond displaying charts by turning data into an investigation and business recommendation.

---

## How It Works

```text
Business Data
      |
      v
Data Loading
      |
      v
Data Quality Checks
      |
      v
Business Metric Detection
      |
      v
Anomaly and Trend Analysis
      |
      v
Evidence Scoring
      |
      v
Strongest Business Signal
      |
      v
Recommended Action
      |
      v
Detective Conclusion
```

---

## Datasets

The application automatically loads six datasets from the `data/` directory.

| Dataset         | Description                                             |
| --------------- | ------------------------------------------------------- |
| `sales.csv`     | Sales, revenue, profit, orders and transaction analysis |
| `customers.csv` | Customer-level analysis                                 |
| `products.csv`  | Product information and performance analysis            |
| `inventory.csv` | Stock levels and inventory-risk analysis                |
| `marketing.csv` | Marketing spend and campaign activity                   |
| `support.csv`   | Customer support tickets and issue analysis             |

### Dataset Size

The RetailIQ sample environment contains:

* 12,000 sales records
* 500 customers
* 20 products
* 360 inventory records
* 72 marketing records
* 3,000 support tickets

---

## Features

### Business Dashboard

Provides an overview of important business KPIs:

* Revenue
* Profit
* Orders
* Customers
* Support tickets
* Regional revenue
* Monthly revenue trends

### AI Business Detective

The detective engine evaluates available business metrics and identifies the strongest evidence-based signal.

Potential signals include:

* Inventory
* Profit
* Customer Support
* Marketing
* Sales Anomalies
* Data Quality

The detective produces:

* Strongest Signal
* Evidence Score
* Supporting Evidence
* Recommended Action
* Detective Conclusion

### Inventory Investigation

Analyzes inventory data to identify potentially risky stock levels.

Includes:

* Inventory records
* Low-stock records
* Stock thresholds
* Product-level inventory analysis

### Marketing Investigation

Analyzes marketing activity using available campaign metrics.

Includes:

* Marketing spend
* Campaign clicks
* Average cost per click
* Campaign activity

### Customer Support Investigation

Analyzes support tickets to identify recurring customer problems.

Includes:

* Total support tickets
* Number of issue types
* Regional distribution
* Most common customer issues

### Automated Data Profiling

For any selected dataset, the application reports:

* Number of rows
* Number of columns
* Missing values
* Duplicate rows
* Data types
* Unique values
* Numeric statistics
* Potential outliers

### Anomaly Detection

The application uses the Interquartile Range method to identify potential numerical outliers.

```text
IQR = Q3 - Q1

Lower Bound = Q1 - 1.5 × IQR

Upper Bound = Q3 + 1.5 × IQR
```

Values outside these boundaries are flagged as potential anomalies.

---

## Technology Stack

### Programming

* Python

### Data Analysis

* Pandas
* NumPy

### Visualization

* Streamlit
* Plotly
* Matplotlib
* Seaborn

### Machine Learning and Statistics

* Scikit-learn
* Statistical anomaly detection techniques

### Data Storage

* CSV

---

## Project Structure

```text
data-detective-ai/
|
├── data/
│   ├── sales.csv
│   ├── customers.csv
│   ├── products.csv
│   ├── inventory.csv
│   ├── marketing.csv
│   └── support.csv
|
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
|
└── .venv/
```

The `.venv/` directory is used only for local development and should not be uploaded to GitHub.

---

## Installation

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd data-detective-ai
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```cmd
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Run the Application

Start the Streamlit application:

```bash
python -m streamlit run app.py
```

The application will be available at:

```text
http://localhost:8501
```

---

## Example Detective Output

```text
Strongest Signal: Inventory

Evidence Score: 92.6 / 100

Evidence:
A significant number of inventory records
show potentially low stock levels.

Recommended Action:
Review low-stock products against sales demand
and prioritize replenishment where demand is strong.
```

The conclusion is generated from the available dataset rather than being manually entered as a business finding.

---

## Currency

The application uses Indian Rupees (INR) for business metrics.

Example:

```text
Revenue: ₹352,367
Marketing Spend: ₹27,546
```

This makes the project relevant to an Indian business analytics environment.

---

## Analytical Skills Demonstrated

This project demonstrates practical experience with:

* Data cleaning
* Exploratory Data Analysis
* Business KPI analysis
* Data profiling
* Missing-value analysis
* Duplicate detection
* Outlier detection
* Trend analysis
* Group-by analysis
* Data aggregation
* Business problem identification
* Evidence-based recommendations
* Dashboard development
* Python data analysis
* Streamlit application development
* Statistical analysis

---

## Business Value

The application follows a business-focused analytics workflow:

```text
What happened?
      |
      v
Where did it happen?
      |
      v
How significant is it?
      |
      v
What evidence supports it?
      |
      v
What should be investigated?
      |
      v
What action could be taken?
```

This demonstrates the progression from raw business data to analysis, insight, and recommendation.

---

## Future Improvements

Planned improvements include:

* Natural-language questions over datasets
* LLM-powered business explanations
* Automated PDF and Excel reports
* Sales forecasting
* Customer segmentation
* Product recommendation analysis
* Marketing ROI analysis
* Profit-margin analysis
* Cross-dataset relationship detection
* Automated root-cause analysis
* Advanced interactive filters
* Database integration
* Cloud deployment

---

## Project Status

**Status: Working Prototype**

The current application automatically loads and investigates six RetailIQ business datasets.

---

## Why Data Detective AI?

Traditional dashboards primarily answer:

> What happened?

Data Detective AI aims to go further:

> What looks important, what evidence supports it, and what should the business investigate next?

---

## License

This project is intended for educational and portfolio purposes.

---

## Author

**Lakshmi Polavaram**

Artificial Intelligence and Data Science

Focus: Data Analytics, Business Intelligence, Python, SQL, Power BI and Data Visualization
