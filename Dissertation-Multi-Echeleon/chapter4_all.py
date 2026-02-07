from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# PATHS (your setup)
# =========================
BASE_OUT = Path("/Users/asus/Documents/Dissertation/WallmartData_old/outputs")
PLOTS_DIR = BASE_OUT / "plots"
TABLES_DIR = BASE_OUT / "tables"
SERIES_DIR = BASE_OUT / "series"

PLOTS_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)
SERIES_DIR.mkdir(parents=True, exist_ok=True)

DEMAND_SERIES_PATH = SERIES_DIR / "demand_series_store14_dept92.csv"

# =========================
# SIMULATION CORE (3-echelon, weekly)
# Echelon 1: Supplier pipeline (lead time)
# Echelon 2: DC inventory
# Echelon 3: Retail inventory (fulfills demand)
# =========================
def simulate_3echelon(
    demand: np.ndarray,
    base_lead_time: int = 2,         # weeks
    lead_time_shock_add: int = 0,    # additional weeks during shock
    shock_start: int = 40,           # index in weeks
    shock_end: int = 55,             # index in weeks
    demand_shock_mult: float = 1.0,  # multiplier during shock
    ss_retail: float = 0.0,
    ss_dc: float = 0.0,
    order_up_to_retail: float = 0.0,
    order_up_to_dc: float = 0.0,
    holding_cost_retail: float = 0.02,  # per unit per week (scaled)
    holding_cost_dc: float = 0.01,
    seed: int = 0
):
    np.random.seed(seed)

    T = len(demand)

    # Apply demand shock
    d = demand.copy().astype(float)
    d[shock_start:shock_end] *= demand_shock_mult

    # State variables
    inv_retail = order_up_to_retail
    inv_dc = order_up_to_dc

    # pipeline: list of (arrival_week, quantity) for supplier->dc orders
    pipeline = []

    fulfilled = np.zeros(T)
    unmet = np.zeros(T)
    inv_retail_hist = np.zeros(T)
    inv_dc_hist = np.zeros(T)
    orders_retail = np.zeros(T)
    orders_dc = np.zeros(T)

    total_hold_cost = 0.0

    for t in range(T):
        # lead time (shock affects supplier->dc)
        lt = base_lead_time
        if shock_start <= t < shock_end:
            lt += lead_time_shock_add

        # 1) Receive pipeline orders into DC
        arrivals = 0.0
        if pipeline:
            still = []
            for (arr_t, qty) in pipeline:
                if arr_t == t:
                    arrivals += qty
                else:
                    still.append((arr_t, qty))
            pipeline = still
        inv_dc += arrivals

        # 2) Retail ordering from DC: order up to target (base stock)
        target_retail = order_up_to_retail + ss_retail
        needed = max(0.0, target_retail - inv_retail)

        # Ship from DC to retail instantly (simplification)
        ship = min(inv_dc, needed)
        inv_dc -= ship
        inv_retail += ship
        orders_retail[t] = ship

        # 3) Demand happens at retail
        dem = d[t]
        fill = min(inv_retail, dem)
        inv_retail -= fill
        fulfilled[t] = fill
        unmet[t] = dem - fill

        # 4) DC ordering from supplier: order up to target (base stock)
        target_dc = order_up_to_dc + ss_dc
        needed_dc = max(0.0, target_dc - inv_dc)

        # Place supplier order (arrives after lt weeks)
        if needed_dc > 0:
            pipeline.append((t + lt, needed_dc))
            orders_dc[t] = needed_dc

        # 5) Holding costs
        total_hold_cost += inv_retail * holding_cost_retail + inv_dc * holding_cost_dc

        # record
        inv_retail_hist[t] = inv_retail
        inv_dc_hist[t] = inv_dc

    service_level = fulfilled.sum() / (d.sum() + 1e-9)
    total_unmet = unmet.sum()

    # simple recovery proxy: weeks after shock_end until unmet demand returns ~0
    recovery = None
    after = unmet[shock_end:]
    if len(after) == 0:
        recovery = 0
    else:
        # first time we see 3 consecutive weeks of near-zero unmet
        eps = 1e-6
        for i in range(len(after) - 2):
            if after[i] <= eps and after[i+1] <= eps and after[i+2] <= eps:
                recovery = i
                break
        recovery = recovery if recovery is not None else len(after)

    out = pd.DataFrame({
        "t": np.arange(T),
        "demand": d,
        "fulfilled": fulfilled,
        "unmet": unmet,
        "inv_retail": inv_retail_hist,
        "inv_dc": inv_dc_hist,
        "order_to_retail": orders_retail,
        "order_to_dc": orders_dc,
    })

    summary = {
        "Service_Level": service_level,
        "Total_Unmet": float(total_unmet),
        "Total_Holding_Cost": float(total_hold_cost),
        "Avg_Inv_Retail": float(inv_retail_hist.mean()),
        "Avg_Inv_DC": float(inv_dc_hist.mean()),
        "Recovery_Weeks_After_Shock": int(recovery),
    }
    return out, summary

