#!/usr/bin/env python3
"""CLI tool for generating Modbus slave workspace JSON.

The script clones the current workspace template and can:

- generate a specific slave count or slave-id range
- set register counts and address spacing
- choose register/group value formats
- randomize or preserve register values

Examples:

  python generate_modbus_workspace.py --help
  python generate_modbus_workspace.py --slave-count 300 --slave-id-start 1 \
      --register-count 100 --randomize-values --replace-existing
  python generate_modbus_workspace.py --slave-id-start 144 --slave-id-end 300 \
      --register-count 100 --randomize-values --replace-existing
"""

from __future__ import annotations

import argparse
import copy
import json
import random
import sys
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any


DEFAULT_TEMPLATE = Path("slave_workspace.json")
DEFAULT_OUTPUT = Path("slave_workspace.generated.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Modbus slave workspace data from an existing template."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_TEMPLATE,
        help="Template workspace JSON file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output workspace JSON file.",
    )
    parser.add_argument(
        "--workspace-index",
        type=int,
        default=0,
        help="Workspace entry index inside the top-level JSON array.",
    )

    slave_range = parser.add_mutually_exclusive_group(required=True)
    slave_range.add_argument(
        "--slave-count",
        type=int,
        help="Total number of slaves to generate.",
    )
    slave_range.add_argument(
        "--slave-id-end",
        type=int,
        help="Inclusive end Modbus address for generated slaves.",
    )

    parser.add_argument(
        "--slave-id-start",
        type=int,
        default=1,
        help="Starting Modbus address for generated slaves.",
    )
    parser.add_argument(
        "--slave-name-prefix",
        default="Slave",
        help="Prefix used to build each slave name.",
    )
    parser.add_argument(
        "--group-count",
        type=int,
        default=1,
        help="Number of register groups per slave.",
    )
    parser.add_argument(
        "--group-name-prefix",
        default="RegisterGroup",
        help="Prefix used to build group names when more than one group exists.",
    )
    parser.add_argument(
        "--register-count",
        type=int,
        default=100,
        help="Number of registers per group.",
    )
    parser.add_argument(
        "--register-start-address",
        type=int,
        default=1,
        help="First register address in each generated group.",
    )
    parser.add_argument(
        "--register-step",
        type=int,
        default=1,
        help="Increment between generated register addresses.",
    )
    parser.add_argument(
        "--register-type",
        type=int,
        default=2,
        help="RegisterType value to use for every generated group.",
    )
    parser.add_argument(
        "--string-value-format",
        type=int,
        default=10,
        help="StringValueFormat value to use for every generated group.",
    )
    parser.add_argument(
        "--value-format",
        type=int,
        default=1,
        help="ValueFormat value to use for every generated register.",
    )
    parser.add_argument(
        "--randomize-values",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Randomize register values instead of reusing template values.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible value generation.",
    )
    parser.add_argument(
        "--replace-existing",
        action="store_true",
        help="Replace the workspace slave list with only the generated slaves.",
    )
    parser.add_argument(
        "--keep-original-order",
        action="store_true",
        help="Preserve the original slave order when merging generated entries.",
    )
    parser.add_argument(
        "--inplace",
        action="store_true",
        help="Overwrite the input workspace file instead of writing a separate output file.",
    )
    parser.add_argument(
        "--slave-config",
        type=Path,
        default=None,
        help=(
            "Optional JSON file that provides per-slave overrides. Keys may be "
            "slave ids or names; values can set register_count, register_type, "
            "value_format, string_value_format, group_count, register_start_address, "
            "register_step, slave_name_prefix, and randomize_values."
        ),
    )
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    if args.workspace_index < 0:
        raise ValueError("--workspace-index must be zero or greater.")
    if args.slave_id_start < 1:
        raise ValueError("--slave-id-start must be greater than zero.")
    if args.group_count <= 0:
        raise ValueError("--group-count must be greater than zero.")
    if args.register_count <= 0:
        raise ValueError("--register-count must be greater than zero.")
    if args.register_start_address < 0:
        raise ValueError("--register-start-address must be zero or greater.")
    if args.register_step <= 0:
        raise ValueError("--register-step must be greater than zero.")


def load_slave_overrides(path: Path | None) -> dict[str, dict[str, Any]]:
    if path is None:
        return {}

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("Slave override file must contain a top-level JSON object.")

    overrides: dict[str, dict[str, Any]] = {}
    for key, value in data.items():
        if not isinstance(key, str):
            raise ValueError("Slave override keys must be strings.")
        if not isinstance(value, dict):
            raise ValueError(f"Override for {key!r} must be a JSON object.")
        overrides[key] = value
    return overrides


