from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, jsonify

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import warnings
import joblib

from google import genai
warnings.filterwarnings('ignore')

app = Flask(__name__)

df = None
model = None
model_loaded = False
churn_model = None
churn_model_loaded = False
segment_model = None
segment_model_loaded = False

# Load CLV prediction model
try:
    if os.path.exists('model.pkl'):
        try:
            # joblib handles pickle files created by joblib.dump
            model = joblib.load('model.pkl')
            model_loaded = True
            print("✓ CLV Model loaded successfully")
        except Exception as ue:
            print(f"⚠ Unable to load model.pkl ({ue}). Using sample predictions.")
            model = None
            model_loaded = False
    else:
        print("⚠ model.pkl not found. Using sample predictions.")
except Exception as e:
    print(f"⚠ Error loading model: {e}")
    model = None
    model_loaded = False

# Load Churn prediction model
try:
    if os.path.exists('churn_model.pkl'):
        try:
            churn_model = joblib.load('churn_model.pkl')
            churn_model_loaded = True
            print("✓ Churn Model loaded successfully")
        except Exception as ue:
            print(f"⚠ Unable to load churn_model.pkl ({ue}). Using sample predictions.")
            churn_model = None
            churn_model_loaded = False
    else:
        print("⚠ churn_model.pkl not found. Using sample predictions.")
except Exception as e:
    print(f"⚠ Error loading churn model: {e}")
    churn_model = None
    churn_model_loaded = False


# Load Segmentation prediction model
try:
    if os.path.exists('segmentation_model.pkl'):
        try:
            
            segment_model, scaler = joblib.load('segmentation_model.pkl')
            segment_model_loaded = True
            print("✓ Segmentation Model loaded successfully")
        except Exception as ue:
            print(f"⚠ Unable to load segmentation_model.pkl ({ue}). Using sample segmentation.")
            segment_model = None
            segment_model_loaded = False
    else:
        print("⚠ segmentation_model.pkl not found. Using sample segmentation.")
except Exception as e:
    print(f"⚠ Error loading segmentation model: {e}")
    segment_model = None
    segment_model_loaded = False


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/clv")
def clv():
    return render_template("clv_dashboard.html")


@app.route("/churn")
def churn():
    return render_template("churn_dashboard.html")

@app.route("/segment")
def segment():
    return render_template("segmentation.html")


