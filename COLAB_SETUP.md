# Google Colab Setup Guide

## Using Urban Energy Analytics with Google Colab

This project is fully compatible with Google Colab. Follow these steps to run the analysis in the cloud:

### Option 1: From GitHub

1. **Clone the repo in Colab:**
   ```python
   !git clone https://github.com/YOUR_ORG/Urban-Energy-Analytics.git
   %cd Urban-Energy-Analytics
   ```

2. **Install dependencies:**
   ```python
   !pip install -r requirements.txt
   ```

3. **Open the notebook:**
   - Upload `notebooks/urban_energy_analysis.ipynb` to Google Drive
   - Open with Google Colab
   - Or run directly in Colab:
     ```python
     exec(open('notebooks/urban_energy_analysis.ipynb').read())
     ```

### Option 2: From Google Drive

1. **Upload to Google Drive:**
   - Create a folder `Urban-Energy-Analytics` in Google Drive
   - Upload the entire project

2. **In Colab, mount Drive and navigate:**
   ```python
   from google.colab import drive
   drive.mount('/content/drive')
   %cd '/content/drive/My Drive/Urban-Energy-Analytics'
   ```

3. **Install dependencies:**
   ```python
   !pip install -r requirements.txt
   ```

4. **Run the notebook:**
   - Open `notebooks/urban_energy_analysis.ipynb` directly or
   - Execute cells in a new notebook with imports from the src/ modules

### Option 3: Upload Notebook Directly

1. **In Colab, create a new notebook**

2. **In the first cell, run:**
   ```python
   # Mount Google Drive
   from google.colab import drive
   drive.mount('/content/drive')
   
   # Navigate to project (or upload project)
   import os
   !mkdir -p /content/urban_energy
   %cd /content/urban_energy
   
   # Download datasets (if from a remote source)
   # OR copy from Google Drive
   
   # Install dependencies
   !pip install pandas numpy scikit-learn matplotlib seaborn scipy jupyter ipython
   ```

3. **Copy the remaining notebook cells from `urban_energy_analysis.ipynb`**

### Why Google Colab Works Well

- ✅ **No setup needed:** Pre-installed Python, Jupyter, most packages
- ✅ **Free GPU (optional):** Select Runtime → Change runtime type → GPU
- ✅ **Cloud storage:** Easily access files from Google Drive
- ✅ **Collaborative:** Share notebooks with team members
- ✅ **Reproducible:** Same environment for everyone

### Tips for Colab

1. **Increase cell output:** Uncomment in Setup section if needed
2. **Save plots:** Add `plt.savefig()` before `plt.show()` to save to Drive
3. **Export results:** Use `df.to_csv()` to save DataFrames to Drive
4. **Runtime limits:** Colab sessions timeout after ~12 hours; save progress

### Troubleshooting

**Issue:** `ModuleNotFoundError: No module named 'src'`
- **Solution:** Ensure `src/` folder is in the working directory, or:
  ```python
  import sys
  sys.path.insert(0, '/path/to/src')
  ```

**Issue:** Data files not found
- **Solution:** Copy `data/raw/` files to Colab environment or update file paths

**Issue:** Plots not displaying
- **Solution:** Add `%matplotlib inline` in first code cell

---

## Example: Full Colab Workflow

```python
# Cell 1: Setup
!git clone https://github.com/YOUR_ORG/Urban-Energy-Analytics.git
%cd Urban-Energy-Analytics
!pip install -r requirements.txt

# Cell 2: Imports
import sys
sys.path.insert(0, 'src')
from data_loader import load_eia_data, load_acs_data
# ... (continue with notebook cells)
```

For more help, see the main README.md or run locally with:
```bash
jupyter notebook notebooks/urban_energy_analysis.ipynb
```
