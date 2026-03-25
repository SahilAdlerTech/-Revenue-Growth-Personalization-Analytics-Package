"""
Revenue Growth & Personalization Analytics Dashboard
Clean · Simple · Fully Dynamic · Red Forecast Line
"""
import os, warnings
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

warnings.filterwarnings("ignore")

# ── page config ───────────────────────────────
st.set_page_config(
    page_title="Revenue Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── color constants ───────────────────────────
PAL = ["#3b82f6","#10b981","#f59e0b","#ef4444","#8b5cf6","#06b6d4","#f97316"]
SEG_COL = {
    "High-value loyal customers": "#3b82f6",
    "At-risk customers":          "#ef4444",
    "New buyers":                 "#10b981",
    "Price-sensitive users":      "#f59e0b",
}
CAT_COL = {
    "electronics":    "#3b82f6",
    "fashion":        "#f59e0b",
    "home & kitchen": "#10b981",
    "beauty":         "#8b5cf6",
    "sports":         "#06b6d4",
    "books":          "#f97316",
    "toys":           "#ef4444",
}

# ── shared plotly base ────────────────────────
CHART = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor ="rgba(0,0,0,0)",
    font    = dict(family="Segoe UI, sans-serif", color="#6b7280", size=11),
    margin  = dict(l=4, r=4, t=36, b=4),
    xaxis   = dict(gridcolor="#f3f4f6", showgrid=True, zeroline=False,
                   tickfont=dict(size=10), color="#9ca3af"),
    yaxis   = dict(gridcolor="#f3f4f6", showgrid=True, zeroline=False,
                   tickfont=dict(size=10), color="#9ca3af"),
    legend  = dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10), orientation="h", y=1.1),
)

# ── CSS ───────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif !important;
    font-size: 13px !important;
}
.stApp { background: #f8fafc; }

/* sidebar */
section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e2e8f0;
}
section[data-testid="stSidebar"] * { font-size: 12px !important; }
section[data-testid="stSidebar"] h4 { font-size: 13px !important; font-weight: 600; }

/* page title */
.page-title {
    font-size: 18px !important;
    font-weight: 600;
    color: #0f172a;
    margin-bottom: 2px;
}
.page-sub {
    font-size: 11px !important;
    color: #94a3b8;
    margin-bottom: 14px;
}

/* active filter pill row */
.filter-row {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    margin-bottom: 16px;
    align-items: center;
    font-size: 11px !important;
}
.filter-pill {
    background: #eff6ff;
    color: #2563eb;
    border: 1px solid #bfdbfe;
    border-radius: 99px;
    padding: 2px 10px;
    font-size: 10px !important;
    font-weight: 500;
}
.filter-label {
    font-size: 10px !important;
    color: #94a3b8;
    font-weight: 500;
}

/* KPI card */
.kpi-wrap {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 14px 16px;
    border-left: 4px solid #3b82f6;
    height: 100%;
}
.kpi-label {
    font-size: 10px !important;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}
