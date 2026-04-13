"""AegisAI - Futuristic Cybersecurity Dashboard.

Run:
    python -m streamlit run app.py
"""

import csv
import hashlib
import io
import random
import re
import time
from datetime import datetime, timedelta
from urllib.parse import urlparse

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="AegisAI Cyber Defense",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def add_style() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        .stApp {
            background:
                radial-gradient(circle at 12% 8%, rgba(0,229,255,.14), transparent 28%),
                radial-gradient(circle at 86% 4%, rgba(57,255,136,.11), transparent 26%),
                linear-gradient(135deg, #020506 0%, #05090c 50%, #000 100%);
            color: #e8fbff;
            font-family: Inter, sans-serif;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #020506 0%, #071015 100%);
            border-right: 1px solid rgba(0,229,255,.28);
        }
        [data-testid="stSidebar"] * { color: #e8fbff; }
        h1, h2, h3 { color: #f4feff; letter-spacing: 0; }
        .hero {
            padding: 28px 30px;
            border: 1px solid rgba(0,229,255,.28);
            background: linear-gradient(135deg, rgba(7,16,21,.96), rgba(0,0,0,.74));
            border-radius: 8px;
            box-shadow: 0 0 38px rgba(0,229,255,.14);
            position: relative;
            overflow: hidden;
        }
        .hero:after {
            content: "";
            position: absolute;
            inset: 0;
            background: repeating-linear-gradient(0deg, rgba(255,255,255,.025), rgba(255,255,255,.025) 1px, transparent 1px, transparent 6px);
            pointer-events: none;
            animation: scanlines 6s linear infinite;
        }
        @keyframes scanlines { from { transform: translateY(-20px); } to { transform: translateY(20px); } }
        .hero-title { font-size: 44px; font-weight: 800; margin-bottom: 8px; color: #fff; }
        .glow { color: #00e5ff; text-shadow: 0 0 18px rgba(0,229,255,.75); }
        .hero-subtitle { color: #a8cbd3; font-size: 16px; max-width: 900px; }
        .stat-card {
            border: 1px solid rgba(0,229,255,.24);
            background: rgba(7,16,21,.92);
            border-radius: 8px;
            padding: 20px;
            min-height: 130px;
            box-shadow: 0 0 30px rgba(0,229,255,.08);
        }
        .stat-label { color: #8fb4bd; font-size: 13px; text-transform: uppercase; font-weight: 700; }
        .stat-value { color: #fff; font-size: 34px; font-weight: 800; margin-top: 8px; }
        .stat-foot { color: #39ff88; font-size: 13px; margin-top: 10px; }
        .pulse-dot {
            display: inline-block; width: 11px; height: 11px; margin-right: 8px; border-radius: 50%;
            background: #39ff88; animation: pulse 1.6s infinite;
        }
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(57,255,136,.8); }
            70% { box-shadow: 0 0 0 13px rgba(57,255,136,0); }
            100% { box-shadow: 0 0 0 0 rgba(57,255,136,0); }
        }
        .status-good { color: #39ff88; font-weight: 800; text-shadow: 0 0 14px rgba(57,255,136,.5); }
        .terminal {
            background: #010405;
            color: #39ff88;
            border: 1px solid rgba(57,255,136,.35);
            border-radius: 8px;
            padding: 18px;
            font-family: Consolas, monospace;
            min-height: 180px;
            box-shadow: inset 0 0 18px rgba(57,255,136,.08);
        }
        .alert-line { padding: 8px 0; border-bottom: 1px solid rgba(57,255,136,.13); }
        .stButton > button, .stDownloadButton > button {
            border-radius: 8px;
            border: 1px solid rgba(0,229,255,.55);
            background: linear-gradient(135deg, #08202a, #041015);
            color: #fff;
            font-weight: 800;
            box-shadow: 0 0 20px rgba(0,229,255,.16);
        }
        .stButton > button:hover, .stDownloadButton > button:hover {
            border-color: #39ff88;
            color: #39ff88;
            box-shadow: 0 0 26px rgba(57,255,136,.2);
        }
        [data-testid="stMetricValue"] { color: #00e5ff; }
        .small-muted { color: #8fb4bd; font-size: 13px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def fake_ip() -> str:
    return f"{random.randint(23, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(2, 254)}"


def risk_level(score: int) -> str:
    if score >= 80:
        return "Critical"
    if score >= 60:
        return "High"
    if score >= 35:
        return "Medium"
    return "Low"


def create_events(rows: int = 24) -> pd.DataFrame:
    now = datetime.now().replace(second=0, microsecond=0)
    names = ["Brute Force", "DDoS Spike", "Phishing", "Port Scan", "Malware Beacon"]
    levels = ["Low", "Medium", "High", "Critical"]
    data = []
    for i in range(rows):
        risk = random.randint(12, 95)
        data.append(
            {
                "time": now - timedelta(minutes=(rows - i) * 10),
                "threat_type": random.choice(names),
                "risk_score": risk,
                "severity": levels[min(3, risk // 25)],
                "source_ip": fake_ip(),
                "status": random.choice(["Blocked", "Monitored", "Quarantined", "Investigating"]),
            }
        )
    return pd.DataFrame(data)


def init_state() -> None:
    if "events" not in st.session_state:
        st.session_state.events = create_events()
    if "chat" not in st.session_state:
        st.session_state.chat = [
            {"role": "assistant", "content": "Hello, I am AegisAI. Ask me about phishing, malware, passwords, logs, or incident response."}
        ]
    if "alerts" not in st.session_state:
        st.session_state.alerts = []
    if "scan_history" not in st.session_state:
        st.session_state.scan_history = []


def hero() -> None:
    st.markdown(
        """
        <div class="hero">
            <div class="hero-title">Aegis<span class="glow">AI</span> Cyber Defense</div>
            <div class="hero-subtitle">
                Predictive threat monitoring, phishing checks, file scanning, AI guidance, and automated response simulation in one command center.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def stat_card(label: str, value: str, foot: str) -> None:
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-label">{label}</div>
            <div class="stat-value">{value}</div>
            <div class="stat-foot">{foot}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def dashboard_page() -> None:
    hero()
    events = st.session_state.events
    current_risk = int(events["risk_score"].tail(1).iloc[0])
    blocked = len(events[events["status"] == "Blocked"])

    st.write("")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        stat_card("Threats Detected", str(len(events)), "Live telemetry active")
    with col2:
        stat_card("Risk Level", risk_level(current_risk), f"Risk score: {current_risk}/100")
    with col3:
        stat_card("Blocked Attacks", str(blocked), "Auto-response simulated")
    with col4:
        stat_card("System Status", "ONLINE", "All sensors operational")

    left, right = st.columns([2, 1])
    with left:
        st.subheader("📈 Threat Score Timeline")
        st.line_chart(events.set_index("time")["risk_score"])
    with right:
        st.subheader("🧬 System Risk")
        st.progress(current_risk / 100)
        st.markdown(f"Current level: **{risk_level(current_risk)}**")
        st.markdown('<span class="pulse-dot"></span><span class="status-good">ACTIVE DEFENSE MODE</span>', unsafe_allow_html=True)
        st.subheader("🌐 Fake IP Tracking")
        st.dataframe(events[["source_ip", "threat_type", "severity", "status"]].tail(6), use_container_width=True, hide_index=True)

    st.subheader("📊 Threat Category Breakdown")
    threat_counts = events["threat_type"].value_counts().reset_index()
    threat_counts.columns = ["threat_type", "count"]
    st.bar_chart(threat_counts.set_index("threat_type"))
    st.subheader("Recent Security Events")
    st.dataframe(events.tail(12), use_container_width=True, hide_index=True)


def scan_url(url: str) -> dict:
    suspicious_words = ["login", "verify", "free", "bonus", "gift", "update", "secure", "bank", "wallet", "password", "otp"]
    shorteners = ["bit.ly", "tinyurl", "t.co", "goo.gl", "ow.ly", "is.gd"]
    score = 5
    reasons = []
    if not url.strip():
        return {"score": 0, "level": "Unknown", "verdict": "Enter a URL to scan.", "reasons": []}

    normalized = url.strip()
    if not normalized.startswith(("http://", "https://")):
        normalized = "http://" + normalized
    parsed = urlparse(normalized)
    domain = parsed.netloc.lower()
    full_text = f"{domain} {parsed.path.lower()}"

    checks = [
        (parsed.scheme == "http", 20, "Uses HTTP instead of HTTPS"),
        ("@" in normalized, 25, "Contains @ symbol, often used to hide real destination"),
        (domain.count(".") >= 3, 15, "Too many subdomains"),
        (bool(re.search(r"\d+\.\d+\.\d+\.\d+", domain)), 25, "Uses raw IP address instead of domain name"),
        (any(shortener in domain for shortener in shorteners), 20, "Uses a URL shortener"),
        ("-" in domain, 10, "Domain contains hyphen"),
        ("xn--" in domain, 20, "Possible punycode/lookalike domain"),
    ]
    for condition, points, reason in checks:
        if condition:
            score += points
            reasons.append(reason)

    matched = [word for word in suspicious_words if word in full_text]
    if matched:
        score += min(30, len(matched) * 8)
        reasons.append("Suspicious words found: " + ", ".join(matched))

    score = min(score, 100)
    verdict = "⚠️ Possible phishing URL" if score >= 45 else "✅ URL looks safe"
    return {"score": score, "level": risk_level(score), "verdict": verdict, "reasons": reasons or ["No major suspicious pattern found"]}


def scan_file(uploaded_file) -> dict:
    content = uploaded_file.getvalue()
    file_hash = hashlib.sha256(content).hexdigest()
    extension = uploaded_file.name.split(".")[-1].lower() if "." in uploaded_file.name else "unknown"
    risky_extensions = {"exe", "bat", "cmd", "js", "vbs", "scr", "ps1", "jar"}
    risky_keywords = [b"powershell", b"cmd.exe", b"eval(", b"base64", b"malware", b"ransom", b"trojan"]
    score = 5
    reasons = []

    if extension in risky_extensions:
        score += 45
        reasons.append(f"Risky file extension: .{extension}")
    if len(content) > 5_000_000:
        score += 10
        reasons.append("Large file size")
    found = [word.decode("utf-8", errors="ignore") for word in risky_keywords if word in content[:100_000].lower()]
    if found:
        score += min(40, len(found) * 15)
        reasons.append("Suspicious content keywords: " + ", ".join(found))

    score = min(score, 100)
    return {
        "score": score,
        "level": risk_level(score),
        "verdict": "🚨 Threat detected" if score >= 50 else "✅ File looks safe",
        "sha256": file_hash,
        "size": len(content),
        "reasons": reasons or ["No obvious malicious pattern found"],
    }


def scanner_page() -> None:
    st.title("🔍 Scanner")
    st.markdown('<p class="small-muted">Scan URLs and uploaded files using safe beginner-friendly logic.</p>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["URL Scanner", "File Scanner"])

    with tab1:
        st.subheader("URL Threat Scanner")
        url = st.text_input("Enter URL", placeholder="https://example.com/login")
        if st.button("Scan URL", use_container_width=True):
            result = scan_url(url)
            st.session_state.scan_history.append({"time": now_text(), "type": "URL", "target": url, **result})
            st.metric("Risk Score", f"{result['score']}/100", result["level"])
            st.progress(result["score"] / 100)
            (st.success if result["score"] < 45 else st.error)(result["verdict"])
            st.write("Reasons:")
            for reason in result["reasons"]:
                st.write(f"- {reason}")

    with tab2:
        st.subheader("File Threat Scanner")
        uploaded_file = st.file_uploader("Upload a file for safe demo scanning")
        if uploaded_file is not None and st.button("Scan File", use_container_width=True):
            with st.spinner("Scanning file signatures, extension, and suspicious content..."):
                time.sleep(1.5)
                result = scan_file(uploaded_file)
            st.session_state.scan_history.append({"time": now_text(), "type": "FILE", "target": uploaded_file.name, **result})
            st.metric("Risk Score", f"{result['score']}/100", result["level"])
            st.progress(result["score"] / 100)
            (st.success if result["score"] < 50 else st.error)(result["verdict"])
            st.code(f"SHA256: {result['sha256']}\nSize: {result['size']} bytes", language="text")
            st.write("Reasons:")
            for reason in result["reasons"]:
                st.write(f"- {reason}")


def assistant_reply(message: str) -> str:
    text = message.lower()
    if "phishing" in text or "email" in text:
        return "Check sender address, urgent language, suspicious links, spelling mistakes, and requests for OTP/password. Never enter credentials from an email link."
    if "password" in text:
        return "Use a long unique password, enable MFA, avoid reuse, and store it in a trusted password manager."
    if "malware" in text or "file" in text:
        return "Do not run unknown files. Check extension, hash, source reputation, and scan in a sandbox or antivirus tool."
    if "ddos" in text:
        return "For DDoS, monitor traffic spikes, rate-limit suspicious IPs, use CDN/WAF protection, and alert the network team."
    if "incident" in text or "response" in text:
        return "Basic incident response steps: identify, contain, eradicate, recover, and document lessons learned."
    if "log" in text:
        return "Look for repeated failures, new admin activity, unusual IPs, impossible travel, and traffic spikes."
    return "I can help with phishing, malware, password safety, DDoS, log analysis, and incident response. For a real system, always verify with trusted security tools."


def ai_assistant_page() -> None:
    st.title("🤖 AI Cybersecurity Assistant")
    st.markdown('<p class="small-muted">Offline rule-based assistant. No API key needed.</p>', unsafe_allow_html=True)
    for message in st.session_state.chat:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    prompt = st.chat_input("Ask about phishing, malware, logs, passwords, or incident response...")
    if prompt:
        st.session_state.chat.append({"role": "user", "content": prompt})
        st.session_state.chat.append({"role": "assistant", "content": assistant_reply(prompt)})
        st.rerun()


def attack_page() -> None:
    st.title("🚨 Live Attack Simulation")
    st.markdown('<p class="small-muted">Safe simulation only. It does not block real IPs or change your system.</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        attack_type = st.selectbox("Choose attack scenario", ["DDoS attack", "Brute-force login", "Phishing campaign", "Malware beacon"])
    with col2:
        target_ip = st.text_input("Target / suspicious IP", value=fake_ip())

    placeholder = st.empty()
    if st.button("Start Simulation", use_container_width=True):
        steps = [
            f"Incoming telemetry from {target_ip}",
            f"{attack_type} detected",
            "Risk score rising above threshold",
            "Blocking IP",
            "Alerting admin",
            "Threat neutralized",
        ]
        rendered = []
        for step in steps:
            rendered.append(f'<div class="alert-line">[{datetime.now().strftime("%H:%M:%S")}] {step}</div>')
            placeholder.markdown('<div class="terminal">' + "".join(rendered) + "</div>", unsafe_allow_html=True)
            time.sleep(0.65)
        st.session_state.alerts.append({"time": now_text(), "attack": attack_type, "ip": target_ip, "action": "Blocked IP, alerted admin, threat neutralized"})
        new_event = pd.DataFrame([{"time": datetime.now(), "threat_type": attack_type, "risk_score": random.randint(82, 99), "severity": "Critical", "source_ip": target_ip, "status": "Blocked"}])
        st.session_state.events = pd.concat([st.session_state.events, new_event], ignore_index=True)
        st.success("Simulation complete. Dashboard telemetry updated.")

    if st.session_state.alerts:
        st.subheader("Simulation History")
        st.dataframe(pd.DataFrame(st.session_state.alerts), use_container_width=True, hide_index=True)


def build_text_report(events: pd.DataFrame, scans: pd.DataFrame) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    buffer.write("AEGISAI CYBER DEFENSE REPORT\n")
    buffer.write(f"Generated: {now_text()}\n\n")
    buffer.write(f"Total events: {len(events)}\n")
    buffer.write(f"Average risk score: {events['risk_score'].mean():.2f}\n")
    buffer.write(f"Critical events: {len(events[events['severity'] == 'Critical'])}\n")
    buffer.write(f"Blocked events: {len(events[events['status'] == 'Blocked'])}\n\n")
    buffer.write("Top recent events:\n")
    writer.writerow(["time", "threat_type", "risk_score", "severity", "source_ip", "status"])
    for _, row in events.tail(8).iterrows():
        writer.writerow([row["time"], row["threat_type"], row["risk_score"], row["severity"], row["source_ip"], row["status"]])
    buffer.write("\nScanner history:\n")
    if scans.empty:
        buffer.write("No scans performed yet.\n")
    else:
        writer.writerow(["time", "type", "target", "score", "level", "verdict"])
        for _, row in scans.iterrows():
            writer.writerow([row["time"], row["type"], row["target"], row["score"], row["level"], row["verdict"]])
    return buffer.getvalue()


def reports_page() -> None:
    st.title("📄 Reports")
    st.markdown('<p class="small-muted">Download scanner results and threat telemetry.</p>', unsafe_allow_html=True)
    events = st.session_state.events.copy()
    scans = pd.DataFrame(st.session_state.scan_history)
    st.subheader("Threat Telemetry")
    st.dataframe(events, use_container_width=True, hide_index=True)
    st.download_button("Download Threat Telemetry CSV", events.to_csv(index=False).encode("utf-8"), "aegisai_threat_telemetry.csv", "text/csv", use_container_width=True)
    st.subheader("Scanner History")
    if scans.empty:
        st.info("No URL or file scans yet. Go to Scanner and run one scan.")
    else:
        st.dataframe(scans, use_container_width=True, hide_index=True)
        st.download_button("Download Scanner History CSV", scans.to_csv(index=False).encode("utf-8"), "aegisai_scan_history.csv", "text/csv", use_container_width=True)
    st.download_button("Download Executive Text Report", build_text_report(events, scans), "aegisai_executive_report.txt", "text/plain", use_container_width=True)


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def sidebar() -> str:
    st.sidebar.markdown("## 🛡️ AegisAI")
    st.sidebar.markdown('<span class="pulse-dot"></span><span class="status-good">SYSTEM ONLINE</span>', unsafe_allow_html=True)
    st.sidebar.write("")
    page = st.sidebar.radio("Navigation", ["Dashboard", "Scanner", "AI Assistant", "Attack Simulation", "Reports"])
    st.sidebar.write("---")
    st.sidebar.markdown("### System Status")
    st.sidebar.write("Firewall: ✅ Active")
    st.sidebar.write("IDS: ✅ Monitoring")
    st.sidebar.write("AI Engine: ✅ Ready")
    st.sidebar.write("Last sync: " + datetime.now().strftime("%H:%M:%S"))
    return page


def main() -> None:
    add_style()
    init_state()
    page = sidebar()
    if page == "Dashboard":
        dashboard_page()
    elif page == "Scanner":
        scanner_page()
    elif page == "AI Assistant":
        ai_assistant_page()
    elif page == "Attack Simulation":
        attack_page()
    elif page == "Reports":
        reports_page()


if __name__ == "__main__":
    main()
