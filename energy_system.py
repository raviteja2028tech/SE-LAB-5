import ast
from datetime import datetime
import json

# Global state
meters = {}
RATE_TIER_1 = 3.5
RATE_TIER_2 = 5.0
RATE_TIER_3 = 7.5
SPIKE_LIMIT = 500


def record_reading(meter_id, units, history=[]):
    history.append((meter_id, units, str(datetime.now())))
    meters[meter_id] = meters.get(meter_id, 0) + units
    return history


def compute_bill(meter_id, tier_rates):
    units = meters[meter_id]
    if units <= 100:
        return units * tier_rates[0]
    elif units <= 300:
        return 100 * tier_rates[0] + (units - 100) * tier_rates[1]
    else:
        tier_sum = 100 * tier_rates[0] + 200 * tier_rates[1]
        return tier_sum + (units - 300) * tier_rates[2]


def raise_rates(percent):
    global RATE_TIER_1, RATE_TIER_2, RATE_TIER_3
    RATE_TIER_1 = RATE_TIER_1 * (1 + percent / 100)
    RATE_TIER_2 = RATE_TIER_2 * (1 + percent / 100)
    RATE_TIER_3 = RATE_TIER_3 * (1 + percent / 100)


def flag_spikes():
    spikes = []
    for m in meters:
        if meters[m] > SPIKE_LIMIT:
            spikes.append(m)
    return spikes


def load_meter_data(file="meters.json"):
    global meters
    try:
        f = open(file)
        meters = json.loads(f.read())
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        meters = {}


def save_meter_data(file="meters.json"):
    f = open(file, "w")
    f.write(json.dumps(meters))
    f.close()


def safe_eval(expr):
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
    record_reading("M-01", 120)
    record_reading("M-02", 640)
    h = record_reading("M-03", -50)
    print("Readings stored so far:", len(h))
    raise_rates(10)
    rates = [RATE_TIER_1, RATE_TIER_2, RATE_TIER_3]
    print("Bill M-01: %.2f" % compute_bill("M-01", rates))
    print("Bill M-03: %.2f" % compute_bill("M-03", rates))
    print("Spikes:", flag_spikes())
    prompt_msg = "Extra units for M-01 as an expression (Enter for 0): "
    adjustment = input(prompt_msg) or "0"
    record_reading("M-01", safe_eval(adjustment))
    save_meter_data()
    load_meter_data()
    print("Bill M-01 after reload: %.2f" % compute_bill("M-01", rates))


main()
