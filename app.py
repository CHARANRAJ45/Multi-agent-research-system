"""
Autonomous Multi-Agent Research: single-file Streamlit app.

Run:  streamlit run app.py
Needs Streamlit >= 1.40. Theme, fonts and layout are all defined in this file,
so no .streamlit/config.toml is required.
If pipeline.py is missing, the app runs in demo mode with sample output.
"""
import asyncio
import inspect
import json
import time

import streamlit as st

try:
    from pipeline import run_research_pipeline  # Adjust if your function name or import differs

    DEMO_MODE = False
except ImportError:
    DEMO_MODE = True

    def run_research_pipeline(topic):
        """Stand-in so the UI can be previewed without the real backend."""
        time.sleep(4)
        return {
            "report": (
                f"# {topic}\n\n"
                "## Summary\n"
                "This is sample output. Add your `pipeline.py` next to this file "
                "to get a real, sourced report.\n\n"
                "## Key points\n"
                "- The Search agent would gather recent sources.\n"
                "- The Reader agent would extract the relevant content.\n"
                "- The Writer and Critic agents would draft and review the report.\n"
            ),
            "sources": [],
        }


# ─────────────────────────────────────────────────────────────
# Page setup
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Multi-Agent Research",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

AGENTS = [
    ("Search", "Finds sources"),
    ("Reader", "Extracts content"),
    ("Writer", "Drafts the report"),
    ("Critic", "Reviews the draft"),
]

EXAMPLES = [
    "Solid-state batteries: where the technology stands in 2026",
    "How retrieval-augmented generation is used in education",
    "Post-quantum cryptography migration timelines",
]

DEPTH_OPTIONS = ["Quick", "Balanced", "Deep"]
SOURCE_OPTIONS = [3, 5, 8, 10]

# ─────────────────────────────────────────────────────────────
# Styling (this block replaces a config.toml theme)
# ─────────────────────────────────────────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=DM+Sans:ital,wght@0,400;0,500;0,600;1,400&display=swap');

:root {
    --ink: #0b0f1a;
    --surface: #131a2b;
    --surface-2: #1a2238;
    --line: #252f4a;
    --text: #e7e9f2;
    --muted: #8f9ab8;
    --amber: #f5b544;
    --mint: #6ee7b7;
    --red: #f87171;
    --display: 'Bricolage Grotesque', 'DM Sans', system-ui, sans-serif;
}

/* Base: force the dark palette regardless of the viewer's Streamlit theme */
.stApp { background: var(--ink); color: var(--text); color-scheme: dark; }
.stApp, .stApp p, .stApp label, .stApp input, .stApp button, .stApp textarea, .stApp li {
    font-family: 'DM Sans', system-ui, sans-serif;
}
.block-container { max-width: 920px; padding-top: 3.5rem; padding-bottom: 5rem; }
header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }
[data-testid="stWidgetLabel"] p, label { color: var(--muted); font-size: .85rem; }
[data-testid="stCaptionContainer"] { color: var(--muted); }

/* Hero */
.hero-title {
    font-family: var(--display);
    font-weight: 800;
    font-size: clamp(2.2rem, 5.2vw, 3.7rem);
    line-height: 1.04;
    letter-spacing: -0.03em;
    color: var(--text);
    margin: 0 0 1rem;
    max-width: 16ch;
}
.hero-sub {
    color: var(--muted);
    font-size: 1.1rem;
    line-height: 1.55;
    max-width: 54ch;
    margin: 0 0 2.25rem;
}

