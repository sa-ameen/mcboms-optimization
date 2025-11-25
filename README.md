# MCBOMs: Multidisciplinary Cost-Benefit Optimization Models

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python framework for optimizing transportation infrastructure investment decisions using Mixed-Integer Linear Programming (MILP). MCBOMs integrates safety, operations, and corridor condition measures into a unified optimization framework.

## Overview

MCBOMs (Multidisciplinary Cost-Benefit Optimization Models) provides transportation agencies with tools to:

- **Optimize project selection** across multiple candidate sites under budget constraints
- **Quantify multidisciplinary benefits** including safety, operations, and corridor conditions
- **Enumerate improvement alternatives** including partial-length treatments
- **Maintain theoretical rigor** while adapting to varying data availability

The framework builds on established methodologies from:
- Harwood et al. (2003) - Systemwide R3 project optimization
- Banihashemi (2007) - Combined safety-operations optimization with IHSDM
- Highway Safety Manual (HSM) - Crash prediction and CMF methodology

## Project Structure

```
mcboms-optimization/
├── src/
│   └── mcboms/
│       ├── core/           # Core optimization engine
│       │   ├── optimizer.py      # MILP formulation and solver
│       │   ├── alternatives.py   # Alternative enumeration
│       │   └── constraints.py    # Constraint definitions
│       ├── benefits/       # Benefit calculation modules
│       │   ├── safety.py         # HSM-based safety benefits
│       │   ├── operations.py     # Travel time, VOC benefits
│       │   └── ccm.py            # Corridor condition measures
│       ├── io/             # Input/output handling
│       │   ├── readers.py        # Data file readers
│       │   └── writers.py        # Results output
│       └── utils/          # Utility functions
│           ├── economics.py      # NPV, discount factors
│           └── validation.py     # Input validation
├── data/
│   ├── input/              # Input data files
│   ├── output/             # Optimization results
│   └── validation/         # Benchmark validation data
├── tests/                  # Unit and integration tests
├── docs/                   # Documentation
├── notebooks/              # Jupyter notebooks for analysis
├── examples/               # Example scripts
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Installation

### Prerequisites

- Python 3.11 or higher
- Gurobi Optimizer (academic license available free)

### Setup

```bash
# Clone the repository
git clone https://github.com/your-org/mcboms-optimization.git
cd mcboms-optimization

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

### Gurobi License

MCBOMs uses Gurobi for MILP optimization. Obtain a license at:
- Academic: https://www.gurobi.com/academia/academic-program-and-licenses/
- Commercial: https://www.gurobi.com/solutions/licensing/

## Quick Start

```python
from mcboms.core import Optimizer
from mcboms.io import load_sites, load_alternatives

# Load data
sites = load_sites('data/input/sites.csv')
alternatives = load_alternatives('data/input/alternatives.csv')

# Create optimizer
optimizer = Optimizer(
    sites=sites,
    alternatives=alternatives,
    budget=10_000_000,
    discount_rate=0.07,
    analysis_horizon=20
)

# Solve
results = optimizer.solve()

# Display results
print(f"Total Net Benefit: ${results.net_benefit:,.0f}")
print(f"Sites Improved: {results.sites_improved}")
print(f"Budget Utilized: ${results.total_cost:,.0f}")
```

## Validation

MCBOMs is validated against published benchmark results:

### Harwood et al. (2003) Benchmark

| Budget | Expected Net Benefit | MCBOMs Result | Difference |
|--------|---------------------|---------------|------------|
| $50M   | $6,159,517          | TBD           | TBD        |
| $10M   | $4,675,033          | TBD           | TBD        |

Run validation tests:

```bash
pytest tests/test_harwood_validation.py -v
```

## Mathematical Formulation

### Objective Function

Maximize total net present value of benefits:

$$\max \sum_{i=1}^{N} \sum_{j \in \mathcal{J}_i} \left( B_{ij}^{\text{NPV}} - C_{ij} \right) \cdot x_{ij}$$

Where:
- $x_{ij} \in \{0, 1\}$ — binary decision variable (1 if alternative $j$ selected for project $i$)
- $B_{ij}^{\text{NPV}}$ — total discounted benefits (safety + operations + CCM)
- $C_{ij}$ — total cost of alternative $j$ at project $i$

### Constraints

1. **Mutual Exclusivity**: Select at most one alternative per project
   $$\sum_{j \in \mathcal{J}_i} x_{ij} \leq 1 \quad \forall i$$

2. **Budget**: Total expenditure within available budget
   $$\sum_{i=1}^{N} \sum_{j \in \mathcal{J}_i} C_{ij} \cdot x_{ij} \leq \mathcal{B}$$

3. **Binary**: Decision variables are binary
   $$x_{ij} \in \{0, 1\} \quad \forall i, j$$

## Benefits Calculation

### Safety Benefits

Based on Highway Safety Manual (HSM) methodology:

$$B_{ij}^{\text{Safety}} = \sum_{t=1}^{T} \sum_{s} \left( N_{\text{baseline}} - N_{\text{build}} \right) \times UC_s \times DF_t$$

Where:
- $N_{\text{build}} = N_{\text{baseline}} \times \prod_{m} CMF_m$
- $CMF_m$ = Crash Modification Factor for improvement $m$
- $UC_s$ = Unit crash cost by severity $s$
- $DF_t$ = Discount factor for year $t$

### Operational Benefits

Based on travel time and vehicle operating cost savings:

$$B_{ij}^{\text{Ops}} = \sum_{t=1}^{T} \left( \Delta TT \times N \times VOT + \Delta VOC \times VMT \right) \times DF_t$$

## Configuration

Key parameters in `config.yaml`:

```yaml
economic:
  discount_rate: 0.07          # USDOT 2024
  analysis_horizon: 20         # years
  
crash_costs:  # USDOT 2024 values
  fatal: 13200000
  injury_a: 800000
  injury_b: 400000
  injury_c: 200000
  pdo: 15000

value_of_time:  # $/hour
  personal: 17.80
  business: 33.60
  truck: 32.80
```

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use MCBOMs in your research, please cite:

```bibtex
@software{mcboms2025,
  title = {MCBOMs: Multidisciplinary Cost-Benefit Optimization Models},
  author = {Texas A&M Transportation Institute},
  year = {2025},
  url = {https://github.com/your-org/mcboms-optimization}
}
```

## References

1. Harwood, D. W., et al. (2003). Systemwide optimization of safety improvements for resurfacing, restoration, or rehabilitation projects. *Transportation Research Record*, 1840(1), 148-157.

2. Banihashemi, M. (2007). Optimization of highway safety and operation by using crash prediction models with accident modification factors. *Transportation Research Record*, 2019(1), 111-117.

3. AASHTO. (2010). *Highway Safety Manual* (1st ed.).

## Acknowledgments

This work was conducted under FHWA Contract HRSO20240009PR.

## Contact

Texas A&M Transportation Institute  
College Station, TX  
