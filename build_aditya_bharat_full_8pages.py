# -*- coding: utf-8 -*-
r"""
ADITYA BHARAT (आदित्य भारत) — FULL 8-PAGE COMBINED & MULTI-TAB CONTROLLER
==========================================================================
Supports:
  1. Single Page Draw / Open (1-1 पेज)
  2. All 8 Pages in 1 Combined Document (Pages 1..8 on Spreads 0..7 -> Aditya_Bharat_Full_8Pages_34x53.pagedesigner)
  3. All 8 Pages in 8 Separate Document Tabs (Tab 1..Tab 8 simultaneously open in Page Designer)
"""

import ctypes
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

VAULT_DIR = Path(__file__).resolve().parent
PD_PORT = 47123
CM_TO_PT = 72.0 / 2.54
MM_TO_PT = CM_TO_PT / 10.0

EIGHT_PAGE_SEQUENCE = [
    ("page_01", "पेज 01 — फ्रंट पेज", "build_aditya_bharat_page1.py", "Aditya_Bharat_Page_01_34x53.pagedesigner"),
    ("page_02", "पेज 02 — महानगर", "build_aditya_bharat_page2.py", "Aditya_Bharat_Page_02_Mahanagar_34x53.pagedesigner"),
    ("page_03", "पेज 03 — प्रादेशिक", "build_aditya_bharat_page3.py", "Aditya_Bharat_Page_03_Pradeshik_34x53.pagedesigner"),
    ("page_04", "पेज 04 — संपादकीय", "build_aditya_bharat_page5_edit.py", "Aditya_Bharat_Page_04_Sampadakiya_34x53.pagedesigner"),
    ("page_05", "पेज 05 — राष्ट्रीय", "build_aditya_bharat_page4.py", "Aditya_Bharat_Page_05_Rashtriya_34x53.pagedesigner"),
    ("page_06", "पेज 06 — कारोबार", "build_aditya_bharat_page6_business.py", "Aditya_Bharat_Page_06_Karobar_34x53.pagedesigner"),
    ("page_07", "पेज 07 — खेल संसार", "build_aditya_bharat_page7_sports.py", "Aditya_Bharat_Page_07_Khel_Sansar_34x53.pagedesigner"),
    ("page_08", "पेज 08 — देश-विदेश", "build_aditya_bharat_page8_desh_videsh.py", "Aditya_Bharat_Page_08_Desh_Videsh_34x53.pagedesigner"),
]


def patch_all_9_builders():
    old_block = '''def rpc(method: str, params: dict = None):
    global req_id
    req_id += 1
    payload = {"id": req_id, "method": method, "params": params or {}}
    sock.sendall((json.dumps(payload, ensure_ascii=False) + "\\n").encode("utf-8"))
    resp = json.loads(f_in.readline())
    if not resp.get("ok"):
        raise RuntimeError(f"RPC {method} failed: {resp}")
    return resp.get("result")


def cmd(command: str, params: dict = None):
    return rpc("engine.execute", {"command": command, "params": params or {}})


def batch(commands: list):
    has_new = any(isinstance(c, dict) and c.get("command") == "file.new" for c in commands)
    if has_new:
        commands = list(commands) + [{"command": "view.fitPage", "params": {}}]
    return rpc("engine.batch", {"commands": commands})'''

    new_block = '''def rpc(method: str, params: dict = None):
    import os
    if os.environ.get("AB_SKIP_SAVE") == "1" and method in ("app.save", "app.export"):
        return None
    global req_id
    req_id += 1
    payload = {"id": req_id, "method": method, "params": params or {}}
    sock.sendall((json.dumps(payload, ensure_ascii=False) + "\\n").encode("utf-8"))
    resp = json.loads(f_in.readline())
    if not resp.get("ok"):
        raise RuntimeError(f"RPC {method} failed: {resp}")
    return resp.get("result")


def cmd(command: str, params: dict = None):
    import os
    if command == "file.close" and (os.environ.get("AB_NO_CLOSE") == "1" or os.environ.get("AB_TARGET_SPREAD") is not None):
        return None
    p = dict(params or {})
    if os.environ.get("AB_TARGET_SPREAD") is not None and "spread" in p:
        p["spread"] = int(os.environ["AB_TARGET_SPREAD"])
    return rpc("engine.execute", {"command": command, "params": p})


def batch(commands: list):
    import os
    ts = os.environ.get("AB_TARGET_SPREAD")
    skip_new = os.environ.get("AB_SKIP_FILE_NEW") == "1"
    new_cmds = []
    for c in commands:
        if not isinstance(c, dict):
            continue
        if skip_new and c.get("command") == "file.new":
            continue
        c2 = dict(c)
        if isinstance(c2.get("params"), dict):
            p2 = dict(c2["params"])
            if ts is not None and "spread" in p2:
                p2["spread"] = int(ts)
            c2["params"] = p2
        new_cmds.append(c2)
    has_new = any(isinstance(c, dict) and c.get("command") == "file.new" for c in new_cmds)
    if has_new:
        new_cmds = list(new_cmds) + [{"command": "view.fitPage", "params": {}}]
    if not new_cmds:
        return []
    return rpc("engine.batch", {"commands": new_cmds})'''

    for f in sorted(VAULT_DIR.glob("build_aditya_bharat_page*.py")):
        txt = f.read_text(encoding="utf-8")
        if old_block in txt:
            f.write_text(txt.replace(old_block, new_block, 1), encoding="utf-8")
            print(f"[PATCHED] {f.name}")
        elif "AB_TARGET_SPREAD" in txt:
            print(f"[ALREADY PATCHED] {f.name}")
        else:
            print(f"[WARN] Could not match block in {f.name}")


