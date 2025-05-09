import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
import statsmodels.api as sm
import statsmodels.formula.api as smf
from linearmodels.panel import PanelOLS, PooledOLS
from linearmodels.panel import RandomEffects

# Suppress pandas warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Create results directory
RESULTS_DIR = Path("riya_results_panel")
RESULTS_DIR.mkdir(exist_ok=True)

# Set visualization style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("deep")
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman']
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10

print("\n" + "="*80)
print("NYISO DIFFERENCE-IN-DIFFERENCES ANALYSIS WITH PANEL REGRESSION")
print("="*80 + "\n")

# Load DiD database that includes control variables
print("Loading DiD database with control variables...")
df = pd.read_excel("DiD database_including weather.xlsx")
print(f"Data loaded: {df.shape[0]} rows, {df.shape[1]} columns")

# Display column names
print("\nColumn Names:")
for i, col in enumerate(df.columns):
    print(f"Column {i}: {col}")

# Check unique zones
print("\nUnique values in Zone column:")
print(df['zone'].unique())

# Prepare data for panel regression
print("\nPreparing data for panel regression...")

# Rename column with spaces for easier handling in formulas
df = df.rename(columns={'natural gas price': 'natural_gas_price'})

# Create a panel ID that's unique for each zone
df['panel_id'] = df['zone']

# Ensure date is in proper datetime format
df['date'] = pd.to_datetime(df['month'])
df['year'] = df['date'].dt.year
df['month_num'] = df['date'].dt.month

# Create variables for time effects
df['year_cat'] = df['year'].astype('category')
df['month_cat'] = df['month_num'].astype('category')

# Create a numeric time index for the panel data
df['time_id'] = pd.factorize(df['date'].dt.strftime('%Y-%m'))[0]

# Log transform prices to handle skewness
df['log_price'] = np.log(df['avg_price'].clip(lower=1))  # Clip to avoid negative values in log

# Create the DiD interaction term
df['did'] = df['treated'] * df['post']

# Count observations in each group
pre_control = ((df['post'] == 0) & (df['treated'] == 0)).sum()
pre_treatment = ((df['post'] == 0) & (df['treated'] == 1)).sum()
post_control = ((df['post'] == 1) & (df['treated'] == 0)).sum()
post_treatment = ((df['post'] == 1) & (df['treated'] == 1)).sum()

print("\nObservations in each group:")
print(f"Pre-treatment, Control (Zone NE & Zone C): {pre_control}")
print(f"Pre-treatment, Treatment (Zone F): {pre_treatment}")
print(f"Post-treatment, Control (Zone NE & Zone C): {post_control}")
print(f"Post-treatment, Treatment (Zone F): {post_treatment}")

# Filter to only include Zone F and Zone C
df_fc = df[df['zone'].isin(['Zone F', 'Zone C'])].copy()
print(f"\nFiltered to Zone F vs Zone C: {len(df_fc)} observations")

# Save prepared data
df.to_csv(RESULTS_DIR / "panel_data_all.csv", index=False)
df_fc.to_csv(RESULTS_DIR / "panel_data_fc.csv", index=False)
print(f"Saved panel data to {RESULTS_DIR}")

# Set up panel data format for linearmodels package
panel_data = df.set_index(['panel_id', 'time_id'])

# Check if the data is properly formatted
print("\nPanel data dimensions:")
print(f"Number of entities (zones): {panel_data.index.get_level_values(0).nunique()}")
print(f"Number of time periods: {panel_data.index.get_level_values(1).nunique()}")

print("\nRunning panel data regression models...")

# Create dummy variables for month and year (time fixed effects)
time_dummies = pd.get_dummies(panel_data['year'], prefix='year', drop_first=True)
month_dummies = pd.get_dummies(panel_data['month_num'], prefix='month', drop_first=True)

# Dependent variables
y_price = panel_data['avg_price']
y_log_price = panel_data['log_price']

# List of models to run - we'll try different specifications
models = []
model_names = []
results = []

# Run panel regression models on the full dataset (all zones)
print("\n==== Models using all zones (F vs C and NE) ====")

