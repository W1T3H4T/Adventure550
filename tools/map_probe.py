#!/usr/bin/env python3
"""Probe Adventure550 navigation and emit a discovered map.

The script reads room text from adventure.text and repeatedly launches the game
with scripted commands to discover movement transitions.

Outputs:
- JSON graph with discovered nodes/edges.
- Mermaid flowchart for visual review and regression planning.

This is intentionally conservative and deterministic: each probe starts from a
fresh process, applies a bootstrap command sequence, replays a known path, then
tries one candidate movement command.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


ROOM_LINE_RE = re.compile(r"^(\d+)\t(.+)$")

LOCATION_PREFIXES = (
    "You are ",
    "You're ",
    "At your feet ",
    "This is ",
    "The stream flows ",
    "The canyon ",
    "A large stalactite ",
    "Dead end",
    "You have climbed ",
    "You have crawled ",
)

EXCLUDED_PROMPTS = {
    "There are some keys on the ground here.",
    "There is no way to go that direction.",
    "You are wandering aimlessly through the forest.",
}

# Canonical movement commands to probe.
MOVE_COMMANDS = ["n", "s", "e", "w", "u", "d", "in", "out", "enter"]
LOOK_AFTER_COMMANDS = set(MOVE_COMMANDS + ["unlock grate", "open grate", "enter"])

# Magic travel words and common variants to probe.
MAGIC_COMMANDS = ["xyzzy", "xyxxy", "plugh"]

KEYWORD_TO_COMMANDS = [
    ("north", ["n"]),
    ("south", ["s"]),
    ("east", ["e"]),
    ("west", ["w"]),
    ("n/s", ["n", "s"]),
    ("e/w", ["e", "w"]),
    ("up", ["u"]),
    ("down", ["d"]),
    ("climb", ["u", "d"]),
    ("stairs", ["d", "u"]),
    ("staircase", ["d", "u"]),
    ("pit", ["d", "u"]),
    ("hole", ["d", "u"]),
    ("crawl", ["in", "out"]),
    ("canyon", ["n", "s", "e", "w"]),
    ("passage", ["n", "s", "e", "w"]),
    ("enters", ["in"]),
    ("inside", ["in", "enter"]),
    ("out", ["out"]),
    ("xyzz", ["xyzzy"]),
    ("plugh", ["plugh"]),
]

FAILED_MOVE_SNIPPETS = (
    "There is no way to go that direction.",
    "You don't fit through",
    "The crack is far too small",
    "You can't get by the snake.",
    "You are wandering aimlessly through the forest.",
)

# We probe from a prepared state where the player has lamp+keys and lamp is on.
BOOTSTRAP_COMMANDS = ["no", "enter", "take lamp", "take keys", "on", "out"]

# Required non-movement actions at specific rooms to keep traversal valid.
ROOM_PRE_ACTIONS: Dict[int, List[str]] = {
    8: ["unlock grate", "open grate"],
}

TREASURE_CANDIDATES = [
    "nugget",
    "coins",
    "jewelry",
    "diamonds",
    "silver",
    "gold",
    "bars",
    "vase",
    "emerald",
    "ruby",
    "chest",
    "eggs",
    "trident",
]

DEATH_SNIPPETS = (
    "You are at the bottom of the pit with a broken neck.",
    "You didn't make it.",
    "You fell into a pit and broke every bone in your body!",
)

REVERSE_MOVE = {
    "n": "s",
    "s": "n",
    "e": "w",
    "w": "e",
    "u": "d",
    "d": "u",
    "in": "out",
    "out": "in",
    "enter": "out",
}


def parse_room_prompts(text_path: Path) -> Dict[int, str]:
    """Extract the first description line for each room id from adventure.text."""
    prompts: Dict[int, str] = {}
    for raw in text_path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = ROOM_LINE_RE.match(raw)
        if not match:
            continue
        room_id = int(match.group(1))
        room_line = match.group(2).strip()
        # The first 1000-ish numeric entries contain room text and related data.
        # We keep short, human-facing location lines.
        if room_id in prompts:
            continue
        if not room_line:
            continue
        if room_line.startswith("%"):
            continue
        if room_line[0].islower():
            continue
        if room_line in EXCLUDED_PROMPTS:
            continue
        if not room_line.startswith(LOCATION_PREFIXES):
            continue
        prompts[room_id] = room_line
    return prompts


def run_game(exe_path: Path, cwd: Path, commands: Iterable[str], timeout: int) -> str:
    """Run adventure.exe once with scripted commands and return stdout."""
    script = "\n".join(commands)
    if not script.endswith("\n"):
        script += "\n"
    # Always terminate the run deterministically.
    script += "quit\nyes\n"

    result = subprocess.run(
        [str(exe_path)],
        input=script,
        text=True,
        capture_output=True,
        cwd=str(cwd),
        timeout=timeout,
        check=False,
    )
    return result.stdout


def inject_look_commands(commands: Iterable[str]) -> List[str]:
    """Expand command sequence by inserting look after navigation/state actions."""
    expanded: List[str] = []
    for cmd in commands:
        expanded.append(cmd)
        if cmd in LOOK_AFTER_COMMANDS:
            expanded.append("look")
    return expanded


def unique_preserve_order(items: Iterable[str]) -> List[str]:
    seen: set[str] = set()
    ordered: List[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def get_room_context_segment(output: str, room_prompt: str) -> str:
    """Return the trailing output segment anchored at the current room prompt."""
    idx = output.lower().rfind(room_prompt.lower())
    if idx == -1:
        return output.lower()
    return output[idx:].lower()


def commands_from_look_context(output: str, room_prompt: str) -> List[str]:
    """Extract likely next commands from room description context."""
    segment = get_room_context_segment(output, room_prompt)
    candidates: List[str] = []
    for keyword, cmds in KEYWORD_TO_COMMANDS:
        if keyword in segment:
            candidates.extend(cmds)
    # Always keep magic words in the candidate pool.
    candidates.extend(MAGIC_COMMANDS)
    # Fall back to core movement probes after context-derived commands.
    candidates.extend(MOVE_COMMANDS)
    return unique_preserve_order(candidates)


def detect_last_room_id(output: str, room_prompts: Dict[int, str]) -> int | None:
    """Return the last room id whose prompt appears in output."""
    best_pos = -1
    best_room: int | None = None
    for room_id, prompt in room_prompts.items():
        pos = output.rfind(prompt)
        if pos > best_pos:
            best_pos = pos
            best_room = room_id
    return best_room


def short_label(room_id: int, prompt: str) -> str:
    # Mermaid labels are cleaner when kept short.
    label = prompt
    if len(label) > 42:
        label = label[:39].rstrip() + "..."
    return f"{room_id}: {label}"


@dataclass
class Edge:
    src: int
    command: str
    dst: int


@dataclass
class NodePath:
    commands: List[str]
    rooms: List[int]


def is_failed_move(output: str) -> bool:
    """Return True when output indicates an invalid/failed move."""
    return any(snippet in output for snippet in FAILED_MOVE_SNIPPETS)


def is_dead_output(output: str) -> bool:
    """Return True when output indicates player death."""
    return any(snippet in output for snippet in DEATH_SNIPPETS)


def has_inventory_item(output: str, item_keyword: str) -> bool:
    """Check if inventory listing contains the requested item keyword."""
    lower = output.lower()
    inventory_idx = lower.rfind("you are currently holding the following")
    if inventory_idx == -1:
        return False
    snippet = lower[inventory_idx: inventory_idx + 500]
    return item_keyword.lower() in snippet


def build_return_moves(forward_moves: List[str]) -> List[str] | None:
    """Build a reverse movement path when all moves are reversible."""
    backtrack: List[str] = []
    for move in reversed(forward_moves):
        reverse = REVERSE_MOVE.get(move)
        if reverse is None:
            return None
        backtrack.append(reverse)
    return backtrack


def replay_with_rooms(
    exe_path: Path,
    cwd: Path,
    room_prompts: Dict[int, str],
    path: NodePath,
    timeout: int,
) -> tuple[int | None, str]:
    """Replay full scripted path and return final room + output."""
    output = run_game(
        exe_path,
        cwd,
        inject_look_commands(BOOTSTRAP_COMMANDS + path.commands),
        timeout,
    )
    return detect_last_room_id(output, room_prompts), output


def discover_graph(
    exe_path: Path,
    cwd: Path,
    room_prompts: Dict[int, str],
    max_hops: int,
    timeout: int,
) -> Tuple[int, Dict[int, NodePath], List[Edge]]:
    """Breadth-first probe over movement commands to build a map graph."""
    start_output = run_game(exe_path, cwd, BOOTSTRAP_COMMANDS, timeout)
    start_room = detect_last_room_id(start_output, room_prompts)
    if start_room is None:
        raise RuntimeError("Could not detect start room from bootstrap run.")

    path_by_room: Dict[int, NodePath] = {
        start_room: NodePath(commands=[], rooms=[start_room])
    }
    queue: deque[int] = deque([start_room])
    seen_edges: set[Tuple[int, str, int]] = set()
    edges: List[Edge] = []

    while queue:
        room_id = queue.popleft()
        node_path = path_by_room[room_id]
        if len(node_path.rooms) - 1 >= max_hops:
            continue

        pre_actions = ROOM_PRE_ACTIONS.get(room_id, [])
        context_output = run_game(
            exe_path,
            cwd,
            inject_look_commands(BOOTSTRAP_COMMANDS + node_path.commands + pre_actions),
            timeout,
        )
        room_prompt = room_prompts.get(room_id, "")
        candidate_commands = commands_from_look_context(context_output, room_prompt)

        for cmd in candidate_commands:
            probe_commands = inject_look_commands(
                BOOTSTRAP_COMMANDS + node_path.commands + pre_actions + [cmd]
            )
            output = run_game(exe_path, cwd, probe_commands, timeout)
            if is_failed_move(output):
                continue
            dst = detect_last_room_id(output, room_prompts)
            if dst is None:
                continue
            if dst == room_id:
                # Drop no-op transitions so output contains only meaningful moves.
                continue

            edge_key = (room_id, cmd, dst)
            if edge_key not in seen_edges:
                seen_edges.add(edge_key)
                edges.append(Edge(src=room_id, command=cmd, dst=dst))

            if dst not in path_by_room:
                new_commands = node_path.commands + pre_actions + [cmd]
                new_rooms = node_path.rooms + [dst]
                candidate = NodePath(commands=new_commands, rooms=new_rooms)
                final_room, _ = replay_with_rooms(
                    exe_path, cwd, room_prompts, candidate, timeout
                )
                if final_room != dst:
                    continue
                path_by_room[dst] = candidate
                queue.append(dst)

    return start_room, path_by_room, edges


def write_mermaid(
    out_path: Path,
    start_room: int,
    room_prompts: Dict[int, str],
    discovered_rooms: Iterable[int],
    edges: List[Edge],
) -> None:
    """Write Mermaid flowchart showing discovered transitions."""
    rooms = sorted(set(discovered_rooms))
    node_ids = {rid: f"R{rid}" for rid in rooms}

    lines: List[str] = []
    lines.append("# Discovered Adventure Graph")
    lines.append("")
    lines.append("```mermaid")
    lines.append("flowchart TD")
    for rid in rooms:
        label = short_label(rid, room_prompts.get(rid, f"Room {rid}"))
        lines.append(f"  {node_ids[rid]}[{label}]")

    lines.append("")
    lines.append("  %% Start room after bootstrap")
    lines.append(f"  START((Start)) --> {node_ids[start_room]}")

    lines.append("")
    lines.append("  %% Discovered transitions")
    transition_commands: Dict[Tuple[int, int], List[str]] = {}
    for edge in edges:
        key = (edge.src, edge.dst)
        transition_commands.setdefault(key, [])
        if edge.command not in transition_commands[key]:
            transition_commands[key].append(edge.command)

    for (src, dst), commands in sorted(transition_commands.items()):
        if src not in node_ids or dst not in node_ids:
            continue
        label = "/".join(commands)
        lines.append(f"  {node_ids[src]} -->|{label}| {node_ids[dst]}")

    lines.append("```")
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- Graph reflects deterministic probes from a fresh process each time.")
    lines.append("- Bootstrap commands: no, enter, take lamp, take keys, on, out.")
    lines.append("- Candidate commands are prioritized from look context.")
    lines.append("- Magic words (xyzzy/xyxxy/plugh) are included in probing.")
    lines.append("- Increase --max-hops for broader exploration (runtime grows quickly).")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_json(
    out_path: Path,
    start_room: int,
    room_prompts: Dict[int, str],
    path_by_room: Dict[int, NodePath],
    edges: List[Edge],
) -> None:
    transition_commands: Dict[Tuple[int, int], List[str]] = {}
    for edge in edges:
        key = (edge.src, edge.dst)
        transition_commands.setdefault(key, [])
        if edge.command not in transition_commands[key]:
            transition_commands[key].append(edge.command)

    data = {
        "start_room": start_room,
        "rooms": {
            str(rid): {
                "prompt": room_prompts.get(rid, ""),
                "path": path_by_room[rid].commands,
                "room_path": path_by_room[rid].rooms,
            }
            for rid in sorted(path_by_room)
        },
        "transitions": [
            {
                "src": src,
                "dst": dst,
                "commands": commands,
            }
            for (src, dst), commands in sorted(transition_commands.items())
        ],
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def write_clear_paths(
    out_path: Path,
    start_room: int,
    room_prompts: Dict[int, str],
    path_by_room: Dict[int, NodePath],
) -> None:
    """Write clean shortest paths (no failed commands) from start to each room."""
    lines: List[str] = []
    lines.append("# Discovered Clear Paths")
    lines.append("")
    lines.append("All routes below are shortest successful command paths discovered from")
    lines.append("the bootstrap start state. Failed or no-op moves are excluded.")
    lines.append("")
    start_prompt = room_prompts.get(start_room, f"Room {start_room}")
    lines.append(f"Start room: {start_room} - {start_prompt}")
    lines.append("")

    for rid in sorted(path_by_room):
        if rid == start_room:
            continue
        prompt = room_prompts.get(rid, f"Room {rid}")
        path = path_by_room[rid].commands
        cmd_text = " -> ".join(path)
        lines.append(f"- Room {rid}: {prompt}")
        lines.append(f"  Path: {cmd_text}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_clean_script(
    out_path: Path,
    start_room: int,
    room_prompts: Dict[int, str],
    path_by_room: Dict[int, NodePath],
) -> None:
    """Write a single clean script to the deepest discovered room and back."""
    if not path_by_room:
        return

    deepest_room = max(
        path_by_room,
        key=lambda rid: (len(path_by_room[rid].rooms), rid),
    )
    target = path_by_room[deepest_room]
    backtrack: List[str] = []
    for move in reversed(target.commands):
        if move in REVERSE_MOVE:
            backtrack.append(REVERSE_MOVE[move])

    lines: List[str] = []
    lines.append("# Clean Probe Script")
    lines.append("")
    lines.append(f"# Start room: {start_room} - {room_prompts.get(start_room, '')}")
    lines.append(
        f"# Target room: {deepest_room} - {room_prompts.get(deepest_room, '')}"
    )
    lines.append("# Commands are validated successful steps from discovery output.")
    lines.append("")

    for cmd in BOOTSTRAP_COMMANDS:
        lines.append(cmd)
        if cmd in LOOK_AFTER_COMMANDS:
            lines.append("look")
    for cmd in target.commands:
        lines.append(cmd)
        if cmd in LOOK_AFTER_COMMANDS:
            lines.append("look")
    for cmd in backtrack:
        lines.append(cmd)
        if cmd in LOOK_AFTER_COMMANDS:
            lines.append("look")
    lines.append("score")
    lines.append("quit")
    lines.append("yes")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def find_treasure_route(
    exe_path: Path,
    cwd: Path,
    room_prompts: Dict[int, str],
    start_room: int,
    path_by_room: Dict[int, NodePath],
    timeout: int,
) -> tuple[NodePath, str, str] | None:
    """Find a validated treasure pickup + return-to-building route."""
    candidates = sorted(
        path_by_room.items(),
        key=lambda kv: (len(kv[1].rooms), kv[0]),
        reverse=True,
    )

    for room_id, node_path in candidates:
        if room_id == start_room:
            continue
        backtrack = build_return_moves(node_path.commands)
        if backtrack is None:
            continue

        for item in TREASURE_CANDIDATES:
            commands = (
                BOOTSTRAP_COMMANDS
                + node_path.commands
                + [f"take {item}", "inventory"]
                + backtrack
                + ["enter", f"drop {item}", "inventory", "score"]
            )
            output = run_game(exe_path, cwd, inject_look_commands(commands), timeout)

            if is_failed_move(output) or is_dead_output(output):
                continue
            if not has_inventory_item(output, item):
                continue
            if "You are inside a building" not in output:
                continue
            if "You scored" not in output:
                continue

            return node_path, item, output

    return None


def write_treasure_route_artifacts(
    script_path: Path,
    report_path: Path,
    start_room: int,
    room_prompts: Dict[int, str],
    route: NodePath,
    item: str,
) -> None:
    """Write a clean treasure-route script and human-readable report."""
    backtrack = build_return_moves(route.commands)
    if backtrack is None:
        return

    script_lines: List[str] = []
    script_lines.append("# Clean Treasure Route Script")
    script_lines.append("")
    script_lines.append(f"# Start room: {start_room}")
    script_lines.append(f"# Treasure item: {item}")
    script_lines.append("")
    for cmd in BOOTSTRAP_COMMANDS:
        script_lines.append(cmd)
        if cmd in LOOK_AFTER_COMMANDS:
            script_lines.append("look")
    for cmd in route.commands:
        script_lines.append(cmd)
        if cmd in LOOK_AFTER_COMMANDS:
            script_lines.append("look")
    script_lines.append(f"take {item}")
    script_lines.append("inventory")
    for cmd in backtrack:
        script_lines.append(cmd)
        if cmd in LOOK_AFTER_COMMANDS:
            script_lines.append("look")
    script_lines.append("enter")
    script_lines.append("look")
    script_lines.append(f"drop {item}")
    script_lines.append("inventory")
    script_lines.append("score")
    script_lines.append("quit")
    script_lines.append("yes")

    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text("\n".join(script_lines) + "\n", encoding="utf-8")

    report_lines: List[str] = []
    report_lines.append("# Discovered Treasure Route")
    report_lines.append("")
    report_lines.append(f"- Start room: {start_room} - {room_prompts.get(start_room, '')}")
    target_room = route.rooms[-1]
    report_lines.append(
        f"- Target room: {target_room} - {room_prompts.get(target_room, '')}"
    )
    report_lines.append(f"- Treasure command: take {item}")
    report_lines.append(f"- Forward path: {' -> '.join(route.commands)}")
    report_lines.append(f"- Return path: {' -> '.join(backtrack)}")
    report_lines.append("")
    report_lines.append(
        f"Script: {script_path.relative_to(report_path.parent.parent).as_posix()}"
    )

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe Adventure navigation graph")
    parser.add_argument(
        "--exe",
        default="build/adventure.exe",
        help="Path to adventure executable",
    )
    parser.add_argument(
        "--cwd",
        default=".",
        help="Working directory for the game process",
    )
    parser.add_argument(
        "--text",
        default="adventure.text",
        help="Path to adventure.text",
    )
    parser.add_argument(
        "--max-hops",
        "--max-depth",
        dest="max_hops",
        type=int,
        default=6,
        help="Maximum discovered movement hops from bootstrap start",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=20,
        help="Per-run timeout in seconds",
    )
    parser.add_argument(
        "--out-mermaid",
        default="docs/discovered-map-mermaid.md",
        help="Output markdown file containing mermaid graph",
    )
    parser.add_argument(
        "--out-json",
        default="build/discovered-map.json",
        help="Output JSON graph file",
    )
    parser.add_argument(
        "--out-paths",
        default="docs/discovered-clear-paths.md",
        help="Output markdown containing clear shortest paths",
    )
    parser.add_argument(
        "--out-script",
        default="tests/discovered_clean_route_input.txt",
        help="Output command script containing a clean route and return",
    )
    parser.add_argument(
        "--objective-treasure",
        action="store_true",
        help="Attempt to discover a validated treasure pickup-and-return route",
    )
    parser.add_argument(
        "--out-treasure-script",
        default="tests/discovered_treasure_route_input.txt",
        help="Output command script for a discovered treasure route",
    )
    parser.add_argument(
        "--out-treasure-report",
        default="docs/discovered-treasure-route.md",
        help="Output markdown report for treasure-route discovery",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    exe_path = Path(args.exe).resolve()
    text_path = Path(args.text).resolve()
    cwd = Path(args.cwd).resolve()
    out_mermaid = Path(args.out_mermaid).resolve()
    out_json = Path(args.out_json).resolve()
    out_paths = Path(args.out_paths).resolve()
    out_script = Path(args.out_script).resolve()
    out_treasure_script = Path(args.out_treasure_script).resolve()
    out_treasure_report = Path(args.out_treasure_report).resolve()

    if not exe_path.is_file():
        raise FileNotFoundError(f"Executable not found: {exe_path}")
    if not text_path.is_file():
        raise FileNotFoundError(f"Text file not found: {text_path}")

    prompts = parse_room_prompts(text_path)
    start_room, path_by_room, edges = discover_graph(
        exe_path=exe_path,
        cwd=cwd,
        room_prompts=prompts,
        max_hops=args.max_hops,
        timeout=args.timeout,
    )

    write_json(out_json, start_room, prompts, path_by_room, edges)
    write_mermaid(out_mermaid, start_room, prompts, path_by_room.keys(), edges)
    write_clear_paths(out_paths, start_room, prompts, path_by_room)
    write_clean_script(out_script, start_room, prompts, path_by_room)

    if args.objective_treasure:
        found = find_treasure_route(
            exe_path=exe_path,
            cwd=cwd,
            room_prompts=prompts,
            start_room=start_room,
            path_by_room=path_by_room,
            timeout=args.timeout,
        )
        if found is not None:
            route, item, _ = found
            write_treasure_route_artifacts(
                script_path=out_treasure_script,
                report_path=out_treasure_report,
                start_room=start_room,
                room_prompts=prompts,
                route=route,
                item=item,
            )
            print(f"Treasure route: found ({item})")
            print(f"Treasure script: {out_treasure_script}")
            print(f"Treasure report: {out_treasure_report}")
        else:
            out_treasure_report.parent.mkdir(parents=True, exist_ok=True)
            out_treasure_report.write_text(
                "# Discovered Treasure Route\n\n"
                "No validated treasure pickup-and-return route was found at this depth.\n"
                "Increase --max-hops and rerun with --objective-treasure.\n",
                encoding="utf-8",
            )
            print("Treasure route: not found")
            print(f"Treasure report: {out_treasure_report}")

    print(f"Discovered rooms: {len(path_by_room)}")
    print(f"Discovered edges: {len(edges)}")
    print(f"JSON: {out_json}")
    print(f"Mermaid: {out_mermaid}")
    print(f"Clear paths: {out_paths}")
    print(f"Clean script: {out_script}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
