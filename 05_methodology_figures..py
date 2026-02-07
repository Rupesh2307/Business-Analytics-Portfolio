from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# Save figures here (your outputs folder)
PLOTS_DIR = Path("/Users/asus/Documents/Dissertation/WallmartData_old/outputs/plots")
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

def _box(ax, xy, text, width=3.2, height=1.0, fontsize=11):
    x, y = xy
    patch = FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        linewidth=1.5
    )
    ax.add_patch(patch)
    ax.text(x + width/2, y + height/2, text, ha="center", va="center", fontsize=fontsize)
    return patch

def _arrow(ax, start, end, text=None, fontsize=10):
    ax.annotate(
        "",
        xy=end, xytext=start,
        arrowprops=dict(arrowstyle="->", linewidth=1.5)
    )
    if text:
        mx = (start[0] + end[0]) / 2
        my = (start[1] + end[1]) / 2
        ax.text(mx, my + 0.15, text, ha="center", va="bottom", fontsize=fontsize)

def figure_3_1_multi_echelon():
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4)
    ax.axis("off")

    _box(ax, (0.6, 1.5), "Upstream Supplier\n(Echelon 1)")
    _box(ax, (4.4, 1.5), "Distribution Center\n(Echelon 2)")
    _box(ax, (8.2, 1.5), "Retail / Customer\n(Echelon 3)")

    # Material flow
    _arrow(ax, (3.8, 2.0), (4.4, 2.0), text="Material Flow")
    _arrow(ax, (7.6, 2.0), (8.2, 2.0))

    # Information/order flow (reverse direction, lower line)
    ax.annotate("", xy=(3.8, 1.6), xytext=(4.4, 1.6),
                arrowprops=dict(arrowstyle="->", linewidth=1.5))
    ax.annotate("", xy=(7.6, 1.6), xytext=(8.2, 1.6),
                arrowprops=dict(arrowstyle="->", linewidth=1.5))
    ax.text(6.0, 1.75, "Orders / Information Flow", ha="center", va="bottom", fontsize=10)

    # Uncertainty annotations
    ax.text(2.2, 3.3, "Supply disruption\n(lead time shock)", ha="center", fontsize=10)
    ax.annotate("", xy=(2.2, 2.6), xytext=(2.2, 3.1),
                arrowprops=dict(arrowstyle="->", linewidth=1.2))

    ax.text(9.8, 3.3, "Demand volatility\n(holiday effects)", ha="center", fontsize=10)
    ax.annotate("", xy=(9.8, 2.6), xytext=(9.8, 3.1),
                arrowprops=dict(arrowstyle="->", linewidth=1.2))

    ax.set_title("Figure 3.1: Conceptual Multi-Echelon Inventory System", fontsize=13)

    png_path = PLOTS_DIR / "figure_3_1_multi_echelon_network.png"
    pdf_path = PLOTS_DIR / "figure_3_1_multi_echelon_network.pdf"

    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)

    return png_path, pdf_path

if __name__ == "__main__":
    print("Saving to:", PLOTS_DIR)
    png_path, pdf_path = figure_3_1_multi_echelon()
    print("✅ Saved:", png_path)
    print("✅ Saved:", pdf_path)
    print("Exists PNG?", png_path.exists())
    print("Exists PDF?", pdf_path.exists())
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Save figures here
PLOTS_DIR = Path("/Users/asus/Documents/Dissertation/WallmartData_old/outputs/plots")
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

# Update this to your chosen demand series file
DEMAND_SERIES_PATH = Path("/Users/asus/Documents/Dissertation/WallmartData_old/outputs/series/demand_series_store14_dept92.csv")

