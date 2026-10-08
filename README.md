# 🏦 Loan Eligibility Analytics System

A **Streamlit-based Loan Eligibility Analytics System** that combines dataset analysis, financial calculations, eligibility scoring, risk analysis, loan recommendations, interactive visualizations, and PDF report generation in a single web application.

The system is designed as a **rule-based and data-driven analytics application** for educational and demonstration purposes.

---

## 📌 Project Overview

The Loan Eligibility Analytics System helps analyze applicant financial information and estimate loan eligibility using predefined financial and credit criteria.

The application provides two major functionalities:

1. **Dataset Analytics** – Analyze historical loan application data.
2. **Eligibility Checker** – Enter applicant details and calculate an eligibility score, risk level, recommended loan amount, EMI, interest, and repayment details.

The application is developed using **Python and Streamlit** with interactive charts powered by Plotly.

---

## ✨ Features

### 📊 Dataset Analytics
- Total applicants analysis
- Approved and rejected application analysis
- Approval rate calculation
- Dataset preview
- Gender, Education and Property Area filters
- Credit History distribution
- Education-wise approval analysis
- Property Area-wise approval analysis
- Applicant Income visualization
- Loan Amount visualization
- Income category analysis
- Loan category analysis
- Filtered CSV download

### 💰 Financial Analysis
- Average applicant income
- Average loan amount
- Maximum loan amount
- Income vs Loan Amount analysis
- Scatter plot with trendline
- Income category comparison

### 🏦 Loan Eligibility Checker
Applicants can enter:

- Applicant Income
- Coapplicant Income
- Loan Amount
- Loan Term
- Loan Type
- Credit Score
- Education
- Employment Type
- Number of Dependents
- Property Area

The system then calculates:

- Eligibility Score
- Eligibility Status
- Recommended Loan Amount
- Interest Rate
- EMI
- Total Interest
- Total Payment
- Financial Risk
- Credit Risk
- EMI Risk
- Recommendation

---

## 🏦 Supported Loan Types

The system supports the following loan categories:

1. Home Loan
2. Car / Vehicle Loan
3. Education Loan
4. Personal Loan
5. Business Loan
6. Agriculture Loan
7. Medical Loan
8. Credit Card Loan
9. Loan Against Property (LAP)
10. Gold Loan
11. Home Renovation Loan
12. Equipment / Machinery Loan

---

## 📈 Eligibility Scoring

The eligibility score is calculated using predefined rule-based criteria.

The maximum internal score is **12 points**, which is converted into a percentage score out of 100.

The system considers:

- Income Capacity
- Credit Score
- Loan-to-Income Ratio
- Debt-to-Income Ratio
- Education
- Employment Type
- Dependents
- Property Area

### Eligibility Status

| Score | Status |
|---|---|
| 90–100 | VERY HIGH |
| 75–89 | HIGH |
| 50–74 | MEDIUM |
| 25–49 | LOW |
| Below 25 | VERY LOW |

---

## 💳 Credit Score Analysis

The application uses credit score ranges to determine the applicant's credit profile and interest-rate adjustment.

| Credit Score | Profile | Risk |
|---|---|---|
| 800+ | Excellent | Very Low |
| 750–799 | Very Good | Low |
| 700–749 | Good | Low |
| 650–699 | Fair | Medium |
| 600–649 | Poor | High |
| Below 600 | Very Poor | Very High |

---

## 💰 Interest Rate Calculation

The application uses predefined base interest rates for different loan types.

The final interest rate is calculated by applying a credit-score-based adjustment to the selected loan type's base rate.

The rates used in this project are **demonstration assumptions** and are not actual lender offers.

---

## 🧮 EMI Calculation

The application calculates EMI using the standard reducing-balance loan formula:

**EMI = P × r × (1+r)ⁿ / ((1+r)ⁿ − 1)**

Where:

- `P` = Principal Loan Amount
- `r` = Monthly Interest Rate
- `n` = Number of Monthly Installments

The application also calculates:

- Monthly EMI
- Total Interest
- Total Payment

---

## ⚠️ Risk Analysis

The system evaluates three major risk categories:

### Income Risk
Based on applicant income.

### Credit Risk
Based on the applicant's credit score.

### EMI Risk
Based on the Debt-to-Income ratio.

Each risk category is classified as:

- Low
- Medium
- High

---

## 🤖 Recommendation System

Based on the final eligibility status, the system provides a recommendation to the applicant.

