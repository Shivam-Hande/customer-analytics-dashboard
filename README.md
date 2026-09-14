# Customer Intelligence & Predictive Analytics Platform

> An end-to-end customer analytics platform combining exploratory analytics, machine learning, customer segmentation, Customer Lifetime Value (CLV) prediction, churn prediction, and an interactive Flask web dashboard.

---

## 📊 Project Overview

**DataCrest** is a customer intelligence and predictive analytics platform designed to help businesses understand customer behavior, identify high-value customers, predict churn risk, and support targeted customer retention strategies.

The project combines:

- Customer data analysis
- Exploratory Data Analysis (EDA)
- Customer Lifetime Value (CLV) prediction
- Churn prediction
- Customer segmentation
- Interactive dashboards
- Automated business recommendations
- Customer analytics chatbot

The complete workflow follows:

**Customer Data → Data Preparation → Exploratory Analysis → Machine Learning → Customer Intelligence → Interactive Dashboard → Business Recommendations**

---

# 🎯 Business Problem

Businesses collect large amounts of customer data but often struggle to convert that data into actionable decisions.

Key business questions include:

- Which customers are most valuable?
- Which customers are at risk of leaving?
- Which customer groups have similar behaviors?
- How much future value can a customer generate?
- Which customers should receive retention efforts?
- How can marketing teams prioritize customers?
- How can customer analytics be made accessible to non-technical users?

DataCrest addresses these questions by combining descriptive and predictive analytics into a single interactive platform.

---

# 🚀 Key Features

## 1. Customer Analytics Dashboard

The platform provides an interactive dashboard for exploring uploaded customer datasets.

Key capabilities include:

- Dataset upload
- Dataset size and structure analysis
- Row and column statistics
- Missing-value analysis
- Numeric feature analysis
- Dynamic chart generation
- Customer-level analytics

The Flask backend exposes API endpoints for dataset processing, KPI analysis, and chart data generation. :contentReference[oaicite:2]{index=2}

---

# 💰 2. Customer Lifetime Value Prediction

The CLV module estimates the potential value of customers using a trained machine learning model.

### Objective

Identify customers with higher expected lifetime value so businesses can prioritize:

- VIP retention
- Upselling
- Loyalty programs
- Personalized offers
- Customer engagement

### Output

The CLV module provides:

- Predicted customer lifetime value
- Prediction confidence
- Customer value segment
- Recommended business action

Customers are classified into:

| Segment | Business Strategy |
|---|---|
| Premium | VIP Retention Program |
| Standard | Upsell Opportunities |
| Basic | Customer Development |

The application loads a persisted CLV model and generates customer-level predictions through the `/predict-clv` endpoint. :contentReference[oaicite:3]{index=3}

---

# ⚠️ 3. Customer Churn Prediction

The churn module identifies customers who may be at risk of leaving.

### Objective

Enable businesses to move from reactive customer retention to proactive retention.

The model produces:

- Churn probability
- Predicted churn status
- Risk segment
- Retention recommendation

### Risk Classification

| Risk Level | Suggested Action |
|---|---|
| High Risk | Immediate Retention Campaign |
| Medium Risk | Personalized Engagement |
| Low Risk | Monitor & Maintain |

The application uses the trained churn model when available and exposes predictions through the `/predict-churn` endpoint. :contentReference[oaicite:4]{index=4}

---

# 👥 4. Customer Segmentation

Customer segmentation groups customers according to behavioral characteristics.

A K-Means-based segmentation model is integrated into the application.

### Customer Value Segments

- Low Value
- Medium Value
- High Value

The segmentation module uses a saved model and scaler to assign customers to behavioral groups. :contentReference[oaicite:5]{index=5}

### Business Applications

Segmentation can support:

- Personalized marketing
- Customer prioritization
- Loyalty programs
- Cross-selling
- Upselling
- Retention campaigns

---

# 🤖 5. Customer Analytics Chatbot

The platform includes an interactive chatbot designed to provide quick answers about the uploaded customer dataset.

The chatbot can respond to questions related to:

- Dataset size
- Number of features
- Average values
- CLV prediction
- Churn analysis
- Customer segmentation
- Retention recommendations

The application also includes an AI-assisted chat endpoint for conversational analysis. :contentReference[oaicite:6]{index=6}

---

# 🧠 Machine Learning Architecture

```text
                 Customer Dataset
                       │
                       ▼
                Data Preparation
                       │
                       ▼
              Feature Engineering
                       │
          ┌────────────┼────────────┐
          │            │            │
          ▼            ▼            ▼
      CLV Model    Churn Model   Segmentation
          │            │            │
          ▼            ▼            ▼
     Customer      Churn Risk    Customer
       Value        Score         Segment
          │            │            │
          └────────────┼────────────┘
                       ▼
              Business Recommendations
                       │
                       ▼
              Interactive Dashboard