def bring_page_designer_window_to_front():
    """Brings the native Windows Page Designer window to the foreground."""
    try:
        user32 = ctypes.windll.user32
        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        found_hwnds = []

        def _enum_cb(hwnd, _lparam):
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buf = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buf, length + 1)
                    title = buf.value
                    if "Page Designer" in title or "आदित्य भारत" in title or "Aditya_Bharat" in title:
                        found_hwnds.append(hwnd)
            return True

        user32.EnumWindows(WNDENUMPROC(_enum_cb), 0)
        for hwnd in found_hwnds:
            user32.ShowWindow(hwnd, 9)  # SW_RESTORE
            user32.SetForegroundWindow(hwnd)
    except Exception:
        pass


def ensure_pd_connection():
    for port in (PD_PORT, 49200):
        try:
            s = socket.create_connection(("127.0.0.1", port), timeout=1.5)
            s.settimeout(60.0)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            return s, s.makefile("r", encoding="utf-8"), port
        except Exception:
            pass
    pd_exe = Path(r"E:\RND\Gujarat_Samachar\Page_Designer_Software\pagedesigner.exe")
    if not pd_exe.exists():
        pd_exe = Path(r"E:\RND\open page layout software\pagedesigner.exe")
    subprocess.Popen([str(pd_exe), "--control", str(PD_PORT)], cwd=str(pd_exe.parent))
    for _ in range(35):
        time.sleep(0.35)
        try:
            s = socket.create_connection(("127.0.0.1", PD_PORT), timeout=1.5)
            s.settimeout(60.0)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            return s, s.makefile("r", encoding="utf-8"), PD_PORT
        except Exception:
            pass
    raise RuntimeError("Could not connect to Page Designer on port 47123")