def fig_3_2_disruption_timeline():
    """
    Figure 3.2: Example disruption timeline (illustration).
    Shows baseline operation, disruption window, and recovery window.
    """
    fig, ax = plt.subplots(figsize=(12, 3))
    weeks = np.arange(1, 53)

    disruption_start = 20
    disruption_end = 30
    recovery_end = 38

    ax.plot(weeks, np.ones_like(weeks), linewidth=2)
    ax.axvspan(disruption_start, disruption_end, alpha=0.25, label="Disruption window")
    ax.axvspan(disruption_end, recovery_end, alpha=0.15, label="Recovery window")

    ax.set_yticks([])
    ax.set_xlabel("Week index (illustrative)")
    ax.set_title("Figure 3.2: Disruption Timeline Used in Scenario Design")

    ax.legend(loc="upper right")
    fig.savefig(PLOTS_DIR / "figure_3_2_disruption_timeline.png", dpi=300, bbox_inches="tight")
    fig.savefig(PLOTS_DIR / "figure_3_2_disruption_timeline.pdf", bbox_inches="tight")
    plt.close(fig)

def fig_3_3_demand_volatility_profile():
    """
    Figure 3.3: Demand series + rolling mean + rolling standard deviation.
    Uses your selected Walmart demand series.
    """
    if not DEMAND_SERIES_PATH.exists():
        print("⚠️ Demand series not found at:", DEMAND_SERIES_PATH)
        print("Please update DEMAND_SERIES_PATH at top of file.")
        return

    df = pd.read_csv(DEMAND_SERIES_PATH)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)

    window = 8  # 8-week rolling window (adjustable)
    df["roll_mean"] = df["Weekly_Sales"].rolling(window).mean()
    df["roll_std"] = df["Weekly_Sales"].rolling(window).std()

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(df["Date"], df["Weekly_Sales"], linewidth=1.5, label="Weekly demand")
    ax.plot(df["Date"], df["roll_mean"], linewidth=2.0, label=f"{window}-week rolling mean")

    ax2 = ax.twinx()
    ax2.plot(df["Date"], df["roll_std"], linewidth=2.0, linestyle="--", label=f"{window}-week rolling std")

    ax.set_title("Figure 3.3: Empirical Demand Volatility Profile (Selected Store–Department)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Weekly Sales (Demand)")
    ax2.set_ylabel("Rolling Std (Volatility)")

    # Combine legends
    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines + lines2, labels + labels2, loc="upper left")

    fig.savefig(PLOTS_DIR / "figure_3_3_demand_volatility_profile.png", dpi=300, bbox_inches="tight")
    fig.savefig(PLOTS_DIR / "figure_3_3_demand_volatility_profile.pdf", bbox_inches="tight")
    plt.close(fig)

def fig_3_4_scenario_matrix():
    """
    Figure 3.4: Scenario matrix (Demand shock x Supply shock severity).
    Simple heatmap-style representation.
    """
    demand_levels = ["Normal", "Moderate surge", "Severe surge"]
    supply_levels = ["Normal lead time", "Moderate delay", "Severe delay"]

    matrix = np.array([
        [1, 2, 3],
        [2, 3, 4],
        [3, 4, 5]
    ])

    fig, ax = plt.subplots(figsize=(8, 5))
    im = ax.imshow(matrix)

    ax.set_xticks(range(len(supply_levels)))
    ax.set_yticks(range(len(demand_levels)))
    ax.set_xticklabels(supply_levels, rotation=20, ha="right")
    ax.set_yticklabels(demand_levels)

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(j, i, f"S{i+1}{j+1}", ha="center", va="center")

    ax.set_title("Figure 3.4: Scenario Matrix (Demand vs Supply Disruption Severity)")
    ax.set_xlabel("Supply-side disruption severity")
    ax.set_ylabel("Demand-side shock severity")

    fig.savefig(PLOTS_DIR / "figure_3_4_scenario_matrix.png", dpi=300, bbox_inches="tight")
    fig.savefig(PLOTS_DIR / "figure_3_4_scenario_matrix.pdf", bbox_inches="tight")
    plt.close(fig)

