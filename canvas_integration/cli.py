import argparse
import sys

from .client import CanvasClient, CanvasError


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="canvas", description="UT Austin Canvas CLI")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("whoami")
    sub.add_parser("courses")
    sub.add_parser("todo")
    for name in ("assignments", "announcements"):
        s = sub.add_parser(name)
        s.add_argument("course_id", type=int)
    args = p.parse_args(argv)
    try:
        c = CanvasClient()
        if args.cmd == "whoami":
            u = c.me()
            print(f"{u['name']} (id {u['id']})")
        elif args.cmd == "courses":
            for x in c.courses():
                print(f"{x['id']}\t{x.get('name', '?')}")
        elif args.cmd == "assignments":
            for x in c.assignments(args.course_id):
                print(f"{x['id']}\t{x.get('due_at') or '-'}\t{x['name']}")
        elif args.cmd == "announcements":
            for x in c.announcements(args.course_id):
                print(f"{x.get('posted_at', '-')}\t{x['title']}")
        elif args.cmd == "todo":
            for x in c.todo():
                a = x.get("assignment", {})
                print(f"{a.get('due_at') or '-'}\t{a.get('name', x.get('type'))}")
    except CanvasError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
