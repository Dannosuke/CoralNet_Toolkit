################################################
#### Coral Statistics and Diversity Indices ####
################################################

# Analyzes .cpc files to compare actual vs. predicted coral data.

import os
import re
import math
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.colors import LinearSegmentedColormap, Normalize
from scipy import stats
from pathlib import Path
from sklearn.metrics import accuracy_score, f1_score, matthews_corrcoef, cohen_kappa_score

# --- Configuration ---
NON_CORAL_FOR_COVER = ['NC', '', 'NONE']
EXCLUDE_FROM_DIVERSITY = ['NC', 'UNKC', '', 'NONE']


# ----------------------------
# Confusion Matrix Heatmap Logic
# ----------------------------
def is_nan_label(x) -> bool:
    if pd.isna(x):
        return True
    s = str(x).strip().lower()
    return s == "nan" or s == ""


def sanitize_for_filename(s: str) -> str:
    s = (s or "").strip()
    s = s.replace(" ", "_")
    s = re.sub(r"[^A-Za-z0-9_\-]+", "", s)
    return s or "dataset"


def format_cell_number(val: float) -> str:
    if val == 0:
        return "0"
    if 0 < val < 1:
        s = f"{val:.2f}"   # nearest hundredth
        return s[1:] if s.startswith("0") else s  # 0.95 -> .95
    return f"{val:.0f}"


def make_heatmap_from_labels(y_true, y_pred, dataset_name, out_dir, annotate=True):
    true_s = pd.Series(y_true, name="True").astype(str).str.strip()
    pred_s = pd.Series(y_pred, name="Pred").astype(str).str.strip()
    keep_mask = ~true_s.apply(is_nan_label) & ~pred_s.apply(is_nan_label)
    true_s, pred_s = true_s[keep_mask], pred_s[keep_mask]
    if len(true_s) == 0:
        return

    # Sort rows by True frequency (largest n to smallest n)
    true_counts = true_s.value_counts()
    labels = true_counts.index.tolist()

    # Include any predicted-only labels
    extra_labels = sorted([l for l in pred_s.unique() if l not in labels])
    labels = labels + extra_labels

    cm_counts = pd.crosstab(true_s, pred_s).reindex(index=labels, columns=labels, fill_value=0)
    mat = cm_counts.values.astype(float)
    row_sums = mat.sum(axis=1, keepdims=True)
    mat_row_pct = np.divide(mat, row_sums, out=np.zeros_like(mat), where=row_sums != 0) * 100.0

    n = mat_row_pct.shape[0]
    fig_w, fig_h = max(8, min(25, 0.45 * n)), max(7, min(25, 0.45 * n))
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=200)

    # Show 0% as white by masking them as NaN for the image
    plot_data = np.ma.masked_invalid(np.where(mat_row_pct == 0, np.nan, mat_row_pct))
    cmap = LinearSegmentedColormap.from_list("blue_to_red", ["blue", "red"])
    cmap.set_bad(color="white")
    im = ax.imshow(plot_data, cmap=cmap, norm=Normalize(vmin=0, vmax=100))

    ax.set_title(
        f"Confusion Matrix: {dataset_name}\n(% Within True Class)",
        fontweight="bold",
        fontsize=28,
        pad=14
    )

    ax.set_xlabel("Predicted Class", fontweight="bold", fontsize=20, labelpad=16)
    ax.set_ylabel("True Class", fontweight="bold", fontsize=20, labelpad=16)

    ax.set_xticks(np.arange(n))
    ax.set_yticks(np.arange(n))

    fs = max(12, int(22 - 0.12 * n))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=fs, fontweight="bold")
    ax.set_yticklabels(
        [f"{lbl} (n={int(true_counts.get(lbl, 0))})" for lbl in labels],
        fontsize=fs,
        fontweight="bold"
    )

    ax.tick_params(axis="x", labelsize=fs, pad=6)
    ax.tick_params(axis="y", labelsize=fs, pad=6)

    # Light grey grid outlining each cell
    ax.set_xticks(np.arange(n + 1) - 0.5, minor=True)
    ax.set_yticks(np.arange(n + 1) - 0.5, minor=True)
    ax.grid(which="minor", color="#c0c0c0", linestyle="-", linewidth=0.6)
    ax.tick_params(which="minor", bottom=False, left=False)

    # Always annotate if requested, and scale font size to fill each cell
    if annotate:
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        ax_bbox = ax.get_window_extent(renderer=renderer)

        cell_w_px = ax_bbox.width / n
        cell_h_px = ax_bbox.height / n

        pad = 0.90
        height_frac = 0.75
        char_width = 0.62

        outline = [pe.withStroke(linewidth=1, foreground="black")]

        for i in range(n):
            if row_sums[i, 0] <= 0:
                continue
            for j in range(n):
                val = mat_row_pct[i, j]
                if val <= 0:
                    continue

                s = format_cell_number(val)
                L = max(1, len(s))

                fs_px_h = cell_h_px * height_frac
                fs_px_w = (cell_w_px * pad) / (char_width * L)
                fs_px = min(fs_px_h, fs_px_w)

                fs_pt = fs_px * 72.0 / fig.dpi
                fs_pt = max(4, min(80, fs_pt))

                ax.text(
                    j, i, s,
                    ha="center", va="center",
                    fontsize=fs_pt,
                    color="white",
                    path_effects=outline,
                    zorder=3
                )

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("% Accuracy per class", fontsize=18, fontweight="bold", labelpad=12)
    cbar.ax.tick_params(labelsize=14)

    plt.tight_layout()
    ds = sanitize_for_filename(dataset_name)
    fig.savefig(os.path.join(out_dir, f"Confusion_Matrix_{ds}.png"), bbox_inches="tight")
    plt.close(fig)


