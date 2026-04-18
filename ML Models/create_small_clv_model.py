import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import joblib

# Generate synthetic CLV data
np.random.seed(42)
n_samples = 1000

data = pd.DataFrame({
    'recency_days': np.random.randint(1, 365, n_samples),
    'frequency': np.random.randint(1, 20, n_samples),
    'monetary_value': np.random.uniform(50, 5000, n_samples)
})

# Calculate CLV
data['avg_order_value'] = data['monetary_value'] / data['frequency']
data['CLV'] = data['avg_order_value'] * data['frequency'] * np.random.uniform(1, 5, n_samples)

# Features and target
X = data[['recency_days', 'frequency', 'monetary_value']]
y = data['CLV']

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestRegressor(n_estimators=10, max_depth=5, random_state=42)
model.fit(X_train, y_train)

# Save model
joblib.dump(model, "model.pkl")

# Check model size
size = os.path.getsize("model.pkl")

print("New CLV model saved as model.pkl")
print(f"Model size: {size/1024:.2f} KB")