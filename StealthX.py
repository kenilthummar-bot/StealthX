#!/usr/bin/env python3
"""
StealthX — Cinematic Cyber Toolkit  
Developer: Kenil Thummar  
"""

# ============================================
# Imports
# ============================================
import os
import re
import secrets
import string
import math
import subprocess
import time
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "zxcvbn"))
# Add local zxcvbn folder to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "zxcvbn"))

# Safe import of zxcvbn
try:
    from zxcvbn import zxcvbn
except Exception as e:
    print("ERROR: Unable to load local zxcvbn module:", e)
    print("Make sure the 'zxcvbn' folder is next to StealthX.py")
    exit()

from colorama import Fore, init as colorama_init
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich.box import ROUNDED

colorama_init(autoreset=True)
console = Console()

# ============================================
# SAFE CLEAR SCREEN
# ============================================
def clear_screen():
    
    try:
        os.system("clear")
    except:
        pass


# ============================================
# CINEMATIC BANNER 
# ============================================
def print_banner():
   
    banner_raw = r"""
███████╗ ████████╗ ███████╗  █████╗  ██╗   ████████╗ ██╗  ██╗  ██╗  ██╗
██╔════╝ ╚══██╔══╝ ██╔════╝ ██╔══██╗ ██║   ╚══██╔══╝ ██║  ██║   ██╗██╔╝
███████╗    ██║    █████╗   ███████║ ██║      ██║    ███████║    ███╔╝
╚════██║    ██║    ██╔══╝   ██╔══██║ ██║      ██║    ██╔══██║   ██╔██╗
███████║    ██║    ███████╗ ██║  ██║ ███████╗ ██║    ██║  ██║  ██╔╝ ██╗
╚══════╝    ╚═╝    ╚══════╝ ╚═╝  ╚═╝ ╚══════╝ ╚═╝    ╚═╝  ╚═╝  ╚═╝  ╚═╝
"""
    banner = Text(banner_raw, style="bright_red bold")

    _, term_height = console.size
    banner_height = banner_raw.count("\n") + 1
    top_padding = max(0, int(term_height * 0.12) - (banner_height // 2))

    console.print("\n" * top_padding)
    console.print(Align.center(banner))
    console.print(Align.center(Text("CYBER PASSWORD ANALYSIS TOOLKIT", style="bright_red")))
    console.print()


# ============================================
# STRENGTH METER
# ============================================
def strength_meter(score):
    score = max(0, min(score, 4))
    labels = ["Very Weak", "Weak", "Fair", "Strong", "Very Strong"]
    bar = "■" * (score + 1) + "□" * (5 - (score + 1))
    colors = ["red", "red", "yellow", "green3", "bright_green"]
    return f"[{colors[score]}]{bar}[/]  {labels[score]}"


# ============================================
# REGEX CHECKS
# ============================================
def regex_strength(password):
    return {
        "Length ≥ 8": len(password) >= 8,
        "Uppercase Letters": bool(re.search(r"[A-Z]", password)),
        "Lowercase Letters": bool(re.search(r"[a-z]", password)),
        "Digits": bool(re.search(r"\d", password)),
        "Symbols": bool(re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\];:/]", password)),
    }


def print_regex_table(checks):
    console.print("\n[bold bright_red]>> REGEX CHECKS <<[/bold bright_red]\n")

    table = Table(show_header=True, header_style="bold bright_red", box=ROUNDED)
    table.add_column("Requirement")
    table.add_column("Status")

    for k, v in checks.items():
        icon = "[green]✔[/green]" if v else "[red]✘[/red]"
        table.add_row(k, icon)

    console.print(table)


# ============================================
# ZXCVBN ANALYSIS
# ============================================
def analyze_zxcvbn(password):
    try:
        return zxcvbn(password)
    except:
        return {
            "score": 0,
            "crack_times_display": {
                "online_throttling_100_per_hour": "unknown",
                "online_no_throttling_10_per_second": "unknown",
                "offline_slow_hashing_1e4_per_second": "unknown",
                "offline_fast_hashing_1e10_per_second": "unknown"
            },
            "feedback": {"warning": "", "suggestions": []}
        }


# ========
# ENTROPY
# ========
def estimate_entropy(password):
    pool = 0
    if re.search(r"[a-z]", password): pool += 26
    if re.search(r"[A-Z]", password): pool += 26
    if re.search(r"[0-9]", password): pool += 10
    if re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\];:/]", password): pool += 32
    if pool == 0: pool = 95
    return round(len(password) * math.log2(pool), 2)


# =================
# SUGGESTION ENGINE
# =================
SYMBOLS = "!@#$%^&*?_+~-"
ALL = string.ascii_letters + string.digits + SYMBOLS


def generate_suggestions(p):
    sug = []
    for _ in range(5):
        base = list(p)
        base.append(secrets.choice(SYMBOLS))
        base.insert(0, secrets.choice(string.ascii_uppercase))
        for i in range(len(base)):
            if base[i].isalpha() and secrets.randbelow(100) < 30:
                base[i] = base[i].upper()
        base.append(str(secrets.randbelow(90) + 10))
        sug.append("".join(base))
    return sug


