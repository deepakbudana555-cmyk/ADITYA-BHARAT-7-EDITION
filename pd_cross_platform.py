#!/usr/bin/env python3
"""
Cross-Platform Bridge for Gujarat Samachar (Hindi Edition) Page Designer Studio
Works identically on:
  - macOS (Apple Silicon M1/M2/M3/M4 & Intel) — sys.platform == "darwin"
  - Windows (10 / 11)                        — sys.platform == "win32"
  - Linux                                    — sys.platform.startswith("linux")

Handles:
  1. Automatic Hindi Font Installation (`DB Hindi.ttf`, `DB Hindi Bold.ttf`, `DB Madhurima.ttf`)
     into `~/Library/Fonts` on macOS or user font dir on Windows/Linux.
  2. Finding & Launching the installed Page Designer app with `--control 47123`
     (no bundled binary needed on macOS — uses the installed `/Applications/Page Designer.app`).
  3. Bringing the Page Designer window to the foreground (`osascript` on macOS,
     `winsta0\\default` + `SetWindowPos` on Windows) so live step-by-step page building
     is always visible to the user.
  4. Launching the Newsroom Studio UI in Chrome/Edge App Mode or the default browser.
"""
from __future__ import annotations

import os
import shutil
import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

IS_MAC = sys.platform == "darwin"
IS_WIN = sys.platform == "win32"
IS_LINUX = sys.platform.startswith("linux")

ROOT_DIR = Path(__file__).resolve().parent
FONTS_DIR = ROOT_DIR / "Fonts"
PHOTOS_DIR = ROOT_DIR / "photos"


def ensure_fonts_installed(fonts_dir: Path | None = None) -> list[str]:
    """
    Ensure all .ttf / .otf fonts in `Fonts/` are installed in the OS user font folder
    so Page Designer on macOS / Windows / Linux immediately renders DB Hindi & DB Madhurima.
    """
    src_dir = fonts_dir or FONTS_DIR
    if not src_dir.exists():
        return []

    installed: list[str] = []
    target_dirs: list[Path] = []

    if IS_MAC:
        target_dirs.append(Path.home() / "Library" / "Fonts")
    elif IS_WIN:
        local_app = os.environ.get("LOCALAPPDATA", "")
        if local_app:
            target_dirs.append(Path(local_app) / "Microsoft" / "Windows" / "Fonts")
        win_fonts = Path(r"C:\Windows\Fonts")
        if win_fonts.exists():
            target_dirs.append(win_fonts)
    else:
        target_dirs.append(Path.home() / ".local" / "share" / "fonts")

    for tdir in target_dirs:
        try:
            tdir.mkdir(parents=True, exist_ok=True)
        except Exception:
            continue
        for f in src_dir.iterdir():
            if f.suffix.lower() in (".ttf", ".otf"):
                dst = tdir / f.name
                try:
                    if not dst.exists():
                        shutil.copy2(f, dst)
                    installed.append(str(dst))
                except Exception:
                    pass
    return installed