if __name__ == "__main__":
    print("Saving methodology figures to:", PLOTS_DIR)
    fig_3_2_disruption_timeline()
    fig_3_3_demand_volatility_profile()
    fig_3_4_scenario_matrix()
    print("✅ Done. Check your plots folder.")
    from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# Paths (match your setup)
# -----------------------------
BASE_OUT = Path("/Users/asus/Documents/Dissertation/WallmartData_old/outputs")
TABLES_DIR = BASE_OUT / "tables"
PLOTS_DIR = BASE_OUT / "plots"
TABLES_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

DEMAND_SERIES_PATH = BASE_OUT / "series/demand_series_store14_dept92.csv"

# -----------------------------
# Table 3.1: Demand Statistics
# -----------------------------
df = pd.read_csv(DEMAND_SERIES_PATH)
df["Date"] = pd.to_datetime(df["Date"])

holiday_mean = df[df["IsHoliday"] == True]["Weekly_Sales"].mean()
nonholiday_mean = df[df["IsHoliday"] == False]["Weekly_Sales"].mean()

stats = {
    "Mean weekly demand": df["Weekly_Sales"].mean(),
    "Standard deviation": df["Weekly_Sales"].std(),
    "Coefficient of variation": df["Weekly_Sales"].std() / df["Weekly_Sales"].mean(),
    "Minimum demand": df["Weekly_Sales"].min(),
    "Maximum demand": df["Weekly_Sales"].max(),
    "Holiday uplift ratio": holiday_mean / nonholiday_mean
}

table_3_1 = pd.DataFrame.from_dict(stats, orient="index", columns=["Value"])
table_3_1.index.name = "Metric"

table_3_1_path = TABLES_DIR / "table_3_1_demand_statistics.csv"
table_3_1.to_csv(table_3_1_path)

# Save as image for Word
fig, ax = plt.subplots(figsize=(7, 3))
ax.axis("off")
tbl = ax.table(
    cellText=np.round(table_3_1.values, 3),
    rowLabels=table_3_1.index,
    colLabels=table_3_1.columns,
    loc="center"
)
tbl.scale(1, 1.4)
ax.set_title("Table 3.1: Demand Series Descriptive Statistics", pad=10)

plt.savefig(PLOTS_DIR / "table_3_1_demand_statistics.png", dpi=300, bbox_inches="tight")
plt.close()

print("✅ Table 3.1 created")

# -----------------------------
# Table 3.2: Scenario Definitions
# -----------------------------
table_3_2 = pd.DataFrame({
    "Scenario": ["Baseline", "Demand Surge", "Supply Disruption", "Combined Disruption"],
    "Demand Shock": ["None", "Increase in mean & variance", "None", "Increase in mean & variance"],
    "Supply Shock": ["None", "None", "Lead-time extension", "Lead-time extension"],
    "Purpose": [
        "Benchmark system performance",
        "Test demand-side resilience",
        "Test supply-side resilience",
        "Test compound risk exposure"
    ]
})

table_3_2_path = TABLES_DIR / "table_3_2_scenario_definitions.csv"
table_3_2.to_csv(table_3_2_path, index=False)

print("✅ Table 3.2 created")

# -----------------------------
# Table 3.3: Performance Metrics
# -----------------------------
table_3_3 = pd.DataFrame({
    "Metric Category": ["Efficiency", "Efficiency", "Resilience", "Resilience", "Resilience"],
    "Metric": [
        "Total inventory holding cost",
        "Average on-hand inventory",
        "Service level (%)",
        "Unmet demand (units)",
        "Recovery duration (proxy)"
    ],
    "Description": [
        "Cost incurred from holding safety stock across echelons",
        "Average inventory held during simulation horizon",
        "Proportion of demand satisfied without stockout",
        "Total demand not fulfilled during disruption",
        "Time required for inventory to return to steady-state"
    ]
})

table_3_3_path = TABLES_DIR / "table_3_3_performance_metrics.csv"
table_3_3.to_csv(table_3_3_path, index=False)

print("✅ Table 3.3 created")

print("\nAll Chapter 3 tables generated successfully.")