# ----------------------------
# Training Summary Graphs
# ----------------------------
def make_training_summary_graphs(master_df: pd.DataFrame, out_dir: str,
                                 filename_base: str = "Training_Relationship_Graphs"):
    if master_df is None or master_df.empty:
        return

    df = master_df.sort_values("Training_%").copy()

    required = {
        "Training_%", "Accuracy", "Kappa", "MCC",
        "Act_Cover", "Pred_Cover",
        "Act_SW", "Pred_SW",
        "Act_Chao", "Pred_Chao"
    }
    if not required.issubset(df.columns):
        return

    x = df["Training_%"].astype(float).values

    act_cover = df["Act_Cover"].dropna().iloc[0] if df["Act_Cover"].notna().any() else None
    act_sw = df["Act_SW"].dropna().iloc[0] if df["Act_SW"].notna().any() else None
    act_chao = df["Act_Chao"].dropna().iloc[0] if df["Act_Chao"].notna().any() else None

    fig, axs = plt.subplots(2, 2, figsize=(12, 8), dpi=200)

    axs[0, 0].plot(x, df["Accuracy"].values, marker="o", linewidth=2, label="Accuracy")
    axs[0, 0].plot(x, df["Kappa"].values, marker="s", linewidth=2, label="Kappa")
    axs[0, 0].plot(x, df["MCC"].values, marker="^", linewidth=2, label="MCC")
    axs[0, 0].set_ylim(0, 1.05)
    axs[0, 0].set_xlabel("Training %", fontweight="bold")
    axs[0, 0].set_title("Classification", fontweight="bold")
    axs[0, 0].legend(frameon=True)

    axs[0, 1].plot(x, df["Pred_Cover"].values, marker="o", linewidth=2)
    if act_cover is not None:
        axs[0, 1].axhline(act_cover, linestyle="--", linewidth=1.5)
    axs[0, 1].set_xlabel("Training %", fontweight="bold")
    axs[0, 1].set_title("Coral Cover %", fontweight="bold")
    axs[0, 1].set_ylim(bottom=0)

    axs[1, 0].plot(x, df["Pred_SW"].values, marker="o", linewidth=2)
    if act_sw is not None:
        axs[1, 0].axhline(act_sw, linestyle="--", linewidth=1.5)
    axs[1, 0].set_xlabel("Training %", fontweight="bold")
    axs[1, 0].set_title("Shannon-Wiener", fontweight="bold")
    axs[1, 0].set_ylim(bottom=0)

    axs[1, 1].plot(x, df["Pred_Chao"].values, marker="o", linewidth=2)
    if act_chao is not None:
        axs[1, 1].axhline(act_chao, linestyle="--", linewidth=1.5)
    axs[1, 1].set_xlabel("Training %", fontweight="bold")
    axs[1, 1].set_title("Chao1 Richness", fontweight="bold")
    axs[1, 1].set_ylim(bottom=0)

    plt.tight_layout()
    os.makedirs(out_dir, exist_ok=True)
    fig.savefig(os.path.join(out_dir, f"{filename_base}.jpg"), dpi=200, bbox_inches="tight")
    fig.savefig(os.path.join(out_dir, f"{filename_base}.png"), dpi=200, bbox_inches="tight")
    plt.close(fig)


