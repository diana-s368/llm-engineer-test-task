
import json
from pathlib import Path

from src.extractor import extract_document

INPUT_DIR = Path("data/input")
OUTPUT_DIR = Path("data/predictions")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    input_files = sorted(INPUT_DIR.glob("*.txt"))
    errors = []

    for input_file in input_files:
        print(f"Processing {input_file.name}...")

        try:
            document_text = input_file.read_text(encoding="utf-8")
            result = extract_document(document_text)

            output_file = OUTPUT_DIR / f"{input_file.stem}.json"
            output_file.write_text(
                json.dumps(
                    result.model_dump(mode="json"),
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            print(f"  Saved: {output_file}")

        except Exception as error:
            errors.append({
                "file": input_file.name,
                "error": str(error),
            })
            print(f"  Failed: {error}")

    if errors:
        error_file = OUTPUT_DIR / "errors.json"
        error_file.write_text(
            json.dumps(errors, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    successful = len(input_files) - len(errors)

    print("\nBatch extraction completed.")
    print(f"Successful: {successful}/{len(input_files)}")
    print(f"Failed: {len(errors)}/{len(input_files)}")


if __name__ == "__main__":
    main()
