import subprocess, sys, re, random, signal, shutil

REAL = shutil.os.environ.get("PING_BIN") or next(
    (p for p in ("/usr/bin/ping", "/bin/ping") if shutil.os.path.exists(p)), shutil.which("ping"))
Y, R, G, D, X = "\033[93m", "\033[91m", "\033[92m", "\033[2m", "\033[0m"

def fast(host, ms):
    return random.choice([
        f"{host} replied in {ms}ms!! they're not mad at me :)",
        f"{ms}ms. they still care. they STILL care.",
        f"ok {host} answered. we're good. we're so good.",
    ])

def slow(host, ms):
    return random.choice([
        f"{ms}ms?? they took {ms}ms to answer me. did I say something wrong",
        f"{host} is typing... {ms}ms... that's longer than usual...",
        f"{ms}ms. they replied but it felt cold. was it the TTL",
    ])

LOST = [
    "no reply. they left me on read.",
    "packet lost. was it me? it was me wasn't it",
    "they're ignoring me. i KNOW they got it.",
    "maybe they're just busy. maybe they're with another client.",
    "should i send another? is that needy? i'm sending another.",
]
SPIRAL = "{n} packets in a row. they've blocked me. i'm going to traceroute their house."
SEQ_GAP = re.compile(r"icmp_seq=(\d+)")
TIME = re.compile(r"time=([\d.]+)")

def main():
    args = sys.argv[1:]
    if not args:
        print("ping who? you have no one to ping. that's ok. me neither.")
        return 2
    if not REAL:
        print("i can't even find ping. install iputils-ping. i'm so alone.")
        return 2
    host = next((a for a in reversed(args) if not a.startswith("-")), "them")
    print(f"{D}reaching out to {host}... please answer please answer please answer{X}")
    proc = subprocess.Popen([REAL, "-O"] + args, stdout=subprocess.PIPE, text=True)
    signal.signal(signal.SIGINT, lambda *_: proc.terminate())
    lost = rtts = 0
    total = []
    for line in proc.stdout:
        t = TIME.search(line)
        if t:
            ms = float(t.group(1))
            total.append(ms)
            lost = 0
            print(f"{G if ms < 60 else Y}{(fast if ms < 60 else slow)(host, round(ms))}{X}")
        elif "no answer yet" in line or "Unreachable" in line or "timeout" in line.lower():
            lost += 1
            print(f"{R}{SPIRAL.format(n=lost) if lost >= 3 else random.choice(LOST)}{X}")
        elif "unknown host" in line.lower() or "Name or service" in line:
            print(f"{R}{host} doesn't exist. were they ever real?{X}")
    proc.wait()
    print()
    if total:
        avg = sum(total) / len(total)
        print(f"{D}conversation summary: {len(total)} replies, avg {avg:.1f}ms.{X}")
        print("they do love me." if avg < 60 else "it's fine. it's FINE. they're just slow. right?")
    else:
        print(f"{R}0 replies. i'm going to go lie down.{X}")
    return proc.returncode

if __name__ == "__main__":
    sys.exit(main())
