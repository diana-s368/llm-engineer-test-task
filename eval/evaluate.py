
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
EXPECTED_DIR = ROOT_DIR / "data" / "expected"
PREDICTIONS_DIR = ROOT_DIR / "data" / "predictions"

FIELDS = [
    "doc_type",
    "supplier_name",
    "supplier_bin",
    "doc_number",
    "doc_date",
    "currency",
    "total_amount",
    "vat_amount",
    "line_items",
]


def load_json(path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def normalize(value):
    if isinstance(value, str):
        return " ".join(value.casefold().split())

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)

    if isinstance(value, list):
        return [normalize(item) for item in value]

    if isinstance(value, dict):
        return {
            key: normalize(item)
            for key, item in value.items()
        }

    return value


def main():
    expected_files = sorted(EXPECTED_DIR.glob("*.json"))

    field_stats = {
        field: {"correct": 0, "total": 0}
        for field in FIELDS
    }

    hallucinations = {field: 0 for field in FIELDS}
    omissions = {field: 0 for field in FIELDS}

    processed = 0

    for expected_file in expected_files:
        prediction_file = PREDICTIONS_DIR / expected_file.name

        if not prediction_file.exists():
            print(f"Missing prediction: {expected_file.name}")
            continue

        expected = load_json(expected_file)
        prediction = load_json(prediction_file)

        processed += 1

        for field in FIELDS:
            expected_value = expected[field]
            predicted_value = prediction[field]

            field_stats[field]["total"] += 1

            if normalize(expected_value) == normalize(predicted_value):
                field_stats[field]["correct"] += 1

            if expected_value is None and predicted_value is not None:
                hallucinations[field] += 1

            if expected_value is not None and predicted_value is None:
                omissions[field] += 1

    print("\n========== EVALUATION REPORT ==========")
    print(f"Documents evaluated: {processed}/{len(expected_files)}")

    print("\nField accuracy:")

    for field, stats in field_stats.items():
        if stats["total"] == 0:
            accuracy = 0
        else:
            accuracy = stats["correct"] / stats["total"] * 100

        print(
            f"{field:20} "
            f"{accuracy:6.2f}% "
            f"({stats['correct']}/{stats['total']})"
        )

    print("\nHallucinations:")
    for field, count in hallucinations.items():
        print(f"{field:20} {count}")

    print("\nOmissions:")
    for field, count in omissions.items():
        print(f"{field:20} {count}")

    print("\n=======================================")


if __name__ == "__main__":
    main()
