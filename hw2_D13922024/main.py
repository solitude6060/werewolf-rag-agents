#!/usr/bin/env python3
import argparse
from pathlib import Path

from src.pipeline import predict_single_game, predict_all_public, predict_all_private
from src.data.loader import get_data_root


def main():
    parser = argparse.ArgumentParser(description="Werewolf Prediction System")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    predict_parser = subparsers.add_parser("predict", help="Predict a single game")
    predict_parser.add_argument("game_id", help="Game index (e.g., 01)")
    predict_parser.add_argument("--private", action="store_true", help="Private game")

    all_parser = subparsers.add_parser("predict-all", help="Predict all public games")
    all_parser.add_argument("--output", type=Path, help="Output CSV path")

    private_parser = subparsers.add_parser("predict-private", help="Predict all private games")
    private_parser.add_argument("--output", type=Path, help="Output CSV path")

    parser.add_argument("--data-dir", type=Path, help="Data directory override")

    args = parser.parse_args()

    data_dir = args.data_dir if args.data_dir else get_data_root()

    if args.command == "predict":
        submission = predict_single_game(
            args.game_id,
            is_private=args.private,
            data_dir=data_dir,
        )
        print(submission.to_csv())

    elif args.command == "predict-all":
        results = predict_all_public(data_dir, output_path=args.output)
        if args.output:
            print(f"Predictions saved to {args.output}")
        else:
            print(f"Processed {len(results)} games")

    elif args.command == "predict-private":
        results = predict_all_private(data_dir, output_path=args.output)
        if args.output:
            print(f"Predictions saved to {args.output}")
        else:
            print(f"Processed {len(results)} private games")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()