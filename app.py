import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Loan Eligibility Analytics",
    page_icon="🏦",
    layout="wide"
)


# =========================================================
# CSS (theme-safe: works in light and dark mode)
# =========================================================

st.markdown("""
<style>

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

.dashboard-title {
    font-size: 38px;
    font-weight: 800;
    color: inherit;
    margin-bottom: 5px;
}

.dashboard-subtitle {
    font-size: 17px;
    color: inherit;
    opacity: 0.7;
    margin-bottom: 25px;
}

.section-title {
    font-size: 25px;
    font-weight: 700;
    color: inherit;
    margin-top: 20px;
    margin-bottom: 15px;
}

/* Status box: light background, so text is forced dark */
.status-box {
    padding: 20px;
    border-radius: 14px;
    margin: 15px 0;
    text-align: center;
}

.status-box h2,
.status-box h3,
.status-box p {
    color: #172033 !important;
}

.very-high {
    background-color: #d1fae5;
    border: 2px solid #10b981;
}

.high {
    background-color: #dcfce7;
    border: 2px solid #22c55e;
}

.medium {
    background-color: #fef3c7;
    border: 2px solid #f59e0b;
}

.low {
    background-color: #ffedd5;
    border: 2px solid #f97316;
}

.very-low {
    background-color: #fee2e2;
    border: 2px solid #ef4444;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# TITLE
# =========================================================

st.markdown(
    '<div class="dashboard-title">🏦 Loan Eligibility Analytics</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="dashboard-subtitle">'
    'Data-driven loan eligibility, financial analysis and risk assessment system'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# LOAD DATA
# =========================================================

DATA_PATH = "data/loan_data.csv"

try:
    df = pd.read_csv(DATA_PATH)
except FileNotFoundError:
    st.error(
        f"Dataset not found at `{DATA_PATH}`. "
        "Please make sure the data folder and loan_data.csv exist."
    )
    st.stop()


# =========================================================
# DATA CLEANING
# =========================================================

df = df.drop_duplicates()

numeric_columns = df.select_dtypes(include=["number"]).columns

for col in numeric_columns:
    df[col] = df[col].fillna(df[col].median())


categorical_columns = df.select_dtypes(include=["object"]).columns

for col in categorical_columns:
    if not df[col].mode().empty:
        df[col] = df[col].fillna(df[col].mode()[0])


# =========================================================
# LOAN TYPES
# =========================================================

LOAN_TYPES = {
    "🏠 Home Loan": {
        "base_rate": 8.5,
        "terms": [120, 180, 240, 300, 360],
        "multiplier": 25
    },

    "🚗 Car / Vehicle Loan": {
        "base_rate": 9.5,
        "terms": [36, 48, 60, 72, 84],
        "multiplier": 18
    },

    "🎓 Education Loan": {
        "base_rate": 10.0,
        "terms": [60, 84, 120, 180],
        "multiplier": 15
    },

    "💼 Personal Loan": {
        "base_rate": 12.5,
        "terms": [12, 24, 36, 48, 60, 72],
        "multiplier": 12
    },

    "🏢 Business Loan": {
        "base_rate": 11.5,
        "terms": [12, 24, 36, 48, 60, 84, 120],
        "multiplier": 20
    },

    "🌾 Agriculture Loan": {
        "base_rate": 10.5,
        "terms": [12, 24, 36, 48, 60, 84, 120],
        "multiplier": 18
    },

    "🏥 Medical Loan": {
        "base_rate": 11.5,
        "terms": [12, 24, 36, 48, 60],
        "multiplier": 10
    },

    "💳 Credit Card Loan": {
        "base_rate": 15.0,
        "terms": [6, 12, 18, 24, 36],
        "multiplier": 8
    },

    "🏦 Loan Against Property (LAP)": {
        "base_rate": 9.5,
        "terms": [60, 84, 120, 180, 240],
        "multiplier": 25
    },

    "🪙 Gold Loan": {
        "base_rate": 9.5,
        "terms": [12, 24, 36, 48, 60],
        "multiplier": 10
    },

    "🏠 Home Renovation Loan": {
        "base_rate": 9.0,
        "terms": [60, 84, 120, 180],
        "multiplier": 15
    },

    "🚜 Equipment / Machinery Loan": {
        "base_rate": 10.5,
        "terms": [24, 36, 48, 60, 84, 120],
        "multiplier": 18
    }
}


# =========================================================
# CREDIT SCORE BASED RATE
# =========================================================

def calculate_interest_rate(loan_type, credit_score):

    base_rate = LOAN_TYPES[loan_type]["base_rate"]

    if credit_score >= 800:
        adjustment = 0.00

    elif credit_score >= 750:
        adjustment = 0.25

    elif credit_score >= 700:
        adjustment = 0.75

    elif credit_score >= 650:
        adjustment = 1.50

    elif credit_score >= 600:
        adjustment = 2.50

    else:
        adjustment = 4.00

    return round(base_rate + adjustment, 2)


# =========================================================
# CREDIT SCORE PROFILE
# =========================================================

def credit_score_profile(credit_score):

    if credit_score >= 800:
        return "Excellent", "Very Low"

    elif credit_score >= 750:
        return "Very Good", "Low"

    elif credit_score >= 700:
        return "Good", "Low"

    elif credit_score >= 650:
        return "Fair", "Medium"

    elif credit_score >= 600:
        return "Poor", "High"

    else:
        return "Very Poor", "Very High"


# =========================================================
# EMI CALCULATION
# =========================================================

def calculate_emi(loan_amount, loan_term, interest_rate):

    if loan_amount <= 0 or loan_term <= 0:
        return 0

    monthly_rate = interest_rate / 12 / 100

    if monthly_rate == 0:
        return loan_amount / loan_term

    emi = (
        loan_amount
        * monthly_rate
        * (1 + monthly_rate) ** loan_term
        / ((1 + monthly_rate) ** loan_term - 1)
    )

    return emi


# =========================================================
# LOAN DETAILS
# =========================================================

def calculate_loan_details(
    loan_amount,
    loan_term,
    loan_type,
    credit_score
):

    interest_rate = calculate_interest_rate(
        loan_type,
        credit_score
    )

    emi = calculate_emi(
        loan_amount,
        loan_term,
        interest_rate
    )

    total_payment = emi * loan_term

    total_interest = total_payment - loan_amount

    return {
        "interest_rate": interest_rate,
        "emi": emi,
        "total_interest": total_interest,
        "total_payment": total_payment
    }


# =========================================================
# ELIGIBILITY CALCULATION
# =========================================================

def calculate_eligibility(
    applicant_income,
    coapplicant_income,
    loan_amount,
    loan_term,
    loan_type,
    credit_score,
    education,
    employment,
    dependents,
    property_area
):

    total_income = applicant_income + coapplicant_income

    loan_details = calculate_loan_details(
        loan_amount,
        loan_term,
        loan_type,
        credit_score
    )

    emi = loan_details["emi"]

    if total_income > 0:
        dti = (emi / total_income) * 100
        loan_income_ratio = loan_amount / total_income
    else:
        dti = 100
        loan_income_ratio = 999

    # -----------------------------------------------------
    # INTERNAL SCORE
    # MAXIMUM = 12
    # -----------------------------------------------------

    score = 0

    score_breakdown = []
    positive_factors = []
    reasons = []

    # Income
    if total_income >= 50000:
        score += 2
        score_breakdown.append(
            ("Income Capacity", 2, "Strong")
        )
        positive_factors.append(
            "Strong combined monthly income."
        )

    elif total_income >= 25000:
        score += 1
        score_breakdown.append(
            ("Income Capacity", 1, "Moderate")
        )

    else:
        score_breakdown.append(
            ("Income Capacity", 0, "Low")
        )
        reasons.append(
            "Monthly income is relatively low."
        )

    # Credit Score
    if credit_score >= 750:
        score += 2
        score_breakdown.append(
            ("Credit Score", 2, "Excellent/Very Good")
        )
        positive_factors.append(
            "Strong credit score improves borrowing profile."
        )

    elif credit_score >= 650:
        score += 1
        score_breakdown.append(
            ("Credit Score", 1, "Fair")
        )

    else:
        score_breakdown.append(
            ("Credit Score", 0, "Poor")
        )
        reasons.append(
            "Low credit score increases lending risk."
        )

    # Loan to Income Ratio
    if loan_income_ratio <= 10:
        score += 2
        score_breakdown.append(
            ("Loan-to-Income", 2, "Strong")
        )
        positive_factors.append(
            "Requested loan is reasonable compared with income."
        )

    elif loan_income_ratio <= 20:
        score += 1
        score_breakdown.append(
            ("Loan-to-Income", 1, "Moderate")
        )

    else:
        score_breakdown.append(
            ("Loan-to-Income", 0, "High")
        )
        reasons.append(
            "Requested loan is high compared with monthly income."
        )

    # DTI
    if dti <= 30:
        score += 2
        score_breakdown.append(
            ("Debt-to-Income", 2, "Low")
        )
        positive_factors.append(
            "EMI burden is comfortably within income."
        )

    elif dti <= 40:
        score += 1
        score_breakdown.append(
            ("Debt-to-Income", 1, "Moderate")
        )

    else:
        score_breakdown.append(
            ("Debt-to-Income", 0, "High")
        )
        reasons.append(
            "EMI burden is high compared with monthly income."
        )

    # Education
    if education == "Graduate":
        score += 1
        score_breakdown.append(
            ("Education", 1, "Graduate")
        )
        positive_factors.append(
            "Graduate education profile."
        )

    else:
        score_breakdown.append(
            ("Education", 0, "Not Graduate")
        )

    # Employment
    if employment == "Salaried":
        score += 1
        score_breakdown.append(
            ("Employment", 1, "Salaried")
        )
        positive_factors.append(
            "Salaried employment indicates stable income."
        )

    else:
        score_breakdown.append(
            ("Employment", 0, "Self Employed")
        )

    # Dependents
    if dependents in ["0", "1"]:
        score += 1
        score_breakdown.append(
            ("Dependents", 1, "Low")
        )

    else:
        score_breakdown.append(
            ("Dependents", 0, "Higher")
        )
        reasons.append(
            "Higher number of dependents may increase financial obligations."
        )

    # Property
    if property_area in ["Urban", "Semiurban"]:
        score += 1
        score_breakdown.append(
            ("Property Area", 1, property_area)
        )

    else:
        score_breakdown.append(
            ("Property Area", 0, property_area)
        )

    # -----------------------------------------------------
    # SCORE CONVERSION
    # -----------------------------------------------------

    original_max_score = 12

    score_out_of_100 = round(
        (score / original_max_score) * 100,
        2
    )

    # -----------------------------------------------------
    # STATUS
    # -----------------------------------------------------

    if score_out_of_100 >= 90:
        status = "VERY HIGH"

        result_message = (
            "Excellent financial profile. "
            "The applicant shows very strong eligibility "
            "based on income, credit score, debt level "
            "and other factors."
        )

    elif score_out_of_100 >= 75:
        status = "HIGH"

        result_message = (
            "Strong eligibility profile. "
            "The applicant appears financially capable "
            "of handling the requested loan."
        )

    elif score_out_of_100 >= 50:
        status = "MEDIUM"

        result_message = (
            "Moderate eligibility. The applicant may qualify, "
            "but some financial factors should be reviewed "
            "before approving the loan."
        )

    elif score_out_of_100 >= 25:
        status = "LOW"

        result_message = (
            "Low eligibility profile. The applicant should "
            "consider reducing the requested loan amount "
            "or improving financial factors."
        )

    else:
        status = "VERY LOW"

        result_message = (
            "Very low eligibility profile. The requested loan "
            "may create a significant financial burden."
        )

    # -----------------------------------------------------
    # RECOMMENDED LOAN
    # -----------------------------------------------------

    multiplier = LOAN_TYPES[loan_type]["multiplier"]

    if status == "VERY HIGH":
        recommended_loan = total_income * multiplier

    elif status == "HIGH":
        recommended_loan = total_income * (multiplier * 0.85)

    elif status == "MEDIUM":
        recommended_loan = total_income * (multiplier * 0.65)

    elif status == "LOW":
        recommended_loan = total_income * (multiplier * 0.45)

    else:
        recommended_loan = total_income * (multiplier * 0.30)

    # -----------------------------------------------------
    # CREDIT RISK
    # -----------------------------------------------------

    if credit_score >= 750:
        credit_risk = "LOW"

    elif credit_score >= 650:
        credit_risk = "MEDIUM"

    else:
        credit_risk = "HIGH"

    # Income risk
    if total_income >= 50000:
        income_risk = "LOW"

    elif total_income >= 25000:
        income_risk = "MEDIUM"

    else:
        income_risk = "HIGH"

    # EMI risk
    if dti <= 30:
        emi_risk = "LOW"

    elif dti <= 40:
        emi_risk = "MEDIUM"

    else:
        emi_risk = "HIGH"

    # -----------------------------------------------------
    # RECOMMENDATION
    # -----------------------------------------------------

    if status == "VERY HIGH":

        recommendation = (
            f"The applicant has a very strong profile for a "
            f"{loan_type}. The credit score and repayment "
            f"capacity are favorable. The requested loan appears "
            f"financially manageable."
        )

    elif status == "HIGH":

        recommendation = (
            f"The applicant has a strong profile for a "
            f"{loan_type}. Approval may be considered subject "
            f"to lender verification and documentation."
        )

    elif status == "MEDIUM":

        recommendation = (
            f"The applicant has moderate eligibility for a "
            f"{loan_type}. Consider reducing the loan amount "
            f"or improving income/credit profile."
        )

    elif status == "LOW":

        recommendation = (
            f"The applicant has a relatively weak profile for "
            f"the selected {loan_type}. A lower loan amount or "
            f"better credit profile is recommended."
        )

    else:

        recommendation = (
            f"The applicant currently has a very weak profile "
            f"for the selected {loan_type}. Improving credit "
            f"score, income and debt capacity is recommended."
        )

    # Credit score message
    credit_profile, credit_risk_profile = credit_score_profile(
        credit_score
    )

    return {

        "total_income": total_income,

        "emi": loan_details["emi"],

        "interest_rate": loan_details["interest_rate"],

        "total_interest": loan_details["total_interest"],

        "total_payment": loan_details["total_payment"],

        "dti": dti,

        "loan_income_ratio": loan_income_ratio,

        "score": score_out_of_100,

        "raw_score": score,

        "max_score": 100,

        "original_max_score": original_max_score,

        "status": status,

        "result_message": result_message,

        "recommended_loan": recommended_loan,

        "positive_factors": positive_factors,

        "reasons": reasons,

        "score_breakdown": score_breakdown,

        "income_risk": income_risk,

        "emi_risk": emi_risk,

        "credit_risk": credit_risk,

        "credit_profile": credit_profile,

        "credit_risk_profile": credit_risk_profile,

        "recommendation": recommendation
    }


# =========================================================
# PDF GENERATION
# =========================================================

def generate_pdf(input_data, result):

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=35,
        leftMargin=35,
        topMargin=35,
        bottomMargin=35
    )

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(
            "<b>Loan Eligibility Analytics Report</b>",
            styles["Title"]
        )
    )

    story.append(
        Spacer(1, 15)
    )

    story.append(
        Paragraph(
            f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M')}",
            styles["Normal"]
        )
    )

    story.append(
        Spacer(1, 15)
    )

    # Applicant Details

    story.append(
        Paragraph(
            "<b>Applicant Details</b>",
            styles["Heading2"]
        )
    )

    applicant_table = [
        ["Parameter", "Value"],
        ["Loan Type", input_data["loan_type"]],
        ["Credit Score", str(input_data["credit_score"])],
        ["Credit Profile", result["credit_profile"]],
        ["Applicant Income", f"₹{input_data['applicant_income']:,.2f}"],
        ["Co-applicant Income", f"₹{input_data['coapplicant_income']:,.2f}"],
        ["Loan Amount", f"₹{input_data['loan_amount']:,.2f}"],
        ["Loan Term", f"{input_data['loan_term']} months"],
        ["Education", input_data["education"]],
        ["Employment", input_data["employment"]],
        ["Dependents", input_data["dependents"]],
        ["Property Area", input_data["property_area"]]
    ]

    table = Table(
        applicant_table,
        colWidths=[190, 300]
    )

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#172033")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 7),
        ])
    )

    story.append(table)

    story.append(
        Spacer(1, 20)
    )

    # Financial Analysis

    story.append(
        Paragraph(
            "<b>Financial Analysis</b>",
            styles["Heading2"]
        )
    )

    financial_table = [
        ["Parameter", "Value"],

        ["Eligibility Score",
         f"{result['score']:.2f} / 100"],

        ["Eligibility Level",
         result["status"]],

        ["Interest Rate",
         f"{result['interest_rate']:.2f}%"],

        ["Total Monthly Income",
         f"₹{result['total_income']:,.2f}"],

        ["Estimated EMI",
         f"₹{result['emi']:,.2f}"],

        ["Total Interest",
         f"₹{result['total_interest']:,.2f}"],

        ["Total Repayment",
         f"₹{result['total_payment']:,.2f}"],

        ["Debt-to-Income Ratio",
         f"{result['dti']:.2f}%"],

        ["Loan-to-Income Ratio",
         f"{result['loan_income_ratio']:.2f}"],

        ["Recommended Loan",
         f"₹{result['recommended_loan']:,.2f}"]
    ]

    table2 = Table(
        financial_table,
        colWidths=[190, 300]
    )

    table2.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#172033")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 7),
        ])
    )

    story.append(table2)

    story.append(
        Spacer(1, 20)
    )

    # Score Breakdown

    story.append(
        Paragraph(
            "<b>Score Breakdown</b>",
            styles["Heading2"]
        )
    )

    breakdown_table = [
        ["Factor", "Points", "Assessment"]
    ]

    for factor, points, assessment in result["score_breakdown"]:

        breakdown_table.append([
            factor,
            str(points),
            assessment
        ])

    table3 = Table(
        breakdown_table,
        colWidths=[210, 80, 200]
    )

    table3.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#172033")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 7),
        ])
    )

    story.append(table3)

    story.append(
        Spacer(1, 20)
    )

    # Positive Factors

    story.append(
        Paragraph(
            "<b>Positive Factors</b>",
            styles["Heading2"]
        )
    )

    if result["positive_factors"]:

        for factor in result["positive_factors"]:

            story.append(
                Paragraph(
                    "✓ " + factor,
                    styles["Normal"]
                )
            )

    else:

        story.append(
            Paragraph(
                "No major positive factors identified.",
                styles["Normal"]
            )
        )

    story.append(
        Spacer(1, 15)
    )

    # Negative Factors

    story.append(
        Paragraph(
            "<b>Factors Requiring Attention</b>",
            styles["Heading2"]
        )
    )

    if result["reasons"]:

        for reason in result["reasons"]:

            story.append(
                Paragraph(
                    "• " + reason,
                    styles["Normal"]
                )
            )

    else:

        story.append(
            Paragraph(
                "No major negative factors identified.",
                styles["Normal"]
            )
        )

    story.append(
        Spacer(1, 15)
    )

    # Recommendation

    story.append(
        Paragraph(
            "<b>Final Recommendation</b>",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph(
            result["recommendation"],
            styles["Normal"]
        )
    )

    story.append(
        Spacer(1, 20)
    )

    story.append(
        Paragraph(
            "<b>Eligibility Scale</b>",
            styles["Heading2"]
        )
    )

    scale_data = [
        ["Score", "Level"],
        ["90 - 100", "VERY HIGH"],
        ["75 - 89.99", "HIGH"],
        ["50 - 74.99", "MEDIUM"],
        ["25 - 49.99", "LOW"],
        ["0 - 24.99", "VERY LOW"]
    ]

    scale_table = Table(
        scale_data,
        colWidths=[190, 300]
    )

    scale_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#172033")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 7),
        ])
    )

    story.append(scale_table)

    story.append(
        Spacer(1, 20)
    )

    story.append(
        Paragraph(
            "<b>Note:</b> This report is a rule-based academic/project "
            "assessment and does not represent actual bank approval.",
            styles["Normal"]
        )
    )

    document.build(story)

    buffer.seek(0)

    return buffer


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🏦 Loan Analytics")

page = st.sidebar.radio(
    "Select Module",
    [
        "📊 Overview",
        "💰 Financial Analysis",
        "📈 Approval Insights",
        "🏦 Eligibility Checker"
    ]
)


# =========================================================
# OVERVIEW
# =========================================================

if page == "📊 Overview":

    st.markdown(
        '<div class="section-title">📊 Dataset Overview</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    total_applicants = len(df)

    if "Loan_Status" in df.columns:

        approved = (
            df["Loan_Status"]
            .astype(str)
            .str.upper()
            .eq("Y")
            .sum()
        )

        rejected = total_applicants - approved

        approval_rate = (
            approved / total_applicants * 100
            if total_applicants > 0
            else 0
        )

    else:

        approved = 0
        rejected = 0
        approval_rate = 0

    col1.metric(
        "Total Applicants",
        total_applicants
    )

    col2.metric(
        "Approved",
        approved
    )

    col3.metric(
        "Rejected",
        rejected
    )

    col4.metric(
        "Approval Rate",
        f"{approval_rate:.2f}%"
    )

    st.markdown(
        '<div class="section-title">Dataset Preview</div>',
        unsafe_allow_html=True
    )

    st.dataframe(
        df.head(20),
        use_container_width=True
    )

    # Approval Distribution

    if "Loan_Status" in df.columns:

        st.markdown(
            '<div class="section-title">Approval Distribution</div>',
            unsafe_allow_html=True
        )

        approval_counts = (
            df["Loan_Status"]
            .value_counts()
            .reset_index()
        )

        approval_counts.columns = [
            "Loan_Status",
            "Count"
        ]

        fig = px.pie(
            approval_counts,
            names="Loan_Status",
            values="Count",
            hole=0.45,
            title="Approved vs Rejected"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # Filters

    st.markdown(
        '<div class="section-title">Applicant Filters</div>',
        unsafe_allow_html=True
    )

    filter_cols = st.columns(3)

    filtered_df = df.copy()

    if "Gender" in df.columns:

        gender_options = ["All"] + sorted(
            df["Gender"].dropna().astype(str).unique().tolist()
        )

        selected_gender = filter_cols[0].selectbox(
            "Gender",
            gender_options
        )

        if selected_gender != "All":

            filtered_df = filtered_df[
                filtered_df["Gender"].astype(str)
                == selected_gender
            ]

    if "Education" in df.columns:

        education_options = ["All"] + sorted(
            df["Education"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        selected_education = filter_cols[1].selectbox(
            "Education",
            education_options
        )

        if selected_education != "All":

            filtered_df = filtered_df[
                filtered_df["Education"].astype(str)
                == selected_education
            ]

    if "Property_Area" in df.columns:

        property_options = ["All"] + sorted(
            df["Property_Area"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        selected_property = filter_cols[2].selectbox(
            "Property Area",
            property_options
        )

        if selected_property != "All":

            filtered_df = filtered_df[
                filtered_df["Property_Area"].astype(str)
                == selected_property
            ]

    st.dataframe(
        filtered_df,
        use_container_width=True
    )

    # CSV Download

    csv_data = filtered_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "⬇️ Download Filtered CSV",
        csv_data,
        "filtered_loan_data.csv",
        "text/csv"
    )

    # Filtered approval rate

    if "Loan_Status" in filtered_df.columns:

        filtered_approved = (
            filtered_df["Loan_Status"]
            .astype(str)
            .str.upper()
            .eq("Y")
            .sum()
        )

        filtered_total = len(filtered_df)

        filtered_rate = (
            filtered_approved / filtered_total * 100
            if filtered_total > 0
            else 0
        )

        st.metric(
            "Filtered Approval Rate",
            f"{filtered_rate:.2f}%"
        )

    # Credit History Distribution

    if "Credit_History" in df.columns:

        st.markdown(
            '<div class="section-title">Credit History Distribution</div>',
            unsafe_allow_html=True
        )

        credit_counts = (
            df["Credit_History"]
            .value_counts()
            .reset_index()
        )

        credit_counts.columns = [
            "Credit_History",
            "Count"
        ]

        fig_credit = px.bar(
            credit_counts,
            x="Credit_History",
            y="Count",
            title="Credit History Distribution"
        )

        st.plotly_chart(
            fig_credit,
            use_container_width=True
        )

    # Education approval rate

    if (
        "Education" in df.columns
        and "Loan_Status" in df.columns
    ):

        education_approval = (
            df.groupby("Education")["Loan_Status"]
            .apply(
                lambda x:
                x.astype(str)
                .str.upper()
                .eq("Y")
                .mean() * 100
            )
            .reset_index()
        )

        education_approval.columns = [
            "Education",
            "Approval Rate"
        ]

        fig_education = px.bar(
            education_approval,
            x="Education",
            y="Approval Rate",
            title="Education-wise Approval Rate"
        )

        st.plotly_chart(
            fig_education,
            use_container_width=True
        )

    # Property approval rate

    if (
        "Property_Area" in df.columns
        and "Loan_Status" in df.columns
    ):

        property_approval = (
            df.groupby("Property_Area")["Loan_Status"]
            .apply(
                lambda x:
                x.astype(str)
                .str.upper()
                .eq("Y")
                .mean() * 100
            )
            .reset_index()
        )

        property_approval.columns = [
            "Property Area",
            "Approval Rate"
        ]

        fig_property = px.bar(
            property_approval,
            x="Property Area",
            y="Approval Rate",
            title="Property Area-wise Approval Rate"
        )

        st.plotly_chart(
            fig_property,
            use_container_width=True
        )

    # Income histogram

    if "ApplicantIncome" in df.columns:

        fig_income = px.histogram(
            df,
            x="ApplicantIncome",
            nbins=30,
            title="Applicant Income Distribution"
        )

        st.plotly_chart(
            fig_income,
            use_container_width=True
        )

    # Loan histogram

    if "LoanAmount" in df.columns:

        fig_loan = px.histogram(
            df,
            x="LoanAmount",
            nbins=30,
            title="Loan Amount Distribution"
        )

        st.plotly_chart(
            fig_loan,
            use_container_width=True
        )

    # Statistics

    stat_cols = st.columns(3)

    if "ApplicantIncome" in df.columns:

        stat_cols[0].metric(
            "Average Income",
            f"₹{df['ApplicantIncome'].mean():,.2f}"
        )

    if "LoanAmount" in df.columns:

        stat_cols[1].metric(
            "Average Loan",
            f"₹{df['LoanAmount'].mean():,.2f}"
        )

        stat_cols[2].metric(
            "Highest Loan",
            f"₹{df['LoanAmount'].max():,.2f}"
        )

    # Income categories

    if "ApplicantIncome" in df.columns:

        df["Income_Category"] = pd.cut(
            df["ApplicantIncome"],
            bins=[
                -float("inf"),
                25000,
                50000,
                100000,
                float("inf")
            ],
            labels=[
                "Low",
                "Medium",
                "High",
                "Very High"
            ]
        )

        income_category = (
            df["Income_Category"]
            .value_counts()
            .reset_index()
        )

        income_category.columns = [
            "Income Category",
            "Count"
        ]

        fig_income_category = px.bar(
            income_category,
            x="Income Category",
            y="Count",
            title="Income Categories"
        )

        st.plotly_chart(
            fig_income_category,
            use_container_width=True
        )

    # Loan categories

    if "LoanAmount" in df.columns:

        df["Loan_Category"] = pd.cut(
            df["LoanAmount"],
            bins=[
                -float("inf"),
                100,
                300,
                500,
                float("inf")
            ],
            labels=[
                "Small",
                "Medium",
                "Large",
                "Very Large"
            ]
        )

        loan_category = (
            df["Loan_Category"]
            .value_counts()
            .reset_index()
        )

        loan_category.columns = [
            "Loan Category",
            "Count"
        ]

        fig_loan_category = px.bar(
            loan_category,
            x="Loan Category",
            y="Count",
            title="Loan Categories"
        )

        st.plotly_chart(
            fig_loan_category,
            use_container_width=True
        )

    # Approved vs rejected comparison

    if (
        "Loan_Status" in df.columns
        and "ApplicantIncome" in df.columns
        and "LoanAmount" in df.columns
    ):

        comparison = (
            df.groupby("Loan_Status")[
                ["ApplicantIncome", "LoanAmount"]
            ]
            .mean()
            .reset_index()
        )

        comparison = comparison.melt(
            id_vars="Loan_Status",
            var_name="Metric",
            value_name="Average"
        )

        fig_comparison = px.bar(
            comparison,
            x="Loan_Status",
            y="Average",
            color="Metric",
            barmode="group",
            title="Approved vs Rejected Financial Comparison"
        )

        st.plotly_chart(
            fig_comparison,
            use_container_width=True
        )

    # Median / ratio

    ratio_cols = st.columns(3)

    if "ApplicantIncome" in df.columns:

        ratio_cols[0].metric(
            "Median Income",
            f"₹{df['ApplicantIncome'].median():,.2f}"
        )

    if "LoanAmount" in df.columns:

        ratio_cols[1].metric(
            "Median Loan",
            f"₹{df['LoanAmount'].median():,.2f}"
        )

    if (
        "ApplicantIncome" in df.columns
        and "LoanAmount" in df.columns
    ):

        ratio = (
            df["LoanAmount"]
            / df["ApplicantIncome"]
        ).median()

        ratio_cols[2].metric(
            "Median Loan/Income Ratio",
            f"{ratio:.2f}"
        )


# =========================================================
# FINANCIAL ANALYSIS
# =========================================================

elif page == "💰 Financial Analysis":

    st.markdown(
        '<div class="section-title">💰 Financial Analysis</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    if "ApplicantIncome" in df.columns:

        col1.metric(
            "Average Applicant Income",
            f"₹{df['ApplicantIncome'].mean():,.2f}"
        )

    if "LoanAmount" in df.columns:

        col2.metric(
            "Average Loan Amount",
            f"₹{df['LoanAmount'].mean():,.2f}"
        )

        col3.metric(
            "Maximum Loan Amount",
            f"₹{df['LoanAmount'].max():,.2f}"
        )

    # Income vs Loan

    if (
        "ApplicantIncome" in df.columns
        and "LoanAmount" in df.columns
    ):

        fig_scatter = px.scatter(
            df,
            x="ApplicantIncome",
            y="LoanAmount",
            title="Applicant Income vs Loan Amount"
        )

        # Manual trendline (linear fit) without statsmodels
        trend_df = df[["ApplicantIncome", "LoanAmount"]].dropna()

        if len(trend_df) > 1:

            slope, intercept = np.polyfit(
                trend_df["ApplicantIncome"],
                trend_df["LoanAmount"],
                1
            )

            x_line = np.linspace(
                trend_df["ApplicantIncome"].min(),
                trend_df["ApplicantIncome"].max(),
                100
            )

            fig_scatter.add_trace(
                go.Scatter(
                    x=x_line,
                    y=slope * x_line + intercept,
                    mode="lines",
                    name="Trendline",
                    line=dict(color="red", width=2)
                )
            )

        st.plotly_chart(
            fig_scatter,
            use_container_width=True
        )

    # Income category

    if "ApplicantIncome" in df.columns:

        income_bins = pd.cut(
            df["ApplicantIncome"],
            bins=[
                -float("inf"),
                25000,
                50000,
                100000,
                float("inf")
            ],
            labels=[
                "Low",
                "Medium",
                "High",
                "Very High"
            ]
        )

        income_analysis = (
            income_bins
            .value_counts()
            .sort_index()
            .reset_index()
        )

        income_analysis.columns = [
            "Income Category",
            "Applicants"
        ]

        fig = px.bar(
            income_analysis,
            x="Income Category",
            y="Applicants",
            title="Applicant Income Category Analysis"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# =========================================================
# APPROVAL INSIGHTS
# =========================================================

elif page == "📈 Approval Insights":

    st.markdown(
        '<div class="section-title">📈 Approval Insights</div>',
        unsafe_allow_html=True
    )

    # Credit history vs approval

    if (
        "Credit_History" in df.columns
        and "Loan_Status" in df.columns
    ):

        credit_approval = pd.crosstab(
            df["Credit_History"],
            df["Loan_Status"]
        )

        fig_credit_approval = px.bar(
            credit_approval,
            barmode="group",
            title="Credit History vs Loan Approval"
        )

        st.plotly_chart(
            fig_credit_approval,
            use_container_width=True
        )

    # Education vs approval

    if (
        "Education" in df.columns
        and "Loan_Status" in df.columns
    ):

        education_approval_count = pd.crosstab(
            df["Education"],
            df["Loan_Status"]
        )

        fig_education_approval = px.bar(
            education_approval_count,
            barmode="group",
            title="Education vs Loan Approval"
        )

        st.plotly_chart(
            fig_education_approval,
            use_container_width=True
        )

    # Property vs approval

    if (
        "Property_Area" in df.columns
        and "Loan_Status" in df.columns
    ):

        property_approval_count = pd.crosstab(
            df["Property_Area"],
            df["Loan_Status"]
        )

        fig_property_approval = px.bar(
            property_approval_count,
            barmode="group",
            title="Property Area vs Loan Approval"
        )

        st.plotly_chart(
            fig_property_approval,
            use_container_width=True
        )


# =========================================================
# ELIGIBILITY CHECKER
# =========================================================

elif page == "🏦 Eligibility Checker":

    st.markdown(
        '<div class="section-title">🏦 Loan Eligibility Checker</div>',
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # RESET
    # -----------------------------------------------------

    if st.button(
        "🔄 Reset Eligibility Checker"
    ):

        st.session_state.pop(
            "eligibility_result",
            None
        )

        st.session_state.pop(
            "eligibility_inputs",
            None
        )

        st.rerun()

    # -----------------------------------------------------
    # INPUT SECTION
    # -----------------------------------------------------

    with st.container(border=True):

        st.subheader("💰 Financial Information")

        col1, col2 = st.columns(2)

        with col1:

            loan_type = st.selectbox(
                "Loan Type",
                list(LOAN_TYPES.keys())
            )

            credit_score = st.number_input(
                "Credit Score",
                min_value=300,
                max_value=900,
                value=750,
                step=1
            )

            applicant_income = st.number_input(
                "Monthly Applicant Income (₹)",
                min_value=0.0,
                value=30000.0,
                step=1000.0
            )

            coapplicant_income = st.number_input(
                "Monthly Co-applicant Income (₹)",
                min_value=0.0,
                value=0.0,
                step=1000.0
            )

        with col2:

            loan_amount = st.number_input(
                "Requested Loan Amount (₹)",
                min_value=1000.0,
                value=500000.0,
                step=10000.0
            )

            available_terms = LOAN_TYPES[
                loan_type
            ]["terms"]

            loan_term = st.selectbox(
                "Loan Term",
                available_terms,
                format_func=lambda x:
                f"{x} months ({x / 12:.1f} years)"
            )

            education = st.selectbox(
                "Education",
                [
                    "Graduate",
                    "Not Graduate"
                ]
            )

            employment = st.selectbox(
                "Employment",
                [
                    "Salaried",
                    "Self Employed"
                ]
            )

    # -----------------------------------------------------
    # PERSONAL / PROPERTY
    # -----------------------------------------------------

    with st.container(border=True):

        st.subheader("👤 Personal & Property Information")

        col1, col2 = st.columns(2)

        with col1:

            dependents = st.selectbox(
                "Dependents",
                [
                    "0",
                    "1",
                    "2",
                    "3+"
                ]
            )

        with col2:

            property_area = st.selectbox(
                "Property Area",
                [
                    "Urban",
                    "Semiurban",
                    "Rural"
                ]
            )

    # -----------------------------------------------------
    # CURRENT RATE PREVIEW
    # -----------------------------------------------------

    current_rate = calculate_interest_rate(
        loan_type,
        credit_score
    )

    current_credit_profile, current_credit_risk = (
        credit_score_profile(credit_score)
    )

    preview_col1, preview_col2, preview_col3 = st.columns(3)

    preview_col1.metric(
        "Selected Loan Type",
        loan_type
    )

    preview_col2.metric(
        "Credit Profile",
        current_credit_profile
    )

    preview_col3.metric(
        "Applicable Interest Rate",
        f"{current_rate:.2f}%"
    )

    # -----------------------------------------------------
    # CHECK ELIGIBILITY
    # -----------------------------------------------------

    if st.button(
        "🔍 Check Loan Eligibility",
        type="primary",
        use_container_width=True
    ):

        result = calculate_eligibility(
            applicant_income,
            coapplicant_income,
            loan_amount,
            loan_term,
            loan_type,
            credit_score,
            education,
            employment,
            dependents,
            property_area
        )

        st.session_state["eligibility_result"] = result

        st.session_state["eligibility_inputs"] = {
            "loan_type": loan_type,
            "credit_score": credit_score,
            "applicant_income": applicant_income,
            "coapplicant_income": coapplicant_income,
            "loan_amount": loan_amount,
            "loan_term": loan_term,
            "education": education,
            "employment": employment,
            "dependents": dependents,
            "property_area": property_area
        }

    # -----------------------------------------------------
    # RESULT
    # -----------------------------------------------------

    if "eligibility_result" in st.session_state:

        result = st.session_state[
            "eligibility_result"
        ]

        input_data = st.session_state[
            "eligibility_inputs"
        ]

        st.markdown(
            '<div class="section-title">📊 Eligibility Result</div>',
            unsafe_allow_html=True
        )

        # Summary metrics

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Monthly Income",
            f"₹{result['total_income']:,.2f}"
        )

        col2.metric(
            "Estimated EMI",
            f"₹{result['emi']:,.2f}"
        )

        col3.metric(
            "Interest Rate",
            f"{result['interest_rate']:.2f}%"
        )

        col4.metric(
            "Eligibility Score",
            f"{result['score']:.2f}/100"
        )

        # Status

        status_class = {
            "VERY HIGH": "very-high",
            "HIGH": "high",
            "MEDIUM": "medium",
            "LOW": "low",
            "VERY LOW": "very-low"
        }

        css_class = status_class[
            result["status"]
        ]

        st.markdown(
            f"""
            <div class="status-box {css_class}">
                <h2>{result['status']}</h2>
                <h3>{result['score']:.2f} / 100</h3>
                <p>{result['result_message']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Loan comparison

        if input_data["loan_amount"] > result["recommended_loan"]:

            st.warning(
                f"Requested loan amount "
                f"₹{input_data['loan_amount']:,.2f} is higher than the "
                f"system's recommended amount of "
                f"₹{result['recommended_loan']:,.2f}."
            )

        else:

            st.success(
                f"Requested loan amount is within the "
                f"system's recommended range of "
                f"₹{result['recommended_loan']:,.2f}."
            )

        # Loan cost summary

        st.markdown(
            '<div class="section-title">💰 Loan Cost Summary</div>',
            unsafe_allow_html=True
        )

        cost1, cost2, cost3 = st.columns(3)

        cost1.metric(
            "Total Interest",
            f"₹{result['total_interest']:,.2f}"
        )

        cost2.metric(
            "Total Repayment",
            f"₹{result['total_payment']:,.2f}"
        )

        cost3.metric(
            "Debt-to-Income",
            f"{result['dti']:.2f}%"
        )

        # -------------------------------------------------
        # GAUGES
        # -------------------------------------------------

        st.markdown(
            '<div class="section-title">📊 Visual Analysis</div>',
            unsafe_allow_html=True
        )

        gauge1, gauge2 = st.columns(2)

        with gauge1:

            score_fig = go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value=result["score"],
                    title={
                        "text": "Eligibility Score"
                    },
                    gauge={
                        "axis": {
                            "range": [0, 100]
                        },
                        "steps": [
                            {
                                "range": [0, 25],
                                "color": "#ef4444"
                            },
                            {
                                "range": [25, 50],
                                "color": "#f97316"
                            },
                            {
                                "range": [50, 75],
                                "color": "#f59e0b"
                            },
                            {
                                "range": [75, 90],
                                "color": "#22c55e"
                            },
                            {
                                "range": [90, 100],
                                "color": "#16a34a"
                            }
                        ],
                        "threshold": {
                            "line": {
                                "color": "black",
                                "width": 4
                            },
                            "thickness": 0.75,
                            "value": result["score"]
                        }
                    }
                )
            )

            st.plotly_chart(
                score_fig,
                use_container_width=True
            )

        with gauge2:

            dti_value = min(
                max(result["dti"], 0),
                100
            )

            dti_fig = go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value=dti_value,
                    title={
                        "text": "Debt-to-Income Ratio"
                    },
                    gauge={
                        "axis": {
                            "range": [0, 100]
                        },
                        "steps": [
                            {
                                "range": [0, 30],
                                "color": "#22c55e"
                            },
                            {
                                "range": [30, 40],
                                "color": "#f59e0b"
                            },
                            {
                                "range": [40, 100],
                                "color": "#ef4444"
                            }
                        ]
                    }
                )
            )

            st.plotly_chart(
                dti_fig,
                use_container_width=True
            )

        # Progress

        st.progress(
            min(
                max(result["score"] / 100, 0),
                1
            )
        )

        # -------------------------------------------------
        # DETAILED ANALYSIS
        # -------------------------------------------------

        st.markdown(
            '<div class="section-title">📋 Detailed Analysis</div>',
            unsafe_allow_html=True
        )

        tab1, tab2, tab3, tab4 = st.tabs(
            [
                "📊 Visual Analysis",
                "🧮 Score Breakdown",
                "⚠️ Risk Analysis",
                "💡 Recommendation"
            ]
        )

        with tab1:

            # Credit score (300-900) normalized to 0-100 so all
            # three bars are on the same scale
            credit_pct = (
                (input_data["credit_score"] - 300) / 600 * 100
            )

            visual_data = pd.DataFrame({
                "Metric": [
                    "Eligibility Score",
                    "Credit Score (%)",
                    "DTI (%)"
                ],
                "Value": [
                    result["score"],
                    credit_pct,
                    min(result["dti"], 100)
                ]
            })

            fig = px.bar(
                visual_data,
                x="Metric",
                y="Value",
                title="Applicant Financial Indicators (0-100 scale)"
            )

            fig.update_yaxes(range=[0, 100])

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with tab2:

            st.subheader(
                "Eligibility Score Breakdown"
            )

            breakdown_df = pd.DataFrame(
                result["score_breakdown"],
                columns=[
                    "Factor",
                    "Points",
                    "Assessment"
                ]
            )

            st.dataframe(
                breakdown_df,
                use_container_width=True,
                hide_index=True
            )

            st.info(
                f"""
The assessment internally uses a maximum
of **12 points**.

The internal score is converted into a
**100-point eligibility score**.

Current internal score:

**{result['raw_score']} / {result['original_max_score']}**

Converted score:

**{result['score']:.2f} / 100**
"""
            )

        with tab3:

            risk_df = pd.DataFrame({
                "Risk Factor": [
                    "Income Risk",
                    "Credit Risk",
                    "EMI Risk"
                ],
                "Risk Level": [
                    result["income_risk"],
                    result["credit_risk"],
                    result["emi_risk"]
                ]
            })

            st.dataframe(
                risk_df,
                use_container_width=True,
                hide_index=True
            )

            risk_col1, risk_col2, risk_col3 = st.columns(3)

            risk_col1.metric(
                "Income Risk",
                result["income_risk"]
            )

            risk_col2.metric(
                "Credit Risk",
                result["credit_risk"]
            )

            risk_col3.metric(
                "EMI Risk",
                result["emi_risk"]
            )

            st.write(
                f"**Credit Profile:** "
                f"{result['credit_profile']}"
            )

            st.write(
                f"**Credit Score:** "
                f"{input_data['credit_score']}"
            )

        with tab4:

            st.subheader(
                "Final Recommendation"
            )

            st.write(
                result["recommendation"]
            )

            if result["positive_factors"]:

                st.subheader(
                    "✅ Positive Factors"
                )

                for factor in result["positive_factors"]:

                    st.success(
                        factor
                    )

            if result["reasons"]:

                st.subheader(
                    "⚠️ Factors Requiring Attention"
                )

                for reason in result["reasons"]:

                    st.warning(
                        reason
                    )

        # -------------------------------------------------
        # PDF
        # -------------------------------------------------

        st.markdown(
            '<div class="section-title">📄 Report</div>',
            unsafe_allow_html=True
        )

        pdf_file = generate_pdf(
            input_data,
            result
        )

        st.download_button(
            label="📥 Download Eligibility Report (PDF)",
            data=pdf_file,
            file_name="loan_eligibility_report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

        # -------------------------------------------------
        # DISCLAIMER
        # -------------------------------------------------

        st.caption(
            "Note: Interest rates used in this academic/project "
            "system are demonstration assumptions. Actual lender "
            "rates depend on the applicant, lender, product, "
            "security, tenure and prevailing market conditions."
        )