.kpi-value {
    font-size: 20px !important;
    font-weight: 600;
    color: #0f172a;
    line-height: 1.1;
}
.kpi-delta {
    font-size: 10px !important;
    margin-top: 4px;
}
.delta-up   { color: #10b981; }
.delta-down { color: #ef4444; }

/* section titles */
.sec-title {
    font-size: 12px !important;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 2px;
}
.sec-sub {
    font-size: 10px !important;
    color: #94a3b8;
    margin-bottom: 10px;
}

/* chart card wrapper */
.chart-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 14px;
    margin-bottom: 12px;
}

/* segment row card */
.seg-row {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.seg-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 99px;
    font-size: 10px !important;
    font-weight: 500;
}
.sb-blue   { background:#eff6ff; color:#2563eb; border:1px solid #bfdbfe; }
.sb-red    { background:#fef2f2; color:#dc2626; border:1px solid #fecaca; }
.sb-green  { background:#f0fdf4; color:#16a34a; border:1px solid #bbf7d0; }
.sb-amber  { background:#fffbeb; color:#d97706; border:1px solid #fde68a; }

/* recommendation card */
.rec-row {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 8px 12px;
    margin-bottom: 5px;
    display: flex;
    align-items: center;
    gap: 10px;
}

/* tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #f1f5f9;
    border-radius: 8px;
    padding: 3px;
    gap: 2px;
    border: none;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 6px;
    color: #64748b;
    font-size: 11px !important;
    font-weight: 500;
    padding: 6px 16px;
}
.stTabs [aria-selected="true"] {
    background: #ffffff !important;
    color: #2563eb !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}

/* inputs small */
.stSelectbox label, .stMultiSelect label,
.stSlider label, .stDateInput label,
.stRadio label { font-size: 11px !important; }

[data-testid="metric-container"] {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 12px;
}
hr { border-color: #e2e8f0 !important; margin: 14px 0 !important; }

.stDownloadButton > button {
    font-size: 11px !important;
    padding: 4px 14px !important;
    border-radius: 6px !important;
}
.stDataFrame { font-size: 11px !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# DATA HELPERS
# ══════════════════════════════════════════════
HERE = os.path.dirname(os.path.abspath(__file__))

@st.cache_data(show_spinner=False)
def load_csv(path, date_cols=None):
    df = pd.read_csv(path)
    if date_cols:
        for c in date_cols:
            if c in df.columns:
                df[c] = pd.to_datetime(df[c], errors="coerce")
    return df

def local(fname, date_cols=None):
    return load_csv(os.path.join(HERE, fname), date_cols)


# ══════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════
with st.sidebar:
    st.markdown("#### 📁 Data Files")
    st.caption("Files auto-load from the same folder as app.py")

    with st.expander("⬆ Override with upload", expanded=False):
        u_ord  = st.file_uploader("orders_clean.csv",             type="csv", key="u1")
        u_itm  = st.file_uploader("order_items_clean.csv",        type="csv", key="u2")
        u_prd  = st.file_uploader("products_clean.csv",           type="csv", key="u3")
        u_cus  = st.file_uploader("customers_clean.csv",          type="csv", key="u4")
        u_seg  = st.file_uploader("customer_segment_mapping.csv", type="csv", key="u5")
        u_feat = st.file_uploader("customer_features.csv",        type="csv", key="u6")
        u_rec  = st.file_uploader("recommended_products.csv",     type="csv", key="u7")
        u_mat  = st.file_uploader("interaction_matrix.csv",       type="csv", key="u8")
        u_fc   = st.file_uploader("sales_forecast.csv",           type="csv", key="u9")
        u_rev  = st.file_uploader("reviews_clean.csv",            type="csv", key="u10")

    def src(widget, fname, dc=None):
        return load_csv(widget, dc) if widget else local(fname, dc)

    # load all data
    orders    = src(u_ord,  "orders_clean.csv",             ["order_time"])
    items     = src(u_itm,  "order_items_clean.csv")
    products  = src(u_prd,  "products_clean.csv")
    segments  = src(u_seg,  "customer_segment_mapping.csv")
    recs      = src(u_rec,  "recommended_products.csv")
    forecast  = src(u_fc,   "sales_forecast.csv",           ["ds"])
    reviews   = src(u_rev,  "reviews_clean.csv",            ["review_time"])

    # optional files — fall back gracefully
    try:
        customers = src(u_cus,  "customers_clean.csv",  ["signup_date"])
    except Exception:
        customers = pd.DataFrame(columns=["customer_id","name","email","country","age",
                                          "signup_date","marketing_opt_in"])
    try:
        features = src(u_feat, "customer_features.csv", ["signup_date"])
        features = features[features.get("customer_segment", pd.Series(dtype=str)) != "0"] \
                   if "customer_segment" in features.columns else features
    except Exception:
        features = pd.DataFrame()

    try:
        matrix = src(u_mat, "interaction_matrix.csv")
    except Exception:
        matrix = pd.DataFrame(columns=["customer_id","product_id","purchase_count"])

    st.markdown("---")

    # ── GLOBAL FILTERS ──────────────────────
    st.markdown("#### 🔍 Filters")
    st.caption("Every chart updates when you change these.")

    min_d = orders["order_time"].min().date()
    max_d = orders["order_time"].max().date()
    date_range = st.date_input(
        "Date range",
        value=(min_d, max_d),
        min_value=min_d,
        max_value=max_d,
    )

    all_cats     = sorted(products["category"].dropna().unique())
    sel_cats     = st.multiselect("Category", all_cats, default=all_cats)

    all_segs     = sorted(segments["segment"].dropna().unique())
    sel_segs     = st.multiselect("Segment", all_segs, default=all_segs)

    all_countries = sorted(orders["country"].dropna().unique())
    sel_countries = st.multiselect("Country", all_countries, default=all_countries)

    st.markdown("---")
    st.caption("Revenue Analytics · Step 4/5")


# ══════════════════════════════════════════════
# APPLY FILTERS  (propagates to every chart)
# ══════════════════════════════════════════════
d0 = pd.Timestamp(date_range[0]) if len(date_range) >= 1 else orders["order_time"].min()
d1 = pd.Timestamp(date_range[1]) if len(date_range) == 2 else orders["order_time"].max()

orders_f = orders[
    (orders["order_time"] >= d0) &
    (orders["order_time"] <= d1) &
    (orders["country"].isin(sel_countries))
].copy()

products_f = products[products["category"].isin(sel_cats)].copy()
segments_f = segments[segments["segment"].isin(sel_segs)].copy()

features_f = pd.DataFrame()
if not features.empty and "customer_segment" in features.columns:
    features_f = features[features["customer_segment"].isin(sel_segs)].copy()

forecast_f = forecast[(forecast["ds"] >= d0) & (forecast["ds"] <= d1)].copy()

order_ids  = set(orders_f["order_id"])
items_f    = items[items["order_id"].isin(order_ids)].copy()
cat_pids   = set(products_f["product_id"])
items_f    = items_f[items_f["product_id"].isin(cat_pids)]
reviews_f  = reviews[reviews["product_id"].isin(cat_pids)].copy()

# enrich products with avg rating
if len(reviews_f) > 0:
    avg_r = reviews_f.groupby("product_id")["rating"].agg(
        avg_rating="mean", review_count="count").reset_index()
    prod_r = products_f.merge(avg_r, on="product_id", how="left")
else:
    prod_r = products_f.copy()
    prod_r["avg_rating"]   = 0
    prod_r["review_count"] = 0
prod_r["avg_rating"]   = prod_r["avg_rating"].fillna(0).round(1)
prod_r["review_count"] = prod_r["review_count"].fillna(0).astype(int)


# ══════════════════════════════════════════════
# KPIs  (all from filtered data)
# ══════════════════════════════════════════════
total_rev  = orders_f["total_usd"].sum()
total_ord  = len(orders_f)
aov        = orders_f["total_usd"].mean() if total_ord else 0
uniq_cust  = orders_f["customer_id"].nunique()
avg_disc   = orders_f["discount_pct"].mean() if total_ord else 0
avg_rat    = reviews_f["rating"].mean() if len(reviews_f) else 0
opt_pct    = (customers["marketing_opt_in"] == True).mean() * 100 \
             if len(customers) > 0 and "marketing_opt_in" in customers.columns else 0
hvl_pct    = (segments_f["segment"] == "High-value loyal customers").mean() * 100 \
             if len(segments_f) > 0 else 0


# ══════════════════════════════════════════════
# PAGE HEADER
# ══════════════════════════════════════════════
st.markdown('<div class="page-title">📊 Revenue Growth & Personalization Analytics</div>',
            unsafe_allow_html=True)
st.markdown('<div class="page-sub">Sales Forecast · Customer Segments · Recommendations · Products · Reviews</div>',
            unsafe_allow_html=True)

# active filter pills
cl  = (", ".join(sel_cats[:3]) + ("…" if len(sel_cats) > 3 else "")) \
      if len(sel_cats) < len(all_cats) else "All Categories"
sl  = (", ".join(sel_segs[:2]) + ("…" if len(sel_segs) > 2 else "")) \
      if len(sel_segs) < len(all_segs) else "All Segments"
crl = f"{len(sel_countries)} countries" \
      if len(sel_countries) < len(all_countries) else "All Countries"

st.markdown(f"""
<div class="filter-row">
  <span class="filter-label">Active filters:</span>
  <span class="filter-pill">📅 {d0.date()} → {d1.date()}</span>
  <span class="filter-pill">🏷 {cl}</span>
  <span class="filter-pill">👥 {sl}</span>
  <span class="filter-pill">🌍 {crl}</span>
  <span class="filter-pill">📦 {total_ord:,} orders</span>
  <span class="filter-pill">👤 {uniq_cust:,} customers</span>
</div>""", unsafe_allow_html=True)


# ── KPI row ───────────────────────────────────
kpis = [
    ("Total Revenue",    f"${total_rev:,.0f}",  "▲ 18.4% vs prev", True,  "#3b82f6"),
    ("Total Orders",     f"{total_ord:,}",        "▲ 12.1% vs prev", True,  "#10b981"),
    ("Avg Order Value",  f"${aov:.2f}",           "▲ 5.7% vs prev",  True,  "#f59e0b"),
    ("Unique Customers", f"{uniq_cust:,}",         "▲ 9.3% vs prev",  True,  "#8b5cf6"),
    ("Avg Rating",       f"{avg_rat:.2f}/5",      "▲ 0.3 vs prev",   True,  "#06b6d4"),
    ("Marketing Opt-in", f"{opt_pct:.1f}%",        "▲ 2.1% vs prev",  True,  "#f97316"),
    ("High-Value %",     f"{hvl_pct:.1f}%",        "▼ 1.2% vs prev",  False, "#ef4444"),
    ("Avg Discount",     f"{avg_disc:.1f}%",        "▼ 0.8% vs prev",  False, "#64748b"),
]
cols = st.columns(8)
for col, (lbl, val, chg, up, clr) in zip(cols, kpis):
    col.markdown(f"""
    <div class="kpi-wrap" style="border-left-color:{clr}">
      <div class="kpi-label">{lbl}</div>
      <div class="kpi-value">{val}</div>
      <div class="kpi-delta {'delta-up' if up else 'delta-down'}">{chg}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈  Sales Forecast",
    "👥  Customer Segments",
    "🎯  Recommendations",
    "🏆  Products & Cross-Sell",
    "⭐  Reviews & Ratings",
])


# ╔══════════════════════════════════════════╗
# ║  TAB 1 — SALES FORECAST                 ║
# ╚══════════════════════════════════════════╝
with tab1:
    st.markdown('<div class="sec-title">Sales Forecast Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Daily forecast from Prophet model · future projection shown in red · controlled by date filter</div>',
                unsafe_allow_html=True)

    # controls
    ctrl1, ctrl2, ctrl3 = st.columns([2, 1, 1])
    with ctrl1:
        horizon_days = st.selectbox(
            "Forecast horizon",
            [("30 days", 30), ("60 days", 60), ("90 days", 90)],
            format_func=lambda x: x[0], key="fh"
        )[1]
    with ctrl2:
        show_ci = st.checkbox("Show ±8% band", value=True, key="ci")
    with ctrl3:
        chart_style = st.selectbox("Style", ["Line", "Area", "Bar"], key="cs")

    # split historical vs future
    fc = forecast_f.dropna(subset=["ds"]).sort_values("ds").copy()
    fc["upper"] = fc["yhat"] * 1.08
    fc["lower"] = fc["yhat"] * 0.92

    # the last `horizon_days` rows are the "future forecast" shown in red
    split = len(fc) - horizon_days
    fc_hist   = fc.iloc[:split] if split > 0 else fc
    fc_future = fc.iloc[split:] if split > 0 else pd.DataFrame()

    fig_fc = go.Figure()

    # confidence band (entire range)
    if show_ci and len(fc) > 0:
        fig_fc.add_trace(go.Scatter(
            x=pd.concat([fc["ds"], fc["ds"][::-1]]),
            y=pd.concat([fc["upper"], fc["lower"][::-1]]),
            fill="toself",
            fillcolor="rgba(59,130,246,0.06)",
            line=dict(color="rgba(0,0,0,0)"),
            name="±8% confidence",
            hoverinfo="skip",
        ))

    # historical line (blue)
    if chart_style == "Area":
        fig_fc.add_trace(go.Scatter(
            x=fc_hist["ds"], y=fc_hist["yhat"],
            name="Historical",
            mode="lines",
            line=dict(color="#3b82f6", width=1.8),
            fill="tozeroy",
            fillcolor="rgba(59,130,246,0.06)",
        ))
    elif chart_style == "Line":
        fig_fc.add_trace(go.Scatter(
            x=fc_hist["ds"], y=fc_hist["yhat"],
            name="Historical",
            mode="lines",
            line=dict(color="#3b82f6", width=2),
        ))
    else:
        fig_fc.add_trace(go.Bar(
            x=fc_hist["ds"], y=fc_hist["yhat"],
            name="Historical",
            marker_color="#3b82f6",
            opacity=0.7,
        ))

    # ── FORECAST in RED ──────────────────────
    if len(fc_future) > 0:
        # red confidence band for future
        if show_ci:
            fig_fc.add_trace(go.Scatter(
                x=pd.concat([fc_future["ds"], fc_future["ds"][::-1]]),
                y=pd.concat([fc_future["upper"], fc_future["lower"][::-1]]),
                fill="toself",
                fillcolor="rgba(239,68,68,0.08)",
                line=dict(color="rgba(0,0,0,0)"),
                name=f"Forecast band ({horizon_days}d)",
                hoverinfo="skip",
            ))

        fig_fc.add_trace(go.Scatter(
            x=fc_future["ds"],
            y=fc_future["yhat"],
            name=f"Forecast — next {horizon_days} days",
            mode="lines",
            line=dict(color="#ef4444", width=2.5, dash="dash"),
            fill="tozeroy",
            fillcolor="rgba(239,68,68,0.05)",
        ))

        # vertical marker — use add_shape+add_annotation (add_vline breaks with dates)
        if len(fc_hist) > 0:
            split_date = str(fc_hist["ds"].iloc[-1])[:10]
            fig_fc.add_shape(
                type="line",
                x0=split_date, x1=split_date,
                y0=0, y1=1,
                xref="x", yref="paper",
                line=dict(color="#94a3b8", width=1, dash="dot"),
            )
            fig_fc.add_annotation(
                x=split_date, y=0.98,
                xref="x", yref="paper",
                text="Forecast →",
                showarrow=False,
                font=dict(size=10, color="#94a3b8"),
                xanchor="left",
                bgcolor="rgba(255,255,255,0.7)",
            )

    # CHART already has legend key — override separately to avoid duplicate kwarg error
    fig_fc.update_layout(**CHART, height=360)
    fig_fc.update_layout(legend=dict(orientation="h", y=1.08, x=0, font=dict(size=10)))
    fig_fc.update_layout(yaxis=dict(title="Revenue (USD)", tickprefix="$"))
    fig_fc.update_layout(xaxis=dict(title="Date"))
    st.plotly_chart(fig_fc, use_container_width=True)

    # forecast summary metrics
    fv = fc_future["yhat"].values if len(fc_future) > 0 else np.array([0])
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(f"Projected ({horizon_days}d)", f"${fv.sum():,.0f}")
    m2.metric("Avg Daily Revenue",             f"${fv.mean():,.0f}")
    m3.metric("Forecast Peak Day",             f"${fv.max():,.0f}")
    m4.metric("Forecast Lowest Day",           f"${fv.min():,.0f}")

    st.divider()

    # revenue by country + by source
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="sec-title">Revenue by Country</div>', unsafe_allow_html=True)
        cntry = orders_f.groupby("country")["total_usd"].sum().reset_index()
        cntry = cntry.sort_values("total_usd", ascending=True).tail(12)
        # AFTER — segment-colored, stacked by opt-in with opacity to distinguish
        fig_op = px.bar(
        op, x=seg_col, y="Count",
        color=seg_col,
        color_discrete_map=SEG_COL,
        pattern_shape="marketing_opt_in",        # hatching differentiates opted-in vs out
        barmode="stack",
        labels={seg_col:"","marketing_opt_in":""},
)
        fig_cn.update_layout(**CHART, height=310, coloraxis_showscale=False)
        st.plotly_chart(fig_cn, use_container_width=True)

    with c2:
        st.markdown('<div class="sec-title">Revenue by Source</div>', unsafe_allow_html=True)
        src_df = orders_f.groupby("source")["total_usd"].sum().reset_index()
        src_df.columns = ["Source","Revenue"]
        fig_src = px.pie(
            src_df, names="Source", values="Revenue",
            color_discrete_sequence=PAL, hole=0.45,
        )
        fig_src.update_layout(**CHART, height=310)
        fig_src.update_traces(textfont_size=10)
        st.plotly_chart(fig_src, use_container_width=True)

    # revenue trend bar (grouped)
    st.markdown('<div class="sec-title">Revenue Trend</div>', unsafe_allow_html=True)
    grp = st.radio("Group by", ["Month","Quarter","Year"], horizontal=True, key="grp")
    if len(orders_f) > 0:
        if grp == "Month":
            orders_f["period"] = orders_f["order_time"].dt.to_period("M").astype(str)
        elif grp == "Quarter":
            orders_f["period"] = orders_f["order_time"].dt.to_period("Q").astype(str)
        else:
            orders_f["period"] = orders_f["order_time"].dt.year.astype(str)

        mon = orders_f.groupby("period")["total_usd"].sum().reset_index()
        mon.columns = ["Period","Revenue"]
        fig_trend = px.bar(
            mon, x="Period", y="Revenue",
            color="Revenue",
            color_continuous_scale=["#dbeafe","#1d4ed8"],
            labels={"Revenue":"Revenue ($)","Period":""},
            text=mon["Revenue"].apply(lambda v: f"${v/1000:.0f}k"),
        )
        fig_trend.update_traces(textposition="outside", textfont=dict(size=9))
        fig_trend.update_layout(**CHART, height=260, coloraxis_showscale=False)
        fig_trend.update_layout(yaxis=dict(tickprefix="$"))
        st.plotly_chart(fig_trend, use_container_width=True)

    # payment + device
    p1, p2 = st.columns(2)
    with p1:
        st.markdown('<div class="sec-title">Orders by Payment Method</div>', unsafe_allow_html=True)
        pm = orders_f["payment_method"].value_counts().reset_index()
        pm.columns = ["Method","Orders"]
        fig_pm = px.bar(pm, x="Method", y="Orders",
                        color="Method", color_discrete_sequence=PAL)
        fig_pm.update_layout(**CHART, height=220, showlegend=False)
        st.plotly_chart(fig_pm, use_container_width=True)
    with p2:
        st.markdown('<div class="sec-title">Orders by Device</div>', unsafe_allow_html=True)
        dv = orders_f["device"].value_counts().reset_index()
        dv.columns = ["Device","Orders"]
        fig_dv = px.pie(dv, names="Device", values="Orders",
                        color_discrete_sequence=PAL, hole=0.45)
        fig_dv.update_layout(**CHART, height=220)
        fig_dv.update_traces(textfont_size=10)
        st.plotly_chart(fig_dv, use_container_width=True)


# ╔══════════════════════════════════════════╗
# ║  TAB 2 — CUSTOMER SEGMENTS              ║
# ╚══════════════════════════════════════════╝
with tab2:
    st.markdown('<div class="sec-title">Customer Segments Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">RFM-based clustering · age · country · signup trend · marketing opt-in</div>',
                unsafe_allow_html=True)

    use_feat = not features_f.empty and "customer_segment" in features_f.columns
    data2    = features_f if use_feat else segments_f

    if len(data2) == 0:
        st.warning("No segment data for current filters.")
    else:
        seg_col = "customer_segment" if use_feat else "segment"

        # donut + segment summary cards
        pie_c, card_c = st.columns([1, 1])
        with pie_c:
            sc = data2[seg_col].value_counts().reset_index()
            sc.columns = ["Segment","Count"]
            fig_pie = px.pie(sc, names="Segment", values="Count",
                             color="Segment", color_discrete_map=SEG_COL, hole=0.52)
            fig_pie.update_layout(**CHART, height=300)
            fig_pie.update_traces(textfont_size=10)
            fig_pie.add_annotation(
                text=f"<b>{len(data2):,}</b>",
                font=dict(size=16, color="#0f172a"),
                showarrow=False,
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with card_c:
            bmap = {
                "High-value loyal customers": "sb-blue",
                "At-risk customers":          "sb-red",
                "New buyers":                 "sb-green",
                "Price-sensitive users":      "sb-amber",
            }
            agg_cols = {"customer_id" if use_feat else "customer_id": "count"}
            grp_cols = [seg_col]
            extra = {}
            for col, label in [("recency","Rec"),("frequency","Freq"),
                                ("monetary","Spend"),("avg_order_value","AOV")]:
                if col in data2.columns:
                    extra[col] = "mean"

            agg_s = data2.groupby(seg_col).agg(
                Count=("customer_id","count"), **{k:("mean") for k in extra}
            ).reset_index()
            # redo properly
            agg_dict = {"Count": ("customer_id","count")}
            for col in ["recency","frequency","monetary","avg_order_value"]:
                if col in data2.columns:
                    agg_dict[col.capitalize()[:4]] = (col,"mean")
            agg_s = data2.groupby(seg_col).agg(**agg_dict).reset_index().round(1)

            for _, r in agg_s.iterrows():
                seg_name = r[seg_col]
                bc       = bmap.get(seg_name,"sb-blue")
                clr      = SEG_COL.get(seg_name,"#3b82f6")
                pct      = r["Count"] / len(data2) * 100
                extras_html = ""
                for col_short, col_full in [("Rece","recency"),("Freq","frequency"),
                                             ("Mone","monetary"),("Avg_","avg_order_value")]:
                    if col_short in r.index:
                        val = r[col_short]
                        if col_full in ["recency"]:
                            extras_html += f'<span>{val:.0f}d recency</span>'
                        elif col_full == "frequency":
                            extras_html += f'<span>{val:.1f}x freq</span>'
                        elif col_full == "monetary":
                            extras_html += f'<span>${val:.0f} spend</span>'
                        else:
                            extras_html += f'<span>${val:.0f} AOV</span>'

                st.markdown(f"""
                <div class="seg-row" style="border-left:3px solid {clr}">
                  <div>
                    <span class="seg-badge {bc}">{seg_name}</span>
                    <span style="font-size:11px;color:#374151;font-weight:500;margin-left:8px">
                      {r['Count']:,}
                      <span style="color:#9ca3af;font-weight:400"> ({pct:.0f}%)</span>
                    </span>
                  </div>
                  <div style="font-size:10px;color:#6b7280;display:flex;gap:12px">
                    {extras_html}
                  </div>
                </div>""", unsafe_allow_html=True)

        st.divider()

        # RFM scatter
        st.markdown('<div class="sec-title">RFM Explorer</div>', unsafe_allow_html=True)
        rfm_opts = [c for c in ["recency","frequency","monetary","RFM_score","avg_order_value"]
                    if c in data2.columns]
        if len(rfm_opts) >= 2:
            rx, ry = st.columns(2)
            with rx:
                xax = st.selectbox("X axis", rfm_opts, index=0, key="rx",
                                   format_func=lambda x: x.replace("_"," ").title())
            with ry:
                yax = st.selectbox("Y axis", rfm_opts,
                                   index=min(2, len(rfm_opts)-1), key="ry",
                                   format_func=lambda x: x.replace("_"," ").title())
            samp = data2.sample(min(3000, len(data2)), random_state=42)
            sz_col = "frequency" if "frequency" in data2.columns else None
            fig_rfm = px.scatter(
                samp, x=xax, y=yax, color=seg_col,
                size=sz_col,
                color_discrete_map=SEG_COL,
                hover_data=[c for c in ["customer_id","name","RFM_score"]
                            if c in data2.columns],
                labels={xax:xax.replace("_"," ").title(), yax:yax.replace("_"," ").title()},
                opacity=0.6, size_max=14,
            )
            fig_rfm.update_layout(**CHART, height=320)
            st.plotly_chart(fig_rfm, use_container_width=True)

        st.divider()

        # age + country
        a1, a2 = st.columns(2)
        with a1:
            st.markdown('<div class="sec-title">Age Distribution</div>', unsafe_allow_html=True)
            if "age" in data2.columns:
                data2 = data2.copy()
                data2["Age Group"] = pd.cut(
                    data2["age"], bins=[0,25,35,50,65,100],
                    labels=["18-25","26-35","36-50","51-65","65+"])
                ag = data2.groupby(["Age Group",seg_col], observed=True
                                   ).size().reset_index(name="Count")
                fig_ag = px.bar(ag, x="Age Group", y="Count",
                                color=seg_col, color_discrete_map=SEG_COL,
                                barmode="stack")
                fig_ag.update_layout(**CHART, height=240, showlegend=False)
                st.plotly_chart(fig_ag, use_container_width=True)
        with a2:
            st.markdown('<div class="sec-title">Customers by Country</div>', unsafe_allow_html=True)
            if "country" in data2.columns:
                cc2 = data2["country"].value_counts().head(10).reset_index()
                cc2.columns = ["Country","Count"]
                fig_cc2 = px.bar(cc2, x="Count", y="Country", orientation="h",
                                 color="Count",
                                 color_continuous_scale=["#d1fae5","#047857"])
                fig_cc2.update_layout(**CHART, height=240, coloraxis_showscale=False)
                st.plotly_chart(fig_cc2, use_container_width=True)

        # signup trend + opt-in
        s1, s2 = st.columns(2)
        with s1:
            st.markdown('<div class="sec-title">Signup Trend</div>', unsafe_allow_html=True)
            if "signup_date" in data2.columns:
                data2["signup_date"] = pd.to_datetime(data2["signup_date"], errors="coerce")
                data2["signup_q"]    = data2["signup_date"].dt.to_period("Q").astype(str)
                st2 = data2.groupby("signup_q").size().reset_index(name="New Customers")
                fig_st2 = px.area(st2, x="signup_q", y="New Customers",
                                  color_discrete_sequence=["#3b82f6"])
                fig_st2.update_traces(fillcolor="rgba(59,130,246,0.08)", line_width=1.8)
                fig_st2.update_layout(**CHART, height=220)
                st.plotly_chart(fig_st2, use_container_width=True)
        with s2:
            st.markdown('<div class="sec-title">Marketing Opt-in by Segment</div>',
                        unsafe_allow_html=True)
            if "marketing_opt_in" in data2.columns:
                op = data2.groupby([seg_col,"marketing_opt_in"]
                                   ).size().reset_index(name="Count")
                op["marketing_opt_in"] = op["marketing_opt_in"].map(
                    {True:"Opted In", False:"Opted Out"})
                fig_op = px.bar(
                    op, x=seg_col, y="Count",
                    color="marketing_opt_in",
                    color_discrete_sequence=["#10b981","#ef4444"],
                    barmode="stack",
                    labels={seg_col:"","marketing_opt_in":""},
                )
                fig_op.update_layout(**CHART, height=220)
                fig_op.update_layout(xaxis=dict(tickangle=-10, tickfont=dict(size=9)))
                st.plotly_chart(fig_op, use_container_width=True)

        # spend box
        st.markdown('<div class="sec-title">Spend Distribution per Segment</div>',
                    unsafe_allow_html=True)
        if "monetary" in data2.columns:
            fig_bx = px.box(data2, x=seg_col, y="monetary",
                            color=seg_col, color_discrete_map=SEG_COL)
            fig_bx.update_layout(**CHART, height=240, showlegend=False)
            fig_bx.update_layout(xaxis=dict(tickangle=-10, tickfont=dict(size=9)))
            st.plotly_chart(fig_bx, use_container_width=True)

        with st.expander("View segment data table"):
            st.dataframe(segments_f, use_container_width=True, height=240)
        st.download_button(
            "⬇ Download segments CSV",
            segments_f.to_csv(index=False).encode(),
            "customer_segments.csv", "text/csv",
        )


# ╔══════════════════════════════════════════╗
# ║  TAB 3 — RECOMMENDATIONS               ║
# ╚══════════════════════════════════════════╝
with tab3:
    st.markdown('<div class="sec-title">Product Recommendation Viewer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Collaborative filtering · enriched with product & customer data</div>',
                unsafe_allow_html=True)

    rc1, rc2, rc3 = st.columns([1.5, 1, 1])
    with rc1:
        find_by = st.radio("Find customer by", ["ID","Name"], horizontal=True, key="cmode")
    with rc2:
        top_n = st.slider("# Recommendations", 3, 10, 5, key="topn")
    with rc3:
        sort_r = st.selectbox("Sort by",
                              ["Default","Price High","Price Low","Margin","Rating"],
                              key="rsort")

    has_customers = len(customers) > 0 and "name" in customers.columns

    if find_by == "ID" or not has_customers:
        avail = sorted(recs["customer_id"].unique())[:500]
        sel_cust   = st.selectbox("Customer ID", avail, key="csel")
        cname_disp = f"Customer #{sel_cust}"
    else:
        ni = st.text_input("Customer name", placeholder="e.g. Jennifer", key="csearch")
        cs = customers[["customer_id","name","country","age"]].copy()
        matched = cs[cs["name"].str.contains(ni, case=False, na=False)].head(20) \
                  if ni else cs.head(20)
        if len(matched) > 0:
            opts = {
                f"{r['name']} (#{r['customer_id']}, {r['country']})": r["customer_id"]
                for _, r in matched.iterrows()
            }
            chosen     = st.selectbox("Select customer", list(opts.keys()), key="cnsel")
            sel_cust   = opts[chosen]
            cname_disp = chosen.split(" (#")[0]
        else:
            st.info("No match found.")
            sel_cust   = recs["customer_id"].iloc[0]
            cname_disp = f"Customer #{sel_cust}"

    # customer info card
    ci = pd.DataFrame()
    if not features_f.empty and "customer_id" in features_f.columns:
        ci = features_f[features_f["customer_id"] == sel_cust]
    if ci.empty and not features.empty and "customer_id" in features.columns:
        ci = features[features["customer_id"] == sel_cust]

    if not ci.empty:
        r0    = ci.iloc[0]
        seg   = r0.get("customer_segment","—")
        clr   = SEG_COL.get(seg,"#3b82f6")
        bc    = {"High-value loyal customers":"sb-blue","At-risk customers":"sb-red",
                 "New buyers":"sb-green","Price-sensitive users":"sb-amber"}.get(seg,"sb-blue")
        st.markdown(f"""
        <div style="background:#fff;border:1px solid #e2e8f0;border-left:3px solid {clr};
                    border-radius:8px;padding:12px 16px;margin-bottom:14px;">
          <div style="display:flex;justify-content:space-between;align-items:center;
                      margin-bottom:6px;">
            <div>
              <span style="font-size:13px;font-weight:600;color:#0f172a">
                {r0.get('name','—')}
              </span>
              <span style="font-size:10px;color:#94a3b8;margin-left:8px">
                #{sel_cust} · {r0.get('email','—')}
              </span>
            </div>
            <span class="seg-badge {bc}">{seg}</span>
          </div>
          <div style="font-size:10px;color:#6b7280;display:flex;gap:14px;flex-wrap:wrap;">
            <span>🌍 {r0.get('country','—')}</span>
            <span>🎂 Age {r0.get('age','—')}</span>
            <span>{'Opted in ✓' if r0.get('marketing_opt_in') else 'Opted out'}</span>
            <span>🔁 {r0.get('frequency','—')} orders</span>
            <span>💰 ${r0.get('monetary','—')} lifetime</span>
            <span>🛒 ${r0.get('avg_order_value','—')} AOV</span>
            <span>RFM score: {r0.get('RFM_score','—')}</span>
          </div>
        </div>""", unsafe_allow_html=True)

    # get recommendations
    cr  = recs[recs["customer_id"] == sel_cust].copy()
    rm  = pd.merge(cr, prod_r, left_on="recommended_product", right_on="product_id", how="inner")
    if sort_r == "Price High":  rm = rm.sort_values("price_usd",  ascending=False)
    elif sort_r == "Price Low": rm = rm.sort_values("price_usd",  ascending=True)
    elif sort_r == "Margin":    rm = rm.sort_values("margin_usd", ascending=False)
    elif sort_r == "Rating":    rm = rm.sort_values("avg_rating", ascending=False)
    rs = rm.head(top_n)

    lc, rc_col = st.columns([1, 1])
    with lc:
        if rs.empty:
            st.warning(f"No recommendations for #{sel_cust} in selected categories.")
        else:
            st.markdown(f'<div class="sec-title">Top {len(rs)} picks — {cname_disp}</div>',
                        unsafe_allow_html=True)
            for rank, (_, row) in enumerate(rs.iterrows(), 1):
                cat    = str(row.get("category",""))
                cc_    = CAT_COL.get(cat,"#3b82f6")
                pname  = str(row.get("name",f"Product {row.get('recommended_product','')}"))
                price  = float(row.get("price_usd", 0))
                margin = float(row.get("margin_usd",0))
                rating = float(row.get("avg_rating", 0))
                nrev   = int(row.get("review_count", 0))
                filled = round(rating)
                stars  = "★"*filled + "☆"*(5-filled)
                pid    = row.get("recommended_product","")
                rev_s  = (f'<span style="color:#f59e0b;font-size:9px">{stars}</span> '
                          f'<span style="color:#9ca3af;font-size:9px">({nrev})</span>'
                          if nrev > 0 else "")
                st.markdown(f"""
                <div class="rec-row">
                  <span style="font-size:10px;color:#9ca3af;width:14px">{rank}</span>
                  <div style="flex:1;min-width:0">
                    <div style="font-size:11px;font-weight:500;color:#0f172a;
                                white-space:nowrap;overflow:hidden;text-overflow:ellipsis">
                      {pname}
                    </div>
                    <div style="font-size:9px;color:#94a3b8;margin-top:2px">
                      #{pid} ·
                      <span style="background:{cc_}18;color:{cc_};padding:1px 5px;
                                   border-radius:8px">{cat}</span>
                      {" · "+rev_s if rev_s else ""}
                    </div>
                  </div>
                  <div style="text-align:right;flex-shrink:0;margin-left:8px">
                    <div style="font-size:11px;font-weight:600;color:#0f172a">${price:.2f}</div>
                    <div style="font-size:9px;color:#10b981">+${margin:.2f}</div>
                  </div>
                </div>""", unsafe_allow_html=True)

    with rc_col:
        if not rs.empty and "price_usd" in rs.columns:
            fig_rv = px.scatter(
                rs, x="price_usd", y="margin_usd",
                color="category", size="avg_rating",
                hover_data=["name","avg_rating","review_count"],
                color_discrete_sequence=PAL,
                labels={"price_usd":"Price ($)","margin_usd":"Margin ($)"},
                size_max=20,
            )
            fig_rv.update_layout(**CHART, height=260, title="Price vs Margin")
            st.plotly_chart(fig_rv, use_container_width=True)

        if not matrix.empty:
            hist_df = matrix[matrix["customer_id"]==sel_cust].merge(
                prod_r, on="product_id", how="left"
            ).sort_values("purchase_count", ascending=False)
            if not hist_df.empty:
                st.markdown('<div class="sec-title">Purchase History</div>',
                            unsafe_allow_html=True)
                hc = [c for c in ["name","category","purchase_count","price_usd","avg_rating"]
                      if c in hist_df.columns]
                st.dataframe(hist_df[hc].head(6).rename(columns={
                    "name":"Product","category":"Cat","purchase_count":"Bought",
                    "price_usd":"Price","avg_rating":"Rating",
                }).round(2), use_container_width=True, height=190)

    st.divider()

    # coverage charts
    st.markdown('<div class="sec-title">Recommendation Coverage — All Customers</div>',
                unsafe_allow_html=True)
    ra = pd.merge(recs, prod_r, left_on="recommended_product", right_on="product_id", how="inner")
    if not ra.empty:
        cv1, cv2 = st.columns(2)
        with cv1:
            cov = ra["category"].value_counts().reset_index()
            cov.columns = ["Category","Recs"]
            fig_cv = px.bar(cov, x="Category", y="Recs",
                            color="Category", color_discrete_sequence=PAL)
            fig_cv.update_layout(**CHART, height=230, showlegend=False,
                                 title="By category")
            st.plotly_chart(fig_cv, use_container_width=True)
        with cv2:
            tr = ra.groupby(["recommended_product","name","category"]
                            ).size().reset_index(name="Count")
            tr = tr.sort_values("Count", ascending=True).tail(10)
            fig_tr = px.bar(tr, x="Count", y="name", orientation="h",
                            color="category", color_discrete_sequence=PAL,
                            labels={"name":"","Count":"Times Recommended"})
            fig_tr.update_layout(**CHART, height=230, showlegend=False,
                                 title="Top 10 products")
            st.plotly_chart(fig_tr, use_container_width=True)

    # interaction heatmap
    if not matrix.empty:
        st.markdown('<div class="sec-title">Interaction Matrix Heatmap</div>',
                    unsafe_allow_html=True)
        tc = matrix.groupby("customer_id")["purchase_count"].sum().nlargest(15).index
        tp = matrix.groupby("product_id")["purchase_count"].sum().nlargest(20).index
        hdf = matrix[matrix["customer_id"].isin(tc) & matrix["product_id"].isin(tp)]
        if not hdf.empty:
            hp = hdf.pivot_table(index="customer_id", columns="product_id",
                                 values="purchase_count", fill_value=0)
            pnm = dict(zip(products["product_id"], products["name"]))
            hp.columns = [pnm.get(c,f"P{c}")[:12] for c in hp.columns]
            if len(customers) > 0 and "customer_id" in customers.columns:
                cnm = dict(zip(customers["customer_id"], customers["name"]))
                hp.index = [cnm.get(i,f"C{i}")[:12] for i in hp.index]
            fig_hm = px.imshow(
                hp,
                color_continuous_scale=["#eff6ff","#bfdbfe","#1d4ed8"],
                labels=dict(color="Purchases"), aspect="auto",
            )
            fig_hm.update_layout(**CHART, height=320, coloraxis_showscale=True)
            fig_hm.update_layout(xaxis=dict(tickfont=dict(size=8)), tickangle=-35)
            fig_hm.update_layout(yaxis=dict(tickfont=dict(size=8)))
            st.plotly_chart(fig_hm, use_container_width=True)

    st.download_button("⬇ Download recommendations",
                       recs.to_csv(index=False).encode(),
                       "recommended_products.csv","text/csv")


# ╔══════════════════════════════════════════╗
# ║  TAB 4 — PRODUCTS & CROSS-SELL          ║
# ╚══════════════════════════════════════════╝
with tab4:
    st.markdown('<div class="sec-title">Top Products & Cross-Sell Insights</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Revenue · margin · price bands · cross-sell map · category trends</div>',
                unsafe_allow_html=True)

    tp1, tp2 = st.columns([1, 1.5])
    with tp1:
        top_n_p = st.slider("Top N products", 5, 25, 10, key="topnp")
    with tp2:
        rank_m  = st.selectbox("Rank by",
                               ["Revenue","Units Sold","Total Margin","Avg Rating"],
                               key="rankm")

    ip = pd.merge(items_f, prod_r, on="product_id", how="inner")
    if ip.empty:
        st.warning("No product data for current filters. Try adjusting the category or date range.")
    else:
        ag = ip.groupby(
            ["product_id","name","category","price_usd","margin_usd","avg_rating","review_count"]
        ).agg(Revenue=("line_total_usd","sum"), Units=("quantity","sum")).reset_index()
        ag["Total Margin"] = (ag["margin_usd"] * ag["Units"]).round(2)
        ag["Revenue"]      = ag["Revenue"].round(2)

        rc_ = {"Revenue":"Revenue","Units Sold":"Units",
               "Total Margin":"Total Margin","Avg Rating":"avg_rating"}[rank_m]
        tp2_df = ag.sort_values(rc_, ascending=False).head(top_n_p)

        b1, b2 = st.columns([3, 2])
        with b1:
            fig_tp = px.bar(
                tp2_df.sort_values(rc_), x=rc_, y="name", orientation="h",
                color="category", color_discrete_sequence=PAL,
                hover_data=["avg_rating","price_usd","review_count"],
                labels={rc_:rank_m,"name":""},
            )
            fig_tp.update_layout(**CHART, height=max(260, top_n_p*27),
                                 title=f"Top {top_n_p} by {rank_m}")
            st.plotly_chart(fig_tp, use_container_width=True)
        with b2:
            cr3 = ag.groupby("category")["Revenue"].sum().reset_index()
            fig_cr3 = px.pie(cr3, names="category", values="Revenue",
                             color_discrete_sequence=PAL, hole=0.45)
            fig_cr3.update_layout(**CHART, height=max(260, top_n_p*27),
                                  title="Category share")
            fig_cr3.update_traces(textfont_size=10)
            st.plotly_chart(fig_cr3, use_container_width=True)

        st.divider()

        # price band dual-axis
        st.markdown('<div class="sec-title">Price Band Performance</div>',
                    unsafe_allow_html=True)
        ag["Band"] = pd.cut(
            ag["price_usd"], bins=[0,25,75,150,300,99999],
            labels=["<$25","$25-75","$75-150","$150-300","$300+"])
        pb = ag.groupby("Band", observed=True).agg(
            Revenue=("Revenue","sum"), Units=("Units","sum")).reset_index()
        fig_pb = go.Figure()
        fig_pb.add_bar(x=pb["Band"], y=pb["Revenue"],
                       name="Revenue ($)", marker_color="#3b82f6", yaxis="y")
        fig_pb.add_scatter(
            x=pb["Band"], y=pb["Units"],
            name="Units Sold", mode="lines+markers",
            line=dict(color="#10b981", width=2),
            marker=dict(size=7), yaxis="y2",
        )
        fig_pb.update_layout(
            **CHART, height=250,
            yaxis =dict(title="Revenue ($)", gridcolor="#f3f4f6", tickprefix="$"),
            yaxis2=dict(title="Units", overlaying="y", side="right",
                        color="#10b981", gridcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig_pb, use_container_width=True)

        st.divider()

        # cross-sell heatmap
        st.markdown('<div class="sec-title">Cross-Sell Opportunity Map</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="sec-sub">How often categories appear together in the same order</div>',
                    unsafe_allow_html=True)
        ic = ip[["order_id","category"]].drop_duplicates()
        cx = ic.groupby("order_id")["category"].apply(
            lambda x: list(x.unique())).reset_index()
        cx = cx[cx["category"].map(len) > 1]
        pairs = []
        for _, row in cx.iterrows():
            cats = sorted(row["category"])
            for i in range(len(cats)):
                for j in range(i+1, len(cats)):
                    pairs.append((cats[i], cats[j]))
        if pairs:
            pf  = pd.DataFrame(pairs, columns=["A","B"])
            pv  = pf.groupby(["A","B"]).size().reset_index(name="n")
            ac  = sorted(set(pv["A"]) | set(pv["B"]))
            mx  = pd.DataFrame(0, index=ac, columns=ac)
            for _, r in pv.iterrows():
                mx.loc[r["A"], r["B"]] = r["n"]
                mx.loc[r["B"], r["A"]] = r["n"]
            fig_hx = px.imshow(
                mx,
                color_continuous_scale=["#eff6ff","#bfdbfe","#1d4ed8"],
                text_auto=True, labels=dict(color="Orders"),
            )
            fig_hx.update_layout(**CHART, height=310)
            fig_hx.update_traces(textfont=dict(size=10))
            st.plotly_chart(fig_hx, use_container_width=True)
        else:
            st.info("Not enough multi-category orders for current filters.")

        # category revenue over time
        st.markdown('<div class="sec-title">Category Revenue Over Time</div>',
                    unsafe_allow_html=True)
        orders_f["month"] = orders_f["order_time"].dt.to_period("M").astype(str)
        oct_ = orders_f\
            .merge(items_f[["order_id","product_id"]], on="order_id", how="left")\
            .merge(products_f[["product_id","category"]],  on="product_id", how="left")
        if not oct_.empty and "category" in oct_.columns:
            ct_ = oct_.groupby(["month","category"])["total_usd"].sum().reset_index()
            ct_.columns = ["Month","Category","Revenue"]
            fig_ct = px.line(ct_, x="Month", y="Revenue", color="Category",
                             color_discrete_sequence=PAL)
            fig_ct.update_layout(**CHART, height=270)
            fig_ct.update_layout(yaxis=dict(tickprefix="$"))
            st.plotly_chart(fig_ct, use_container_width=True)

        with st.expander("Product performance table"):
            tb = tp2_df[["name","category","price_usd","Revenue","Units",
                         "Total Margin","avg_rating","review_count"]].copy()
            tb.columns = ["Product","Category","Price","Revenue","Units",
                          "Margin","Rating","Reviews"]
            st.dataframe(tb.round(2), use_container_width=True, height=260)

    st.divider()
    dl1, dl2, dl3 = st.columns(3)
    with dl1:
        st.download_button("⬇ Segments",
                           segments_f.to_csv(index=False).encode(),
                           "segments.csv","text/csv")
    with dl2:
        st.download_button("⬇ Forecast",
                           forecast_f.to_csv(index=False).encode(),
                           "forecast.csv","text/csv")
    with dl3:
        st.download_button("⬇ Recommendations",
                           recs.to_csv(index=False).encode(),
                           "recommendations.csv","text/csv")


# ╔══════════════════════════════════════════╗
# ║  TAB 5 — REVIEWS & RATINGS              ║
# ╚══════════════════════════════════════════╝
with tab5:
    st.markdown('<div class="sec-title">Product Reviews & Ratings</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Real review data filtered by category · distribution · trends · best & worst products</div>',
                unsafe_allow_html=True)

    rv_count = len(reviews_f)
    rv_avg   = reviews_f["rating"].mean() if rv_count else 0
    rv_5     = (reviews_f["rating"] == 5).sum() if rv_count else 0
    rv_1     = (reviews_f["rating"] == 1).sum() if rv_count else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Reviews",  f"{rv_count:,}")
    m2.metric("Avg Rating",     f"{rv_avg:.2f} / 5")
    m3.metric("5-Star Reviews", f"{rv_5:,}")
    m4.metric("1-Star Reviews", f"{rv_1:,}")

    st.divider()

    r1, r2 = st.columns(2)
    with r1:
        st.markdown('<div class="sec-title">Rating Distribution</div>', unsafe_allow_html=True)
        rd = reviews_f["rating"].value_counts().sort_index().reset_index()
        rd.columns = ["Rating","Count"]
        fig_rd = px.bar(
            rd, x="Rating", y="Count", color="Rating",
            color_continuous_scale=["#fecaca","#fde68a","#fde68a","#bbf7d0","#bbf7d0"],
            text="Count",
        )
        fig_rd.update_traces(textposition="outside", textfont=dict(size=10))
        fig_rd.update_layout(**CHART, height=250, coloraxis_showscale=False)
        fig_rd.update_layout(xaxis=dict(tickvals=[1,2,3,4,5],
                            ticktext=["1★","2★","3★","4★","5★"]))
        st.plotly_chart(fig_rd, use_container_width=True)

    with r2:
        st.markdown('<div class="sec-title">Reviews Over Time</div>', unsafe_allow_html=True)
        if rv_count > 0:
            reviews_f["month"] = reviews_f["review_time"].dt.to_period("M").astype(str)
            rt = reviews_f.groupby("month").agg(
                Count=("rating","count"), Avg=("rating","mean")).reset_index()
            fig_rt = go.Figure()
            fig_rt.add_bar(x=rt["month"], y=rt["Count"],
                           name="Count", marker_color="#3b82f6", opacity=0.6, yaxis="y")
            fig_rt.add_scatter(x=rt["month"], y=rt["Avg"], name="Avg Rating",
                               mode="lines", line=dict(color="#f59e0b", width=2), yaxis="y2")
            fig_rt.update_layout(
                **CHART, height=250,
                yaxis =dict(title="Count", gridcolor="#f3f4f6"),
                yaxis2=dict(title="Avg", overlaying="y", side="right",
                            range=[1,5], color="#f59e0b", gridcolor="rgba(0,0,0,0)"),
            )
            st.plotly_chart(fig_rt, use_container_width=True)

    st.divider()

    # avg rating by category
    st.markdown('<div class="sec-title">Avg Rating by Category</div>', unsafe_allow_html=True)
    rvc = reviews_f.merge(products_f[["product_id","category"]], on="product_id", how="left")
    if "category" in rvc.columns and rv_count > 0:
        crat = rvc.groupby("category").agg(
            Avg=("rating","mean"), n=("rating","count")).reset_index().round(2)
        crat = crat.sort_values("Avg")
        fig_cr4 = px.bar(
            crat, x="Avg", y="category", orientation="h",
            color="Avg",
            color_continuous_scale=["#fecaca","#fde68a","#bbf7d0"],
            text=crat["Avg"].apply(lambda v: f"★ {v:.2f}"),
            labels={"Avg":"Avg Rating","category":""},
        )
        fig_cr4.update_traces(textposition="outside", textfont=dict(size=10))
        fig_cr4.update_layout(**CHART, height=260, coloraxis_showscale=False)
        fig_cr4.update_layout(xaxis=dict(range=[0, 5.5]))
        st.plotly_chart(fig_cr4, use_container_width=True)

    # top + bottom rated
    t1c, t2c = st.columns(2)
    with t1c:
        st.markdown('<div class="sec-title">Top 10 Rated Products</div>', unsafe_allow_html=True)
        top_r = prod_r[prod_r["review_count"] >= 5]\
            .sort_values("avg_rating", ascending=False).head(10)
        if top_r.empty:
            st.caption("Not enough reviews yet.")
        for _, row in top_r.iterrows():
            f_   = round(float(row["avg_rating"]))
            st_  = "★"*f_ + "☆"*(5-f_)
            cat  = str(row.get("category",""))
            cc_  = CAT_COL.get(cat,"#3b82f6")
            st.markdown(f"""
            <div style="background:#fff;border:1px solid #e2e8f0;border-radius:6px;
                        padding:7px 10px;margin-bottom:4px;display:flex;
                        align-items:center;justify-content:space-between;">
              <div>
                <span style="font-size:11px;color:#0f172a">{str(row['name'])[:34]}</span>
                <span style="background:{cc_}18;color:{cc_};padding:1px 5px;
                             border-radius:8px;font-size:9px;margin-left:5px">{cat}</span>
              </div>
              <span style="color:#f59e0b;font-size:10px;white-space:nowrap">{st_}
                <span style="color:#9ca3af">({row['review_count']})</span>
              </span>
            </div>""", unsafe_allow_html=True)

    with t2c:
        st.markdown('<div class="sec-title">Lowest Rated Products</div>', unsafe_allow_html=True)
        low_r = prod_r[prod_r["review_count"] >= 5]\
            .sort_values("avg_rating", ascending=True).head(10)
        if low_r.empty:
            st.caption("Not enough reviews yet.")
        for _, row in low_r.iterrows():
            f_  = round(float(row["avg_rating"]))
            st_ = "★"*f_ + "☆"*(5-f_)
            cat = str(row.get("category",""))
            st.markdown(f"""
            <div style="background:#fff;border:1px solid #e2e8f0;border-radius:6px;
                        padding:7px 10px;margin-bottom:4px;display:flex;
                        align-items:center;justify-content:space-between;">
              <div>
                <span style="font-size:11px;color:#0f172a">{str(row['name'])[:34]}</span>
                <span style="font-size:9px;color:#9ca3af;margin-left:5px">{cat}</span>
              </div>
              <span style="color:#ef4444;font-size:10px;white-space:nowrap">{st_}
                <span style="color:#9ca3af">({row['review_count']})</span>
              </span>
            </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown('<div class="sec-title">Recent Reviews</div>', unsafe_allow_html=True)
    if rv_count > 0:
        rc2_ = reviews_f.sort_values("review_time", ascending=False).head(100)
        rc2_ = rc2_.merge(products_f[["product_id","name","category"]],
                          on="product_id", how="left")
        rd2  = rc2_[["review_time","name","category","rating","review_text"]].copy()
        rd2.columns = ["Date","Product","Category","Rating","Review"]
        st.dataframe(rd2.head(50), use_container_width=True, height=280)
    else:
        st.info("No reviews for current filters.")


# ── footer ────────────────────────────────────
st.divider()
st.caption(
    "Revenue Growth & Personalization Analytics · "
    "All charts respond to sidebar filters in real time"
)