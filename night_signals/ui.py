from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st

from .data import load_survey


def _hero_art_uri() -> str:
    asset = Path(__file__).resolve().parents[1] / "assets" / "night-signals-hero.png"
    return "data:image/png;base64," + base64.b64encode(asset.read_bytes()).decode("ascii")


def inject_brand_surface() -> None:
    """Global visual system for the Night Signals research product."""
    st.html(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Caveat:wght@500;600;700&family=Cormorant+Garamond:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&family=Inter:wght@400;500;600;700&family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&family=Outfit:wght@500;600;700&display=swap');
        :root { color-scheme: dark; }
        [data-testid="stAppViewContainer"] { background: #07101c; }
        [data-testid="stHeader"] { background: rgba(7,16,28,.82); }
        [data-testid="stMainBlockContainer"] { max-width: 1480px; padding-top: 2.2rem; padding-bottom: 4rem; }
        [data-testid="stSidebar"] { background: linear-gradient(180deg,#0c0818 0%,#080611 100%); border-right: 1px solid rgba(177,153,255,.14); }
        [data-testid="stSidebar"] > div:first-child { padding: 1.1rem .78rem .9rem; }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #93a4b8; }
        [data-testid="stSidebarNav"] { padding: .25rem 0 0; }
        [data-testid="stSidebarNav"] ul { gap: .25rem; }
        [data-testid="stSidebarNav"] li { margin: 0; }
        [data-testid="stSidebarNav"] li > div:first-child { color: #81749b; font: 600 .64rem 'IBM Plex Mono', monospace; letter-spacing: .16em; text-transform: uppercase; padding: 1.2rem .78rem .45rem; }
        [data-testid="stSidebarNav"] a { min-height: 2.35rem; border: 1px solid transparent; border-radius: 10px; color: #b5aac8; padding: .58rem .72rem; font: 400 .82rem/1.2 'IBM Plex Sans', sans-serif; transition: background .18s ease, border-color .18s ease, color .18s ease, transform .18s ease; }
        [data-testid="stSidebarNav"] a:hover { background: rgba(183,148,255,.07); border-color: rgba(183,148,255,.16); color: #f4efff; transform: translateX(2px); }
        [data-testid="stSidebarNav"] a[aria-current="page"] { background: linear-gradient(90deg, rgba(135,103,209,.22), rgba(68,49,112,.12)); border-color: rgba(185,157,255,.3); color: #f8f4ff; box-shadow: inset 2px 0 #c5a7ff, 0 8px 22px rgba(0,0,0,.16); }
        [data-testid="stSidebarNav"] a[aria-current="page"] span { color: #dbc9ff; }
        .ns-status-dot { width: .38rem; height: .38rem; border-radius: 999px; background: #9be8cf; box-shadow: 0 0 0 .2rem rgba(155,232,207,.09), 0 0 12px rgba(155,232,207,.55); }
        .ns-sidebar-rule { height: 1px; margin: 1rem .15rem .2rem; background: linear-gradient(90deg, rgba(190,168,255,.3), transparent); }
        .ns-sidebar-footer { margin: 1.2rem .15rem 0; padding: .82rem .15rem 0; border-top: 1px solid rgba(177,153,255,.14); color: #756a89; font: 400 .68rem/1.5 'IBM Plex Sans', sans-serif; }
        .ns-sidebar-footer b { color: #eee8fa; font: 600 .68rem 'IBM Plex Mono', monospace; letter-spacing: .04em; }
        .ns-sidebar-status { display: flex; align-items: center; gap: .48rem; margin-bottom: .2rem; }
        .ns-sidebar-foot-rule { height: 1px; margin: .9rem 0 .8rem; background: rgba(177,153,255,.14); }
        [data-testid="stMetric"] { position: relative; overflow: hidden; background: linear-gradient(160deg,rgba(19,34,53,.94),rgba(10,22,36,.9)); border: 1px solid rgba(125,211,252,.14); border-radius: 16px; padding: 1rem 1.1rem; min-height: 112px; transition: border-color .16s ease, transform .16s ease, box-shadow .16s ease; }
        [data-testid="stMetric"]:before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, #5eead4, transparent 76%); opacity: .9; }
        [data-testid="stMetric"]:hover { border-color: rgba(94,234,212,.38); transform: translateY(-2px); box-shadow: 0 18px 32px rgba(0,0,0,.18); }
        [data-testid="stMetricLabel"] { color: #93a4b8; font-size: .72rem; text-transform: uppercase; letter-spacing: .1em; }
        [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] p { white-space: normal !important; overflow: visible !important; text-overflow: clip !important; line-height: 1.25 !important; }
        [data-testid="stMetricValue"] { color: #f4f8fb; font-family: 'IBM Plex Mono', monospace; }
        .ns-kpi-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: .78rem; margin: .35rem 0 .95rem; }
        .ns-kpi-tile { position: relative; min-height: 126px; overflow: hidden; padding: .92rem 1rem .78rem; border: 1px solid rgba(190,210,192,.15); border-radius: 15px; background: linear-gradient(160deg, rgba(255,255,255,.055), rgba(255,255,255,.014)), rgba(11,24,40,.75); box-shadow: inset 0 1px rgba(255,255,255,.035); transition: transform .16s ease, border-color .16s ease, box-shadow .16s ease; }
        .ns-kpi-tile:before { content: ''; position: absolute; left: 0; right: 0; top: 0; height: 2px; background: linear-gradient(90deg, var(--tile-accent), transparent 78%); }
        .ns-kpi-tile:hover { transform: translateY(-2px); border-color: color-mix(in srgb, var(--tile-accent) 60%, transparent); box-shadow: 0 16px 30px rgba(0,0,0,.18); }
        .ns-kpi-label { color: #9bb0c0; font: 600 .66rem 'Inter', sans-serif; letter-spacing: .13em; text-transform: uppercase; white-space: normal; }
        .ns-kpi-value { margin: .28rem 0 .12rem; color: var(--tile-accent); font: 700 1.82rem/1.05 'Outfit', 'Inter', sans-serif; letter-spacing: -.025em; font-variant-numeric: tabular-nums; }
        .ns-kpi-note { color: #718596; font: 400 .72rem/1.35 'Inter', sans-serif; }
        .ns-kpi-chart { position: absolute; right: .78rem; bottom: .72rem; width: 31%; height: 34px; color: var(--tile-accent); opacity: .9; }
        .ns-kpi-spark { display: block; width: 100%; height: 100%; overflow: visible; }
        [data-testid="stVerticalBlockBorderWrapper"] { border-color: rgba(125,211,252,.13); background: rgba(11,24,40,.56); border-radius: 18px; }
        [data-testid="stPlotlyChart"] { border-radius: 14px; overflow: hidden; }
        [data-testid="stImage"] img { border: 1px solid rgba(125,211,252,.2); border-radius: 24px; box-shadow: 0 24px 70px rgba(0,0,0,.3); }
        button[data-testid="baseButton-secondary"] { border-color: rgba(125,211,252,.18); }
        h1, h2, h3 { letter-spacing: -.035em; font-family: 'Outfit', 'IBM Plex Sans', sans-serif; }
        h2 { margin-top: 2rem; }
        .ns-hero {
          position: relative; overflow: hidden; min-height: 330px; padding: 2.6rem 2.8rem;
          border: 1px solid rgba(125, 211, 252, .22); border-radius: 24px;
          background:
            radial-gradient(circle at 92% 8%, rgba(94,234,212,.2), transparent 24%),
            radial-gradient(circle at 5% 100%, rgba(77,107,255,.17), transparent 36%),
            linear-gradient(135deg, #0c1d31, #07111f 70%);
          box-shadow: 0 24px 90px rgba(0,0,0,.28), inset 0 1px rgba(255,255,255,.04);
        }
        .ns-hero-art { position: absolute; z-index: 0; right: 0; top: 0; width: 54%; height: 100%; object-fit: cover; opacity: .55; filter: saturate(.78) contrast(1.05); mask-image: linear-gradient(90deg, transparent 0%, rgba(0,0,0,.72) 34%, #000 78%); }
        .ns-hero-content { position: relative; z-index: 1; max-width: 64%; }
        .ns-hero:after {
          content: ""; position: absolute; inset: 0; pointer-events: none; opacity: .35;
          background-image: radial-gradient(circle, rgba(167,243,208,.55) 1px, transparent 1px);
          background-size: 26px 26px; mask-image: linear-gradient(90deg, transparent 30%, #000);
        }
        .ns-kicker { color: #69dbc8; letter-spacing: .16em; text-transform: uppercase; font: 600 .76rem 'IBM Plex Mono', monospace; }
        .ns-hero h1 { position: relative; z-index: 1; max-width: 760px; margin: .7rem 0 .9rem; font: 600 clamp(2.45rem,5vw,5.25rem)/.94 'Newsreader', serif; letter-spacing: -.045em; color: #f5f8fb; }
        .ns-hero p { position: relative; z-index: 1; max-width: 720px; color: #b9c6d4; font-size: 1.03rem; line-height: 1.65; }
        .ns-hero-meta { position: relative; z-index: 1; display: flex; gap: .55rem; flex-wrap: wrap; margin-top: 1.45rem; }
        .ns-chip { border: 1px solid rgba(94,234,212,.28); background: rgba(94,234,212,.08); border-radius: 999px; padding: .42rem .72rem; color: #a7f3d0; font: 600 .68rem 'IBM Plex Mono', monospace; letter-spacing: .08em; text-transform: uppercase; }
        .ns-media { position: relative; overflow: hidden; border: 1px solid rgba(125,211,252,.2); border-radius: 24px; background: #050b13; box-shadow: 0 24px 70px rgba(0,0,0,.3); }
        .ns-media video { display: block; width: 100%; height: 345px; object-fit: cover; filter: saturate(.9) contrast(1.04) brightness(.72); }
        .ns-media-large video { height: 610px; }
        .ns-media:after { content: ''; position: absolute; inset: 0; pointer-events: none; background: linear-gradient(180deg, transparent 42%, rgba(4,10,17,.82)); }
        .ns-media-label { position: absolute; z-index: 1; left: 1.2rem; right: 1.2rem; bottom: 1rem; color: #e5eef7; font: 600 .72rem 'IBM Plex Mono', monospace; letter-spacing: .09em; text-transform: uppercase; }
        .ns-media-label span { display: block; margin-top: .3rem; color: #94a9bd; font: 400 .78rem Inter, sans-serif; letter-spacing: 0; text-transform: none; }
        .ns-section-kicker { color: #69dbc8; font: 600 .7rem 'IBM Plex Mono', monospace; letter-spacing: .15em; text-transform: uppercase; }
        .ns-brand { display: flex; align-items: center; gap: .7rem; margin: .2rem 0 .25rem; color: #f5f1fb; font: 600 1.5rem/.88 'Cormorant Garamond', Georgia, serif; letter-spacing: -.035em; }
        .ns-brand-mark { position: relative; display: block; width: 2.15rem; height: 2.15rem; border: 1px solid rgba(202,174,255,.7); border-radius: 50%; background: #0f0a1c; box-shadow: 0 0 18px rgba(170,133,255,.18); }
        .ns-brand-mark:before { content: ''; position: absolute; width: 1.55rem; height: 1.55rem; left: .27rem; top: .25rem; border-radius: 50%; background: #d4baff; }
        .ns-brand-mark:after { content: ''; position: absolute; width: 1.55rem; height: 1.55rem; left: .52rem; top: .08rem; border-radius: 50%; background: #0f0a1c; }
        .ns-brand small { display: block; margin-top: .28rem; color: #9a8eaa; font: 500 .58rem 'IBM Plex Mono', monospace; letter-spacing: .12em; text-transform: uppercase; }
        .ns-script { color: #a7f3d0; font: 600 1.35rem/1.1 Caveat, cursive; letter-spacing: .01em; }
        .ns-landing-kicker { color: #69dbc8; font: 600 .72rem 'IBM Plex Mono', monospace; letter-spacing: .18em; text-transform: uppercase; }
        .ns-landing-title { margin: .9rem 0 1rem; color: #f7fafc; font: 600 clamp(3.8rem, 8vw, 7.8rem)/.78 'Newsreader', Georgia, serif; letter-spacing: -.065em; }
        .ns-landing-title em { display: block; color: #c7a4ff; font-family: Caveat, cursive; font-size: .82em; font-style: italic; letter-spacing: -.02em; }
        .ns-landing-tagline { max-width: 560px; color: #b6c2d0; font-size: 1.05rem; line-height: 1.65; }
        .ns-landing-stat { border-top: 1px solid rgba(148,163,184,.18); padding-top: 1rem; margin-top: 2rem; color: #f2f6fa; font: 500 .82rem 'IBM Plex Mono', monospace; letter-spacing: .08em; text-transform: uppercase; }
        .ns-landing-stat span { color: #7e8fa1; }
        .ns-landing-rule { height: 1px; margin: 1.5rem 0; background: linear-gradient(90deg, rgba(148,163,184,.35), transparent); }
        .ns-landing-footnote { color: #8393a5; font-size: .78rem; line-height: 1.5; }
        .ns-note { border-left: 3px solid #5eead4; padding: .2rem 0 .2rem 1rem; color: #b8c4d1; }
        .ns-label { color: #8fa1b4; font: 500 .73rem 'IBM Plex Mono', monospace; letter-spacing: .1em; text-transform: uppercase; }
        /* Research-dashboard pass: quiet surfaces, readable type, and a restrained data palette. */
        [data-testid="stAppViewContainer"] { background: #0b0f14; }
        [data-testid="stHeader"] { background: rgba(11,15,20,.88); border-bottom: 1px solid rgba(148,163,184,.08); }
        [data-testid="stMainBlockContainer"] { max-width: 1540px; padding-top: 1.6rem; }
        [data-testid="stSidebar"] { width: 266px !important; background: #0d141c; border-right: 1px solid rgba(148,163,184,.16); }
        [data-testid="stSidebar"] > div:first-child { padding: 1.15rem .82rem .85rem; }
        [data-testid="stSidebar"] { font-family: 'Segoe UI', Arial, sans-serif; }
        .ns-brand { color: #edf3f7; font: 600 .92rem/1 'Segoe UI', Arial, sans-serif; letter-spacing: .08em; text-transform: uppercase; }
        .ns-brand small { color: #7f92a4; font: 500 .57rem 'Segoe UI', Arial, sans-serif; letter-spacing: .08em; }
        .ns-brand-mark { width: 2.15rem; height: 2.15rem; border-color: rgba(94,234,212,.5); background: #111c26; box-shadow: 0 0 18px rgba(45,212,191,.12); }
        .ns-brand-mark:before { background: #79e2d0; }
        .ns-brand-mark:after { background: #111c26; }
        .ns-sidebar-rule { margin: 1rem .2rem .35rem; background: linear-gradient(90deg, rgba(94,234,212,.28), transparent); }
        [data-testid="stSidebarNav"] li > div:first-child { color: #6f8497; font: 600 .62rem 'Segoe UI', Arial, sans-serif; letter-spacing: .1em; }
        [data-testid="stSidebarNav"] a { color: #a9bac8; font: 400 .82rem/1.2 'Segoe UI', Arial, sans-serif; border-radius: 9px; }
        [data-testid="stSidebarNav"] a:hover { background: rgba(45,212,191,.07); border-color: rgba(45,212,191,.16); color: #f2fbfa; }
        [data-testid="stSidebarNav"] a[aria-current="page"] { background: #172533; border-color: rgba(56,189,248,.3); box-shadow: inset 2px 0 #2dd4bf; color: #f5fbff; }
        [data-testid="stSidebarNav"] a[aria-current="page"] span { color: #8ce9db; }
        .ns-sidebar-footer { color: #708496; border-top-color: rgba(148,163,184,.13); font-family: 'Segoe UI', Arial, sans-serif; }
        .ns-sidebar-footer b { color: #c6d3dd; font-family: 'Segoe UI', Arial, sans-serif; letter-spacing: .04em; }
        .ns-sidebar-foot-rule { background: rgba(148,163,184,.13); }
        [data-testid="stMetric"] { background: #131a22; border: 1px solid rgba(148,163,184,.16); border-radius: 12px; box-shadow: none; }
        [data-testid="stMetricLabel"] { color: #8da0b1; font-family: 'IBM Plex Sans', sans-serif; }
        [data-testid="stMetricValue"] { color: #eef6f8; font-family: 'IBM Plex Sans', sans-serif; font-weight: 600; }
        [data-testid="stVerticalBlockBorderWrapper"] { background: #111820; border: 1px solid rgba(148,163,184,.15); border-radius: 14px; box-shadow: none; }
        [data-testid="stPlotlyChart"] { border: 1px solid rgba(148,163,184,.11); border-radius: 12px; background: #0f161e; }
        h1, h2, h3 { color: #edf4f7 !important; letter-spacing: -.035em; }
        p, li, label { color: #b7c4cf; }
        div[data-testid="stCaptionContainer"] p { color: #7f92a3 !important; }
        button[data-testid="baseButton-primary"] { background: #2dd4bf; border-color: #2dd4bf; color: #071315; }
        button[data-testid="baseButton-primary"] p { color: #071315 !important; }
        button[data-testid="baseButton-primary"] { box-shadow: 0 10px 28px -14px rgba(45,212,191,.9), inset 0 1px rgba(255,255,255,.22); font-weight: 700; transition: transform .16s ease, filter .16s ease, box-shadow .16s ease; }
        button[data-testid="baseButton-primary"] p, button[data-testid="baseButton-primary"] span { color: #05201f !important; font-weight: 700 !important; }
        button[data-testid="baseButton-primary"]:hover { filter: brightness(1.08); transform: translateY(-1px); box-shadow: 0 14px 34px -12px rgba(45,212,191,.95), inset 0 1px rgba(255,255,255,.25); }
        [data-testid="stAlert"] { background: rgba(217,178,106,.08) !important; border: 1px solid rgba(217,178,106,.32) !important; border-radius: 12px !important; color: #c6d2cf !important; }
        button[data-testid="baseButton-secondary"] { background: #141e28; border-color: rgba(148,163,184,.23); color: #d3e0e8; }
        [data-testid="stDataFrame"] { border: 1px solid rgba(148,163,184,.14); border-radius: 12px; overflow: hidden; }
        /* Keep the normal font change scoped to the left navigation only. */
        [data-testid="stSidebar"], [data-testid="stSidebar"] *, [data-testid="stSidebarNav"],
        [data-testid="stSidebarNav"] * { font-family: Arial, 'Segoe UI', sans-serif !important; }
        [data-testid="stSidebarNav"] li > div:first-child { letter-spacing: .04em !important; text-transform: none !important; }
        [data-testid="stSidebarNav"] a { letter-spacing: normal !important; text-transform: none !important; }
        [data-testid="stSidebarNav"] a span { font-family: Arial, 'Segoe UI', sans-serif !important; }
        /* Streamlit icons are ligatures; never replace their icon font with the body font. */
        [data-testid="stSidebar"] [data-testid="stIconMaterial"],
        [data-testid="stSidebar"] .material-symbols-rounded,
        [data-testid="stSidebar"] .material-symbols-outlined,
        [data-testid="stMainBlockContainer"] [data-testid="stIconMaterial"],
        [data-testid="stMainBlockContainer"] .material-symbols-rounded,
        [data-testid="stMainBlockContainer"] .material-symbols-outlined,
        [class*="material-symbols"] { font-family: 'Material Symbols Rounded', 'Material Symbols Outlined' !important; font-weight: normal !important; letter-spacing: normal !important; text-transform: none !important; }
        .ns-brand, .ns-brand small { font-family: Arial, 'Segoe UI', sans-serif !important; }
        /* Compact navigation rail: keep the atlas dense while giving the main heading priority. */
        [data-testid="stSidebar"] { width: 224px !important; min-width: 224px !important; }
        [data-testid="stSidebar"] > div:first-child { padding: .72rem .62rem .65rem; }
        [data-testid="stSidebarNav"] { padding-top: 0; }
        [data-testid="stSidebarNav"] ul { gap: .12rem; }
        [data-testid="stSidebarNav"] li > div:first-child { padding: .78rem .62rem .28rem; font-size: .58rem; }
        [data-testid="stSidebarNav"] a { min-height: 2.08rem; padding: .43rem .58rem; font-size: .76rem; }
        .ns-sidebar-rule { margin: .72rem .12rem .18rem; }
        .ns-sidebar-footer { margin-top: .78rem; padding-top: .65rem; font-size: .62rem; }
        [data-testid="stMainBlockContainer"] { max-width: 1540px; padding-top: 4.15rem !important; }
        [data-testid="stMainBlockContainer"] h1 { margin-top: .15rem !important; }
        .ns-topbar { position: fixed; z-index: 10000; top: 0; left: 0; right: 0; height: 58px; display: flex; align-items: center; justify-content: space-between; padding: 0 1.35rem 0 1.55rem; background: rgba(5,13,24,.98); border-bottom: 1px solid rgba(91,177,227,.14); box-shadow: 0 10px 30px rgba(0,0,0,.16); }
        .ns-topbar-brand { display: flex; align-items: center; gap: .72rem; color: #f5fbff; font: 700 .98rem/1 'Outfit', 'Inter', sans-serif; letter-spacing: .1em; }
        .ns-topbar-brand small { display: block; margin-top: .24rem; color: #27d9e0; font: 500 .56rem 'IBM Plex Mono', monospace; letter-spacing: .15em; }
        .ns-topbar-mark { position: relative; display: grid; place-items: center; width: 2rem; height: 2rem; border-radius: 15px; color: #5eead4; background: radial-gradient(circle at 32% 26%, rgba(127,181,130,.3), rgba(94,163,143,.1) 58%, transparent 74%), #0b1d2a; border: 1px solid rgba(94,234,212,.35); font-size: 1.35rem; line-height: 1; box-shadow: 0 0 28px -8px rgba(94,234,212,.8), inset 0 1px rgba(255,255,255,.08); }
        .ns-topbar-mark:before { content: ''; position: absolute; inset: -4px; z-index: -1; border-radius: 19px; background: conic-gradient(#5eead4, #8b9cff, #f6c177, #5eead4); filter: blur(8px); opacity: .25; animation: ns-ring-spin 10s linear infinite; }
        @keyframes ns-ring-spin { to { transform: rotate(360deg); } }
        .ns-topbar-actions { display: flex; align-items: center; gap: 1.05rem; color: #dbe9f2; font: 500 .78rem 'IBM Plex Sans', sans-serif; }
        .ns-topbar-actions span:first-child { padding: .48rem .72rem; border: 1px solid rgba(148,163,184,.2); border-radius: 8px; white-space: nowrap; }
        .ns-topbar-icon { font-size: 1.15rem; color: #f5fbff; }
        .ns-sidebar-brand { position: fixed; z-index: 10001; top: 0; left: 0; width: 224px; height: 58px; display: flex; align-items: center; gap: .68rem; padding: 0 1.1rem; box-sizing: border-box; background: rgba(5,13,24,.98); border-right: 1px solid rgba(91,177,227,.14); border-bottom: 1px solid rgba(91,177,227,.14); color: #f5fbff; }
        .ns-sidebar-brand b { display: block; font: 700 .88rem/1 'Outfit', 'Inter', sans-serif; letter-spacing: .1em; }
        .ns-sidebar-brand small { display: block; margin-top: .24rem; color: #27d9e0; font: 500 .5rem 'IBM Plex Mono', monospace; letter-spacing: .13em; }
        [data-testid="stHeader"] { background: transparent !important; z-index: 1001; }
        [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"], .stDeployButton, #MainMenu { display: none !important; }
        [data-testid="stSidebar"] { padding-top: 58px !important; }
        [data-testid="stMainBlockContainer"] { padding-top: 5.1rem !important; }
        .ns-section-kicker { color: #31dfe0; }
        .ns-overview-hero { min-height: 342px; padding: 1.95rem 2.7rem; border-color: rgba(42,191,241,.32); background: linear-gradient(112deg, rgba(5,22,39,.98) 0%, rgba(5,18,32,.9) 52%, rgba(8,24,42,.45) 100%); }
        .ns-overview-hero .ns-hero-art { width: 58%; opacity: .74; mask-image: linear-gradient(90deg, transparent 0%, rgba(0,0,0,.48) 20%, #000 60%); }
        .ns-overview-hero .ns-hero-content { max-width: 61%; }
        .ns-overview-hero .ns-hero h1 { font-size: clamp(3.05rem, 5.3vw, 4.8rem); line-height: .91; margin-bottom: .65rem; }
        .ns-overview-hero .ns-hero p { max-width: 680px; font-size: .96rem; line-height: 1.48; }
        .ns-overview-hero .ns-hero-accent { color: #61ead4; }
        .ns-overview-hero .ns-chip { border-color: rgba(45,212,191,.5); background: rgba(5,40,54,.7); }
        .ns-explore-bar { margin-top: .9rem; }
        .ns-panel-label { color: #d8edf5; font: 600 .72rem 'Inter', sans-serif; letter-spacing: .13em; text-transform: uppercase; }
        .ns-takeaway { min-height: 290px; border: 1px solid rgba(45,212,191,.22); border-radius: 14px; padding: 1.25rem; background: linear-gradient(150deg, rgba(11,33,50,.88), rgba(7,20,32,.92)); }
        .ns-takeaway p { color: #c5d7e3; line-height: 1.55; }
        @media (prefers-reduced-motion: reduce) { *, *::before, *::after { scroll-behavior: auto !important; } }
        @media (max-width: 980px) { .ns-kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .ns-overview-hero .ns-hero-content { max-width: 68%; } }
        @media (max-width: 680px) { .ns-kpi-grid { grid-template-columns: 1fr; } .ns-hero { padding: 1.5rem; min-height: 320px; } .ns-hero-content { max-width: 100%; } .ns-hero-art { width: 100%; opacity: .24; mask-image: linear-gradient(180deg, rgba(0,0,0,.8), transparent 92%); } .ns-overview-hero .ns-hero-content { max-width: 100%; } .ns-topbar-actions span:not(:first-child) { display:none; } }
        </style>
        <div class="ns-topbar">
          <div class="ns-topbar-brand"><span class="ns-topbar-mark">◔</span><span><b>NIGHT SIGNALS</b><small>RESEARCH ATLAS</small></span></div>
          <div class="ns-topbar-actions"><span>↗&nbsp; Share</span><span class="ns-topbar-icon">◉</span><span class="ns-topbar-icon">☼</span></div>
        </div>
        """
    )
    hero_uri = _hero_art_uri()
    st.html(
        "<style>"
        "[data-testid='stAppViewContainer']{background:linear-gradient(180deg,rgba(5,13,24,.91),rgba(4,11,19,.98)),url('"
        + hero_uri
        + "') center/cover fixed no-repeat;}"
        "[data-testid='stMainBlockContainer']{max-width:1540px;padding-left:1.25rem;padding-right:1.25rem;}"
        "[data-testid='stVerticalBlockBorderWrapper']{background:rgba(6,18,30,.72);backdrop-filter:blur(14px) saturate(1.08);border-radius:16px;}"
        "[data-testid='stMetric']{background:linear-gradient(145deg,rgba(15,33,48,.94),rgba(7,21,34,.88));box-shadow:inset 0 1px rgba(255,255,255,.035),0 12px 30px rgba(0,0,0,.12);}\n"
        ".ns-topbar,.ns-sidebar-brand{backdrop-filter:blur(14px) saturate(1.1);}\n"
        "</style>"
    )


def hero(kicker: str, title: str, body: str, class_name: str = "ns-overview-hero") -> None:
    st.html(
        f'<section class="ns-hero {class_name}"><img class="ns-hero-art" src="{_hero_art_uri()}" alt="Nighttime phone use and signal network visual"><div class="ns-hero-content"><div class="ns-kicker">{kicker}</div><h1>{title}</h1><p>{body}</p><div class="ns-hero-meta"><span class="ns-chip">1,000 synthetic records</span><span class="ns-chip">3 separate data layers</span><span class="ns-chip">Internal validation</span></div></div></section>'
    )


def _sparkline(values: list[float]) -> str:
    if not values:
        return ""
    lo, hi = min(values), max(values)
    span = hi - lo or 1
    points = " ".join(
        f"{index * 100 / max(len(values) - 1, 1):.1f},{34 - ((value - lo) / span) * 26:.1f}"
        for index, value in enumerate(values)
    )
    return (
        '<svg class="ns-kpi-spark" viewBox="0 0 100 36" preserveAspectRatio="none" aria-hidden="true">'
        f'<polyline points="{points}" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>'
        "</svg>"
    )


def kpi_tiles(items: list[tuple[str, str, str, list[float], str]]) -> None:
    """Render the authored metric tiles used by the atlas overview."""
    cards = []
    for label, value, note, trend, accent in items:
        cards.append(
            f'<article class="ns-kpi-tile" style="--tile-accent:{accent}">'
            f'<div class="ns-kpi-label">{label}</div>'
            f'<div class="ns-kpi-value">{value}</div>'
            f'<div class="ns-kpi-note">{note}</div>'
            f'<div class="ns-kpi-chart">{_sparkline(trend)}</div>'
            "</article>"
        )
    st.html(f'<section class="ns-kpi-grid">{"".join(cards)}</section>')


def cinematic_media(large: bool = False) -> None:
    """Render the original cinematic asset with a resilient poster fallback."""
    st.html(
        """
        <div class="ns-media {media_size}" role="img" aria-label="Cinematic night-time phone use visual">
          <video autoplay muted loop playsinline preload="metadata" poster="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260806_132328_5f9029c8-218f-4489-82b6-29ff2849920e.png">
            <source src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260806_133255_956f653f-5d80-4b06-abd5-0f46c98b60fa.mp4" type="video/mp4">
          </video>
          <div class="ns-media-label">Signal / 00:47<span>Nighttime digital behaviour is the exposure. Sleep is the outcome.</span></div>
        </div>
        """.format(media_size="ns-media-large" if large else "")
    )


def evidence_note(text: str) -> None:
    st.html(f'<div class="ns-note">{text}</div>')


def page_intro(title: str, caption: str, icon: str) -> None:
    st.title(title, icon=icon)
    st.caption(caption)


def cohort_filter_bar() -> None:
    """Responsive in-page cohort filters, replacing a persistent sidebar control rail."""
    df = load_survey()
    with st.container(border=True, horizontal=True, gap="medium"):
        st.html('<div class="ns-section-kicker">Cohort lens</div>')
        st.multiselect("Gender", sorted(df["gender"].dropna().unique()), key="global_gender", placeholder="All genders")
        st.multiselect("Occupation", sorted(df["occupation_status"].dropna().unique()), key="global_occupation", placeholder="All occupations")
        st.multiselect("Exposure quartile", ["Q1 · lowest", "Q2", "Q3", "Q4 · highest"], key="global_exposure", placeholder="All quartiles")


def footer() -> None:
    st.space("large")
    st.caption(
        "Night Signals is an educational research atlas. Results are associative or predictive, not causal, diagnostic, or clinical advice."
    )