# MODEL 1: Pooled OLS (no fixed effects)
print("\nRunning Pooled OLS model...")
X_pooled = sm.add_constant(panel_data[['treated', 'post', 'did']])
model_pooled = PooledOLS(y_price, X_pooled)
result_pooled = model_pooled.fit(cov_type='robust')
models.append(model_pooled)
model_names.append("Pooled OLS")
results.append(result_pooled)
print(result_pooled)

# MODEL 2: Pooled OLS with controls
print("\nRunning Pooled OLS model with controls...")
X_pooled_ctrls = sm.add_constant(panel_data[['treated', 'post', 'did', 'load', 'natural_gas_price', 'weather']])
model_pooled_ctrls = PooledOLS(y_price, X_pooled_ctrls)
result_pooled_ctrls = model_pooled_ctrls.fit(cov_type='robust')
models.append(model_pooled_ctrls)
model_names.append("Pooled OLS with Controls")
results.append(result_pooled_ctrls)
print(result_pooled_ctrls)

# MODEL 3: Entity fixed effects with two-ways
print("\nRunning Entity Fixed Effects model...")
X_entity_fe = sm.add_constant(panel_data[['post', 'did']])  # No need for 'treated' as it's captured by entity FE
model_entity_fe = PanelOLS(y_price, X_entity_fe, entity_effects=True)
result_entity_fe = model_entity_fe.fit(cov_type='robust')
models.append(model_entity_fe)
model_names.append("Entity FE")
results.append(result_entity_fe)
print(result_entity_fe)

# MODEL 4: Entity fixed effects with controls
print("\nRunning Entity Fixed Effects model with controls...")
X_entity_fe_ctrls = sm.add_constant(panel_data[['post', 'did', 'load', 'natural_gas_price', 'weather']])
model_entity_fe_ctrls = PanelOLS(y_price, X_entity_fe_ctrls, entity_effects=True)
result_entity_fe_ctrls = model_entity_fe_ctrls.fit(cov_type='robust')
models.append(model_entity_fe_ctrls)
model_names.append("Entity FE with Controls")
results.append(result_entity_fe_ctrls)
print(result_entity_fe_ctrls)

# MODEL 5: Entity and time fixed effects (two-way FE)
print("\nRunning Two-way Fixed Effects model...")
X_two_way_fe = sm.add_constant(panel_data[['did']])  # Both 'treated' and 'post' captured by the FEs
model_two_way_fe = PanelOLS(y_price, X_two_way_fe, entity_effects=True, time_effects=True)
result_two_way_fe = model_two_way_fe.fit(cov_type='robust')
models.append(model_two_way_fe)
model_names.append("Two-way FE")
results.append(result_two_way_fe)
print(result_two_way_fe)

# MODEL 6: Two-way fixed effects with controls
print("\nRunning Two-way Fixed Effects model with controls...")
X_two_way_fe_ctrls = sm.add_constant(panel_data[['did', 'load', 'natural_gas_price', 'weather']])
model_two_way_fe_ctrls = PanelOLS(y_price, X_two_way_fe_ctrls, entity_effects=True, time_effects=True)
result_two_way_fe_ctrls = model_two_way_fe_ctrls.fit(cov_type='robust')
models.append(model_two_way_fe_ctrls)
model_names.append("Two-way FE with Controls")
results.append(result_two_way_fe_ctrls)
print(result_two_way_fe_ctrls)

# MODEL 7: Log price with two-way fixed effects
print("\nRunning Log Price Two-way Fixed Effects model...")
log_model_two_way_fe = PanelOLS(y_log_price, X_two_way_fe, entity_effects=True, time_effects=True)
log_result_two_way_fe = log_model_two_way_fe.fit(cov_type='robust')
models.append(log_model_two_way_fe)
model_names.append("Log Two-way FE")
results.append(log_result_two_way_fe)
print(log_result_two_way_fe)

# MODEL 8: Log price with two-way fixed effects and controls
print("\nRunning Log Price Two-way Fixed Effects model with controls...")
log_model_two_way_fe_ctrls = PanelOLS(y_log_price, X_two_way_fe_ctrls, entity_effects=True, time_effects=True)
log_result_two_way_fe_ctrls = log_model_two_way_fe_ctrls.fit(cov_type='robust')
models.append(log_model_two_way_fe_ctrls)
model_names.append("Log Two-way FE with Controls")
results.append(log_result_two_way_fe_ctrls)
print(log_result_two_way_fe_ctrls)