# --- Helper Functions ---
def extract_percent(folder_name):
    match = re.search(r'(\d+)', folder_name)
    return int(match.group(1)) if match else 0


def get_sig_star(p):
    if pd.isna(p) or p > 0.05:
        return "ns"
    return '***' if p < 0.001 else '**' if p < 0.01 else '*'


def get_diversity_metrics(series, is_global=False):
    labels = series.astype(str).str.strip().str.upper()
    coral_only = labels[~labels.isin(EXCLUDE_FROM_DIVERSITY)]
    total = len(coral_only)
    if total == 0:
        return 0.0, 0.0, 0.0
    counts = coral_only.value_counts()
    sw = -sum((c / total) * math.log2(c / total) for c in counts)
    simp = 1 - sum((c / total) ** 2 for c in counts)
    s_obs = len(counts)
    f1, f2 = sum(counts == 1), sum(counts == 2)
    chao1 = s_obs + (f1 ** 2) / (2 * f2) if f2 > 0 else s_obs + (f1 * (f1 - 1)) / 2
    return (sw, simp, int(round(chao1))) if is_global else (sw, simp, chao1)


def calculate_coral_cover(series):
    labels = series.astype(str).str.strip().str.upper()
    return (labels[~labels.isin(NON_CORAL_FOR_COVER)].count() / len(labels)) * 100 if len(labels) > 0 else 0


