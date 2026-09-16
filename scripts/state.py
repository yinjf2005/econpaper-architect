#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EconPaper Architect · 状态机
----------------------------
管理 S0–S9 阶段推进、D-1~D-10 决策确认与决策日志落盘（映射手册第八部分 Skill 1）。

用法:
  python state.py init <项目名> [--dir <输出根目录>]   # 初始化项目与 state.json
  python state.py show                                 # 查看当前状态
  python state.py set-stage <S0..S9>                    # 推进阶段（校验跳步）
  python state.py log <决策项> <内容> <依据>            # 记录决策（默认待确认）
  python state.py confirm <决策项> [--note <备注>]      # 确认某项决策
  python state.py unconfirm <决策项>                    # 撤销确认（用户说"我改一下"）
  python state.py set-track <标准|快通道>               # 设置轨道
  python state.py note <文本>                           # 追加自由备注

状态文件默认位于 ./econpaper-output/<项目名>/state.json，
可用环境变量 ECONPAPER_STATE 指定绝对路径以跨目录续跑。
"""
import os
import sys
import json
import argparse
import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

STAGES = ["S0", "S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9"]
DECISIONS = ["D-1", "D-2", "D-3", "D-4", "D-5", "D-6", "D-7", "D-8", "D-9", "D-10"]
DEFAULT_ROOT = "econpaper-output"


def state_path():
    env = os.environ.get("ECONPAPER_STATE")
    if env:
        return os.path.abspath(env)
    here = os.path.join(os.getcwd(), DEFAULT_ROOT)
    if not os.path.isdir(here):
        return None
    # 取该目录下唯一/最近修改的项目
    subs = [d for d in os.listdir(here) if os.path.isdir(os.path.join(here, d))]
    if not subs:
        return None
    subs.sort(key=lambda d: os.path.getmtime(os.path.join(here, d)), reverse=True)
    return os.path.join(here, subs[0], "state.json")


def load(path):
    if not path or not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, st):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=2)


def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def cmd_init(args):
    env = os.environ.get("ECONPAPER_STATE")
    if env:
        proj_dir = os.path.dirname(os.path.abspath(env))
    else:
        root = args.dir or os.path.join(os.getcwd(), DEFAULT_ROOT)
        proj_dir = os.path.join(root, args.name)
    os.makedirs(os.path.join(proj_dir, "sections"), exist_ok=True)
    os.makedirs(os.path.join(proj_dir, "figures"), exist_ok=True)
    path = os.path.join(proj_dir, "state.json")
    st = dict(
        project=args.name,
        track="标准",
        stage="S0",
        created=now(),
        updated=now(),
        decisions={d: {"content": None, "basis": None, "confirmed": False, "note": None} for d in DECISIONS},
        log=[],
        notes=[],
    )
    save(path, st)
    print(f"✔ 项目已初始化：{proj_dir}")
    print(f"✔ state.json：{path}")
    print(f"  续跑请设置： export ECONPAPER_STATE=\"{path}\"  (PowerShell: $env:ECONPAPER_STATE=\"{path}\")")


def require():
    path = state_path()
    st = load(path) if path else None
    if not path or st is None:
        print("✘ 未找到可用的 state.json。")
        print("  处理：先执行 `python state.py init <项目名>`，")
        print("        或设置环境变量 ECONPAPER_STATE 指向已存在的 state.json 绝对路径后重试。")
        sys.exit(1)
    return path, st


def cmd_show(args):
    path, st = require()
    print(f"项目：{st['project']}   轨道：{st['track']}   当前阶段：{st['stage']}")
    print(f"state.json：{path}")
    print("\n— 决策状态 —")
    for d in DECISIONS:
        v = st["decisions"][d]
        mark = "✔" if v.get("confirmed") else "·"
        content = v.get("content") or "（未定）"
        basis = v.get("basis") or ""
        print(f"  [{mark}] {d}: {content}" + (f"   —— {basis}" if basis else ""))
    pending = [d for d in DECISIONS if not st["decisions"][d].get("confirmed")]
    print(f"\n待确认：{', '.join(pending) if pending else '无'}")
    if st["log"]:
        print("\n— 决策日志 —")
        for i, e in enumerate(st["log"], 1):
            flag = "✔" if e.get("confirmed") else "·"
            print(f"  {i}. [{flag}] {e['time']} {e['item']} | {e['content']} | 依据：{e['basis']}"
                  + (f" | 备注：{e['note']}" if e.get("note") else ""))
    if st["notes"]:
        print("\n— 备注 —")
        for n in st["notes"]:
            print(f"  · {n['time']} {n['text']}")


def cmd_set_stage(args):
    path, st = require()
    target = args.stage.upper()
    if target not in STAGES:
        print(f"✘ 非法阶段：{target}。合法值：{' '.join(STAGES)}")
        sys.exit(1)
    cur = st["stage"]
    if STAGES.index(target) > STAGES.index(cur) + 1 and st["track"] == "标准":
        print(f"⚠ 标准模式不得跳步：当前 {cur}，请求 {target}（将跳过中间阶段）。")
        print("  若确需跳步，请先执行： set-track 快通道 —— 或由用户明确授权后重试。")
        sys.exit(2)
    st["stage"] = target
    st["updated"] = now()
    st["log"].append({"time": now(), "item": "阶段", "content": f"{cur} → {target}",
                      "basis": "手册 §2.1", "confirmed": True, "note": args.note})
    save(path, st)
    print(f"✔ 阶段推进：{cur} → {target}")


def cmd_log(args):
    path, st = require()
    item = args.item.upper() if args.item.upper() in DECISIONS or args.item.upper() == "STAGE" else args.item
    entry = {"time": now(), "item": item, "content": args.content, "basis": args.basis,
             "confirmed": False, "note": args.note}
    st["log"].append(entry)
    if item in st["decisions"]:
        st["decisions"][item].update({"content": args.content, "basis": args.basis, "confirmed": False,
                                      "note": args.note})
    st["updated"] = now()
    save(path, st)
    print(f"✔ 已记录（待确认）：{item} | {args.content} | 依据：{args.basis}")


def cmd_confirm(args):
    path, st = require()
    item = args.item.upper()
    if item in st["decisions"]:
        st["decisions"][item]["confirmed"] = True
        if args.note:
            st["decisions"][item]["note"] = args.note
    for e in reversed(st["log"]):
        if e["item"] == item:
            e["confirmed"] = True
            if args.note:
                e["note"] = args.note
            break
    st["updated"] = now()
    save(path, st)
    print(f"✔ 已确认：{item}")


def cmd_unconfirm(args):
    path, st = require()
    item = args.item.upper()
    if item in st["decisions"]:
        st["decisions"][item]["confirmed"] = False
    st["updated"] = now()
    save(path, st)
    print(f"↩ 已撤销确认：{item}（需重新确认）")


def cmd_set_track(args):
    path, st = require()
    st["track"] = args.track
    st["updated"] = now()
    save(path, st)
    print(f"✔ 轨道已设为：{args.track}"
          + ("（启用前须向用户说明：快通道属手册未覆盖情形）" if args.track == "快通道" else ""))


def cmd_note(args):
    path, st = require()
    st["notes"].append({"time": now(), "text": args.text})
    st["updated"] = now()
    save(path, st)
    print("✔ 备注已追加")


def main():
    ap = argparse.ArgumentParser(description="EconPaper Architect 状态机")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init")
    p.add_argument("name")
    p.add_argument("--dir")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("show")
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("set-stage")
    p.add_argument("stage")
    p.add_argument("--note")
    p.set_defaults(func=cmd_set_stage)

    p = sub.add_parser("log")
    p.add_argument("item")
    p.add_argument("content")
    p.add_argument("basis")
    p.add_argument("--note")
    p.set_defaults(func=cmd_log)

    p = sub.add_parser("confirm")
    p.add_argument("item")
    p.add_argument("--note")
    p.set_defaults(func=cmd_confirm)

    p = sub.add_parser("unconfirm")
    p.add_argument("item")
    p.set_defaults(func=cmd_unconfirm)

    p = sub.add_parser("set-track")
    p.add_argument("track", choices=["标准", "快通道"])
    p.set_defaults(func=cmd_set_track)

    p = sub.add_parser("note")
    p.add_argument("text")
    p.set_defaults(func=cmd_note)

    args = ap.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
