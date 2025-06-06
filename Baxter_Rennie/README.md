# Financial Calculus — Baxter & Rennie (Study and Implementation)

This repository provides a structured, chapter-by-chapter exploration of the key concepts and models from:

**Financial Calculus: An Introduction to Derivative Pricing**  
by Martin Baxter and Andrew Rennie

The focus is on developing a working understanding of each chapter's mathematical content, supported by corresponding Python implementations.

---

## Overview

The repository includes:

- Detailed explanations in Markdown for each chapter.
- Python implementations of key results and models.
- Numerical simulations and visualizations.
- A modular codebase for reuse and testing.

---

## Repository Structure

```
financial-calculus-baxter-rennie/
│
├── notebooks/                  # One Jupyter notebook per chapter
│   ├── chapter01_expectation_vs_arbitrage.ipynb
│   ├── chapter02_discrete_processes.ipynb
│   ├── chapter03_continuous_processes.ipynb
│   ├── ...
│   └── appendices/
│       ├── A1_further_reading.ipynb
│       ├── A2_notation.ipynb
│       ├── A3_exercise_answers.ipynb
│       └── A4_glossary.ipynb
│
├── utils/                      # Supporting Python modules
│   ├── stochastic_tools.py
│   └── plotting.py
│
├── data/                       # Data files and simulations
│   └── simulated_price_paths.csv
│
├── tests/                      # Unit tests
│   └── test_stochastic_tools.py
│
├── requirements.txt            # Python dependencies
├── LICENSE
└── README.md
```

---

## Topics Covered

- Expectation pricing and arbitrage
- Discrete-time models (binomial trees)
- Brownian motion and continuous processes
- Ito calculus and stochastic differential equations
- Girsanov's theorem and change of measure
- Martingale representation and hedging
- Black-Scholes pricing
- Foreign exchange and dividend-paying equities
- Fixed income models (HJM and short-rate frameworks)
- Advanced topics (multi-factor models, numeraires)

---

## Setup Instructions

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/financial-calculus-baxter-rennie.git
   cd financial-calculus-baxter-rennie
   ```

2. (Optional) Create a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install required packages:

   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

Each notebook is self-contained and can be executed sequentially. Mathematical theory is introduced section-by-section, followed by corresponding Python implementations.

For example:

- `chapter02_discrete_processes.ipynb` includes a simulation of a binomial tree and a demonstration of arbitrage-based pricing.
- `chapter03_continuous_processes.ipynb` introduces stochastic calculus and implements key results such as Ito's lemma and Black-Scholes pricing.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Author

This repository is maintained by Jorge Miralles, as a companion to independent study and implementation of concepts from _Financial Calculus_.
