import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib

# Load dataset
df = pd.read_csv("../Notebooks/Mall_Customers.csv")

# Select numeric columns
X = df.select_dtypes(include=['number'])

# Handle missing values
X = X.fillna(X.mean())

# ✅ ADD SCALING (VERY IMPORTANT)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train modelcd
kmeans = KMeans(n_clusters=3, random_state=42)
kmeans.fit(X_scaled)

# Save BOTH model + scaler
joblib.dump((kmeans, scaler), "segmentation_model.pkl")

print("✅ Improved Segmentation Model Saved!")