# Now let's run the same models but specifically for Zone F vs Zone C
print("\n==== Models using only Zone F vs Zone C ====")

# Set up panel data for Zone F vs Zone C
panel_data_fc = df_fc.set_index(['panel_id', 'time_id'])
y_price_fc = panel_data_fc['avg_price']
y_log_price_fc = panel_data_fc['log_price']

# MODEL 9: Zone F vs C - Two-way fixed effects
print("\nRunning Two-way Fixed Effects model (Zone F vs C)...")
X_fc_two_way_fe = sm.add_constant(panel_data_fc[['did']])
model_fc_two_way_fe = PanelOLS(y_price_fc, X_fc_two_way_fe, entity_effects=True, time_effects=True)
result_fc_two_way_fe = model_fc_two_way_fe.fit(cov_type='robust')
models.append(model_fc_two_way_fe)
model_names.append("F vs C Two-way FE")
results.append(result_fc_two_way_fe)
print(result_fc_two_way_fe)

# MODEL 10: Zone F vs C - Two-way fixed effects with controls
print("\nRunning Two-way Fixed Effects model with controls (Zone F vs C)...")
X_fc_two_way_fe_ctrls = sm.add_constant(panel_data_fc[['did', 'load', 'natural_gas_price', 'weather']])
model_fc_two_way_fe_ctrls = PanelOLS(y_price_fc, X_fc_two_way_fe_ctrls, entity_effects=True, time_effects=True)
result_fc_two_way_fe_ctrls = model_fc_two_way_fe_ctrls.fit(cov_type='robust')
models.append(model_fc_two_way_fe_ctrls)
model_names.append("F vs C Two-way FE with Controls")
results.append(result_fc_two_way_fe_ctrls)
print(result_fc_two_way_fe_ctrls)

# MODEL 11: Zone F vs C - Log price with two-way fixed effects
print("\nRunning Log Price Two-way Fixed Effects model (Zone F vs C)...")
log_model_fc_two_way_fe = PanelOLS(y_log_price_fc, X_fc_two_way_fe, entity_effects=True, time_effects=True)
log_result_fc_two_way_fe = log_model_fc_two_way_fe.fit(cov_type='robust')
models.append(log_model_fc_two_way_fe)
model_names.append("F vs C Log Two-way FE")
results.append(log_result_fc_two_way_fe)
print(log_result_fc_two_way_fe)

# MODEL 12: Zone F vs C - Log price with two-way fixed effects and controls
print("\nRunning Log Price Two-way Fixed Effects model with controls (Zone F vs C)...")
log_model_fc_two_way_fe_ctrls = PanelOLS(y_log_price_fc, X_fc_two_way_fe_ctrls, entity_effects=True, time_effects=True)
log_result_fc_two_way_fe_ctrls = log_model_fc_two_way_fe_ctrls.fit(cov_type='robust')
models.append(log_model_fc_two_way_fe_ctrls)
model_names.append("F vs C Log Two-way FE with Controls")
results.append(log_result_fc_two_way_fe_ctrls)
print(log_result_fc_two_way_fe_ctrls)

# Save regression results
print("\nSaving regression results...")
with open(RESULTS_DIR / "panel_regression_results.txt", "w") as f:
    f.write("DIFFERENCE-IN-DIFFERENCES ANALYSIS WITH PANEL REGRESSION\n")
    f.write("="*80 + "\n\n")
    
    for name, result in zip(model_names, results):
        f.write(f"{name} MODEL\n")
        f.write("-"*80 + "\n")
        f.write(str(result))
        f.write("\n\n")

# Extract DiD coefficients and p-values for comparison
did_coefs = []
p_values = []
r_squared = []

for result in results:
    # Extract coefficient for 'did' - index might vary between models
    param_names = result.params.index.tolist()
    if 'did' in param_names:
        did_idx = param_names.index('did')
        did_coefs.append(result.params[did_idx])
        p_values.append(result.pvalues[did_idx])
    else:
        # For some models, 'did' might be at a different position
        did_coefs.append(result.params.iloc[-1])  # Generally the last parameter
        p_values.append(result.pvalues.iloc[-1])
    
    # Get R-squared
    r_squared.append(result.rsquared)