It also calculates a suggested loan amount using the applicant's total income and the selected loan type.

The recommendation is generated using predefined business rules rather than a machine-learning prediction model.

---

## 📄 PDF Report Generation

The application can generate a downloadable PDF report containing:

- Applicant Details
- Financial Analysis
- Eligibility Score
- Score Breakdown
- Positive Factors
- Attention Factors
- Risk Analysis
- Loan Details
- Recommendation
- Disclaimer

---

## 📊 Interactive Visualizations

The project uses **Plotly** for interactive data visualization.

Charts include:

- Approval Distribution
- Credit History vs Loan Approval
- Education vs Loan Approval
- Property Area vs Loan Approval
- Applicant Income Distribution
- Loan Amount Distribution
- Income vs Loan Amount
- Eligibility Score Gauge
- Credit Score Visualization
- Risk Analysis

---

## 🗂️ Project Structure

```text
Loan-Eligibility-Analytics/
│
├── app.py
│
├── data/
│   └── loan_data.csv
│
├── requirements.txt
│
└── README.md
```

---

## 🛠️ Technologies Used

- **Python**
- **Streamlit**
- **Pandas**
- **NumPy**
- **Plotly**
- **ReportLab**

---

## 📦 Installation

Clone or download the repository and open the project folder in VS Code.

Install the required Python libraries:

```bash
pip install -r requirements.txt
```

---

## ▶️ Run the Application

Open the project folder in the VS Code terminal and run:

```bash
streamlit run app.py
```

The Streamlit application will open in your browser.

---

## 🔄 Application Workflow

```text
Applicant / Dataset
        ↓
Data Cleaning
        ↓
Financial Analysis
        ↓
Eligibility Calculation
        ↓
Credit Score Analysis
        ↓
Risk Analysis
        ↓
Loan Recommendation
        ↓
EMI & Repayment Calculation
        ↓
Interactive Dashboard
        ↓
PDF Report
```

---

## 🧹 Data Processing

Before analysis, the application performs basic data cleaning:

- Removes duplicate records
- Fills missing numerical values using the median
- Fills missing categorical values using the mode

This helps maintain consistency during dataset analysis.

---

## 🎯 Project Objectives

The main objectives of this project are:

1. To develop an interactive loan analytics dashboard.
2. To analyze historical loan application data.
3. To calculate loan eligibility using predefined financial rules.
4. To analyze credit score and financial risk.
5. To calculate EMI and repayment information.
6. To provide loan recommendations.
7. To generate downloadable PDF reports.
8. To provide an easy-to-use interface for loan analysis.

---

## 👍 Advantages

- Simple and user-friendly interface
- Interactive dashboard
- Multiple loan categories
- Financial analysis
- Credit score analysis
- Risk analysis
- EMI calculation
- Loan recommendation
- PDF report generation
- CSV download functionality
- Rule-based and easy to understand
- Suitable for academic demonstration

---

## ⚠️ Limitations

- Eligibility calculation is based on predefined rules.
- It is not a machine-learning prediction system.
- Interest rates are demonstration assumptions.
- Actual banks and financial institutions may use additional factors.
- The system does not connect directly to banking or credit-bureau APIs.
- The recommendation should not be considered an actual loan approval.

---

## 🚀 Future Scope

The project can be extended by adding:

- Machine Learning-based eligibility prediction
- Real-time credit score API integration
- Bank API integration
- Login and authentication
- Applicant database
- Admin dashboard
- Cloud deployment
- Email/SMS notifications
- Advanced fraud detection
- Personalized loan recommendations
- Real-time lender interest rates

---

## 📌 Disclaimer

This application is developed for **educational and demonstration purposes only**.

The eligibility score, interest rates, recommended loan amount, risk levels, and loan calculations are based on predefined assumptions and should not be considered an actual financial or banking decision.

Actual loan approval depends on the policies, verification procedures, and criteria of individual financial institutions.

---

## 👨‍💻 Developer

**Mahipal Singh**

B.Tech – Computer Science & Engineering

---

## 📚 References

- Python Documentation
- Streamlit Documentation
- Pandas Documentation
- NumPy Documentation
- Plotly Documentation
- ReportLab Documentation

---

## ⭐ Project

**Loan Eligibility Analytics System**

A Python-based interactive analytics application for loan eligibility assessment, financial analysis, risk evaluation, and loan recommendation.