/* Input form */
[data-testid="stForm"] {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 20px;
    padding: 1.25rem 1.25rem 1rem;
}
.stTextInput div[data-baseweb="input"] {
    background: var(--ink);
    border: 1px solid var(--line);
    border-radius: 12px;
    transition: border-color .15s, box-shadow .15s;
}
.stTextInput div[data-baseweb="input"]:focus-within {
    border-color: var(--amber);
    box-shadow: 0 0 0 3px rgba(245, 181, 68, .25);
}
.stTextInput input {
    font-size: 1.05rem;
    padding: .95rem 1rem;
    color: var(--text);
    background: transparent;
}
.stTextInput input::placeholder { color: #5d6784; }

/* Segmented controls (depth, sources) */
button[data-testid="stBaseButton-segmented_control"] {
    background: var(--surface-2);
    border: 1px solid var(--line);
    color: var(--muted);
}
button[data-testid="stBaseButton-segmented_control"] p { color: var(--muted); }
button[data-testid="stBaseButton-segmented_control"]:hover { border-color: var(--amber); }
button[data-testid="stBaseButton-segmented_controlActive"] {
    background: var(--amber);
    border: 1px solid var(--amber);
}
button[data-testid="stBaseButton-segmented_controlActive"] p { color: #1a1200; font-weight: 600; }

/* Submit */
[data-testid="stFormSubmitButton"] button {
    background: var(--amber);
    border: 0;
    border-radius: 12px;
    height: 3rem;
    font-weight: 600;
    transition: filter .15s, transform .15s;
}
[data-testid="stFormSubmitButton"] button p { color: #1a1200; }
[data-testid="stFormSubmitButton"] button:hover { filter: brightness(1.08); }
[data-testid="stFormSubmitButton"] button:active { transform: translateY(1px); }
[data-testid="stFormSubmitButton"] button:focus-visible {
    outline: 2px solid var(--text);
    outline-offset: 2px;
}

/* Example chips */
.stButton button {
    background: transparent;
    border: 1px solid var(--line);
    border-radius: 999px;
    color: var(--muted);
    font-size: .88rem;
    line-height: 1.3;
    padding: .5rem .95rem;
    height: auto;
    min-height: 0;
    text-align: left;
    transition: border-color .15s, color .15s;
}
.stButton button p { color: inherit; }
.stButton button:hover { border-color: var(--amber); color: var(--text); }
.stButton button:focus-visible { outline: 2px solid var(--amber); outline-offset: 2px; }

/* Agent pipeline */
.pipeline {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin: 2.25rem 0 .75rem;
}
.node {
    position: relative;
    display: flex;
    gap: .75rem;
    align-items: flex-start;
    padding: .9rem 1rem;
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 14px;
    transition: border-color .3s, background .3s;
}
.node:not(:last-child)::after {
    content: "";
    position: absolute;
    top: 50%;
    right: -1rem;
    width: 1rem;
    height: 1px;
    background: var(--line);
}
.node .dot {
    flex: none;
    width: 28px;
    height: 28px;
    display: grid;
    place-items: center;
    border-radius: 50%;
    border: 1.5px solid var(--line);
    color: var(--muted);
    font: 600 .8rem var(--display);
}
.node b { display: block; color: var(--text); font-size: .95rem; font-weight: 600; }
.node small { display: block; color: var(--muted); font-size: .8rem; margin-top: .1rem; }

.pipeline.running .node { animation: lit 1.6s ease-in-out infinite; animation-delay: calc(var(--i) * .4s); }
.pipeline.running .dot {
    border-color: var(--amber);
    color: var(--amber);
    animation: pulse 1.6s ease-in-out infinite;
    animation-delay: calc(var(--i) * .4s);
}
@keyframes lit {
    0%, 100% { border-color: var(--line); background: var(--surface); }
    40% { border-color: var(--amber); background: var(--surface-2); }
}
@keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(245, 181, 68, 0); }
    50% { box-shadow: 0 0 0 6px rgba(245, 181, 68, .22); }
}

.pipeline.done .node { border-color: rgba(110, 231, 183, .3); }
.pipeline.done .dot { background: var(--mint); border-color: var(--mint); color: #04261a; }
.pipeline.error .node { border-color: rgba(248, 113, 113, .35); }
.pipeline.error .dot { border-color: var(--red); color: var(--red); }

.pipeline-status { color: var(--muted); font-size: .92rem; margin: 0 0 2.25rem; }

@media (max-width: 720px) {
    .pipeline { grid-template-columns: 1fr 1fr; }
    .node:not(:last-child)::after { display: none; }
}
@media (prefers-reduced-motion: reduce) {
    .pipeline.running .node, .pipeline.running .dot { animation: none; }
    .pipeline.running .dot { box-shadow: 0 0 0 3px rgba(245, 181, 68, .3); }
}

/* Alerts */
[data-testid="stAlert"] {
    background: var(--surface-2);
    border: 1px solid var(--line);
    border-radius: 12px;
    color: var(--text);
}

/* Results */
.stats {
    display: flex;
    flex-wrap: wrap;
    gap: 2.5rem;
    padding: 1rem 0;
    margin: 0 0 1.5rem;
    border-top: 1px solid var(--line);
    border-bottom: 1px solid var(--line);
}
.stats b { display: block; font: 700 1.45rem var(--display); color: var(--text); }
.stats span { color: var(--muted); font-size: .85rem; }

[data-baseweb="tab-list"] { border-bottom: 1px solid var(--line); }
[data-baseweb="tab"] p { color: var(--muted); }
[data-baseweb="tab"][aria-selected="true"] p { color: var(--amber); }
[data-baseweb="tab-highlight"] { background-color: var(--amber); }

.st-key-report {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 2rem 2.25rem;
    margin-bottom: 1rem;
}
.st-key-report p, .st-key-report li {
    font-size: 1.05rem;
    line-height: 1.75;
    color: #d5d9e8;
    max-width: 72ch;
}
.st-key-report h1, .st-key-report h2, .st-key-report h3 {
    font-family: var(--display);
    letter-spacing: -0.015em;
    color: var(--text);
}
.st-key-report a { color: var(--amber); }

[data-testid="stCode"] {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 12px;
}
[data-testid="stCode"] pre, [data-testid="stCode"] code { background: transparent; color: #d5d9e8; }

.stDownloadButton button {
    background: var(--surface-2);
    border: 1px solid var(--line);
    border-radius: 12px;
}
.stDownloadButton button p { color: var(--text); }
.stDownloadButton button:hover { border-color: var(--amber); }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────
def pipeline_html(state: str, message: str) -> str:
    """Render the four-agent tracker. state: idle | running | done | error."""
    nodes = []
    for i, (name, desc) in enumerate(AGENTS):
        marker = {"done": "✓", "error": "!"}.get(state, str(i + 1))
        nodes.append(
            f'<div class="node" style="--i:{i}">'
            f'<span class="dot">{marker}</span>'
            f"<div><b>{name}</b><small>{desc}</small></div>"
            f"</div>"
        )
    return (
        f'<div class="pipeline {state}">{"".join(nodes)}</div>'
        f'<div class="pipeline-status" role="status">{message}</div>'
    )


def call_pipeline(topic: str, depth: str, max_sources: int):
    """Call the backend, passing depth / source limits only if it accepts them."""
    params = inspect.signature(run_research_pipeline).parameters
    candidates = {
        "depth": depth,
        "research_depth": depth,
        "max_sources": max_sources,
        "num_sources": max_sources,
    }
    kwargs = {k: v for k, v in candidates.items() if k in params}

    if inspect.iscoroutinefunction(run_research_pipeline):
        return asyncio.run(run_research_pipeline(topic, **kwargs))
    return run_research_pipeline(topic, **kwargs)


def extract_report(output) -> str:
    if isinstance(output, dict):
        for key in ("report", "final_report", "summary", "final_output"):
            if output.get(key):
                return str(output[key])
    return str(output)


def fmt_duration(seconds: float) -> str:
    seconds = int(round(seconds))
    return f"{seconds}s" if seconds < 60 else f"{seconds // 60}m {seconds % 60:02d}s"


def use_example(text: str) -> None:
    st.session_state["topic"] = text


def render_result(result: dict) -> None:
    report = result["report"]
    words = len(report.split())
    minutes = max(1, round(words / 220))

    st.markdown(
        '<div class="stats">'
        f"<div><b>{words:,}</b><span>words</span></div>"
        f"<div><b>{minutes} min</b><span>read</span></div>"
        f"<div><b>{fmt_duration(result['elapsed'])}</b><span>research time</span></div>"
        f"<div><b>{result['depth']}</b><span>depth, up to {result['max_sources']} sources</span></div>"
        "</div>",
        unsafe_allow_html=True,
    )

    tab_report, tab_state = st.tabs(["Report", "Pipeline state"])

    with tab_report:
        with st.container(key="report"):
            st.markdown(report)
        st.download_button(
            "Download report (.md)",
            data=report,
            file_name=f"research_report_{result['ts']}.md",
            mime="text/markdown",
        )

    with tab_state:
        st.code(json.dumps(result["output"], indent=2, default=str), language="json")


# ─────────────────────────────────────────────────────────────
# Hero
# ─────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="hero-title">Ask a question. Get a researched report.</div>
    <div class="hero-sub">Four agents search the web, read the pages, write a draft and review it before it reaches you.</div>
    """,
    unsafe_allow_html=True,
)
if DEMO_MODE:
    st.caption("Demo mode: pipeline.py wasn't found, so results are sample text.")

# ─────────────────────────────────────────────────────────────
# Input
# ─────────────────────────────────────────────────────────────
st.session_state.setdefault("topic", "")


def choice(label, options, default):
    """Segmented control, with a radio fallback for older Streamlit."""
    if hasattr(st, "segmented_control"):
        value = st.segmented_control(label, options, default=default)
    else:
        value = st.radio(label, options, index=options.index(default), horizontal=True)
    return value or default


with st.form(key="research_form"):
    topic_input = st.text_input(
        "Research topic",
        key="topic",
        placeholder="e.g. The impact of quantum computing on cryptography in 2026",
        label_visibility="collapsed",
    )

    col_depth, col_sources, col_submit = st.columns([1.5, 1.5, 1], vertical_alignment="bottom")
    with col_depth:
        depth = choice("Depth", DEPTH_OPTIONS, "Balanced")
    with col_sources:
        max_sources = choice("Max sources", SOURCE_OPTIONS, 5)
    with col_submit:
        submitted = st.form_submit_button("Start research", use_container_width=True)

st.caption("Or start from an example")
example_cols = st.columns(len(EXAMPLES))
for i, (col, text) in enumerate(zip(example_cols, EXAMPLES)):
    with col:
        st.button(text, key=f"example_{i}", on_click=use_example, args=(text,), use_container_width=True)

# ─────────────────────────────────────────────────────────────
# Pipeline tracker + run
# ─────────────────────────────────────────────────────────────
tracker = st.empty()
existing = st.session_state.get("result")

if existing:
    tracker.markdown(
        pipeline_html("done", f"Finished in {fmt_duration(existing['elapsed'])}."),
        unsafe_allow_html=True,
    )
else:
    tracker.markdown(
        pipeline_html("idle", "Every topic passes through these four agents in order."),
        unsafe_allow_html=True,
    )

if submitted:
    topic = topic_input.strip()
    if not topic:
        st.warning("Enter a topic to start the research.")
    else:
        st.session_state.pop("result", None)
        tracker.markdown(
            pipeline_html("running", "Agents are working on your topic. Keep this tab open."),
            unsafe_allow_html=True,
        )
        started = time.time()
        try:
            output = call_pipeline(topic, depth, max_sources)
        except Exception as e:
            tracker.markdown(
                pipeline_html("error", "The pipeline stopped before finishing."),
                unsafe_allow_html=True,
            )
            st.error(
                f"The pipeline failed: `{e}`. Check that `GOOGLE_API_KEY` and "
                "`TAVILY_API_KEY` are set in your `.env` file, then run it again."
            )
            st.stop()

        elapsed = time.time() - started
        st.session_state["result"] = {
            "output": output,
            "report": extract_report(output),
            "elapsed": elapsed,
            "depth": depth,
            "max_sources": max_sources,
            "ts": int(time.time()),
        }
        tracker.markdown(
            pipeline_html("done", f"Finished in {fmt_duration(elapsed)}."),
            unsafe_allow_html=True,
        )

# ─────────────────────────────────────────────────────────────
# Results (kept in session state so downloads don't wipe the report)
# ─────────────────────────────────────────────────────────────
if st.session_state.get("result"):
    render_result(st.session_state["result"])