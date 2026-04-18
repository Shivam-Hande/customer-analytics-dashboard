import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import joblib

# Load dataset
data = pd.read_csv("Notebooks/Telco-Customer-Churn.csv")
# Convert categorical columns
le = LabelEncoder()

for col in data.select_dtypes(include='object').columns:
    data[col] = le.fit_transform(data[col])

# Target column
X = data.drop("Churn", axis=1)
y = data["Churn"]

# Train Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Model
model = RandomForestClassifier()

model.fit(X_train, y_train)

# Save model
joblib.dump(model, "churn_model.pkl")

print("Model Saved Successfully")