# =========================
# HELPERS: save table as CSV + PNG
# =========================
def save_table(df: pd.DataFrame, name: str, title: str):
    csv_path = TABLES_DIR / f"{name}.csv"
    df.to_csv(csv_path, index=False)

    # as PNG for Word
    fig, ax = plt.subplots(figsize=(10, 0.6 + 0.35 * len(df)))
    ax.axis("off")
    tbl = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        loc="center"
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1, 1.4)
    ax.set_title(title, pad=12)
    png_path = PLOTS_DIR / f"{name}.png"
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print("✅ Saved table:", csv_path.name, "and", png_path.name)

def plot_timeseries(df: pd.DataFrame, name: str, title: str, shock_start=None, shock_end=None):
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(df["t"], df["demand"], label="Demand")
    ax.plot(df["t"], df["fulfilled"], label="Fulfilled")

    if shock_start is not None and shock_end is not None:
        ax.axvspan(shock_start, shock_end, alpha=0.2, label="Shock window")

    ax.set_title(title)
    ax.set_xlabel("Week index")
    ax.set_ylabel("Units")
    ax.legend()
    fig.savefig(PLOTS_DIR / f"{name}.png", dpi=300, bbox_inches="tight")
    fig.savefig(PLOTS_DIR / f"{name}.pdf", bbox_inches="tight")
    plt.close(fig)

    print("✅ Saved figure:", f"{name}.png/.pdf")

def plot_inventory(df: pd.DataFrame, name: str, title: str, shock_start=None, shock_end=None):
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(df["t"], df["inv_retail"], label="Retail inventory")
    ax.plot(df["t"], df["inv_dc"], label="DC inventory")

    if shock_start is not None and shock_end is not None:
        ax.axvspan(shock_start, shock_end, alpha=0.2, label="Shock window")

    ax.set_title(title)
    ax.set_xlabel("Week index")
    ax.set_ylabel("Inventory units")
    ax.legend()
    fig.savefig(PLOTS_DIR / f"{name}.png", dpi=300, bbox_inches="tight")
    fig.savefig(PLOTS_DIR / f"{name}.pdf", bbox_inches="tight")
    plt.close(fig)

    print("✅ Saved figure:", f"{name}.png/.pdf")

def plot_tradeoff(trade: pd.DataFrame, name: str):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(trade["Total_Holding_Cost"], trade["Service_Level"])
    ax.set_title("Cost vs Service Level Trade-off (Safety Stock Sweep)")
    ax.set_xlabel("Total holding cost")
    ax.set_ylabel("Service level")
    fig.savefig(PLOTS_DIR / f"{name}.png", dpi=300, bbox_inches="tight")
    fig.savefig(PLOTS_DIR / f"{name}.pdf", bbox_inches="tight")
    plt.close(fig)
    print("✅ Saved figure:", f"{name}.png/.pdf")

