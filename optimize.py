## C’est ton utilitaire d’optimisation.Il génère plusieurs placements, choisit le meilleur (selon coût réel) et l’affiche.

import matplotlib.pyplot as plt
import math
import random

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

# Composants
COMPONENTS = ["TR1", "MOS1", "D1", "L1", "C1", "PWM1", "OPTO1", "ATX_CONN"]

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

# === Vérifie si une case est dans une zone interdite ===
def is_in_keepout(x, y, keepouts):
    for (x1, y1, x2, y2) in keepouts:
        if x1 <= x <= x2 and y1 <= y <= y2:
            return True
    return False

# === Générer un placement aléatoire ===
def generate_random_placement(grid_size=(12, 8), keep_out=KEEP_OUT_ZONES):
    placement = {}
    occupied = set()
    for comp in COMPONENTS:
        while True:
            x = random.randint(0, grid_size[0] - 1)
            y = random.randint(0, grid_size[1] - 1)
            if (x, y) not in occupied and not is_in_keepout(x, y, keep_out):
                placement[comp] = (x, y)
                occupied.add((x, y))
                break
    return placement

# === Calcul du coût réel ===
def calculate_cost(placement, netlist):
    total_distance = 0
    for comp1, comp2 in netlist:
        x1, y1 = placement[comp1]
        x2, y2 = placement[comp2]
        total_distance += math.hypot(x2 - x1, y2 - y1)
    return total_distance

# === Visualisation du meilleur placement ===
def plot_best_placement(placement, cost, keepouts):
    fig, ax = plt.subplots(figsize=(8, 6))
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
    for comp, (x, y) in placement.items():
        color, _ = COMP_INFO.get(comp, ("white", comp))
        ax.scatter(x, y, s=300, color=color, edgecolors="black", zorder=3)
        ax.text(x, y, comp, fontsize=8, ha="center", va="center", color="black", weight="bold")

    # Connexions en L
    for a, b in NETLIST:
        if a in placement and b in placement:
            x1, y1 = placement[a]
            x2, y2 = placement[b]
            xm = (x1 + x2) / 2
            ax.plot([x1, xm], [y1, y1], color="gray", linewidth=1, alpha=0.7)
            ax.plot([xm, xm], [y1, y2], color="gray", linewidth=1, alpha=0.7)
            ax.plot([xm, x2], [y2, y2], color="gray", linewidth=1, alpha=0.7)

    # Titre
    ax.set_title(f"Meilleur placement trouvé\nCoût = {cost:.2f}", fontsize=11, color="white")

    # Légende explicative
    legend_text = " | ".join([f"{k} = {v[1]}" for k, v in COMP_INFO.items()])
    plt.figtext(0.5, 0.01, f"Légende : {legend_text}", ha="center", fontsize=8, color="black", weight="bold")

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

# === Main ===
if __name__ == "__main__":
    N = 300
    best_cost = float("inf")
    best_placement = None

    for _ in range(N):
        placement = generate_random_placement()
        cost = calculate_cost(placement, NETLIST)
        if cost < best_cost:
            best_cost = cost
            best_placement = placement

    # Résumé explicatif
    print(f"✅ Optimisation terminée : {N} placements testés")
    print(f"➡️  Meilleur coût trouvé : {best_cost:.2f}")
    print("📍 Placement choisi :")
    for comp, (x, y) in best_placement.items():
        print(f"   - {comp} ({COMP_INFO[comp][1]}) → ({x}, {y})")

    # Affichage graphique
    plot_best_placement(best_placement, best_cost, KEEP_OUT_ZONES)
