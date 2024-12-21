import argparse
import sys

from src.logics.file import make_parent_dirs_and_return_path


def _parse_args(args: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--v1",
        type=float,
        required=True,
        default=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--v2",
        type=float,
        required=True,
        default=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--sum",
        type=make_parent_dirs_and_return_path,
        required=True,
        default=argparse.SUPPRESS,
    )
    parsed_args, _ = parser.parse_known_args(args)
    return parsed_args


def add(v1: float, v2: float) -> float:
    return v1 + v2


def main(argv: list[str]) -> None:
    args = _parse_args(argv)
    sum = add(args.v1, args.v2)
    with open(args.sum, "w") as f:
        f.write(str(sum))


if __name__ == "__main__":
    main(sys.argv[1:])