def plot_unmet_comparison(scenario_runs, name: str, title: str, shock_start=None, shock_end=None):
    """
    Fig. 10: Unmet demand comparison across scenarios.
    """
    fig, ax = plt.subplots(figsize=(12, 5))

    order = ["baseline", "demand_shock", "supply_shock", "combined_shock"]
    labels = {
        "baseline": "Baseline",
        "demand_shock": "Demand shock",
        "supply_shock": "Supply shock (lead time)",
        "combined_shock": "Combined shock",
    }

    for key in order:
        df = scenario_runs[key][0]
        ax.plot(df["t"], df["unmet"], label=labels[key])

    if shock_start is not None and shock_end is not None:
        ax.axvspan(shock_start, shock_end, alpha=0.2, label="Shock window")

    ax.set_title(title)
    ax.set_xlabel("Week index")
    ax.set_ylabel("Unmet demand (units)")
    ax.legend()

    ax.set_ylim(bottom=0)

    fig.savefig(PLOTS_DIR / f"{name}.png", dpi=300, bbox_inches="tight")
    fig.savefig(PLOTS_DIR / f"{name}.pdf", bbox_inches="tight")
    plt.close(fig)

    print("✅ Saved figure:", f"{name}.png/.pdf")

# =========================
# MAIN: generate ALL missing outputs
# =========================
def main():
    if not DEMAND_SERIES_PATH.exists():
        raise FileNotFoundError(f"Demand series not found: {DEMAND_SERIES_PATH}")

    data = pd.read_csv(DEMAND_SERIES_PATH)
    demand = data["Weekly_Sales"].to_numpy()
    T = len(demand)

    # Define a standard shock window in the middle
    shock_start = int(T * 0.55)
    shock_end = int(T * 0.70)

    # Base policy (order-up-to) from demand mean
    mean_d = float(np.mean(demand))
    order_up_to_retail = mean_d * 2.0  # 2 weeks cover
    order_up_to_dc = mean_d * 3.0      # 3 weeks cover

    # Choose one safety stock setting for scenario comparisons
    ss_retail = mean_d * 0.5
    ss_dc = mean_d * 0.8

    # -------------------------
    # SCENARIOS
    # -------------------------
    scenarios = [
        ("baseline", dict(demand_shock_mult=1.0, lead_time_shock_add=0)),
        ("demand_shock", dict(demand_shock_mult=1.4, lead_time_shock_add=0)),
        ("supply_shock", dict(demand_shock_mult=1.0, lead_time_shock_add=3)),
        ("combined_shock", dict(demand_shock_mult=1.4, lead_time_shock_add=3)),
    ]

    results = []
    scenario_runs = {}

    for scen_name, scen in scenarios:
        df_run, summ = simulate_3echelon(
            demand=demand,
            base_lead_time=2,
            lead_time_shock_add=scen["lead_time_shock_add"],
            shock_start=shock_start,
            shock_end=shock_end,
            demand_shock_mult=scen["demand_shock_mult"],
            ss_retail=ss_retail,
            ss_dc=ss_dc,
            order_up_to_retail=order_up_to_retail,
            order_up_to_dc=order_up_to_dc,
            seed=0
        )
        scenario_runs[scen_name] = (df_run, summ)
        results.append({"Scenario": scen_name, **summ})

    results_df = pd.DataFrame(results)

    # -------------------------
    # TABLES (Chapter 4)
    # -------------------------
    for i, scen in enumerate(["baseline", "demand_shock", "supply_shock", "combined_shock"], start=1):
        summ = scenario_runs[scen][1]
        table = pd.DataFrame([{
            "Scenario": scen,
            "Service_Level": round(summ["Service_Level"], 4),
            "Total_Unmet": round(summ["Total_Unmet"], 2),
            "Total_Holding_Cost": round(summ["Total_Holding_Cost"], 2),
            "Avg_Inv_Retail": round(summ["Avg_Inv_Retail"], 2),
            "Avg_Inv_DC": round(summ["Avg_Inv_DC"], 2),
            "Recovery_Weeks_After_Shock": summ["Recovery_Weeks_After_Shock"],
        }])
        save_table(table, f"table_4_{i}_{scen}_performance", f"Table {i}: {scen.replace('_',' ').title()} Performance Metrics")

    # Table 4.5: trade-off sweep
    sweep = []
    for mult in np.linspace(0.0, 2.0, 11):
        df_run, summ = simulate_3echelon(
            demand=demand,
            base_lead_time=2,
            lead_time_shock_add=3,
            shock_start=shock_start,
            shock_end=shock_end,
            demand_shock_mult=1.4,
            ss_retail=mean_d * 0.5 * mult,
            ss_dc=mean_d * 0.8 * mult,
            order_up_to_retail=order_up_to_retail,
            order_up_to_dc=order_up_to_dc,
            seed=0
        )
        sweep.append({
            "SS_Multiplier": round(float(mult), 2),
            "Service_Level": summ["Service_Level"],
            "Total_Unmet": summ["Total_Unmet"],
            "Total_Holding_Cost": summ["Total_Holding_Cost"],
            "Recovery_Weeks_After_Shock": summ["Recovery_Weeks_After_Shock"],
        })

    trade_df = pd.DataFrame(sweep)
    save_table(trade_df.round(4), "table_4_5_tradeoff_sweep", "Table 5: Trade-off Sweep (Safety Stock Multiplier)")

    # -------------------------
    # FIGURES (Chapter 4)
    # -------------------------
    plot_timeseries(
        scenario_runs["baseline"][0],
        "fig_1_baseline_demand_vs_fulfilled",
        "Fig. 1: Baseline Demand vs Fulfilled Demand",
        shock_start=shock_start,
        shock_end=shock_end
    )
    plot_inventory(
        scenario_runs["baseline"][0],
        "fig_1b_baseline_inventory_levels",
        "Fig. 1b: Baseline Inventory Levels (Retail vs DC)",
        shock_start=shock_start,
        shock_end=shock_end
    )

    plot_timeseries(
        scenario_runs["demand_shock"][0],
        "fig_2_demand_shock_demand_vs_fulfilled",
        "Fig. 2: Demand Shock Scenario (Demand vs Fulfilled)",
        shock_start=shock_start,
        shock_end=shock_end
    )
    plot_inventory(
        scenario_runs["demand_shock"][0],
        "fig_2b_demand_shock_inventory_levels",
        "Fig. 2b: Demand Shock Scenario (Inventory Levels)",
        shock_start=shock_start,
        shock_end=shock_end
    )

    plot_timeseries(
        scenario_runs["supply_shock"][0],
        "fig_3_supply_shock_demand_vs_fulfilled",
        "Fig. 3: Supply Lead-Time Shock Scenario (Demand vs Fulfilled)",
        shock_start=shock_start,
        shock_end=shock_end
    )
    plot_inventory(
        scenario_runs["supply_shock"][0],
        "fig_3b_supply_shock_inventory_levels",
        "Fig. 3b: Supply Shock Scenario (Inventory Levels)",
        shock_start=shock_start,
        shock_end=shock_end
    )

    plot_timeseries(
        scenario_runs["combined_shock"][0],
        "fig_4_combined_shock_demand_vs_fulfilled",
        "Fig. 4: Combined Demand + Supply Shock (Demand vs Fulfilled)",
        shock_start=shock_start,
        shock_end=shock_end
    )
    plot_inventory(
        scenario_runs["combined_shock"][0],
        "fig_4b_combined_shock_inventory_levels",
        "Fig. 4b: Combined Shock (Inventory Levels)",
        shock_start=shock_start,
        shock_end=shock_end
    )

    plot_tradeoff(trade_df, "fig_5_tradeoff_cost_vs_service")

    # Fig. 10 unmet comparison (FIXED: inside main, after scenario_runs exists)
    plot_unmet_comparison(
        scenario_runs,
        "fig_10_unmet_demand_comparison_all_scenarios",
        "Fig. 10: Unmet Demand Over Time Across All Scenarios",
        shock_start=shock_start,
        shock_end=shock_end
    )

    results_df.to_csv(TABLES_DIR / "chapter4_all_scenario_summaries.csv", index=False)

    print("\n✅ DONE. Generated all Chapter 4 tables + figures (including Fig. 10).")
    print("Tables:", TABLES_DIR)
    print("Figures:", PLOTS_DIR)

if __name__ == "__main__":
    main()
    