def read_cpc(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        start = next(i for i, line in enumerate(lines) if line.startswith('"1"'))
        labels = [
            line.split(',')[1].strip('" ')
            for line in lines[start:]
            if len(line.split(',')) > 1 and line.split(',')[0].strip('"').isdigit()
        ]
        return pd.Series(labels)
    except:
        return pd.Series(dtype=str)


# --- Main Analysis Engine ---
def run_analysis():
    act_dir, pred_path = dir1_var.get(), dir2_var.get()
    if not act_dir or not pred_path:
        messagebox.showwarning("Input Error", "Please select folders.")
        return

    output.delete(1.0, tk.END)

    # Ground truth file set is fixed across all runs
    actual_files = {f for f in os.listdir(act_dir) if f.endswith('.cpc')}

    if not actual_files:
        messagebox.showerror("Input Error", "No .cpc files found in the Actual (Ground Truth) folder.")
        return

    sub_folders = (
        [f.path for f in os.scandir(pred_path) if f.is_dir() and os.path.basename(f.path) != "Results"]
        if batch_var.get()
        else [pred_path]
    )
    sub_folders.sort(key=lambda x: extract_percent(os.path.basename(x)))

    main_res_path = os.path.join(pred_path, "Results")
    os.makedirs(main_res_path, exist_ok=True)

    master_summary, master_frequencies = [], {}

    for sub_path in sub_folders:
        folder_name = os.path.basename(sub_path)
        output.insert(tk.END, f"Processing: {folder_name}\n")
        output.see(tk.END)
        root.update_idletasks()

        predicted_files = {f for f in os.listdir(sub_path) if f.endswith('.cpc')}
        common_files = sorted(list(actual_files & predicted_files))

        # NEW: enforce "all actual must match", prompt if not
        missing_in_pred = sorted(list(actual_files - predicted_files))
        if missing_in_pred:
            preview = "\n".join(missing_in_pred[:12])
            more = "" if len(missing_in_pred) <= 12 else f"\n...and {len(missing_in_pred) - 12} more"

            msg = (
                "All ground truth data do not have matching predicted data.\n\n"
                f"Actual .cpc files: {len(actual_files)}\n"
                f"Predicted .cpc files: {len(predicted_files)}\n"
                f"Matched files: {len(common_files)}\n"
                f"Missing matches: {len(missing_in_pred)}\n\n"
                "Examples:\n"
                f"{preview}{more}\n\n"
                "Would you like to proceed using only the matched files?"
            )

            proceed = messagebox.askyesno("Missing matches", msg)
            if not proceed:
                output.insert(tk.END, "Cancelled by user due to missing matches.\n")
                output.see(tk.END)
                return

        if not common_files:
            messagebox.showerror(
                "No matching CPC files",
                "No matching .cpc filenames were found between the Actual and Predicted folders.\n\n"
                "This tool matches by exact filename."
            )
            return

        per_img_stats, a_all, p_all = [], [], []
        for f in common_files:
            a = read_cpc(os.path.join(act_dir, f))
            p = read_cpc(os.path.join(sub_path, f))
            if a.empty or p.empty or len(a) != len(p):
                continue

            div_a, div_p = get_diversity_metrics(a), get_diversity_metrics(p)
            per_img_stats.append({
                'ca': calculate_coral_cover(a),
                'cp': calculate_coral_cover(p),
                'sa': div_a[0],
                'sp': div_p[0],
                'ia': div_a[1],
                'ip': div_p[1],
                'cha': div_a[2],
                'chp': div_p[2]
            })
            a_all.append(a)
            p_all.append(p)

        if not a_all:
            continue

        df_img = pd.DataFrame(per_img_stats)
        all_act = pd.concat(a_all)
        all_pred = pd.concat(p_all)

        # Calculate P-Values & Metrics
        p_vals = {
            k: stats.ttest_rel(df_img[a_col], df_img[p_col]).pvalue
            for k, a_col, p_col in [('cov', 'ca', 'cp'), ('sw', 'sa', 'sp'), ('simp', 'ia', 'ip'), ('chao', 'cha', 'chp')]
        }

        acc = accuracy_score(all_act, all_pred)
        f1 = f1_score(all_act, all_pred, average='weighted')
        mcc = matthews_corrcoef(all_act, all_pred)
        kappa = cohen_kappa_score(all_act, all_pred)

        ga = get_diversity_metrics(all_act, True)
        gp = get_diversity_metrics(all_pred, True)
        c_ga = calculate_coral_cover(all_act)
        c_gp = calculate_coral_cover(all_pred)

        master_summary.append({
            'Training_%': extract_percent(folder_name),
            'Folder': folder_name,
            'Accuracy': acc,
            'F1': f1,
            'MCC': mcc,
            'Kappa': kappa,
            'Act_Cover': c_ga,
            'Pred_Cover': c_gp,
            'P_Cover': p_vals['cov'],
            'Act_SW': ga[0],
            'Pred_SW': gp[0],
            'P_SW': p_vals['sw'],
            'Act_Chao': ga[2],
            'Pred_Chao': gp[2],
            'P_Chao': p_vals['chao']
        })

        # Save Individual Folder Data
        dest = os.path.join(main_res_path, folder_name)
        os.makedirs(dest, exist_ok=True)

        make_heatmap_from_labels(all_act.tolist(), all_pred.tolist(), folder_name, dest)

        freq_df = pd.DataFrame({
            'Actual Count': all_act.value_counts(),
            'Predicted Count': all_pred.value_counts()
        }).fillna(0)

        freq_df['Actual %'] = (freq_df['Actual Count'] / len(all_act)) * 100
        freq_df['Predicted %'] = (freq_df['Predicted Count'] / len(all_pred)) * 100
        master_frequencies[folder_name] = freq_df.sort_values('Actual Count', ascending=False)

        summary_df = pd.DataFrame({
            'Metric Group': ['Classification'] * 4 + ['Diversity/Cover'] * 4,
            'Metric Name': [
                'Accuracy', 'F1 (Weighted)', 'MCC', 'Kappa',
                'Coral Cover (%)', 'Shannon-Wiener', 'Simpsons', 'Chao1'
            ],
            'Actual / Value': [acc, f1, mcc, kappa, c_ga, ga[0], ga[1], ga[2]],
            'Predicted': [None] * 4 + [c_gp, gp[0], gp[1], gp[2]],
            'P-Value': [None] * 4 + [p_vals['cov'], p_vals['sw'], p_vals['simp'], p_vals['chao']],
            'Sig': [None] * 4 + [
                get_sig_star(p_vals['cov']),
                get_sig_star(p_vals['sw']),
                get_sig_star(p_vals['simp']),
                get_sig_star(p_vals['chao'])
            ]
        })

        with pd.ExcelWriter(os.path.join(dest, f"{folder_name}_Results.xlsx")) as writer:
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            master_frequencies[folder_name].to_excel(writer, sheet_name='Labels')

        # Individual Plotting
        fig_sub, axs_sub = plt.subplots(2, 2, figsize=(11, 8))
        plot_items = [
            ('Cover %', c_ga, c_gp, df_img['ca'].sem(), df_img['cp'].sem(), p_vals['cov'], 0, 0),
            ('Shannon-Wiener', ga[0], gp[0], df_img['sa'].sem(), df_img['sp'].sem(), p_vals['sw'], 0, 1),
            ('Simpsons', ga[1], gp[1], df_img['ia'].sem(), df_img['ip'].sem(), p_vals['simp'], 1, 0),
            ('Chao1', ga[2], gp[2], df_img['cha'].sem(), df_img['chp'].sem(), p_vals['chao'], 1, 1)
        ]

        for title, av, pv, ase, pse, pval, r, c in plot_items:
            axs_sub[r, c].bar(
                ['Actual', 'Pred'],
                [av, pv],
                yerr=[ase, pse],
                capsize=6,
                color=['#3498db', '#e74c3c'],
                alpha=0.8,
                edgecolor='black'
            )
            axs_sub[r, c].set_title(f"{title}\np={pval:.4f} ({get_sig_star(pval)})",
                                    fontsize=10, fontweight='bold')

        plt.tight_layout()
        plt.savefig(os.path.join(dest, f"{folder_name}_Plots.jpg"), dpi=200)
        plt.close(fig_sub)

    # Final Master Report + Summary Graphs
    master_df = pd.DataFrame(master_summary)

    if master_df.empty:
        messagebox.showerror(
            "No comparable data",
            "No summary rows were produced.\n\n"
            "This means there were zero matching .cpc filenames between the Actual and Predicted folders, "
            "or there were no overlapping point indices after alignment.\n\n"
        )
        return

    if "Training_%" not in master_df.columns:
        master_df = master_df.sort_values(master_df.columns[0])
    else:
        master_df = master_df.sort_values("Training_%")

    with pd.ExcelWriter(os.path.join(main_res_path, "Master_Summary_Report.xlsx")) as writer:
        master_df.to_excel(writer, sheet_name='Overview', index=False)
        for name, fdf in master_frequencies.items():
            fdf.to_excel(writer, sheet_name=name[:31])

    make_training_summary_graphs(master_df, main_res_path)

    messagebox.showinfo("Success", "Full Analysis Complete.\nCheck the 'Results' folder.")


# --- GUI ---
root = tk.Tk()
root.title("CPCe Ultimate Statistical Analysis & Matrix Suite")

dir1_var, dir2_var, batch_var = tk.StringVar(), tk.StringVar(), tk.BooleanVar(value=True)

for label, var in [("Actual Folder (Ground Truth):", dir1_var), ("Predicted Folder (Parent if batch):", dir2_var)]:
    tk.Label(root, text=label, font=('Arial', 10, 'bold')).pack(pady=(10, 0))
    tk.Entry(root, textvariable=var, width=90).pack()
    tk.Button(root, text="Browse", command=lambda v=var: v.set(filedialog.askdirectory())).pack()

tk.Checkbutton(root, text="Batch Mode (Process all sub-folders)", variable=batch_var, font=('Arial', 10)).pack(pady=10)

tk.Button(
    root,
    text="RUN COMPLETE ANALYSIS",
    bg="#1a5276",
    fg="white",
    font=('Arial', 12, 'bold'),
    command=run_analysis,
    width=30
).pack(pady=15)

output = tk.Text(root, height=12, width=100, font=('Courier', 10), bg="#f4f6f7")
output.pack(padx=20, pady=10)

root.mainloop()
