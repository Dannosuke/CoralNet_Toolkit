# CoralNet Toolkit

Welcome to the Coral Statistics Toolkit, a collection of Python tools designed to assist in analyzing coral cover data from .cpc files. This toolkit provides a range of functionalities, including statistical analysis of coral cover, diversity indices, and random file selection, all in an easy-to-use, GUI-based format.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Random File Selector](#1-random-file-selector)
  - [Coral Cover Analysis](#2-coral-cover-analysis)
  - [CPCe Direct Comparison and Matrix Suite](#3-cpce-direct-comparison-and-matrix-suite)
- [Requirements](#requirements)
- [CPCe Direct Comparison validation](#cpce-direct-comparison-validation)
- [Source code](#source-code)
- [Appendix (verbatim)](#appendix-verbatim)

## Overview

This repository contains three primary tools. The CPCe comparison tool is provided in both its original GUI form and an expanded matrix/reporting version:

- **Random File Selector:** Creates random replicate datasets by copying a user-selected percentage of files from a source directory.

- **Coral Cover Analysis:** Analyzes coral cover across multiple sites, transects, and depths, with exportable summaries in CSV format.

- **CPCe Direct Comparison:** Compares CoralNet-predicted annotations against ground-truth CPCe annotations using four machine-learning performance measures and three ecological diversity indices. The expanded matrix suite also produces statistical tests, confusion matrices, plots, and Excel reports.

## Features

- **Graphical User Interface (GUI):** Each script includes a Tkinter-based GUI for user-friendly interaction.
- **Data Sampling:** Randomly select files from a directory by a specified percentage.
- **Coral Cover Analysis:** Calculate site-, transect-, and depth-level coral cover summaries and export the data as CSV files.
- **Statistical Comparison:** Evaluate predicted versus actual annotations using accuracy, weighted F1-score, Cohen's kappa, and Matthews Correlation Coefficient (MCC).
- **Ecological Comparison:** Compare coral cover, Shannon-Wiener diversity, Simpson's diversity, and Chao1 richness.
- **Reports and Figures:** Export Excel summaries, label frequencies, confusion-matrix heatmaps, comparison plots, and batch-level training summary graphs.

## Installation

Clone the repository:

```bash
git clone https://github.com/Dannosuke/Coral_Statistics.git
cd Coral_Statistics
```

Install the required Python libraries:

```bash
python3 -m pip install numpy pandas scikit-learn scipy matplotlib openpyxl
```

Run a script with Python:

```bash
python3 "script_name.py"
```

## Usage

### 1. Random File Selector

#### Background

The Random File Selector streamlines the selection of random `.cpc` files for creating random replicates. It is designed to improve the efficiency and objectivity of data sampling in coral reef studies. Randomization helps ensure that files are selected without human bias, improving the validity and reliability of later statistical analyses.

By automating this process, the tool helps samples reflect the true variability within the dataset—an important requirement for robust ecological assessments and unbiased comparisons. Its core function is to select a specified percentage of files randomly from a source directory and copy them to a target directory.

Users can select **3%, 5%, 10%, 20%, 40%, 60%, 80%, 90%, or 100%** of the source files, allowing sampling intensity to be adapted to a research question. After the source folder, target folder, and percentage are selected, the script randomly chooses the appropriate number of files and copies them to the target folder.

#### Running the script

The script is included in this repository as [`Random File Mover GUI`](./Random%20File%20Mover%20GUI).

1. Install Python 3.
2. Open a terminal and change to the repository directory.
3. Run:

   ```bash
   python3 "Random File Mover GUI"
   ```

4. In the window, click **Select** under **Source Folder** and choose the folder from which files will be sampled.
5. Click **Select** under **Target Folder** and choose the destination.
6. Choose the percentage of files to copy.
7. Click **Copy Files**. The randomly selected files will be copied into the target folder.

This tool uses only Python standard-library modules: `os`, `random`, `shutil`, and `tkinter`.

### 2. Coral Cover Analysis

This script calculates coral cover averages at site, transect, and depth levels within a selected folder structure. Data is organized into summaries and can be saved as CSV files.

Launch [`Coral Cover Analysis per Site over Depth GUI (CSV)`](./Coral%20Cover%20Analysis%20per%20Site%20over%20Depth%20GUI%20%28CSV%29).

1. Select the main folder containing `.cpc` files.
2. Review the calculated summaries in the GUI text box.
3. Save the site, transect, depth-per-site, and island-wide depth summaries as CSV files.

### 3. CPCe Direct Comparison and Matrix Suite

#### Background

The CPCe Direct Comparison GUI is a Python tool for validating the performance of a CoralNet classifier. It quickly compares sets of CPCe (`.cpc`) annotations and reports four key measures of machine-learning performance:

- Accuracy
- Weighted F1-score
- Cohen's kappa
- Matthews Correlation Coefficient (MCC)

It also measures community diversity using:

- Shannon-Wiener Index
- Simpson's Index of Diversity
- Chao1 Index

Together, the classification measures provide a broad and reliable assessment of classifier performance. The ecological indices add a multi-faceted characterization of community structure that complements classification accuracy.

The original implementation is available as [`CPCe Direct Comparison GUI`](./CPCe%20Direct%20Comparison%20GUI). The new [`CPC Direct Comparison - matrix.py`](./CPC%20Direct%20Comparison%20-%20matrix.py) version expands the workflow with exact-filename matching, batch analysis, coral-cover comparisons, paired tests, confusion-matrix heatmaps, plots, and Excel reports.

#### Classification metrics

- **Accuracy** provides an intuitive measure of overall correctness, but it can be misleading in the presence of class imbalance, which is common in ecological datasets.
- **F1-score**, defined as the harmonic mean of precision and recall, emphasizes performance in correctly identifying labeled classes. It is particularly informative when false positives and false negatives are unevenly distributed. The script calculates a weighted F1-score so that each class contributes according to its number of observations.
- **Cohen's kappa** quantifies agreement between predicted and reference labels while explicitly accounting for agreement expected by chance. This makes it well suited to comparisons between automated classifiers and human annotations.
- **Matthews Correlation Coefficient (MCC)** summarizes all elements of a confusion matrix in a single correlation statistic. It remains robust under severe class imbalance and provides a balanced assessment of overall predictive performance.

#### Ecological metrics

- **Shannon-Wiener Index** incorporates both richness and evenness. It provides a sensitive measure of changes in relative abundance distributions and is useful for detecting shifts in community composition.
- **Simpson's Index of Diversity** emphasizes dominance and is less sensitive to rare taxa. It provides a stable indication of whether classifications are disproportionately driven by common categories.
- **Chao1 Index** estimates true richness by accounting for unseen taxa based on the frequency of rare observations. It is particularly valuable in sparse or undersampled datasets.

Together, these indices provide a robust characterization of community structure. The expanded matrix suite additionally calculates **coral cover (%)**, defined as the percentage of annotations not labeled `NC`, blank, or `NONE`.

`NC`, `UNKC`, blank labels, and `NONE` are excluded from the diversity calculations. The script also performs paired t-tests on per-image coral cover and diversity values.

#### Prepare the input

1. Install Python 3 and the dependencies listed under [Requirements](#requirements).
2. Prepare two folders:

   - An **Actual** folder containing `.cpc` files annotated by a human expert.
   - A **Predicted** folder containing the CoralNet-predicted versions.

The Actual and Predicted folders should contain identical sets of `.cpc` filenames with different annotations—for example, Actual files annotated by a human expert and Predicted files annotated by CoralNet.

The matrix suite matches files by exact filename, including the `.cpc` extension, and each pair should contain the same number of annotation points. If predicted files are missing, the GUI identifies the mismatch and asks whether to continue with only the matched files. Unreadable pairs and pairs with unequal annotation counts are skipped.

#### Run the script

```bash
python3 "CPC Direct Comparison - matrix.py"
```

1. Click **Browse** and select the Actual (Ground Truth) folder.
2. Select the Predicted folder.
3. Choose whether to use **Batch Mode**.
4. Click **RUN COMPLETE ANALYSIS**.

With Batch Mode enabled, the Predicted folder is treated as a parent directory and every subfolder except `Results` is analyzed separately. Folder names containing percentages, such as `3%`, `10%`, and `20%`, are ordered by their numeric value for the training summary. With Batch Mode disabled, the selected Predicted folder is analyzed directly.

Progress is displayed in the GUI text box. When analysis is complete, a confirmation dialog directs the user to the generated `Results` folder.

#### Output

The script creates a `Results` folder inside the selected Predicted folder. It contains:

- A result directory for each analyzed prediction folder.
- A row-normalized confusion-matrix heatmap (`.png`).
- An Excel workbook with a metric summary and actual/predicted label frequencies.
- A four-panel comparison plot (`.jpg`) for coral cover and the three diversity indices.
- `Master_Summary_Report.xlsx`, containing the combined overview and label-frequency sheets.
- Training relationship graphs in both `.jpg` and `.png` formats.

## Requirements

- Python 3.x
- Tkinter (normally included with standard Python desktop installations)
- NumPy
- pandas
- scikit-learn
- SciPy
- Matplotlib
- openpyxl

Install the Python dependencies with:

```bash
python3 -m pip install numpy pandas scikit-learn scipy matplotlib openpyxl
```

## CPCe Direct Comparison validation

The classification models used by the script—accuracy, weighted F1-score, MCC, and Cohen's kappa—come from the `scikit-learn` Python library. The paired statistical tests in the matrix suite use SciPy.

For additional verification, create or modify two CPCe datasets using the test annotations from the validation label dataset (Table 1). Run the CPCe Comparison Tool and compare its output with the expected values in Tables 2 and 3.

> **Table 1 — Test label dataset:** The original appendix references a test annotation table, but no individual labels were included in the supplied appendix text. Add those labels here when the validation dataset is available.

**Table 2 — Expected machine-learning performance measures**

| Statistical measure | Expected output |
|---|---:|
| Accuracy | 0.78 |
| Weighted F1 | 0.82669 |
| MCC | 0.68407 |
| Cohen's kappa | 0.67456 |

**Table 3 — Expected ecological measures**

| Ecological measure | Actual | Predicted |
|---|---:|---:|
| Shannon-Wiener | 1.7942 | 2.1782 |
| Simpson's | 0.6248 | 0.7112 |
| Chao1 | 20.5 | 8 |

## Source code

The source code is kept in standalone files rather than duplicated inside this README. This ensures that the documented code link always points to the current implementation:

- [`CPC Direct Comparison - matrix.py`](./CPC%20Direct%20Comparison%20-%20matrix.py) — expanded comparison, matrix, plotting, batch, and reporting tool.
- [`CPCe Direct Comparison GUI`](./CPCe%20Direct%20Comparison%20GUI) — original direct-comparison GUI.
- [`Random File Mover GUI`](./Random%20File%20Mover%20GUI) — random replicate file selector.
- [`Coral Cover Analysis per Site over Depth GUI (CSV)`](./Coral%20Cover%20Analysis%20per%20Site%20over%20Depth%20GUI%20%28CSV%29) — coral-cover summary tool.

## Appendix (verbatim)

Tool 1 – CPCe Direct Comparison GUI

Background

The CPCe Direct Comparison GUI is a python script that can be run to validate the performance of a CoralNet Classifier. The tool allows users to quickly compare sets of CPCe (.CPCe) annotations and returns to the user 4 key statistical measures of Machine Learning performance as well as 3 ecological metrics* (Accuracy, F1-Score, Cohens Kappa, Matthews Correlation Coefficient, Shannon-Weiner Index, Simpsons Index, Chao1 Index).

• Accuracy provides an intuitive measure of overall correctness but can be misleading in the presence of class imbalance, which is common in ecological datasets.

• F1-score, defined as the harmonic mean of precision and recall, emphasizes performance on correctly identifying labeled classes and is particularly informative when false positives and false negatives are unevenly distributed.

• Cohen’s kappa quantifies agreement between predicted and reference labels while explicitly accounting for agreement expected by chance, making it well suited for comparisons between automated classifiers and human annotations.

• Matthews Correlation Coefficient (MCC) summarizes all elements of a confusion matrix into a single correlation statistic and remains robust under severe class imbalance, providing a balanced assessment of overall predictive performance.

Together, these metrics offer a complete and reliable evaluation. This script also includes the ability to assess community diversity.

• The Shannon–Wiener Index incorporates both richness and evenness, providing a sensitive measure of changes in relative abundance distributions and making it useful for detecting shifts in community composition.

• The Simpson’s Index of diversity emphasizes dominance and is less sensitive to rare taxa, offering a stable measure of whether classifications are disproportionately driven by common categories.

• The Chao1 Index estimates true species richness by accounting for unseen taxa based on the frequency of rare observations, making it particularly valuable in sparse or undersampled datasets.

Together, these indices provide a robust, multi-faceted characterization of community structure that complements classification accuracy metrics.

Running Script

To run this script, install Python 3 on your computer and make sure you have these extra Python packages installed: pandas, scikit-learn, and scipy (to install run ‘pip install pandas scikit-learn scipy’ in your python terminal if not previously installed). Once installed, follow instructions below to run the script.

1) Save the code below into a txt file ending in .py (for example, cpc_compare.py).

2) Prepare two folders for comparison:

a. The first containing your ‘Actual’ .cpc files.

b. The second containing your “Predicted” .cpc files

Note: Your Actual and Predicted folders should contain identical sets .cpc files, just with different annotations. Ex: Actual has been annotated by a human expert, Predicted by CoralNet

3) Open a terminal, go to the folder where you saved the script, and run it with python cpc_compare.py (or python3 cpc_compare.py).

4) A small window will appear: click Browse to select the Actual folder and the Predicted folder, then click Perform Analysis; the results (Accuracy, F1, MCC, Cohen’s Kappa, and diversity indices for each set) will appear in the big text box.

Requirements

Python 3.x

Libraries: numpy, pandas, scikit-learn, scipy, tkinter Install dependencies with:

Copy code: pip install numpy pandas scikit-learn scipy

Copy Script Below

```python
import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from sklearn.metrics import matthews_corrcoef, accuracy_score, f1_score, cohen_kappa_score
from scipy.stats import chisquare
import math

def get_cpc_filenames(directory):
    return [f for f in os.listdir(directory) if f.endswith('.cpc')]


def read_cpc(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    try:
        start_line = next(i for i, line in enumerate(lines) if line.startswith('"1"'))
        try:
            end_line = next(i for i, line in enumerate(lines) if line.startswith('"75"'))
        except StopIteration:
            end_line = next(i for i, line in enumerate(lines) if line.startswith('"50"'))
    except StopIteration:
        print(f"Could not find required lines in file: {file_path}")
        return None  # or raise an exception, or continue with an empty DataFrame

    annotation_lines = lines[start_line:end_line + 1]

    # Assuming the rest of your code for parsing the lines into a DataFrame remains the same
    data = []
    for line in annotation_lines:
        parts = line.strip().split(',')
        index, annotation, _, subcategory = parts
        data.append([index.strip('"'), annotation.strip('"'), subcategory.strip('"')])

    dt = pd.DataFrame(data, columns=['Index', 'Annotation', 'Subcategory'])
    dt['Index'] = dt['Index'].astype(int)

    return dt


def calculate_mcc(x, y):
    return matthews_corrcoef(x, y)

def shannon_wiener_index(series):
    total = len(series)
    value_counts = series.value_counts()
    sw_index = -sum((count / total) * math.log2(count / total) for count in value_counts)
    return sw_index

def simpsons_index(series):
    total = len(series)
    value_counts = series.value_counts()
    simpsons_index = 1 - sum((count / total) ** 2 for count in value_counts)
    return simpsons_index

def chao1_index(series):
    value_counts = series.value_counts()
    singletons = sum(value_counts == 1)
    doubletons = sum(value_counts == 2)
    if doubletons == 0:
        return len(value_counts)
    else:
        chao1 = len(value_counts) + ((singletons ** 2) / (2 * doubletons))
        return chao1

def perform_analysis():
    dir1 = dir1_var.get()  # Actual data
    dir2 = dir2_var.get()  # Predicted data

    files1 = get_cpc_filenames(dir1)
    files2 = get_cpc_filenames(dir2)

    # Debug print statements
    print(f"Number of files in Actual Data folder: {len(files1)}")
    print(f"Number of files in Predicted Data folder: {len(files2)}")

    output.delete(1.0, tk.END)

    aggregated_actual = pd.DataFrame(columns=['Index', 'Annotation', 'Notes', 'Subcategory'])
    aggregated_predicted = pd.DataFrame(columns=['Index', 'Annotation', 'Notes', 'Subcategory'])

    for filename in files1:
        file_path1 = os.path.join(dir1, filename)
        dt1 = read_cpc(file_path1)
        aggregated_actual = pd.concat([aggregated_actual, dt1], ignore_index=True)

    for filename in files2:
        file_path2 = os.path.join(dir2, filename)
        dt2 = read_cpc(file_path2)
        aggregated_predicted = pd.concat([aggregated_predicted, dt2], ignore_index=True)

    # More debug print statements
    print(f"Number of annotations in aggregated actual data: {len(aggregated_actual)}")
    print(f"Number of annotations in aggregated predicted data: {len(aggregated_predicted)}")

    x1 = aggregated_actual['Annotation']
    x2 = aggregated_predicted['Annotation']

    mcc = calculate_mcc(x1, x2)
    acc = accuracy_score(x1, x2)
    f1 = f1_score(x1, x2, average='weighted')
    ck = cohen_kappa_score(x1, x2)

    # Shannon-Wiener Index
    sw1 = shannon_wiener_index(x1)
    sw2 = shannon_wiener_index(x2)

    # Simpson's Index of Diversity
    simp1 = simpsons_index(x1)
    simp2 = simpsons_index(x2)

    # Chao1 Index
    chao1_1 = chao1_index(x1)
    chao1_2 = chao1_index(x2)

    output.insert(tk.END, f"Accuracy: {acc}\n")
    output.insert(tk.END, f"F1 Score: {f1}\n")
    output.insert(tk.END, f"Matthews Correlation Coefficient: {mcc}\n")
    output.insert(tk.END, f"Cohen's Kappa: {ck}\n")

    output.insert(tk.END, f"Actual Shannon-Wiener Index: {sw1}\n")
    output.insert(tk.END, f"Predicted Shannon-Wiener Index: {sw2}\n")
    output.insert(tk.END, f"Actual Simpsons Index: {simp1}\n")
    output.insert(tk.END, f"Predicted Simpson's Index: {simp2}\n")
    output.insert(tk.END, f"Actual Chao Index: {chao1_1}\n")
    output.insert(tk.END, f"Predicted Chao Index: {chao1_2}\n")

root = tk.Tk()
root.title("CPC File Comparison")

dir1_var = tk.StringVar()
dir2_var = tk.StringVar()

tk.Label(root, text="Select the folder for Actual Data:").pack()
tk.Button(root, text="Browse", command=lambda: dir1_var.set(filedialog.askdirectory())).pack()
tk.Label(root, text="Select the folder for Predicted Data:").pack()
tk.Button(root, text="Browse", command=lambda: dir2_var.set(filedialog.askdirectory())).pack()

tk.Button(root, text="Perform Analysis", command=perform_analysis).pack()

output = tk.Text(root, height=20, width=100)
output.pack()

root.mainloop()
```

Validation

The statistical models used in this script are from the ~sklearn python library.

For extra verification, create or modify 2 cpce files to consist of the following annotations Table 1. Run the CPCe Comparison Tool and the results should be Table 2.

Table 1: Test Label Dataset for Validation of statistical tools.

Table 2: Accuracy, F1, MCC, Cohens Kappa, Shannons Index, Simpsons Index, Chao Index determined from example above

Statistical Measures

Output

Accuracy

.78

F1

.82669

MCC

.68407

Cohens Kappa

.67456

Ecological Measures

Actual

Predicted

Shannons

1.7942

2.1782

Simpsons

0.6248

0.7112

Chao

20.5

8

Tool 2: Random File Selector

Background

The Random File Selector tool is a python script to streamline the selection of random .cpc files from a folder to create random replicates. This tool is specifically designed to enhance the efficiency and objectivity of data sampling for coral reef studies. Randomization is essential to ensure that the selection of files for analysis is free from human bias and representative of the entire dataset, thereby enhancing the validity and reliability of subsequent statistical analyses. By automating this process, the tool ensures that the data sampling accurately reflects the true variability within the dataset, a necessary step for robust ecological assessments and unbiased comparisons. The core functionality involves selecting a specified percentage of .cpc files randomly from a given source directory and copying them to a target directory. Users can choose from predefined percentages for file selection, such as 3%, 5%, 10%, up to 100%, allowing flexibility in sampling intensity based on specific research questions. Once the user selects the source and target folders and the desired percentage, the script then randomly selects the appropriate number of files and copies them to the target directory.

Running Script

To run this script, install Python 3 on your computer and make sure you have these extra Python packages installed: pandas, scikit-learn, and scipy (to install run ‘pip install pandas scikit-learn scipy’ in your python terminal if not previously installed). Once installed, follow instructions below to run the script

5) Save the code into a file ending in .py (for example, cpc_compare.py).

6) Open a terminal, go to the folder where you saved the script, and run it with python cpc_compare.py (or python3 cpc_compare.py).

7) A small window will appear: Select the Source Folder you wish to randomly select from. Select the Target Folder you wish to copy to. Then select the percentage of files you would like to copy and click ‘Copy Files’, your files will be copied to your target folder

Requirements

Python 3.x

```python
import os
import random
import shutil
import tkinter as tk
from tkinter import filedialog

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # Set the window title and geometry
        self.title("Random File Selector")
        self.geometry("800x600")

        # Set the font
        self.font = ("TkDefaultFont", 12)

        # Create the title label
        self.title_label = tk.Label(self, text="Random File Selector", font=("TkDefaultFont", 24, "bold"))
        self.title_label.pack(pady=20)

        # Create the source folder selection button and label
        self.source_label = tk.Label(self, text="Source Folder:", font=self.font)
        self.source_label.pack(padx=20, pady=10, anchor="w")
        self.source_button = tk.Button(self, text="Select", command=self.select_source_folder)
        self.source_button.pack(padx=20, pady=10, anchor="w")
        self.source_path_label = tk.Label(self, text="", font=self.font)
        self.source_path_label.pack(padx=20, pady=10, anchor="w")

        # Create the target folder selection button and label
        self.target_label = tk.Label(self, text="Target Folder:", font=self.font)
        self.target_label.pack(padx=20, pady=10, anchor="w")
        self.target_button = tk.Button(self, text="Select", command=self.select_target_folder)
        self.target_button.pack(padx=20, pady=10, anchor="w")
        self.target_path_label = tk.Label(self, text="", font=self.font)
        self.target_path_label.pack(padx=20, pady=10, anchor="w")

        # Create the percentage dropdown and label
        self.percentage_label = tk.Label(self, text="Percentage to Copy:", font=self.font)
        self.percentage_label.pack(padx=20, pady=10, anchor="w")
        self.percentage_var = tk.StringVar()
        self.percentage_dropdown = tk.OptionMenu(self, self.percentage_var, "3%", "5%", "10%", "20%", "40%", "60%", "80%", "90%", "100%")
        self.percentage_dropdown.pack(padx=20, pady=10, anchor="w")

        # Create the copy button
        self.copy_button = tk.Button(self, text="Copy Files", command=self.copy_files)
        self.copy_button.pack(padx=20, pady=10)

        # Initialize the source and target folder paths
        self.source_path = ""
        self.target_path = ""

    def select_source_folder(self):
        # Open the file dialog to select the source folder
        self.source_path = filedialog.askdirectory()
        self.source_path_label.config(text=self.source_path)

    def select_target_folder(self):
        # Open the file dialog to select the target folder
        self.target_path = filedialog.askdirectory()
        self.target_path_label.config(text=self.target_path)

    def copy_files(self):
        if not self.source_path or not self.target_path:
            # Display an error message if the source or target folder is not selected
            tk.messagebox.showerror("Error", "Please select both source and target folders")
            return

        # Get the selected percentage from the dropdown and calculate the number of files to copy
        percentage = self.percentage_var.get()
        if percentage == "3%":
            num_files_to_copy = int(len(os.listdir(self.source_path)) * 0.03 + 0.5)
        elif percentage == "5%":
            num_files_to_copy = int(len(os.listdir(self.source_path)) * 0.05 + 0.5)
        elif percentage == "10%":
            num_files_to_copy = int(len(os.listdir(self.source_path)) * 0.1 + 0.5)
        elif percentage == "20%":
            num_files_to_copy = int(len(os.listdir(self.source_path)) * 0.2 + 0.5)
        elif percentage == "40%":
            num_files_to_copy = int(len(os.listdir(self.source_path)) * 0.4 + 0.5)
        elif percentage == "60%":
            num_files_to_copy = int(len(os.listdir(self.source_path)) * 0.6 + 0.5)
        elif percentage == "80%":
            num_files_to_copy = int(len(os.listdir(self.source_path)) * 0.8 + 0.5)
        elif percentage == "90%":
            num_files_to_copy = int(len(os.listdir(self.source_path)) * 0.9 + 0.5)
        elif percentage == "100%":
            num_files_to_copy = int(len(os.listdir(self.source_path)) * 1.0 + 0.5)
        else:
            # Set the number of files to copy to 0 if the percentage is not valid
            num_files_to_copy = 0

        # Randomly select the files to copy
        files_to_copy = random.sample(os.listdir(self.source_path), num_files_to_copy)

        # Copy the selected files to the target folder
        for filename in files_to_copy:
            source_path = os.path.join(self.source_path, filename)
            target_path = os.path.join(self.target_path, filename)
            shutil.copy(source_path, target_path)

        # Display a success message
        tk.messagebox.showinfo("Success", "Files copied successfully")

if __name__ == "__main__":
    app = App()
    app.mainloop()
```

Validation

The statistical models used in this script are from the  ~sklearn python library.