def find_pagedesigner_bin() -> Path | None:
    """
    Locate the installed Page Designer executable or macOS .app binary across platforms.
    Can also be overridden via the `PAGEDESIGNER_BIN` environment variable.
    """
    env_bin = os.environ.get("PAGEDESIGNER_BIN", "").strip()
    if env_bin:
        p = Path(env_bin).expanduser()
        if p.exists():
            if IS_MAC and p.suffix == ".app":
                macos_dir = p / "Contents" / "MacOS"
                if macos_dir.exists():
                    for child in macos_dir.iterdir():
                        if os.access(child, os.X_OK):
                            return child
            return p

    if IS_MAC:
        mac_candidates = [
            Path("/Applications/Page Designer.app/Contents/MacOS/Page Designer"),
            Path("/Applications/Page Designer.app/Contents/MacOS/pagedesigner"),
            Path("/Applications/Page Designer 1.0.app/Contents/MacOS/Page Designer"),
            Path("/Applications/Page Designer 1.0.app/Contents/MacOS/pagedesigner"),
            Path("/Applications/PageDesigner.app/Contents/MacOS/PageDesigner"),
            Path("/Applications/PageDesigner.app/Contents/MacOS/pagedesigner"),
            Path.home() / "Applications/Page Designer.app/Contents/MacOS/Page Designer",
            Path.home() / "Applications/Page Designer.app/Contents/MacOS/pagedesigner",
            Path.home() / "Applications/PageDesigner.app/Contents/MacOS/PageDesigner",
            Path.home() / "Applications/PageDesigner.app/Contents/MacOS/pagedesigner",
            ROOT_DIR.parent / "Page Designer.app/Contents/MacOS/Page Designer",
            ROOT_DIR.parent / "Page Designer 1.0/pagedesigner",
        ]
        for c in mac_candidates:
            if c.exists():
                return c

        # Search /Applications and ~/Applications for any *Page*Designer*.app bundle
        for apps_root in [Path("/Applications"), Path.home() / "Applications", ROOT_DIR.parent]:
            if not apps_root.exists():
                continue
            try:
                for item in apps_root.iterdir():
                    if item.suffix.lower() == ".app" and "page" in item.name.lower() and "designer" in item.name.lower():
                        macos_dir = item / "Contents" / "MacOS"
                        if macos_dir.exists():
                            for child in macos_dir.iterdir():
                                if child.is_file() and os.access(child, os.X_OK):
                                    return child
            except Exception:
                pass

    elif IS_WIN:
        win_candidates = [
            ROOT_DIR.parent / "Gujarat_Samachar" / "Page_Designer_Software" / "pagedesigner.exe",
            ROOT_DIR.parent / "open page layout software" / "pagedesigner.exe",
            ROOT_DIR.parent / "Page Designer 1.0" / "pagedesigner.exe",
            ROOT_DIR / "Page Designer 1.0" / "pagedesigner.exe",
            Path(r"E:\RND\Gujarat_Samachar\Page_Designer_Software\pagedesigner.exe"),
            Path(r"E:\RND\open page layout software\pagedesigner.exe"),
            Path(r"E:\RND\Page Designer 1.0\pagedesigner.exe"),
            Path(r"C:\Program Files\Page Designer 1.0\pagedesigner.exe"),
            Path(r"C:\Program Files\Page Designer\pagedesigner.exe"),
            Path.home() / "Desktop" / "Page Designer 1.0" / "pagedesigner.exe",
        ]
        for c in win_candidates:
            if c.exists():
                return c

    which_bin = shutil.which("pagedesigner") or shutil.which("Page Designer")
    if which_bin:
        return Path(which_bin)

    return None


def is_pd_running(host: str = "127.0.0.1", port: int = 47123) -> bool:
    """Check if Page Designer's TCP control socket is accepting connections."""
    try:
        with socket.create_connection((host, port), timeout=1.0) as s:
            s.sendall(b'{"command":"doc.info","params":{}}\n')
            data = s.recv(4096)
            return bool(data)
    except Exception:
        return False


def focus_pagedesigner_window() -> bool:
    """
    Bring the Page Designer GUI window to the front on macOS or Windows
    so the user can watch the page being built step-by-step.
    """
    if IS_MAC:
        applescript = r'''
        tell application "System Events"
            set foundProc to false
            repeat with p in (every process whose background only is false)
                set pName to name of p
                if pName contains "Page Designer" or pName contains "PageDesigner" or pName contains "pagedesigner" then
                    set frontmost of p to true
                    set foundProc to true
                    exit repeat
                end if
            end repeat
        end tell
        '''
        try:
            subprocess.run(["osascript", "-e", applescript], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3)
            return True
        except Exception:
            return False

    elif IS_WIN:
        try:
            import ctypes
            from ctypes import wintypes

            user32 = ctypes.windll.user32
            found_hwnds: list[int] = []

            WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

            def cb(hwnd, lParam):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buf = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buf, length + 1)
                    if "Page Designer" in buf.value:
                        found_hwnds.append(hwnd)
                        SW_RESTORE = 9
                        SW_MAXIMIZE = 3
                        HWND_TOPMOST = -1
                        HWND_NOTOPMOST = -2
                        SWP_NOMOVE = 0x0002
                        SWP_NOSIZE = 0x0001
                        SWP_SHOWWINDOW = 0x0040
                        user32.ShowWindow(hwnd, SW_RESTORE)
                        user32.ShowWindow(hwnd, SW_MAXIMIZE)
                        user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW)
                        user32.SetWindowPos(hwnd, HWND_NOTOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW)
                        user32.SetForegroundWindow(hwnd)
                        user32.BringWindowToTop(hwnd)
                return True

            enum_cb = WNDENUMPROC(cb)
            try:
                hdesk = user32.OpenDesktopW("default", 0, False, 0x01FF)
                if hdesk:
                    user32.EnumDesktopWindows(hdesk, enum_cb, 0)
                    user32.CloseDesktop(hdesk)
            except Exception:
                pass
            if not found_hwnds:
                user32.EnumWindows(enum_cb, 0)
            return len(found_hwnds) > 0
        except Exception:
            return False

    return True