# Create a DataFrame for model comparison
model_comparison = pd.DataFrame({
    'Model': model_names,
    'DiD Coefficient': did_coefs,
    'P-value': p_values,
    'R-squared': r_squared,
    'Significant': [p < 0.05 for p in p_values]
})

print("\nModel Comparison:")
print(model_comparison)

# Create visualizations
print("\nCreating visualizations...")

# 1. DiD coefficient comparison across models
plt.figure(figsize=(12, 8))
colors = ['blue' if sig else 'gray' for sig in model_comparison['Significant']]
y_pos = np.arange(len(model_names))

plt.barh(y_pos, model_comparison['DiD Coefficient'], color=colors, alpha=0.7)
plt.axvline(x=0, color='red', linestyle='--', alpha=0.7)
plt.yticks(y_pos, model_names)
plt.xlabel('DiD Coefficient Estimate')
plt.title('DiD Coefficient Comparison Across Panel Models')
plt.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig(RESULTS_DIR / "did_coefficient_comparison.png", dpi=300, bbox_inches='tight')
plt.close()

# 2. Price trends over time by treatment status
plt.figure(figsize=(12, 6))
# Group by actual date instead of time_id
df['year_month'] = df['date'].dt.strftime('%Y-%m')
avg_by_group = df.groupby(['year_month', 'treated'])['avg_price'].mean().reset_index()
avg_by_group['treatment_label'] = avg_by_group['treated'].map({1: 'Treatment (Zone F)', 0: 'Control'})
avg_by_group['month'] = pd.to_datetime(avg_by_group['year_month'])
avg_by_group = avg_by_group.sort_values('month')

treatment_date = df[df['post'] == 1]['date'].min()

plt.plot(avg_by_group[avg_by_group['treated']==1]['month'], 
         avg_by_group[avg_by_group['treated']==1]['avg_price'], 
         'b-', label='Treatment (Zone F)', marker='o')
plt.plot(avg_by_group[avg_by_group['treated']==0]['month'], 
         avg_by_group[avg_by_group['treated']==0]['avg_price'], 
         'r-', label='Control', marker='s')
plt.axvline(x=treatment_date, color='green', linestyle='--', 
           linewidth=2, label='Treatment Date')
plt.title('Average Price by Group Over Time')
plt.xlabel('Month')
plt.ylabel('Average Price')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(RESULTS_DIR / "price_trends.png", dpi=300, bbox_inches='tight')
plt.close()

# 3. Price trends over time specifically for Zone F vs Zone C
plt.figure(figsize=(12, 6))
df_fc['year_month'] = df_fc['date'].dt.strftime('%Y-%m')
avg_by_group_fc = df_fc.groupby(['year_month', 'zone'])['avg_price'].mean().reset_index()
avg_by_group_fc['month'] = pd.to_datetime(avg_by_group_fc['year_month'])
avg_by_group_fc = avg_by_group_fc.sort_values('month')

plt.plot(avg_by_group_fc[avg_by_group_fc['zone']=='Zone F']['month'], 
         avg_by_group_fc[avg_by_group_fc['zone']=='Zone F']['avg_price'], 
         'b-', label='Zone F', marker='o')
plt.plot(avg_by_group_fc[avg_by_group_fc['zone']=='Zone C']['month'], 
         avg_by_group_fc[avg_by_group_fc['zone']=='Zone C']['avg_price'], 
         'g-', label='Zone C', marker='s')
plt.axvline(x=treatment_date, color='red', linestyle='--', 
           linewidth=2, label='Treatment Date')
plt.title('Average Price: Zone F vs Zone C')
plt.xlabel('Month')
plt.ylabel('Average Price')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(RESULTS_DIR / "price_trends_F_vs_C.png", dpi=300, bbox_inches='tight')
plt.close()

# 4. Control variable trends
control_vars = ['load', 'natural_gas_price', 'weather']
for control_var in control_vars:
    plt.figure(figsize=(12, 6))
    avg_control = df.groupby(['year_month'])[control_var].mean().reset_index()
    avg_control['month'] = pd.to_datetime(avg_control['year_month'])
    avg_control = avg_control.sort_values('month')
    
    plt.plot(avg_control['month'], avg_control[control_var], 'b-', marker='o')
    plt.axvline(x=treatment_date, color='green', linestyle='--', 
               linewidth=2, label='Treatment Date')
    plt.title(f'{control_var.replace("_", " ")} Over Time')
    plt.xlabel('Month')
    plt.ylabel(control_var.replace("_", " "))
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / f"{control_var}_trend.png", dpi=300, bbox_inches='tight')
    plt.close()

