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
        @import url('https://fonts.googleapis.com/css2?family=Caveat:wght@500;600;700&family=Cormorant+Garamond:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&display=swap');
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
        [data-testid="stMetric"] { background: linear-gradient(145deg,rgba(19,34,53,.88),rgba(10,22,36,.9)); border: 1px solid rgba(125,211,252,.14); border-radius: 16px; padding: 1rem 1.1rem; min-height: 112px; }
        [data-testid="stMetricLabel"] { color: #93a4b8; font-size: .72rem; text-transform: uppercase; letter-spacing: .1em; }
        [data-testid="stMetricValue"] { color: #f4f8fb; font-family: 'IBM Plex Mono', monospace; }
        [data-testid="stVerticalBlockBorderWrapper"] { border-color: rgba(125,211,252,.13); background: rgba(11,24,40,.56); border-radius: 18px; }
        [data-testid="stPlotlyChart"] { border-radius: 14px; overflow: hidden; }
        [data-testid="stImage"] img { border: 1px solid rgba(125,211,252,.2); border-radius: 24px; box-shadow: 0 24px 70px rgba(0,0,0,.3); }
        button[data-testid="baseButton-secondary"] { border-color: rgba(125,211,252,.18); }
        h1, h2, h3 { letter-spacing: -.035em; }
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
        @media (prefers-reduced-motion: reduce) { *, *::before, *::after { scroll-behavior: auto !important; } }
        @media (max-width: 680px) { .ns-hero { padding: 1.5rem; min-height: 320px; } .ns-hero-content { max-width: 100%; } .ns-hero-art { width: 100%; opacity: .24; mask-image: linear-gradient(180deg, rgba(0,0,0,.8), transparent 92%); } }
        </style>
        """
    )


def hero(kicker: str, title: str, body: str) -> None:
    st.html(
        f'<section class="ns-hero"><img class="ns-hero-art" src="{_hero_art_uri()}" alt="Nighttime phone use and signal network visual"><div class="ns-hero-content"><div class="ns-kicker">{kicker}</div><h1>{title}</h1><p>{body}</p><div class="ns-hero-meta"><span class="ns-chip">1,000 respondents</span><span class="ns-chip">3 evidence layers</span><span class="ns-chip">Internal validation</span></div></div></section>'
    )


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
