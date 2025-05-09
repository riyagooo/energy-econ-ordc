# NYISO Enhanced Scarcity Pricing Policy: Impacts on Consumer Prices

## Project Overview
This repository contains analysis and results from our study examining the impact of NYISO's Enhanced Scarcity Pricing Policy on electricity prices. The policy, implemented in May 2022, involves a revamped Operating Reserve Demand Curve (ORDC) designed to increase day-ahead energy prices during stressed conditions to encourage resource availability.

## Key Findings
Our analysis shows that the ORDC revamp led to higher prices during:
- Peak hours (+7.24 $/MWh, p=0.006)
- Volatile market conditions (+23.68 $/MWh, p=0.016)

## Methodology
We applied two primary analytical approaches:
1. **Difference-in-Differences (DiD)** analysis comparing NYISO Zone F (treated) with Zone C and ISO-NE (controls)
2. **Synthetic Control** method to construct a counterfactual for Zone F prices

## Repository Structure

```
├── code/                      # Analysis scripts
│   ├── nyiso_panel_regression.py  # Panel regression analysis
│   └── Synthetic_control.py       # Synthetic control methodology
│
├── data/                      # Input datasets
│   ├── NYISO Price Data.xlsx
│   ├── DiD database_0422.xlsx
│   ├── DiD database_including weather.xlsx
│   └── Sythetic control regression database.xlsx
│
├── results/                   # Analysis outputs
│   └── panel_results/         # Panel regression outputs
│       ├── panel_treatment_effects.png
│       ├── panel_analysis_summary.txt
│       └── ... (other result files)
│
├── paper/                     # Final academic paper
│   └── INAFU6065FinalPaperNYISO-ORDC.pdf
│
├── requirements.txt           # Project dependencies
├── LICENSE                    # Apache 2.0 license
└── README.md                  # This file
```

## Code
- `code/nyiso_panel_regression.py`: Panel regression analysis of NYISO price data
- `code/Synthetic_control.py`: Implementation of synthetic control methodology

## Data
- `data/NYISO Price Data.xlsx`: Primary dataset with price information
- `data/DiD database_0422.xlsx`: Database for difference-in-differences analysis
- `data/DiD database_including weather.xlsx`: DiD database with weather controls
- `data/Sythetic control regression database.xlsx`: Data for synthetic control analysis

## Results
- `results/panel_results/`: Directory containing all panel regression outputs
  - Model summaries
  - Coefficients and statistics
  - Visualizations of treatment effects

## Paper
- `paper/INAFU6065FinalPaperNYISO-ORDC.pdf`: Full academic paper with detailed methodology and findings

## Getting Started
To reproduce our analysis:
1. Install the required dependencies: `pip install -r requirements.txt`
2. Run the panel regression analysis: `python code/nyiso_panel_regression.py`
3. Run the synthetic control analysis: `python code/Synthetic_control.py`

## Contact
This is the final project for Columbia University's INAFU6065 Economics of Energy course.

## License
This project is licensed under the Apache 2.0 License - see the LICENSE file for details.