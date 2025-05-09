import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
import matplotlib.pyplot as plt


# Load the dataset
file_path = “”
df = pd.read_excel(file_path)


# Convert Date column to datetime
df['Date'] = pd.to_datetime(df['Date'])


# Step 1: Filter for peak hours (17–20), calculate daily avg DA_LMP
df_peak = df[df['Hr_End'].between(17, 20)].groupby(['Date', 'zone', 'treated', 'post'])['DA_LMP'].mean().reset_index()
df_peak.rename(columns={'DA_LMP': 'avg_price'}, inplace=True)


# Identify treated zone
treated_zone = df_peak[df_peak['treated'] == 1]['zone'].unique()[0]


# Step 2: Create synthetic control for the treated zone
pre_data = df_peak[df_peak['post'] == 0]
X_controls = pre_data[pre_data['treated'] == 0].pivot(index='Date', columns='zone', values='avg_price')
y_treated = pre_data[pre_data['treated'] == 1].pivot(index='Date', columns='zone', values='avg_price').iloc[:, 0]


# Fit Ridge regression model
model = Ridge(alpha=1.0, fit_intercept=False)
model.fit(X_controls, y_treated)
weights = model.coef_


# Apply weights to all periods
X_full = df_peak[df_peak['treated'] == 0].pivot(index='Date', columns='zone', values='avg_price')
X_full = X_full[X_controls.columns]
synthetic = X_full @ weights
actual = df_peak[df_peak['treated'] == 1].set_index('Date')['avg_price']


# Step 3: Compute treatment effect (actual - synthetic)
result_df = actual.to_frame(name='actual')
result_df['synthetic'] = synthetic
result_df['gap'] = result_df['actual'] - result_df['synthetic']
result_df['post'] = result_df.index >= pd.Timestamp('2022-05-01')
avg_effect = result_df[result_df['post']]['gap'].mean()


# Step 4: Plot actual vs synthetic
plt.figure(figsize=(12, 6))
plt.plot(result_df.index, result_df['actual'], label="Actual (Treated Zone)", linewidth=2)
plt.plot(result_df.index, result_df['synthetic'], label="Synthetic Control", linestyle='--', linewidth=2)
plt.axvline(x=pd.Timestamp('2022-05-01'), color='gray', linestyle=':', label='Policy Start (May 2022)')
plt.title("Synthetic Control (Peak Hours 16–19 Avg Price)")
plt.ylabel("DA_LMP ($/MWh)")
plt.xlabel("Date")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()


# Step 5: Plot the treatment effect (gap)
plt.figure(figsize=(12, 5))
plt.plot(result_df.index, result_df['gap'], label='Treatment Effect (Actual - Synthetic)', color='crimson')
plt.axvline(x=pd.Timestamp('2022-05-01'), color='gray', linestyle=':', label='Policy Start')
plt.axhline(0, color='black', linestyle='--')
plt.title('Estimated Treatment Effect on DA_LMP (Peak Hours)')
plt.xlabel('Date')
plt.ylabel('Price Gap ($/MWh)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()


# Step 6: Placebo tests — run synthetic control for each control zone
control_zones = df_peak[df_peak['treated'] == 0]['zone'].unique()
post_policy_start = pd.Timestamp('2022-05-01')
pseudo_gaps = []


for zone in control_zones:
   try:
       # Create placebo outcome
       y_placebo = pre_data[pre_data['zone'] == zone].pivot(index='Date', columns='zone', values='avg_price').iloc[:, 0]


       # Donor pool excludes this placebo zone
       donor_data = pre_data[(pre_data['zone'] != zone) & (pre_data['treated'] == 0)]
       X_donors = donor_data.pivot(index='Date', columns='zone', values='avg_price')


       if X_donors.shape[1] < 2:
           continue  # skip if not enough donor zones


       # Fit synthetic model for placebo
       model_placebo = Ridge(alpha=1.0, fit_intercept=False)
       model_placebo.fit(X_donors, y_placebo)
       weights_placebo = model_placebo.coef_


       # Apply to full period
       full_donor = df_peak[df_peak['zone'].isin(X_donors.columns)].pivot(index='Date', columns='zone', values='avg_price')
       full_donor = full_donor[X_donors.columns]
       synth_placebo = full_donor @ weights_placebo


       # Actual placebo zone price
       actual_placebo = df_peak[df_peak['zone'] == zone].set_index('Date')['avg_price']


       # Calculate gap
       gap_placebo = actual_placebo - synth_placebo
       pseudo_avg_gap = gap_placebo[gap_placebo.index >= post_policy_start].mean()
       pseudo_gaps.append(pseudo_avg_gap)


   except Exception as e:
       print(f"Skipped {zone} due to error: {e}")
       continue


# Step 7: Calculate pseudo p-value
pseudo_gaps = np.array(pseudo_gaps)
treated_effect = avg_effect
p_value = (np.sum(np.abs(pseudo_gaps) >= np.abs(treated_effect)) + 1) / (len(pseudo_gaps) + 1)


# Final output
print(f"Average Treatment Effect: {treated_effect:.2f} $/MWh")
print(f"Pseudo P-Value: {p_value:.3f}")