def launch_pagedesigner(host: str = "127.0.0.1", port: int = 47123) -> bool:
    """
    Ensure Page Designer is running with `--control <port>` and visible on the user's screen.
    Works on both macOS (using `/Applications/Page Designer.app`) and Windows.
    """
    ensure_fonts_installed()

    if is_pd_running(host, port):
        if IS_WIN:
            if focus_pagedesigner_window():
                return True
            # If running in hidden session on Windows, restart on interactive desktop
            subprocess.run(["taskkill", "/F", "/IM", "pagedesigner.exe"], capture_output=True)
            time.sleep(0.6)
        else:
            focus_pagedesigner_window()
            return True

    pd_bin = find_pagedesigner_bin()

    if IS_MAC:
        if pd_bin and pd_bin.exists():
            # Launch binary directly with --control <port>
            subprocess.Popen(
                [str(pd_bin), "--control", str(port)],
                cwd=str(pd_bin.parent),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        else:
            # Fallback to macOS `open -a` for standard .app bundle name
            for app_name in ("Page Designer", "PageDesigner", "Page Designer 1.0"):
                res = subprocess.run(
                    ["open", "-a", app_name, "--args", "--control", str(port)],
                    capture_output=True,
                )
                if res.returncode == 0:
                    break

    elif IS_WIN and pd_bin and pd_bin.exists():
        launched = False
        try:
            import ctypes
            from ctypes import wintypes

            kernel32 = ctypes.windll.kernel32

            class STARTUPINFOW(ctypes.Structure):
                _fields_ = [
                    ("cb", wintypes.DWORD),
                    ("lpReserved", wintypes.LPWSTR),
                    ("lpDesktop", wintypes.LPWSTR),
                    ("lpTitle", wintypes.LPWSTR),
                    ("dwX", wintypes.DWORD),
                    ("dwY", wintypes.DWORD),
                    ("dwXSize", wintypes.DWORD),
                    ("dwYSize", wintypes.DWORD),
                    ("dwXCountChars", wintypes.DWORD),
                    ("dwYCountChars", wintypes.DWORD),
                    ("dwFillAttribute", wintypes.DWORD),
                    ("dwFlags", wintypes.DWORD),
                    ("wShowWindow", wintypes.WORD),
                    ("cbReserved2", wintypes.WORD),
                    ("lpReserved2", ctypes.POINTER(wintypes.BYTE)),
                    ("hStdInput", wintypes.HANDLE),
                    ("hStdOutput", wintypes.HANDLE),
                    ("hStdError", wintypes.HANDLE),
                ]

            class PROCESS_INFORMATION(ctypes.Structure):
                _fields_ = [
                    ("hProcess", wintypes.HANDLE),
                    ("hThread", wintypes.HANDLE),
                    ("dwProcessId", wintypes.DWORD),
                    ("dwThreadId", wintypes.DWORD),
                ]

            si = STARTUPINFOW()
            si.cb = ctypes.sizeof(STARTUPINFOW)
            si.lpDesktop = "winsta0\\default"
            si.dwFlags = 0x00000001  # STARTF_USESHOWWINDOW
            si.wShowWindow = 3        # SW_MAXIMIZE
            pi = PROCESS_INFORMATION()
            cmd_line = ctypes.create_unicode_buffer(f'"{pd_bin}" --control {port}')
            ok = kernel32.CreateProcessW(
                None,
                cmd_line,
                None,
                None,
                False,
                0x00000010,
                None,
                str(pd_bin.parent),
                ctypes.byref(si),
                ctypes.byref(pi),
            )
            if ok:
                kernel32.CloseHandle(pi.hProcess)
                kernel32.CloseHandle(pi.hThread)
                launched = True
        except Exception:
            pass

        if not launched:
            subprocess.Popen([str(pd_bin), "--control", str(port)], cwd=str(pd_bin.parent))

    elif pd_bin and pd_bin.exists():
        subprocess.Popen([str(pd_bin), "--control", str(port)], cwd=str(pd_bin.parent))

    for _ in range(45):
        time.sleep(0.25)
        if is_pd_running(host, port):
            time.sleep(0.35)
            focus_pagedesigner_window()
            return True

    return False


def open_studio_browser(url: str) -> None:
    """Open the Page Designer Studio UI in Chrome/Edge App mode or default browser on macOS/Windows."""
    if IS_MAC:
        mac_browsers = [
            Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
            Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
            Path("/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"),
        ]
        for b in mac_browsers:
            if b.exists():
                try:
                    subprocess.Popen(
                        [str(b), f"--app={url}", "--start-maximized"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    return
                except Exception:
                    pass
        try:
            subprocess.Popen(["open", url])
            return
        except Exception:
            pass

    elif IS_WIN:
        win_browsers = [
            Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
            Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
            Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
            Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
        ]
        for b in win_browsers:
            if b.exists():
                try:
                    subprocess.Popen([str(b), f"--app={url}", "--start-maximized"])
                    return
                except Exception:
                    pass

    webbrowser.open(url)
