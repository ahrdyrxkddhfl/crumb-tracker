"""crumb CLI. 지금은 수집이 제대로 되는지 눈으로 확인하는 용도만 있다.

요약·세션화는 실제 로그를 며칠 쌓아본 다음에 붙인다.
"""

import argparse
import sqlite3
import sys

from crumb.record import DB_PATH


def cmd_status(args):
    if not DB_PATH.exists():
        print(f"DB 없음: {DB_PATH}")
        print("훅이 등록됐는지 확인하고 새 터미널을 열어보세요.")
        return 1

    conn = sqlite3.connect(DB_PATH)
    total = conn.execute("SELECT count(*) FROM events").fetchone()[0]
    print(f"DB: {DB_PATH}")
    print(f"총 이벤트: {total}")
    for source, n, fails in conn.execute(
        "SELECT source, count(*), sum(exit_code != 0) FROM events GROUP BY source"
    ):
        print(f"  {source:12} {n:6}건  실패 {fails or 0}건")
    conn.close()
    return 0


def cmd_tail(args):
    if not DB_PATH.exists():
        print(f"DB 없음: {DB_PATH}")
        return 1

    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT ts, source, exit_code, command FROM events"
        " ORDER BY id DESC LIMIT ?", (args.n,)
    ).fetchall()
    for ts, source, code, command in reversed(rows):
        mark = " " if code in (0, None) else "x"
        print(f"{mark} {ts[11:19]}  {source:11} {(command or '')[:70]}")
    conn.close()
    return 0


def main():
    parser = argparse.ArgumentParser(prog="crumb")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("status", help="수집 상태 확인")

    p_tail = sub.add_parser("tail", help="최근 이벤트 보기")
    p_tail.add_argument("-n", type=int, default=30)

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return 0

    return {"status": cmd_status, "tail": cmd_tail}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
