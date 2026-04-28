import streamlit as st
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(
    page_title="World Clock — Trading Hubs",
    page_icon="🕒",
    layout="wide",
)

# ----------------------------
# Minimal, professional styling (pure CSS)
# ----------------------------
st.markdown(
    """
    <style>
      .app-title { font-size: 2.0rem; font-weight: 700; margin-bottom: 0.25rem; }
      .app-subtitle { color: #6b7280; margin-bottom: 1.25rem; }
      .card {
        border: 1px solid rgba(120,120,120,0.25);
        border-radius: 14px;
        padding: 18px 18px 14px 18px;
        background: rgba(255,255,255,0.02);
        box-shadow: 0 1px 10px rgba(0,0,0,0.06);
        height: 100%;
      }
      .city { font-size: 1.25rem; font-weight: 650; margin-bottom: 0.25rem; }
      .time { font-size: 2.2rem; font-weight: 750; letter-spacing: 0.2px; margin: 0.25rem 0 0.25rem 0; }
      .date { color: #6b7280; margin-bottom: 0.75rem; }
      .meta-row { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 0.35rem; }
      .pill {
        font-size: 0.85rem;
        border-radius: 999px;
        padding: 4px 10px;
        border: 1px solid rgba(120,120,120,0.25);
        background: rgba(255,255,255,0.03);
      }
      .pill-ok { border-color: rgba(34,197,94,0.45); }
      .pill-warn { border-color: rgba(234,179,8,0.50); }
      .footer { color: #6b7280; font-size: 0.9rem; margin-top: 1.0rem; }
      .small { color: #6b7280; font-size: 0.9rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# Sidebar controls
# ----------------------------
with st.sidebar:
    st.header("Settings")
    refresh_seconds = st.slider("Auto refresh (seconds)", min_value=1, max_value=60, value=1)
    use_24h = st.toggle("24-hour clock", value=True)
    show_seconds = st.toggle("Show seconds", value=True)

# ----------------------------
# Auto refresh (no extra deps)
# ----------------------------
# Streamlit reruns script; we trigger reruns by using a query param "tick"
# that changes every refresh_seconds via a tiny JS snippet.
st.markdown(
    f"""
    <script>
      const refreshMs = {refresh_seconds} * 1000;
      setTimeout(() => {{
        const url = new URL(window.location);
        url.searchParams.set("tick", Date.now());
        window.location.replace(url);
      }}, refreshMs);
    </script>
    """,
    unsafe_allow_html=True
)

# ----------------------------
# Time zone definitions (IANA names)
# These automatically handle DST transitions where applicable.
# ----------------------------
CITIES = [
    ("New York", "America/New_York", "🇺🇸"),
    ("London", "Europe/London", "🇬🇧"),
    ("Oslo", "Europe/Oslo", "🇳🇴"),
    ("Singapore", "Asia/Singapore", "🇸🇬"),
]

def fmt_offset(dt: datetime) -> str:
    """Return UTC offset like +02:00."""
    off = dt.utcoffset()
    if off is None:
        return "+00:00"
    total_minutes = int(off.total_seconds() // 60)
    sign = "+" if total_minutes >= 0 else "-"
    total_minutes = abs(total_minutes)
    hh, mm = divmod(total_minutes, 60)
    return f"{sign}{hh:02d}:{mm:02d}"

def is_dst(dt: datetime) -> bool:
    """Return True if DST is active for the dt's timezone."""
    dst = dt.dst()
    return bool(dst and dst.total_seconds() != 0)

def format_time(dt: datetime, use_24h: bool, show_seconds: bool) -> str:
    if use_24h:
        return dt.strftime("%H:%M:%S" if show_seconds else "%H:%M")
    else:
        return dt.strftime("%I:%M:%S %p" if show_seconds else "%I:%M %p").lstrip("0")

# ----------------------------
# Header
# ----------------------------
st.markdown('<div class="app-title">World Clock — Trading Hubs</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-subtitle">Live local times with correct daylight saving handling (where applicable).</div>',
    unsafe_allow_html=True
)

# Use UTC as the single "source of truth", then convert into each timezone.
now_utc = datetime.now(timezone.utc)

# ----------------------------
# Layout: 4 cards in a row
# ----------------------------
cols = st.columns(4, gap="large")

for col, (city, tz_name, flag) in zip(cols, CITIES):
    with col:
        tz = ZoneInfo(tz_name)
        local = now_utc.astimezone(tz)

        dst_active = is_dst(local)
        offset = fmt_offset(local)

        time_str = format_time(local, use_24h=use_24h, show_seconds=show_seconds)
        date_str = local.strftime("%A, %d %B %Y")

        dst_pill_class = "pill-ok" if dst_active else "pill-warn"
        dst_label = "DST active" if dst_active else "Standard time"

        st.markdown(
            f"""
            <div class="card">
              <div class="city">{flag} {city}</div>
              <div class="time">{time_str}</div>
              <div class="date">{date_str}</div>

              <div class="meta-row">
                <span class="pill">TZ: {tz_name}</span>
                <span class="pill">UTC {offset}</span>
                <span class="pill {dst_pill_class}">{dst_label}</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

# ----------------------------
# Footer / small print
# ----------------------------
st.markdown(
    """
    <div class="footer">
      Tip: Times are computed from UTC and converted using the IANA time zone database (ZoneInfo), which automatically applies DST rules.
    </div>
    """,
    unsafe_allow_html=True
)

st.caption(
    "If DST rules change (rare but possible), keep your Python/OS timezone data updated. "
    "On Windows, installing/keeping Python updated usually keeps the bundled tzdata current when needed."
)


#run using: python -m streamlit run .\app.py