# ==============
# PASSWORD CHECK
# ==============
def password_check(history):
    clear_screen()
    print_banner()

    while True:
        pwd = console.input("[cyan]Enter password ('0' to exit): [/cyan] ")

        if pwd in ("0", "exit"):
            return

        checks = regex_strength(pwd)
        z = analyze_zxcvbn(pwd)
        entropy = estimate_entropy(pwd)
        suggestions = generate_suggestions(pwd)

        console.print("\n[bold bright_red]>> PASSWORD SUMMARY <<[/bold bright_red]")
        console.print(f"[bold white]Password:[/bold white] {pwd}")
        console.print(f"[bold white]Strength:[/bold white] {strength_meter(z['score'])}")
        console.print(f"[bold white]Entropy:[/bold white] {entropy} bits\n")

        ct = z["crack_times_display"]
        console.print("[bold bright_red]Crack Time Estimates:[/bold bright_red]")
        console.print(f" • Throttled (100/h):  {ct['online_throttling_100_per_hour']}")
        console.print(f" • Online (10/s):       {ct['online_no_throttling_10_per_second']}")
        console.print(f" • Slow Hash:           {ct['offline_slow_hashing_1e4_per_second']}")
        console.print(f" • Fast Hash:           {ct['offline_fast_hashing_1e10_per_second']}\n")

        print_regex_table(checks)

        console.print("[bold bright_red]\n>> STRONG PASSWORD SUGGESTIONS <<[/bold bright_red]")
        for i, s in enumerate(suggestions, 1):
            console.print(f"[cyan]{i}.[/cyan] {s}")

        history.append({"score": z['score'], "entropy": entropy})
        console.print()


# ================
# PASSWORD HISTORY
# ================
def view_history(history):
    clear_screen()
    print_banner()

    table = Table(title="Password History Summary", box=ROUNDED, border_style="bright_red")
    table.add_column("#")
    table.add_column("Score")
    table.add_column("Entropy (bits)")

    for i, h in enumerate(history):
        table.add_row(str(i + 1), str(h["score"]), str(h["entropy"]))

    console.print(table)
    input(Fore.CYAN + "Press Enter to return...")


