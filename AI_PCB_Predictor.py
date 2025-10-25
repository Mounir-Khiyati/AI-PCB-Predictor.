import random
import math
import csv
import json
import os
import matplotlib.pyplot as plt

# -------------------------
# CONFIG
# -------------------------
SEED = 42
random.seed(SEED)

GRID_SIZE = (10, 10)
NUM_SAMPLES = 2000
OUTPUT_CSV = "data/pcb_dataset.csv"
SAMPLES_DIR = "data/placements_examples"

COMPONENTS = [
    {"name": "TR1", "type": "transformer", "power": 5.0, "heat": 2.0},
    {"name": "MOS1", "type": "mosfet", "power": 3.0, "heat": 1.8},
    {"name": "D1", "type": "diode_schottky", "power": 0.5, "heat": 0.3},
    {"name": "L1", "type": "inductor", "power": 0.2, "heat": 0.1},
    {"name": "C1", "type": "capacitor_electrolytic", "power": 0.1, "heat": 0.05},
    {"name": "PWM1", "type": "pwm_controller", "power": 1.5, "heat": 0.8},
    {"name": "OPTO1", "type": "optocoupler", "power": 0.2, "heat": 0.1},
    {"name": "ATX_CONN", "type": "connector_atx", "power": 0.0, "heat": 0.0},
]

NETLIST = [
    ("TR1", "MOS1", 1.0),
    ("MOS1", "D1", 1.0),
    ("D1", "L1", 0.8),
    ("L1", "C1", 0.5),
    ("C1", "ATX_CONN", 1.0),
    ("PWM1", "MOS1", 1.2),
    ("PWM1", "OPTO1", 0.7),
    ("OPTO1", "MOS1", 0.6),
]

KEEP_OUT_ZONES = [
    (2, 2, 3, 3),
    (6, 0, 7, 2),
]

# -------------------------
# HELPERS
# -------------------------
def is_in_keepout(pos, zones):
    x, y = pos
    return any(x1 <= x <= x2 and y1 <= y <= y2 for x1, y1, x2, y2 in zones)

def generate_random_placement(grid_size, components, keep_out):
    placed = {}
    occupied = set()
    for comp in components:
        for _ in range(200):
            x = random.randint(0, grid_size[0] - 1)
            y = random.randint(0, grid_size[1] - 1)
            if (x, y) not in occupied and not is_in_keepout((x, y), keep_out):
                placed[comp["name"]] = (x, y)
                occupied.add((x, y))
                break
        else:
            return None
    return placed

def euclidean(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def calculate_cost(placement, netlist, components_by_name, keep_out):
    total = 0.0
    for a, b, w in netlist:
        total += w * euclidean(placement[a], placement[b])
    for pos in placement.values():
        if is_in_keepout(pos, keep_out):
            total += 10000.0
    heat_threshold = 0.8
    names = list(placement.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            h1 = components_by_name[names[i]]["heat"]
            h2 = components_by_name[names[j]]["heat"]
            if h1 > heat_threshold and h2 > heat_threshold:
                d = euclidean(placement[names[i]], placement[names[j]])
                if d < 3.0:
                    total += (3.0 - d) * (h1 + h2) * 2.0
    return total

def visualize(placement, keepouts, title="Placement", show=True):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(-0.5, GRID_SIZE[0] - 0.5)
    ax.set_ylim(-0.5, GRID_SIZE[1] - 0.5)
    ax.set_xticks(range(GRID_SIZE[0]))
    ax.set_yticks(range(GRID_SIZE[1]))
    ax.grid(True)
    for x1, y1, x2, y2 in keepouts:
        rect = plt.Rectangle((x1 - 0.5, y1 - 0.5), x2 - x1 + 1, y2 - y1 + 1, color="red", alpha=0.3)
        ax.add_patch(rect)
    for name, (x, y) in placement.items():
        ax.plot(x, y, marker='s')
        ax.text(x + 0.1, y + 0.1, name, fontsize=8)
    ax.set_title(title)
    if show:
        plt.show()
    plt.close(fig)

def generate_dataset():
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    os.makedirs(SAMPLES_DIR, exist_ok=True)
    components_by_name = {c["name"]: c for c in COMPONENTS}
    with open(OUTPUT_CSV, "w", newline='') as f:
        writer = csv.writer(f)
        header = [f"{c['name']}_x" for c in COMPONENTS] + [f"{c['name']}_y" for c in COMPONENTS] + ["cost"]
        writer.writerow(header)
        sample_id = 0
        while sample_id < NUM_SAMPLES:
            placement = generate_random_placement(GRID_SIZE, COMPONENTS, KEEP_OUT_ZONES)
            if placement is None:
                print("⚠️ Placement impossible, trop de contraintes.")
                break
            cost = calculate_cost(placement, NETLIST, components_by_name, KEEP_OUT_ZONES)
            row = [placement[c["name"]][0] for c in COMPONENTS] + [placement[c["name"]][1] for c in COMPONENTS] + [cost]
            writer.writerow(row)
            with open(f"{SAMPLES_DIR}/placement_{sample_id}.json", "w") as jf:
                json.dump({"placement": placement, "cost": cost}, jf)
            sample_id += 1
            if sample_id % 100 == 0:
                print(f"✅ {sample_id}/{NUM_SAMPLES} placements générés")
    print(f"✅ Nouveau dataset généré avec succès dans '{OUTPUT_CSV}'")

    # Visualiser le dernier placement
    if os.path.exists(f"{SAMPLES_DIR}/placement_{NUM_SAMPLES - 1}.json"):
        with open(f"{SAMPLES_DIR}/placement_{NUM_SAMPLES - 1}.json") as jf:
            d = json.load(jf)
            visualize(d["placement"], KEEP_OUT_ZONES, title=f"Placement #{NUM_SAMPLES - 1} (coût={d['cost']:.2f})")

if __name__ == "__main__":
    generate_dataset()
