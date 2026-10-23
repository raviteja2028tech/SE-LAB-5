"""Energy Consumption and Tariff Calculator Module.

This module tracks utility meter readings, computes tiered electricity
tariffs, detects anomalous usage spikes, and manages JSON persistence.
"""

import ast
from datetime import datetime
import json

# Global state and configuration constants
meters = {}
RATE_TIERS = {
    "tier_1": 3.5,
    "tier_2": 5.0,
    "tier_3": 7.5,
}
SPIKE_LIMIT = 500


READING_HISTORY = []


def record_reading(meter_id, units, history=None):
    """Record a meter reading with timestamp and update the total units.

    Args:
        meter_id (str): The identifier of the utility meter.
        units (float): The energy consumption units to record.
        history (list, optional): Historical log of readings. Defaults to None.

    Returns:
        list: The updated history list containing tuples of readings.
    """
    if history is None:
        history = READING_HISTORY
    if units < 0:
        print(f"Warning: Negative reading for {meter_id}: {units}")

    history.append((meter_id, units, str(datetime.now())))
    meters[meter_id] = meters.get(meter_id, 0) + units
    return history


def compute_bill(meter_id, tier_rates):
    """Compute the tiered electricity bill for a given meter.

    Tier 1: 0 - 100 units
    Tier 2: 101 - 300 units
    Tier 3: > 300 units

    Args:
        meter_id (str): The identifier of the utility meter.
        tier_rates (list): A list or sequence of three tier rate prices.

    Returns:
        float: The total calculated bill amount.
    """
    units = meters.get(meter_id, 0)
    if units <= 100:
        return max(0.0, units * tier_rates[0])
    if units <= 300:
        return 100 * tier_rates[0] + (units - 100) * tier_rates[1]

    tier_sum = 100 * tier_rates[0] + 200 * tier_rates[1]
    return tier_sum + (units - 300) * tier_rates[2]


def raise_rates(percent):
    """Increase all tariff tier rates by a given percentage.

    Args:
        percent (float): Percentage rate increase.
    """
    for tier in RATE_TIERS:
        RATE_TIERS[tier] *= 1 + percent / 100


def get_tier_rates():
    """Retrieve the current tariff rates as a list.

    Returns:
        list: Current tier rates [tier_1, tier_2, tier_3].
    """
    return [
        RATE_TIERS["tier_1"],
        RATE_TIERS["tier_2"],
        RATE_TIERS["tier_3"],
    ]


def flag_spikes():
    """Identify meters whose energy consumption exceeds the spike limit.

    Returns:
        list: Identifiers of meters exceeding SPIKE_LIMIT.
    """
    return [m for m, reading in meters.items() if reading > SPIKE_LIMIT]


def load_meter_data(file="meters.json"):
    """Load meter consumption records from a JSON file.

    Args:
        file (str): Path to the JSON data file. Defaults to 'meters.json'.
    """
    try:
        with open(file, "r", encoding="utf-8") as f:
            meters.clear()
            meters.update(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        meters.clear()


def save_meter_data(file="meters.json"):
    """Save current meter consumption records to a JSON file.

    Args:
        file (str): Path to the JSON data file. Defaults to 'meters.json'.
    """
    with open(file, "w", encoding="utf-8") as f:
        json.dump(meters, f, indent=2)


def safe_eval(expr):
    """Safely evaluate simple arithmetic expressions without code execution.

    Args:
        expr (str): Arithmetic expression string (e.g., '10 + 20').

    Returns:
        float: The calculated numeric value or 0.0 on invalid expression.
    """
    try:
        parsed = ast.parse(expr.strip(), mode="eval")
        ops = {
            ast.Add: lambda a, b: a + b,
            ast.Sub: lambda a, b: a - b,
            ast.Mult: lambda a, b: a * b,
            ast.Div: lambda a, b: a / b,
        }

        def _eval_node(node):
            if isinstance(node, ast.Expression):
                return _eval_node(node.body)
            if (
                isinstance(node, ast.Constant)
                and isinstance(node.value, (int, float))
            ):
                return float(node.value)
            if isinstance(node, ast.BinOp) and type(node.op) in ops:
                left = _eval_node(node.left)
                right = _eval_node(node.right)
                return ops[type(node.op)](left, right)
            if (
                isinstance(node, ast.UnaryOp)
                and isinstance(node.op, (ast.UAdd, ast.USub))
            ):
                val = _eval_node(node.operand)
                return -val if isinstance(node.op, ast.USub) else val
            raise ValueError("Unsupported operation")

        return _eval_node(parsed)
    except (SyntaxError, ValueError, ZeroDivisionError, TypeError):
        return 0.0


def main():
    """Main execution entry point demonstrating utility tracking."""
    record_reading("M-01", 120)
    record_reading("M-02", 640)
    history = record_reading("M-03", -50)
    print("Readings stored so far:", len(history))

    raise_rates(10)
    rates = get_tier_rates()

    print(f"Bill M-01: {compute_bill('M-01', rates):.2f}")
    print(f"Bill M-03: {compute_bill('M-03', rates):.2f}")
    print("Spikes:", flag_spikes())

    prompt = "Extra units for M-01 as an expression (Enter for 0): "
    adjustment = input(prompt) or "0"
    record_reading("M-01", safe_eval(adjustment))

    save_meter_data()
    load_meter_data()
    print(f"Bill M-01 after reload: {compute_bill('M-01', rates):.2f}")


if __name__ == "__main__":
    main()