def send_rpc(s, f_in, method: str, params: dict = None):
    payload = {"id": 1, "method": method, "params": params or {}}
    s.sendall((json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8"))
    return json.loads(f_in.readline())


def build_combined_8page_document():
    """Creates ONE 8-Page Document (Pages 1 to 8 on Spreads 0..7) in Page Designer and draws all 8 pages into it."""
    t0 = time.perf_counter()
    s, f_in, _ = ensure_pd_connection()

    # Close old tabs first so the 8-page combined master book is clean and front-and-center
    for _ in range(12):
        try:
            r = send_rpc(s, f_in, "engine.execute", {"command": "file.close", "params": {"save": False}})
            if not r.get("ok"):
                break
        except Exception:
            break

    w_pt = round(34.0 * CM_TO_PT, 2)
    h_pt = round(53.0 * CM_TO_PT, 2)
    m_pt = round(1.0 * CM_TO_PT, 2)
    g_pt = round(4.0 * MM_TO_PT, 2)

    send_rpc(s, f_in, "engine.batch", {"commands": [
        {"command": "file.new", "params": {
            "width": w_pt,
            "height": h_pt,
            "pages": 8,
            "facingPages": False,
            "columns": 8,
            "gutter": g_pt,
            "margins": m_pt,
            "title": "आदित्य भारत — संपूर्ण 8-पेज संस्करण (Pages 01 to 08 | 34x53 cm)",
        }},
        {"command": "document.preferences", "params": {
            "baselineGrid": {
                "start": m_pt,
                "increment": 11.25,
                "relativeTo": "topOfPage",
            }
        }},
        {"command": "swatch.create", "params": {"name": "FlyerCrimson", "color": "#c4121a"}},
        {"command": "swatch.create", "params": {"name": "ClosingGray", "color": "#808285"}},
        {"command": "swatch.create", "params": {"name": "EditPointerBg", "color": "#f2f2f2"}},
        {"command": "window.panel", "params": {"panel": "pages"}},
    ]})
    s.close()

    for spread_idx, (pid, title_hi, script_name, _pd_name) in enumerate(EIGHT_PAGE_SEQUENCE):
        env = os.environ.copy()
        env["AB_TARGET_SPREAD"] = str(spread_idx)
        env["AB_SKIP_FILE_NEW"] = "1"
        env["AB_SKIP_SAVE"] = "1"
        env["AB_NO_CLOSE"] = "1"
        t_p = time.perf_counter()
        proc = subprocess.run(
            [sys.executable, str(VAULT_DIR / script_name)],
            cwd=str(VAULT_DIR),
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        print(f"  -> Drawn Spread {spread_idx + 1}/8 ({title_hi}) in {time.perf_counter() - t_p:.2f}s (exit={proc.returncode})")

    s2, f_in2, _ = ensure_pd_connection()
    out_combined_pd = VAULT_DIR / "Aditya_Bharat_Full_8Pages_34x53.pagedesigner"
    out_combined_pdf = VAULT_DIR / "Aditya_Bharat_Full_8Pages_CMYK_34x53.pdf"
    send_rpc(s2, f_in2, "app.save", {"path": str(out_combined_pd)})
    try:
        send_rpc(s2, f_in2, "engine.execute", {"command": "file.exportPdf", "params": {"path": str(out_combined_pdf)}})
    except Exception:
        pass
    send_rpc(s2, f_in2, "engine.execute", {"command": "view.goToPage", "params": {"page": 1}})
    send_rpc(s2, f_in2, "engine.execute", {"command": "view.fitPage", "params": {}})
    send_rpc(s2, f_in2, "ui.focus", {})
    s2.close()
    bring_page_designer_window_to_front()
    print(f"=== FULL 8-PAGE COMBINED EDITION BUILT & OPENED IN {time.perf_counter() - t0:.2f}s ===")
    print(f"    Saved Combined .pagedesigner: {out_combined_pd}")
    print(f"    Saved Combined CMYK .pdf    : {out_combined_pdf}")


def open_all_8_tabs_in_page_designer(close_existing: bool = True):
    """Opens all 8 individual .pagedesigner files as 8 separate tabs simultaneously in Page Designer."""
    s, f_in, _ = ensure_pd_connection()
    if close_existing:
        for _ in range(12):
            try:
                r = send_rpc(s, f_in, "engine.execute", {"command": "file.close", "params": {"save": False}})
                if not r.get("ok"):
                    break
            except Exception:
                break
    opened = []
    for _pid, title_hi, _script_name, pd_name in EIGHT_PAGE_SEQUENCE:
        target = VAULT_DIR / pd_name
        if target.exists():
            r = send_rpc(s, f_in, "app.open", {"path": str(target)})
            send_rpc(s, f_in, "engine.execute", {"command": "view.fitPage", "params": {}})
            opened.append(f"{title_hi} ({pd_name}) -> Tab #{r.get('result', {}).get('index')}")
    # Also activate Tab 0 (Page 01) and focus window
    send_rpc(s, f_in, "engine.execute", {"command": "file.activate", "params": {"index": 0}})
    send_rpc(s, f_in, "engine.execute", {"command": "view.fitPage", "params": {}})
    send_rpc(s, f_in, "ui.focus", {})
    s.close()
    bring_page_designer_window_to_front()
    return opened


if __name__ == "__main__":
    if "--patch" in sys.argv:
        patch_all_9_builders()
    elif "--combined" in sys.argv:
        patch_all_9_builders()
        build_combined_8page_document()
    elif "--open-all-tabs" in sys.argv:
        open_all_8_tabs_in_page_designer(close_existing=True)
