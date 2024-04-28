# ECS-Sim
A SImpy-based EV Charging Station Simulator.

## Quick Start

### Install Dependencies

* Install with `uv`

```
pip install uv

# Install without venv
uv pip install --python=$(which python) simpy numpy pandas
```

* Install without `uv`

```
pip install -r requirements.txt
```

### Install Packages

```
pip install -e .
```

### Quick run (Alpha Version)

```
python main.py
```

## Introduction

In alpha version, we generate a random number and decide if a car comes to charging station with a given threshold. In recent version, we achieve three important features:

(1) Generate random charging event.
(2) Construct a toy charging station simulator.
(3) Using the `Resources` object provided by `Simpy` to control the capacity of charging station.

## Recent Problems

In alpha version, the charing event is running automatically. There is no endpoint for us to control the charging scheduler, and hard to extract the charing history due to the process of charging event steps with `while True` loop.

## TODO

1. Constrcut `EV` object with `charing` and `discharge` methods to control the energy flow.
2. Make the charing event evolve with a controlable process.