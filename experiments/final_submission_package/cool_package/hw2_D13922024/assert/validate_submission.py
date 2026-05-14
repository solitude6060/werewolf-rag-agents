#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.schema import Submission


def validate_submission(csv_path: str) -> bool:
    content = Path(csv_path).read_text()
    lines = content.strip().split("\n")

    if not lines:
        print("ERROR: Empty file")
        return False

    header = lines[0]
    expected = "id,index,character,role,wolf_score"
    if header != expected:
        print(f"ERROR: Wrong header. Expected: {expected}, Got: {header}")
        return False

    if len(lines) < 2:
        print("ERROR: No data rows")
        return False

    for i, line in enumerate(lines[1:], start=2):
        parts = line.split(",")
        if len(parts) != 5:
            print(f"ERROR: Line {i} has {len(parts)} columns, expected 5")
            return False

        try:
            pid = int(parts[0])
            idx = parts[1]
            char = parts[2]
            role = parts[3]
            score = float(parts[4])

            if score < 0.0 or score > 1.0:
                print(f"ERROR: Line {i} - wolf_score {score} out of [0,1]")
                return False

            valid_roles = ["Villager", "Werewolf", "Seer", "Medium", "Madman", "Hunter"]
            if role not in valid_roles:
                print(f"ERROR: Line {i} - invalid role {role}")
                return False

        except ValueError as e:
            print(f"ERROR: Line {i} - {e}")
            return False

    print(f"OK: {len(lines)-1} predictions validated")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_submission.py <csv_path>")
        sys.exit(1)

    csv_path = sys.argv[1]
    if not Path(csv_path).exists():
        print(f"ERROR: File not found: {csv_path}")
        sys.exit(1)

    success = validate_submission(csv_path)
    sys.exit(0 if success else 1)