def load_workspace(path: Path, index: int) -> tuple[list[Any], dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Workspace file must contain a top-level JSON array.")
    if not data:
        raise ValueError("Workspace file does not contain any workspace entries.")
    if index >= len(data):
        raise IndexError(
            f"Workspace index {index} is out of range for {len(data)} entries."
        )

    workspace = data[index]
    if not isinstance(workspace, dict):
        raise ValueError("Workspace entry must be a JSON object.")
    return data, workspace


def make_value_factory(randomize: bool, seed: int | None) -> Callable[[], int]:
    rng = random.Random(seed)

    def next_value() -> int:
        if randomize:
            return rng.randint(0, 65535)
        return 0

    return next_value


def build_slave_ids(args: argparse.Namespace) -> list[int]:
    if args.slave_count is not None:
        if args.slave_count <= 0:
            raise ValueError("--slave-count must be greater than zero.")
        return list(range(args.slave_id_start, args.slave_id_start + args.slave_count))

    if args.slave_id_end < args.slave_id_start:
        raise ValueError(
            "--slave-id-end must be greater than or equal to --slave-id-start."
        )
    return list(range(args.slave_id_start, args.slave_id_end + 1))


def get_override(
    overrides: dict[str, dict[str, Any]], slave_id: int, slave_name: str
) -> dict[str, Any]:
    return overrides.get(str(slave_id), overrides.get(slave_name, {}))


def index_existing_slaves(
    slaves: Iterable[Any],
) -> tuple[dict[int, dict[str, Any]], list[dict[str, Any]]]:
    by_id: dict[int, dict[str, Any]] = {}
    ordered: list[dict[str, Any]] = []
    for slave in slaves:
        if not isinstance(slave, dict):
            raise ValueError("Each slave entry must be a JSON object.")
        slave_id = slave.get("SlaveId")
        if not isinstance(slave_id, int):
            raise ValueError("Each slave entry must have an integer SlaveId.")
        by_id[slave_id] = slave
        ordered.append(slave)
    return by_id, ordered


def clone_register(
    template: dict[str, Any],
    address: int,
    value: int,
    value_format: int,
) -> dict[str, Any]:
    register = copy.deepcopy(template)
    register["Address"] = address
    register["Value"] = value
    register["ValueFormat"] = value_format
    return register


def generate_registers(
    template_group: dict[str, Any],
    register_count: int,
    start_address: int,
    step: int,
    value_format: int,
    next_value: Callable[[], int],
) -> list[dict[str, Any]]:
    template_registers = template_group.get("RegisterModels", [])
    if not template_registers:
        raise ValueError("Template register group does not contain any registers.")

    registers: list[dict[str, Any]] = []
    address = start_address
    for index in range(register_count):
        template_register = template_registers[index % len(template_registers)]
        if not isinstance(template_register, dict):
            raise ValueError("Template register must be a JSON object.")
        registers.append(
            clone_register(
                template_register,
                address=address,
                value=next_value(),
                value_format=value_format,
            )
        )
        address += step
    return registers


def clone_group(
    template_group: dict[str, Any],
    group_name: str,
    register_count: int,
    start_address: int,
    step: int,
    register_type: int,
    string_value_format: int,
    value_format: int,
    next_value: Callable[[], int],
) -> dict[str, Any]:
    group = copy.deepcopy(template_group)
    group["GroupName"] = group_name
    group["RegisterType"] = register_type
    group["Quantity"] = register_count
    group["StringValueFormat"] = string_value_format
    group["RegisterModels"] = generate_registers(
        template_group,
        register_count=register_count,
        start_address=start_address,
        step=step,
        value_format=value_format,
        next_value=next_value,
    )
    return group


def clone_slave(
    template_slave: dict[str, Any],
    slave_id: int,
    slave_name_prefix: str,
    group_count: int,
    group_name_prefix: str,
    register_count: int,
    start_address: int,
    step: int,
    register_type: int,
    string_value_format: int,
    value_format: int,
    next_value: Callable[[], int],
    randomize_values: bool,
) -> dict[str, Any]:
    slave = copy.deepcopy(template_slave)
    slave["Name"] = f"{slave_name_prefix}{slave_id}"
    slave["SlaveId"] = slave_id
    slave["UserRandomValue"] = randomize_values

    template_groups = template_slave.get("RegisterGroupModels", [])
    if not template_groups:
        raise ValueError("Template slave does not contain any register groups.")

    slave["EnableScript"] = template_slave.get("EnableScript", False)
    if "Code" in template_slave:
        slave["Code"] = template_slave["Code"]

    groups: list[dict[str, Any]] = []
    for group_index in range(group_count):
        template_group = template_groups[group_index % len(template_groups)]
        if not isinstance(template_group, dict):
            raise ValueError("Template register group must be a JSON object.")
        group_name = (
            template_group.get("GroupName")
            if group_count == 1
            else f"{group_name_prefix}{group_index + 1}"
        )
        groups.append(
            clone_group(
                template_group,
                group_name=str(group_name),
                register_count=register_count,
                start_address=start_address,
                step=step,
                register_type=register_type,
                string_value_format=string_value_format,
                value_format=value_format,
                next_value=next_value,
            )
        )

    slave["RegisterGroupModels"] = groups
    return slave


def main() -> int:
    args = parse_args()
    validate_args(args)

    _, workspace = load_workspace(args.input, args.workspace_index)
    template_slaves = workspace.get("SlaveModels", [])
    if not template_slaves:
        raise ValueError("Workspace does not contain any slave models.")

    template_slave = template_slaves[0]
    if not isinstance(template_slave, dict):
        raise ValueError("Template slave must be a JSON object.")

    slave_ids = build_slave_ids(args)
    next_value = make_value_factory(args.randomize_values, args.seed)

    generated_slaves = [
        clone_slave(
            template_slave,
            slave_id=slave_id,
            slave_name_prefix=args.slave_name_prefix,
            group_count=args.group_count,
            group_name_prefix=args.group_name_prefix,
            register_count=args.register_count,
            start_address=args.register_start_address,
            step=args.register_step,
            register_type=args.register_type,
            string_value_format=args.string_value_format,
            value_format=args.value_format,
            next_value=next_value,
            randomize_values=args.randomize_values,
        )
        for slave_id in slave_ids
    ]

    overrides = load_slave_overrides(args.slave_config)
    if overrides:
        for slave in generated_slaves:
            slave_id = slave["SlaveId"]
            override = get_override(overrides, slave_id, slave["Name"])
            if not override:
                continue

            slave_name_prefix = override.get(
                "slave_name_prefix", args.slave_name_prefix
            )
            slave["Name"] = override.get("name", f"{slave_name_prefix}{slave_id}")
            slave["UserRandomValue"] = override.get(
                "randomize_values", slave["UserRandomValue"]
            )

            group_count = int(
                override.get("group_count", len(slave["RegisterGroupModels"]))
            )
            register_count = int(override.get("register_count", args.register_count))
            register_type = int(override.get("register_type", args.register_type))
            string_value_format = int(
                override.get("string_value_format", args.string_value_format)
            )
            value_format = int(override.get("value_format", args.value_format))
            register_start_address = int(
                override.get("register_start_address", args.register_start_address)
            )
            register_step = int(override.get("register_step", args.register_step))

            template_groups = template_slave.get("RegisterGroupModels", [])
            rebuilt_groups: list[dict[str, Any]] = []
            for group_index in range(group_count):
                template_group = template_groups[group_index % len(template_groups)]
                if not isinstance(template_group, dict):
                    raise ValueError("Template register group must be a JSON object.")
                group_name = (
                    template_group.get("GroupName")
                    if group_count == 1
                    else f"{override.get('group_name_prefix', args.group_name_prefix)}{group_index + 1}"
                )
                rebuilt_groups.append(
                    clone_group(
                        template_group,
                        group_name=str(group_name),
                        register_count=register_count,
                        start_address=register_start_address,
                        step=register_step,
                        register_type=register_type,
                        string_value_format=string_value_format,
                        value_format=value_format,
                        next_value=make_value_factory(
                            bool(slave["UserRandomValue"]), args.seed
                        ),
                    )
                )
            slave["RegisterGroupModels"] = rebuilt_groups

    if args.replace_existing:
        workspace["SlaveModels"] = generated_slaves
    else:
        existing_by_id, existing_order = index_existing_slaves(
            workspace.get("SlaveModels", [])
        )
        for slave in generated_slaves:
            existing_by_id[slave["SlaveId"]] = slave

        if args.keep_original_order:
            merged: list[dict[str, Any]] = []
            seen: set[int] = set()
            for slave in existing_order:
                slave_id = slave["SlaveId"]
                merged.append(existing_by_id[slave_id])
                seen.add(slave_id)
            for slave_id in sorted(existing_by_id):
                if slave_id not in seen:
                    merged.append(existing_by_id[slave_id])
            workspace["SlaveModels"] = merged
        else:
            workspace["SlaveModels"] = [
                existing_by_id[key] for key in sorted(existing_by_id)
            ]

    output_path = args.input if args.inplace else args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump([workspace], f, ensure_ascii=False, separators=(",", ":"))

    print(f"Wrote {output_path} with {len(workspace['SlaveModels'])} slaves.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
