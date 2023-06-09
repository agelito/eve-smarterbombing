# Eve Smarterbombing

[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/agelito/eve-smarterbombing/ci-cd.yml)](https://github.com/agelito/eve-smarterbombing/actions/workflows/ci-cd.yml)
[![PyPI](https://img.shields.io/pypi/v/smarterbombing)](https://pypi.org/project/smarterbombing/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/smarterbombing)](https://pypi.org/project/smarterbombing/)
[![codecov](https://codecov.io/gh/agelito/adm-bot/branch/main/graph/badge.svg?token=OHRY3OW18Y)](https://codecov.io/gh/agelito/eve-smarterbombing)

---


An application analyzing Eve Online combat logs and presenting data in a Web interface.

## ⚡ Quick Start

### 📦 From PyPI
```shell
pip install smarterbombing
python -m smarterbombing
```

### 📂 From Source
```shell
poetry install
poetry run python -m smarterbombing
```
Open with your preferred browser:
- Open [Web UI](http://localhost:42069)
- Open [Web UI (Dark Mode)](http://127.0.0.1:42069/?__theme=dark)


### 📃 Command line options
| Flag | Valid Values | Default | Description |
|---   |---     |---      | ---         |
| `--mode` | `webui` | `webui` | Which UI mode to run  |
| `--port` | Any valid port | `42069` | Which port to host webui |


## 🚧 Development
When developing it's most convenient to use the `poetry` `shell` which will provides a virtual
environment with all the dependencies and tools required. Install dependencies and activate the
virtual environment using the following commands:
```shell
poetry install
poetry shell
```

### 🟢 Running
```shell
python -m smarterbombing
```

### 📋 Unit Tests
```shell
pytest tests/ --cov=smarterbombing --cov-branch
```

### 🏋️‍♀️ Performance Benchmarks
```shell
# Damage Graph Aggregator
python benchmark/damage_graph_aggregator.py

# Combat Log Parser
python benchmark/parse_combat_log_line.py
```


