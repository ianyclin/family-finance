#!/usr/bin/env python3
import sys
import os
import json

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

EXCLUDE_SUBSTRINGS = ("<system-reminder>", "<task-notification>", "<command-name>")


def is_excluded_text(text):
    if not isinstance(text, str):
        return True
    for s in EXCLUDE_SUBSTRINGS:
        if s in text:
            return True
    if text.lstrip().startswith("This session is being continued"):
        return True
    return False


def extract_user_texts(obj):
    """Return list of qualifying text strings from a genuine user-typed message line."""
    if obj.get("type") != "user":
        return []
    if obj.get("isMeta"):
        return []
    if obj.get("isSidechain"):
        return []
    message = obj.get("message", {})
    if not isinstance(message, dict):
        return []
    content = message.get("content")
    texts = []
    if isinstance(content, str):
        texts.append(content)
    elif isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                t = block.get("text")
                if isinstance(t, str):
                    texts.append(t)
    result = []
    for t in texts:
        if not is_excluded_text(t):
            result.append(t)
    return result


def process_file(path):
    basename = os.path.basename(path)
    uuid8 = basename[:8]
    out_path = os.path.join(OUTPUT_DIR, f"user-msgs-{uuid8}.txt")

    stats = {
        "first_timestamp": None,
        "last_timestamp": None,
        "user_msg_count": 0,
        "assistant_msg_count": 0,
        "agent_task_tool_use_count": 0,
        "subagent_type_counts": {},
        "parse_error_count": 0,
    }

    line_count = 0
    with open(path, "r", encoding="utf-8", errors="replace") as f, \
         open(out_path, "w", encoding="utf-8") as out:
        for line in f:
            line_count += 1
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                stats["parse_error_count"] += 1
                continue

            ts = obj.get("timestamp")
            if ts:
                if stats["first_timestamp"] is None:
                    stats["first_timestamp"] = ts
                stats["last_timestamp"] = ts

            otype = obj.get("type")

            if otype == "assistant":
                stats["assistant_msg_count"] += 1
                message = obj.get("message", {})
                if isinstance(message, dict):
                    content = message.get("content")
                    if isinstance(content, list):
                        for block in content:
                            if isinstance(block, dict) and block.get("type") == "tool_use":
                                name = block.get("name")
                                if name in ("Agent", "Task"):
                                    stats["agent_task_tool_use_count"] += 1
                                    inp = block.get("input", {})
                                    if not isinstance(inp, dict):
                                        inp = {}
                                    subtype = inp.get("subagent_type", "UNSPECIFIED")
                                    if subtype is None:
                                        subtype = "UNSPECIFIED"
                                    stats["subagent_type_counts"][subtype] = \
                                        stats["subagent_type_counts"].get(subtype, 0) + 1

            if otype == "user":
                texts = extract_user_texts(obj)
                for t in texts:
                    stats["user_msg_count"] += 1
                    ts_line = ts if ts else "NO_TIMESTAMP"
                    out.write(f"{ts_line}\n")
                    out.write(t[:1500])
                    out.write("\n----\n")

    print(f"{basename}: {line_count} lines processed", file=sys.stderr)
    return basename, stats


def main():
    paths = sys.argv[1:]
    if not paths:
        print("usage: extract_user_msgs.py <jsonl> [<jsonl> ...]", file=sys.stderr)
        sys.exit(1)

    all_stats = {}
    for path in paths:
        basename, stats = process_file(path)
        all_stats[basename] = stats

    stats_path = os.path.join(OUTPUT_DIR, "stats.json")
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(all_stats, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
