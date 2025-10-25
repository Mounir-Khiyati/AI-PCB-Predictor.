import pandas as pd
import matplotlib.pyplot as plt
import math

# === Netlist ===
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

# Zones interdites
KEEP_OUT_ZONES = [(2, 2, 3, 3), (7, 1, 8, 3)]

# Couleurs + légende explicative
COMP_INFO = {
    "TR1": ("orange", "Transformateur"),
    "MOS1": ("blue", "MOSFET"),
    "D1": ("red", "Diode Schottky"),
    "L1": ("green", "Inductance"),
    "C1": ("cyan", "Condensateur"),
    "PWM1": ("purple", "Contrôleur PWM"),
    "OPTO1": ("pink", "Optocoupleur"),
    "ATX_CONN": ("yellow", "Connecteur ATX")
}

# Fonction coût réel
def calculate_cost(row, netlist):
    total_distance = 0
    for comp1, comp2 in netlist:
        x1, y1 = row[f"{comp1}_x"], row[f"{comp1}_y"]
        x2, y2 = row[f"{comp2}_x"], row[f"{comp2}_y"]
        total_distance += math.hypot(x2 - x1, y2 - y1)
    return total_distance

# Connexions en L
def draw_connection(ax, x1, y1, x2, y2):
    xm = (x1 + x2) / 2
    ax.plot([x1, xm], [y1, y1], color="gray", linewidth=1, alpha=0.7)
    ax.plot([xm, xm], [y1, y2], color="gray", linewidth=1, alpha=0.7)
    ax.plot([xm, x2], [y2, y2], color="gray", linewidth=1, alpha=0.7)

# Affichage
def plot_placement(ax, row, title, netlist, keepouts):
    ax.set_facecolor("#004225")
    ax.set_xlim(-0.5, 12.5)
    ax.set_ylim(-0.5, 7.5)
    ax.set_xticks(range(13))
    ax.set_yticks(range(8))
    ax.grid(True, color="white", linestyle="--", alpha=0.2)

    # Zones interdites
    for (x1, y1, x2, y2) in keepouts:
        rect = plt.Rectangle((x1 - 0.5, y1 - 0.5),
                             x2 - x1 + 1, y2 - y1 + 1,
                             color="red", alpha=0.3)
        ax.add_patch(rect)
        ax.text(x1, y1, "⚠ Zone interdite", color="red", fontsize=7, weight="bold")

    # Composants
    comps = [c[:-2] for c in row.index if "_x" in c]
    positions = {}
    for comp in comps:
        x, y = row[f"{comp}_x"], row[f"{comp}_y"]
        positions[comp] = (x, y)
        color, _ = COMP_INFO.get(comp, ("white", comp))
        ax.scatter(x, y, s=300, color=color, edgecolors="black", zorder=3)
        ax.text(x, y, comp, fontsize=7, ha="center", va="center", color="black", weight="bold")

    # Connexions
    for a, b in netlist:
        if a in positions and b in positions:
            x1, y1 = positions[a]
            x2, y2 = positions[b]
            draw_connection(ax, x1, y1, x2, y2)

    # Titre
    cost = calculate_cost(row, netlist)
    ax.set_title(f"{title}\nCoût réel = {cost:.2f}", fontsize=9, color="white")

# === Main ===
if __name__ == "__main__":
    data = pd.read_csv("data/pcb_dataset.csv")

    best = data.loc[data["cost"].idxmin()]
    worst = data.loc[data["cost"].idxmax()]
    random_row = data.sample(1).iloc[0]

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    plot_placement(axes[0], best, "Bon placement", NETLIST, KEEP_OUT_ZONES)
    plot_placement(axes[1], worst, "Mauvais placement", NETLIST, KEEP_OUT_ZONES)
    plot_placement(axes[2], random_row, "Placement aléatoire", NETLIST, KEEP_OUT_ZONES)

    # Légende explicative en haut
    legend_text = " | ".join([f"{k} = {v[1]}" for k, v in COMP_INFO.items()])
    plt.figtext(0.5, 0.98, f"Légende : {legend_text}", ha="center", fontsize=9, color="black", weight="bold")

    plt.tight_layout(rect=[0, 0, 1, 0.95])  # laisse de la place en haut pour la légende
    plt.show()