# Create a summary file
print("\nCreating analysis summary...")
with open(RESULTS_DIR / "panel_analysis_summary.txt", "w") as f:
    f.write("NYISO DIFFERENCE-IN-DIFFERENCES ANALYSIS WITH PANEL REGRESSION\n")
    f.write("="*50 + "\n\n")
    f.write(f"Total observations: {len(df)}\n")
    f.write(f"Control variables: load, natural gas price, weather\n")
    f.write(f"Treatment group: Zone F\n")
    f.write(f"Control group for full models: Zone NE and Zone C\n")
    f.write(f"Additional models comparing Zone F vs Zone C only\n")
    f.write(f"Post-treatment period begins: {treatment_date}\n\n")
    
    f.write("GROUP SIZES\n")
    f.write("-"*50 + "\n")
    f.write(f"Pre-treatment, Control: {pre_control}\n")
    f.write(f"Pre-treatment, Treatment (Zone F): {pre_treatment}\n")
    f.write(f"Post-treatment, Control: {post_control}\n")
    f.write(f"Post-treatment, Treatment (Zone F): {post_treatment}\n\n")
    
    f.write("MODEL COMPARISON\n")
    f.write("-"*50 + "\n")
    f.write(model_comparison.to_string(index=False))
    f.write("\n\n")
    
    f.write("INTERPRETATION\n")
    f.write("-"*50 + "\n")
    best_model_idx = np.argmax(r_squared)
    best_model_name = model_names[best_model_idx]
    
    f.write(f"Best-fitting model based on R-squared: {best_model_name} (R² = {r_squared[best_model_idx]:.4f})\n\n")
    
    f.write(f"DiD coefficient in best model: {did_coefs[best_model_idx]:.4f}\n")
    f.write(f"P-value: {p_values[best_model_idx]:.4f}\n\n")
    
    if p_values[best_model_idx] < 0.05:
        f.write("The DiD coefficient is statistically significant (p < 0.05).\n")
        if did_coefs[best_model_idx] > 0:
            f.write("This suggests that the policy change led to a significant price increase in Zone F relative to the control zones.\n")
        else:
            f.write("This suggests that the policy change led to a significant price decrease in Zone F relative to the control zones.\n")
    else:
        f.write("The DiD coefficient is not statistically significant (p >= 0.05).\n")
        f.write("This suggests no significant difference in how the policy change affected Zone F compared to the control zones.\n")
    
    f.write("\nKEY FINDINGS\n")
    f.write("-"*50 + "\n")
    f.write("1. Panel regression with two-way fixed effects provides a robust estimation of the policy effect\n")
    f.write("2. Including both entity and time fixed effects controls for unobserved heterogeneity\n")
    f.write("3. The most reliable models are those with two-way fixed effects and controls\n")
    
    # Compare results from different model groups
    f.write("\nCOMPARISON OF DIFFERENT MODEL SPECIFICATIONS\n")
    f.write("-"*50 + "\n")
    f.write("Pooled vs Fixed Effects: ")
    if abs(did_coefs[0] - did_coefs[4]) > 5:
        f.write("Large differences between pooled and FE models suggest important unobserved heterogeneity\n")
    else:
        f.write("Similar results between pooled and FE models suggest limited unobserved heterogeneity\n")
        
    f.write("\nAll zones vs F-C only: ")
    if abs(did_coefs[5] - did_coefs[9]) > 5:
        f.write("Different results when using only Zone C as control suggest heterogeneous policy effects\n")
    else:
        f.write("Similar results regardless of control group composition suggest robust policy effects\n")
        
    f.write("\nLog vs Linear models: ")
    if (did_coefs[5] > 0 and did_coefs[7] < 0) or (did_coefs[5] < 0 and did_coefs[7] > 0):
        f.write("Log and linear models show different signs, suggesting sensitivity to extreme values\n")
    else:
        f.write("Log and linear models show consistent direction, suggesting robust results\n")

print("\n" + "="*80)
print("Panel regression analysis complete! Results saved in the 'riya_results_panel' directory.")
print("="*80 + "\n")