# ============================================
# ATTACK SIMULATION (Real John the Ripper)
# ============================================
def attack_simulation():
    while True:
        clear_screen()
        print_banner()

        console.print("[bold bright_red]>>  A T T A C K   S I M U L A T I O N  <<[/bold bright_red]\n")

        # =====================
        # Ask user for password
        # =====================
        pwd = console.input("[cyan]Enter a password to simulate cracking ('0' to exit): [/cyan] ").strip()
        if pwd in ("0", "exit"):
            return

        # ===================
        # Choose attack mode
        # ==================
        console.print("\n[bold bright_cyan]Choose attack mode:[/bold bright_cyan]")
        console.print("[cyan]1.[/cyan] Dictionary Attack (rockyou.txt)")
        console.print("[cyan]2.[/cyan] Brute Force (Incremental Mode)")
        console.print("[cyan]3.[/cyan] Hybrid Attack (Wordlist + Rules)\n")

        mode = console.input("[cyan]Select mode: [/cyan]").strip()
        if mode not in ("1", "2", "3"):
            console.print("[red]Invalid mode. Try again.[/red]")
            time.sleep(1)
            continue

        # ===========================
        # Generate hash using OpenSSL
        # ===========================
        console.print("\n[yellow]Generating secure hash using OpenSSL...[/yellow]")

        try:
            hash_output = subprocess.run(
                ["openssl", "passwd", "-1", pwd],
                capture_output=True, text=True
            ).stdout.strip()
        except Exception as e:
            console.print(f"[red]OpenSSL error: {e}[/red]")
            time.sleep(2)
            continue

        if not hash_output:
            console.print("[red]Failed to generate hash![/red]")
            time.sleep(1)
            continue

        # Write hash to file
        hashfile = "attack_hash.txt"
        with open(hashfile, "w") as f:
            f.write("user:" + hash_output + "\n")

        console.print("\n[bold yellow]Launching attack using John the Ripper...[/bold yellow]")

        # ===================
        # Build John command
        # ===================
        if mode == "1":
            attack_cmd = ["john", "--wordlist=/usr/share/wordlists/rockyou.txt", hashfile]
            mode_name = "Dictionary Attack (rockyou.txt)"
        elif mode == "2":
            attack_cmd = ["john", "--incremental", hashfile]
            mode_name = "Brute Force (Incremental)"
        else:
            attack_cmd = ["john", "--wordlist=/usr/share/wordlists/rockyou.txt", "--rules", hashfile]
            mode_name = "Hybrid Attack (Wordlist + Rules)"
        # ==============================================
        # Run attack + cinematic pulsing cyber bar
        # ==============================================
        console.print(f"\n[cyan]→ Mode:[/cyan] [white]{mode_name}[/white]\n")

        start = time.time()

        try:
            proc = subprocess.Popen(
                attack_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            console.print("[yellow]Cracking in progress...[/yellow]\n")

            # -----------------
            # Pulsing Cyber Bar 
            # -----------------
            pulse_frames = [
                "▓░░░░░░░░░",
                "▓▓▓░░░░░░░",
                "▓▓▓▓▓░░░░░",
                "▓▓▓▓▓▓▓░░░",
                "▓▓▓▓▓▓▓▓▓▓",
                "▓▓▓▓▓▓▓░░░",
                "▓▓▓▓▓░░░░░",
            ]

            frame_index = 0

           
            while proc.poll() is None:
                bar = pulse_frames[frame_index % len(pulse_frames)]
                console.print(
                    f"[bright_red][{bar}] [/bright_red]",
                    end="\r"
                )
                time.sleep(0.1)
                frame_index += 1

            proc.wait()
            console.print()   

        except FileNotFoundError:
            console.print("[red]ERROR: John the Ripper not installed![/red]")
            console.print("Install it: [cyan]sudo apt install john[/cyan]")
            time.sleep(2)
            continue

        duration = round(time.time() - start, 2)


        # ==============================================
        # Retrieve cracked password
        # ==============================================
        result = subprocess.run(
            ["john", "--show", hashfile],
            capture_output=True, text=True
        ).stdout

        console.print("\n\n[bold bright_green]>>  A T T A C K   R E S U L T S  <<[/bold bright_green]\n")

        if ":" in result:
            console.print("[green]Cracked Successfully![/green]")
            console.print(f"[white]{result}[/white]\n")
        else:
            console.print("[red]Password was NOT cracked.[/red]\n")

        # ==============================================
        # Summary
        # ==============================================
        console.print("\n[bold cyan]Attack Summary:[/bold cyan]")
        console.print(f"• Mode Used: [white]{mode_name}[/white]")
        console.print(f"• Time Taken: [white]{duration} sec[/white]")
        console.print(f"• Hash Type: [white]MD5Crypt[/white]\n")

        console.print("[dim]Press Enter to continue...[/dim]")
        input()


# ============================================
# ABOUT SCREEN 
# ============================================
def about_screen():
    clear_screen()
    print_banner()

    # Title
    console.print("[bold bright_red]A B O U T   S T E A L T H X[/bold bright_red]\n")

    # Description
    console.print(
        "StealthX is a command-line toolkit for analysing password strength and\n"
        "simulating real-world cracking techniques in a safe, offline environment.\n"
    )

   
    dev_text = "Developer: Pathan Rakib"
    line = "═" * ((console.size.width - len(dev_text) - 4) // 2)
    console.print(f"[bright_red]{line}  {dev_text}  {line}[/bright_red]\n", justify="center")

    # ---- Features ----
    console.print("[cyan]Features:[/cyan]")
    console.print(" • Regex-based password validation")
    console.print(" • ZXCVBN scoring & realistic crack-time estimates")
    console.print(" • Entropy calculation")
    console.print(" • Strong password suggestions engine")
    console.print(" • Secure random password generator")
    console.print(" • Attack Simulation using John the Ripper")
    console.print(" • Fully offline local analysis — no network usage\n")

    console.print("[cyan]Press Enter to return...[/cyan]")
    input()


# ============================================
# MENU SYSTEM
# ============================================
def menu():
    clear_screen()     
    print_banner()     

    title = Text(">>  M A I N   M E N U  <<", style="bright_red bold")
    console.print(title)
    console.print()

    options = [
        ("1", "Check Password Strength"),
        ("2", "Generate a Strong Password"),
        ("3", "View Password History"),
        ("4", "Attack Simulation (John the Ripper)"),
        ("5", "About StealthX"),
        ("0", "Exit")
    ]

    for num, text in options:
        color = "bright_cyan" if num != "0" else "bright_red"
        console.print(f"[{color}]{num}[/{color}]  •  [white]{text}[/white]")

    console.print()
    console.print("[dim]Tip: Type 0 or exit anytime.[/dim]\n")


# ============================================
# MAIN LOOP
# ============================================
def main():
    history = []

    while True:
        menu()
        choice = input("Enter choice: ").strip()

        if choice == "1":
            password_check(history)

        elif choice == "2":
            clear_screen()
            print_banner()
            try:
                length = int(input("Enter length (8–64): ") or 12)
            except:
                length = 12
            pwd = ''.join(secrets.choice(ALL) for _ in range(length))
            console.print(f"\n[green]Generated Password:[/green] {pwd}\n")
            input("Press ENTER...")

        elif choice == "3":
            view_history(history)

        elif choice == "4":
            attack_simulation()

        elif choice == "5":
            about_screen()

        elif choice == "0":
            clear_screen()
            console.print("[red bold]Exiting StealthX... Stay Safe.[/red bold]")
            break

        else:
            console.print("[red]Invalid option. Try again.[/red]")


if __name__ == "__main__":
    main()
