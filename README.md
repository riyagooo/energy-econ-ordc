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
├── LICENSE                    # Creative Commons Attribution 4.0 license
├── CITATION.cff               # Citation information
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
To reproduce our analysis, you will need to:
1. Install the required dependencies: `pip install -r requirements.txt`
2. Request the data files by contacting the authors (data files are not included in this repository)
3. Run the panel regression analysis: `python code/nyiso_panel_regression.py`
4. Run the synthetic control analysis: `python code/Synthetic_control.py`

## Citation
If you use this code or findings in your work, please cite:

```
Zubairi, I., Guo, R.Y., Li, L., Dorcély, C., Murata, M., Chu, I., & Villa, P.J. (2023). 
NYISO Enhanced Scarcity Pricing Policy: Impacts on Consumer Prices. 
Columbia University, School of International and Public Affairs.
```

For more citation formats, please see the `CITATION.cff` file.

## Contact
This is the final project for Columbia University's INAFU6065 Economics of Energy course.

## License
This project is licensed under the Creative Commons Attribution 4.0 International License (CC BY 4.0) - see the LICENSE file for details. This license allows reusers to distribute, remix, adapt, and build upon the material in any medium or format, so long as attribution is given to the creator.