# ObesityMine - MLOps Project for Obesity Estimation

A machine learning project for obesity estimation following Cookiecutter Data Science standards.

## Project Organization
```
├── LICENSE            <- MIT License
├── Makefile           <- Makefile with commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project
├── data
│   ├── interim        <- Intermediate data that has been transformed
│   ├── processed      <- The final, canonical data sets for modeling
│   └── raw            <- The original, immutable data dump
│
├── docs               <- A default documentation directory
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks. Naming convention: phase.number-initials-description.ipynb
│                         Phase 0: Exploration
│                         Phase 1: Data cleaning and feature engineering
│                         Phase 2: Visualizations
│                         Phase 3: Modeling
│                         Phase 4: Publication-ready figures
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the environment
│                         pip install -r requirements.txt
│
├── setup.py           <- Makes project pip installable (pip install -e .) so src can be imported
├── pyproject.toml     <- Modern Python project configuration
├── src                <- Source code for use in this project (installable package)
│   ├── __init__.py    <- Makes src a Python module
│   ├── cargar_analisis.py    <- Data loading and initial analysis
│   ├── limpieza.py            <- Data cleaning functions
│   ├── eda.py                 <- Exploratory data analysis
│   ├── feature_engeenering.py <- Feature engineering pipeline
│   ├── modelos.py             <- Model definitions
│   ├── train.py               <- Training pipeline
│   ├── pipelines.py           <- MLOps pipelines
│   ├── carga_dvc.py           <- DVC integration utilities
│   └── utils                  <- Utility scripts
│
├── tests              <- Unit tests for src/
│
├── config             <- Configuration files (credentials, parameters)
│   ├── config.yaml         <- Main configuration
│   └── credentials.yaml    <- Credentials (git-ignored)
│
├── .dvc               <- DVC configuration
├── .git               <- Git repository
├── environment.yml    <- Conda environment specification
└── test_environment.py <- Test script for environment validation
```

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/JCGarcesDC/ObesityEstimation53.git
cd ObesityMine53
```

### 2. Set up environment

#### Using Conda (recommended):
```bash
# Create environment from environment.yml
conda env create -f environment.yml

# Activate the environment
conda activate obesitymine

# Install the project as an editable package
pip install -e .
```

Or using Make:
```bash
make create_environment
conda activate obesitymine
pip install -e .
```

#### Using pip (alternative):
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
pip install -e .
```

### 3. Download data from DVC remote
```bash
# Configure DVC remote (if not already done)
dvc remote list

# Pull data from remote storage
dvc pull
# or
make sync_data_down
```

### 4. Test your environment
```bash
python test_environment.py
# or
make test_environment
```

## Usage

### Running the Project

#### Make commands (recommended)
```bash
make help              # Show all available commands
make requirements      # Install Python dependencies
make sync_data_down    # Download data from DVC remote
make sync_data_up      # Upload data to DVC remote
make clean             # Remove Python file artifacts
make lint              # Check code style with flake8 and black
make format            # Format code with black and isort
make test              # Run unit tests with pytest
```

### Working with Notebooks

Notebooks follow the naming convention: `phase.number-initials-description.ipynb`

**Phases:**
- `0.xx` - Exploration and initial analysis
- `1.xx` - Data cleaning and feature engineering
- `2.xx` - Data visualizations
- `3.xx` - Modeling and evaluation
- `4.xx` - Publication-ready outputs

**Example:** `1.02-jc-data-cleaning.ipynb`

### Importing from src/

Since the project is installed as a package, you can import modules directly:

```python
from src.limpieza import eliminar_atipicos, limpiar_dataframe
from src.cargar_analisis import cargar_datos, analisis_inicial
from src.feature_engeenering import crear_features
```

### Data Version Control (DVC)

```bash
# Check status
dvc status

# Add new data file
dvc add data/raw/new_data.csv
git add data/raw/new_data.csv.dvc .gitignore
git commit -m "Add new data"

# Push to remote storage (GCS)
dvc push

# Pull from remote storage
dvc pull
```

## MLOps Stack

This project implements a complete MLOps workflow:

### Experiment Tracking - MLflow
```bash
# Start MLflow UI
mlflow ui

# Access at http://localhost:5000
```

### Model Registry
All trained models are logged to MLflow with:
- Parameters
- Metrics (accuracy, F1-score, etc.)
- Artifacts (model files, plots)

### Data Versioning - DVC + Google Cloud Storage
- Remote storage: `gs://obesityestimation-mna-mlops-53`
- Automatic data versioning
- Content-addressed storage for efficiency

### Code Quality Tools
- **black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **pytest**: Unit testing

### Cloud Deployment - Databricks

1. Configure Databricks CLI:
```bash
databricks configure --token
```

2. Update `config/config.yaml` with your workspace URL and cluster ID

## Development Workflow

1. **Explore**: Create notebooks in `notebooks/` (phase 0.xx for exploration)
2. **Clean Code**: Move stable code to `src/` modules
3. **Track Experiments**: Use MLflow for model tracking
4. **Version Data**: Use `dvc add` for new datasets
5. **Test**: Write tests in `tests/`
6. **Format**: Run `make format` before committing
7. **Commit**: Push to git (data stays in DVC remote)

### Git Workflow
```bash
# Current branch: dev2
git add .
git commit -m "Description"
git push origin dev2

# Push data to DVC remote
dvc push
```

## Configuration

### Main Configuration (`config/config.yaml`)
Contains:
- Databricks settings
- MLflow tracking URI
- Data paths
- Model hyperparameters
- DVC remote settings

### Credentials (`config/credentials.yaml`)
**⚠️ Never commit this file! Already in .gitignore**

Contains sensitive information:
- GitHub tokens
- API keys
- Service account credentials

## Testing

```bash
# Ejecución rápida (recomendada)
pytest -q

# Opcionales
pytest --cov=src tests/      # con cobertura
pytest tests/test_*.py       # archivo(s) específico(s)
```

## Project Features

✅ Conda environment with Python 3.11  
✅ MLflow experiment tracking  
✅ DVC data versioning with GCS remote  
✅ Modular source code in `src/`  
✅ Installable package (via setup.py)  
✅ Automated tasks via Makefile  
✅ Git version control  
✅ Databricks integration ready  
✅ Code quality tools (black, flake8, isort)  
✅ Unit testing framework  
✅ Cookiecutter Data Science structure  

## References

- [Cookiecutter Data Science](https://cookiecutter-data-science.drivendata.org/) - Project structure
- [DVC Documentation](https://dvc.org/doc) - Data versioning
- [MLflow Documentation](https://mlflow.org/docs/latest/) - Experiment tracking
- Data dictionary available in `references/README.md`

1. Create a new branch
2. Make changes
3. Run tests
4. Submit PR

## License

[Your License Here]