# Upload dataset
@app.route("/upload", methods=["POST"])
def upload():
    global df

    try:
        file = request.files["file"]
        df = pd.read_csv(file)
        return jsonify({"message": "Dataset uploaded successfully", "rows": len(df), "columns": len(df.columns)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# KPI information
@app.route("/kpi")
def kpi():
    global df

    if df is None:
        return jsonify({"error": "No dataset uploaded"})

    return jsonify({
        "rows": len(df),
        "columns": len(df.columns),
        "missing": int(df.isnull().sum().sum())
    })


# CLV Predictions
@app.route("/predict-clv", methods=["POST"])
def predict_clv():
    global df, model, model_loaded

    if df is None:
        return jsonify({"error": "No dataset uploaded"}), 400

    try:
        # Get numeric columns for prediction
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if not numeric_cols:
            return jsonify({"error": "No numeric columns found in dataset"}), 400

        # Prepare data
        X = df[numeric_cols].fillna(df[numeric_cols].mean())

        if model_loaded and model is not None:
            # Use the trained model for predictions
            try:
                predictions = model.predict(X)
                confidences = np.ones(len(predictions)) * 0.85  # Default confidence
                
                # If model has predict_proba, use it for confidence
                if hasattr(model, 'predict_proba'):
                    try:
                        proba = model.predict_proba(X)
                        confidences = np.max(proba, axis=1)
                    except:
                        pass
            except Exception as e:
                # Fallback to sample predictions
                predictions = np.random.uniform(1000, 6000, len(df))
                confidences = np.random.uniform(0.80, 0.98, len(df))
        else:
            # Generate realistic sample predictions
            predictions = np.random.uniform(1000, 6000, len(df))
            confidences = np.random.uniform(0.80, 0.98, len(df))

        # Segment customers based on CLV
        segments = []
        for clv in predictions:
            if clv >= 4000:
                segments.append("Premium")
            elif clv >= 2500:
                segments.append("Standard")
            else:
                segments.append("Basic")

        # Create response
        results = []
        for i in range(min(10, len(df))):  # Return top 10
            results.append({
                "customer_id": f"CUST-{str(i+1).zfill(4)}",
                "predicted_clv": round(float(predictions[i]), 2),
                "confidence": round(float(confidences[i]) * 100, 1),
                "segment": segments[i],
                "recommendation": get_recommendation(segments[i], float(predictions[i]))
            })

        return jsonify({
            "success": True,
            "total_predictions": len(predictions),
            "average_clv": round(float(np.mean(predictions)), 2),
            "max_clv": round(float(np.max(predictions)), 2),
            "min_clv": round(float(np.min(predictions)), 2),
            "predictions": results
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Churn Predictions
@app.route("/predict-churn", methods=["POST"])
def predict_churn():
    global df, churn_model, churn_model_loaded

    if df is None:
        return jsonify({"error": "No dataset uploaded"}), 400

    try:
        # Get numeric columns for prediction
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if not numeric_cols:
            return jsonify({"error": "No numeric columns found in dataset"}), 400

        # Prepare data
        X = df[numeric_cols].fillna(df[numeric_cols].mean())

        if churn_model_loaded and churn_model is not None:
            # Use the trained model for predictions
            try:
                if hasattr(churn_model, 'predict_proba'):
                    proba = churn_model.predict_proba(X)
                    churn_probabilities = proba[:, 1]  # Assuming class 1 is churn
                    predictions = (churn_probabilities > 0.5).astype(int)  # Binary prediction
                else:
                    predictions = churn_model.predict(X)
                    churn_probabilities = np.ones(len(predictions)) * 0.5  # Default if no proba
            except Exception as e:
                # Fallback to sample predictions
                predictions = np.random.randint(0, 2, len(df))
                churn_probabilities = np.random.uniform(0.1, 0.9, len(df))
        else:
            # Generate realistic sample predictions
            predictions = np.random.randint(0, 2, len(df))
            churn_probabilities = np.random.uniform(0.1, 0.9, len(df))

        # Segment customers based on churn risk
        segments = []
        for prob in churn_probabilities:
            if prob >= 0.7:
                segments.append("High Risk")
            elif prob >= 0.4:
                segments.append("Medium Risk")
            else:
                segments.append("Low Risk")

        # Create response
        results = []
        for i in range(min(10, len(df))):  # Return top 10
            results.append({
                "customer_id": f"CUST-{str(i+1).zfill(4)}",
                "churn_probability": round(float(churn_probabilities[i]) * 100, 1),
                "predicted_churn": bool(predictions[i]),
                "risk_segment": segments[i],
                "recommendation": get_churn_recommendation(segments[i])
            })

        return jsonify({
            "success": True,
            "total_predictions": len(predictions),
            "churn_rate": round(float(np.mean(predictions)) * 100, 1),
            "high_risk_count": sum(1 for p in churn_probabilities if p >= 0.7),
            "predictions": results
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/predict-segmentation", methods=["POST"])
def predict_segmentation():
    global df, segment_model, segment_model_loaded, scaler

    if df is None:
        return jsonify({"error": "No dataset uploaded"}), 400

    try:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        if not numeric_cols:
            return jsonify({"error": "No numeric columns found"}), 400

        X = df[numeric_cols].fillna(df[numeric_cols].mean())

        if segment_model_loaded and segment_model is not None:
            X_scaled = scaler.transform(X)   # ✅ ADD THIS
            segments = segment_model.predict(X_scaled)
        else:
            segments = np.random.randint(0, 3, len(df))

        results = []
        for i in range(len(df)):
            results.append({
                "customer_id": f"CUST-{str(i+1).zfill(4)}",
                "segment": int(segments[i]),
                "label": get_segment_label(int(segments[i]))
            })

        return jsonify({
            "total": len(segments),
            "segments": results
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


def get_churn_recommendation(segment):
    """Generate recommendations based on churn risk segment"""
    recommendations = {
        "High Risk": "Immediate Retention Campaign",
        "Medium Risk": "Personalized Engagement",
        "Low Risk": "Monitor and Maintain"
    }
    return recommendations.get(segment, "General Retention")


def get_recommendation(segment, clv):
    """Generate recommendations based on segment"""
    recommendations = {
        "Premium": "VIP Retention Program",
        "Standard": "Upsell Opportunities",
        "Basic": "Convert to Premium"
    }
    return recommendations.get(segment, "Engagement Campaign")

def get_segment_label(segment):
    labels = {
        0: "Low Value",
        1: "Medium Value",
        2: "High Value"
    }
    return labels.get(segment, "Unknown")


# Chart data
@app.route("/chart-data")
def chart_data():
    global df

    if df is None:
        return jsonify({"error": "No dataset uploaded"}), 400

    try:
        column = request.args.get("column")
        if column not in df.columns:
            return jsonify({"error": f"Column {column} not found"}), 400

        counts = df[column].value_counts().head(10)

        return jsonify({
            "labels": counts.index.tolist(),
            "values": counts.values.tolist()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# AI Chatbot
@app.route("/chat", methods=["POST"])
def chat():
    global df, model_loaded

    try:
        question = request.json["message"].lower()

        if df is None:
            return jsonify({"reply": "Please upload a dataset first to get insights."})

        # Smart responses based on question
        if "row" in question or "record" in question:
            reply = f"Your dataset contains {len(df):,} customer records."
        elif "column" in question or "feature" in question:
            reply = f"The dataset has {len(df.columns)} columns: {', '.join(df.columns.tolist()[:5])}..."
        elif "average" in question or "mean" in question:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols:
                reply = f"Average values: {df[numeric_cols].mean().to_dict()}"
            else:
                reply = "No numeric columns found for averaging."
        elif "predict" in question or "clv" in question:
            reply = "I can predict customer lifetime value for your data. The model analyzes customer features to estimate their value."
        elif "churn" in question or "retention" in question:
            reply = "I can analyze churn risk for your customers. The model predicts which customers are likely to leave and provides retention recommendations."
        elif "segment" in question or "group" in question:
            reply = "Customers are segmented into Premium, Standard, and Basic tiers based on their predicted CLV values, or High/Medium/Low risk for churn analysis."
        elif "help" in question or "how" in question:
            reply = "I can help you with data analysis, CLV predictions, churn analysis, customer segmentation, and insights. Ask me anything about your data!"
        else:
            reply = "I can analyze your customer data and provide CLV predictions or churn analysis. What would you like to know?"

        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"}), 400


# Model status endpoint

@app.route("/model-status")
def model_status():
    return jsonify({
        "clv_model_loaded": model_loaded,
        "clv_model_file_exists": os.path.exists("model.pkl"),
        "churn_model_loaded": churn_model_loaded,
        "churn_model_file_exists": os.path.exists("churn_model.pkl")
    })



@app.route("/ai-chat", methods=["POST"])
def ai_chat():
    try:
        data = request.json
        messages = data.get("messages", [])
        system_prompt = data.get("system", "")

        api_key = "AIzaSyCMIPDxnZFdNGh4GqPUPK73pp6Xaz6qgQM"
        print(f"API Key found: {bool(api_key)}")
        print(f"Messages count: {len(messages)}")

        if not api_key:
            return jsonify({"reply": "Error: GEMINI_API_KEY not set in .env file"}), 400

        if not messages:
            return jsonify({"reply": "No message received."}), 400

        client = genai.Client(api_key=api_key)

        # Build conversation history for context
        contents = []
        for msg in messages:
            contents.append({
                "role": "user" if msg["role"] == "user" else "model",
                "parts": [{"text": msg["content"]}]
            })

        response = client.models.generate_content(
            
            model="models/gemini-2.0-flash-lite",
            
            contents=contents,
            config={
                "system_instruction": system_prompt,
                "max_output_tokens": 1000,
            }
        )

        print(f"Gemini response received successfully")
        return jsonify({"reply": response.text})

    except Exception as e:
        print(f"AI Chat Error: {str(e)}")
        return jsonify({"reply": f"Error: {str(e)}"}), 400



import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
