from pathlib import Path

import joblib
from data_loader import load_kaggle_csv
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import BernoulliNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_ASSETS_DIR = PROJECT_ROOT / "backend" / "model_assets"
MODEL_ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# Load dataset
df = load_kaggle_csv(
    "atharvaingle/crop-recommendation-dataset",
    "Crop_recommendation.csv"
)

print(df['label'].value_counts())
print(df['label'].nunique())

"""Preprocessing"""
X_train, X_test, y_train, y_test = train_test_split(df.drop("label", axis=1), df["label"], test_size=0.2, random_state=42)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)
encoder = LabelEncoder()
y_train = encoder.fit_transform(y_train)
y_test = encoder.transform(y_test)

joblib.dump(encoder, MODEL_ASSETS_DIR / "cr_encoder.pkl")
joblib.dump(scaler, MODEL_ASSETS_DIR / "cr_scaler.pkl")


"""MODEL SELECTION"""
models = [
    BernoulliNB(),
    LinearSVC(),
    KNeighborsClassifier(),
    DecisionTreeClassifier(),
    RandomForestClassifier(),
    LogisticRegression(),
    XGBClassifier(),
    GradientBoostingClassifier(),
]

accuracy=[]
for model in models:
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    print(f"{model.__class__.__name__}: {accuracy_score(y_test, y_pred):.4f}")
    accuracy.append(accuracy_score(y_test, y_pred))

model = models[accuracy.index(max(accuracy))]
joblib.dump(model, MODEL_ASSETS_DIR / "cr_model.pkl")
print('-'*50)
print('Model used: ', model.__class__.__name__)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
print(f"{model.__class__.__name__}: {accuracy_score(y_test, y_pred):.4f}")
print(classification_report(y_test, y_pred))
print('-'*50)
