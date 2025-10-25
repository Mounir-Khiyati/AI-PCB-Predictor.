import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import math
import joblib

# === Définir la netlist (même que dans generate_data.py) ===
NETLIST = [
    ("TR1", "MOS1"),
    ("MOS1", "D1"),
    ("D1", "L1"),
    ("L1", "C1"),
    ("C1", "ATX_CONN"),
    ("PWM1", "MOS1"),
    ("PWM1", "OPTO1"),
    ("OPTO1", "MOS1"),
]

# === Fonction pour calculer la distance moyenne ===
def compute_avg_distance(row):
    coords = [(row[f"{name}_x"], row[f"{name}_y"]) for name in set(col[:-2] for col in row.index if "_x" in col)]
    total_dist, count = 0, 0
    for i in range(len(coords)):
        for j in range(i + 1, len(coords)):
            x1, y1 = coords[i]
            x2, y2 = coords[j]
            dist = math.hypot(x2 - x1, y2 - y1)
            total_dist += dist
            count += 1
    return total_dist / count if count > 0 else 0

# === Fonction pour calculer le coût réel à partir d'un placement ===
def calculate_cost(row, netlist):
    total_distance = 0
    for comp1, comp2 in netlist:
        x1, y1 = row[f"{comp1}_x"], row[f"{comp1}_y"]
        x2, y2 = row[f"{comp2}_x"], row[f"{comp2}_y"]
        dist = math.hypot(x2 - x1, y2 - y1)
        total_distance += dist
    return total_distance

# === Charger le dataset ===
data = pd.read_csv("data/pcb_dataset.csv")

# Ajouter la moyenne des distances comme feature supplémentaire
data["avg_distance"] = data.apply(compute_avg_distance, axis=1)

# === Séparer features et cible ===
X = data.drop("cost", axis=1)
y = data["cost"]

# === Division train/test ===
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# === Entraînement du modèle ===
model = RandomForestRegressor(n_estimators=300, random_state=42)
model.fit(X_train, y_train)
joblib.dump(model, "models/placement_model.pkl")
print("✅ Modèle sauvegardé dans models/placement_model.pkl")
# === Évaluation globale ===
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("\n📊 Évaluation du modèle :")
print(f"  - Erreur quadratique moyenne : {mse:.3f}")
print(f"  - Score R² : {r2:.3f}")

# === Tester plusieurs prédictions ===
print("\n🔮 Comparaison sur quelques placements de test :")
for idx in range(5):  # affiche 5 placements
    sample = X_test.iloc[idx]
    pred_cost = y_pred[idx]
    real_cost = calculate_cost(sample, NETLIST)

    print(f"\nPlacement n°{idx+1} :")
    for i in range(0, len(sample) - 1, 2):  # -1 pour exclure avg_distance
        comp_name = X.columns[i][:-2]
        x = sample.iloc[i]
        y_ = sample.iloc[i + 1]
        print(f"  - {comp_name} : ({x}, {y_})")

    print(f"  📏 Moyenne des distances : {sample['avg_distance']:.2f}")
    print(f"  ⚖️  Coût réel    : {real_cost:.2f}")
    print(f"  🔮 Coût prédit  : {pred_cost:.2f}")
    error = abs(real_cost - pred_cost) / real_cost * 100
    print(f"  ❌ Erreur relative : {error:.2f}%")
