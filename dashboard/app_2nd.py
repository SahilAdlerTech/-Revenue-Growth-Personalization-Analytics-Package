import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(page_title="app_2nd", layout="wide")

st.title("Revenue Growth & Personalization Analytics Dashboard")

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_data():

    orders          = pd.read_csv("orders_clean.csv")
    order_items     = pd.read_csv("order_items_clean.csv")
    products        = pd.read_csv("products_clean.csv")
    customer_feat   = pd.read_csv("customer_features.csv")   # no 'Regular customers' / '0'
    recommendations = pd.read_csv("recommended_products.csv")
    forecast        = pd.read_csv("sales_forecast.csv")

    orders["order_time"] = pd.to_datetime(orders["order_time"])
    forecast["ds"]       = pd.to_datetime(forecast["ds"])

    # Standardise product name column
    if "product_name" not in products.columns:
        products.rename(columns={"name": "product_name"}, inplace=True)

    # Clean segment lookup — 4 segments, one row per customer
    seg_lookup = (
        customer_feat[["customer_id", "customer_segment"]]
        .rename(columns={"customer_segment": "segment"})
        .drop_duplicates("customer_id")
    )

    return orders, order_items, products, seg_lookup, recommendations, forecast


orders, order_items, products, seg_lookup, recommendations, forecast = load_data()

# --------------------------------------------------
# BUILD SALES TABLE
# --------------------------------------------------

sales = pd.merge(order_items, orders, on="order_id", how="left")
sales = pd.merge(sales, products, on="product_id", how="left")

# Distribute post-discount order total proportionally across line items
# so line-item revenue always sums to the correct order total_usd
sales["line_subtotal"] = sales["quantity"] * sales["unit_price_usd"]
order_subtotals        = sales.groupby("order_id")["line_subtotal"].transform("sum")
sales["revenue"]       = sales["line_subtotal"] * (sales["total_usd"] / order_subtotals)

# --------------------------------------------------
# DEFAULT FILTER VALUES
# --------------------------------------------------

default_start = sales["order_time"].min()
default_end   = sales["order_time"].max()

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("Filters")

if "date_from" not in st.session_state:
    st.session_state.date_from = default_start
if "date_to" not in st.session_state:
    st.session_state.date_to = default_end
if "country" not in st.session_state:
    st.session_state.country = "All"
if "category" not in st.session_state:
    st.session_state.category = "All"
if "segment" not in st.session_state:
    st.session_state.segment = "All"

if st.sidebar.button("Clear Filters"):
    st.session_state.date_from = default_start
    st.session_state.date_to   = default_end
    st.session_state.country   = "All"
    st.session_state.category  = "All"
    st.session_state.segment   = "All"
    st.rerun()

date_from = st.sidebar.date_input("Date From", key="date_from")
date_to   = st.sidebar.date_input("Date To",   key="date_to")

country_filter = st.sidebar.selectbox(
    "Country",
    ["All"] + sorted(sales["country"].dropna().unique()),
    key="country"
)

category_filter = st.sidebar.selectbox(
    "Category",
    ["All"] + sorted(sales["category"].dropna().unique()),
    key="category"
)

# Segment dropdown uses fixed 4-segment lookup (no Regular customers / 0)
segment_filter = st.sidebar.selectbox(
    "Customer Segment",
    ["All"] + sorted(seg_lookup["segment"].dropna().unique()),
    key="segment"
)

# --------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------

filtered = sales.copy()

filtered = filtered[
    (filtered["order_time"] >= pd.to_datetime(date_from)) &
    (filtered["order_time"] <= pd.to_datetime(date_to))
]

if country_filter != "All":
    filtered = filtered[filtered["country"] == country_filter]

if category_filter != "All":
    filtered = filtered[filtered["category"] == category_filter]

if segment_filter != "All":
    seg_customers = seg_lookup[seg_lookup["segment"] == segment_filter]["customer_id"]
    filtered      = filtered[filtered["customer_id"].isin(seg_customers)]

# Attach segment label to every filtered row
filtered_segments = pd.merge(filtered, seg_lookup, on="customer_id", how="left")

# --------------------------------------------------
# KPI METRICS
# Correct values (no filters):
#   Total Revenue   → $4,493,217.47
#   Total Orders    → 33,580
#   Total Customers → 16,268
#   AOV             → $133.81
# --------------------------------------------------

st.subheader("Business KPIs")

col1, col2, col3, col4, col5 = st.columns(5)

revenue         = filtered.drop_duplicates("order_id")["total_usd"].sum()
orders_count    = filtered["order_id"].nunique()
# Total registered customers from customers_clean (always 20,000 unfiltered)
total_customers = len(pd.read_csv("customers_clean.csv"))
active_customers_count = filtered["customer_id"].nunique()
aov             = revenue / orders_count if orders_count > 0 else 0

col1.metric("Total Revenue",      f"${revenue:,.2f}")
col2.metric("Total Orders",       f"{orders_count:,}")
col3.metric("Total Customers",    f"{total_customers:,}")
col4.metric("Active Customers",   f"{active_customers_count:,}")
col5.metric("Avg Order Value",    f"${aov:,.2f}")

# --------------------------------------------------
# TABS
# --------------------------------------------------

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Sales Forecast",
    "Customer Segments",
    "Recommendations",
    "Top Products",
    "Business Insights",
])

# ======================================================
# TAB 1 — SALES FORECAST
# ======================================================

with tab1:

    st.subheader("Sales Forecast Overview")

    ctrl1, _, _ = st.columns([2, 1, 1])
    with ctrl1:
        horizon_days = st.selectbox(
            "Forecast Horizon",
            [("30 days", 30), ("60 days", 60), ("90 days", 90)],
            format_func=lambda x: x[0],
        )[1]

    fc          = forecast.sort_values("ds").copy()
    fc["upper"] = fc["yhat"] * 1.08
    fc["lower"] = fc["yhat"] * 0.92
    split       = len(fc) - horizon_days
    fc_hist     = fc.iloc[:split] if split > 0 else fc
    fc_future   = fc.iloc[split:] if split > 0 else pd.DataFrame()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=fc_hist["ds"], y=fc_hist["yhat"],
        mode="lines", name="Historical",
    ))

    if len(fc_future) > 0:
        # Confidence band (±8%)
        fig.add_trace(go.Scatter(
            x=pd.concat([fc_future["ds"], fc_future["ds"][::-1]]),
            y=pd.concat([fc_future["upper"], fc_future["lower"][::-1]]),
            fill="toself", fillcolor="rgba(255,0,0,0.1)",
            line=dict(color="rgba(255,255,255,0)"),
            name="Confidence Band",
        ))
        fig.add_trace(go.Scatter(
            x=fc_future["ds"], y=fc_future["yhat"],
            mode="lines", line=dict(color="red", dash="dash"),
            name="Forecast",
        ))

    fig.update_layout(xaxis_title="Date", yaxis_title="Revenue ($)", height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Forecast KPI cards
    # Verified values (30d): projected=$67,827  avg=$2,261  peak=$2,443  low=$2,068
    fv = fc_future["yhat"].values if len(fc_future) > 0 else np.array([0])
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Projected Revenue",   f"${fv.sum():,.0f}")
    m2.metric("Avg Daily Revenue",   f"${fv.mean():,.0f}")
    m3.metric("Peak Forecast Day",   f"${fv.max():,.0f}")
    m4.metric("Lowest Forecast Day", f"${fv.min():,.0f}")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Revenue by Country")

        # drop_duplicates("order_id") prevents double-counting
        # sort ascending=True so largest bar appears at top in horizontal chart
        country_rev = (
            filtered
            .drop_duplicates("order_id")
            .groupby("country")["total_usd"]
            .sum()
            .reset_index()
            .rename(columns={"total_usd": "revenue"})
            .sort_values("revenue", ascending=True)
        )

        fig_country = px.bar(
            country_rev, x="revenue", y="country",
            orientation="h",
            labels={"revenue": "Revenue ($)", "country": "Country"},
        )
        st.plotly_chart(fig_country, use_container_width=True)

    with col2:
        st.subheader("Revenue Trend")

        grp = st.radio("Group By", ["Month", "Quarter", "Year"], horizontal=True)

        # drop_duplicates("order_id") + total_usd for correct revenue trend
        temp = filtered.drop_duplicates("order_id").copy()

        if grp == "Month":
            temp["period"] = temp["order_time"].dt.to_period("M").astype(str)
        elif grp == "Quarter":
            temp["period"] = temp["order_time"].dt.to_period("Q").astype(str)
        else:
            temp["period"] = temp["order_time"].dt.year.astype(str)

        trend = (
            temp.groupby("period")["total_usd"]
            .sum()
            .reset_index()
            .rename(columns={"total_usd": "revenue"})
        )

        fig_trend = px.bar(
            trend, x="period", y="revenue",
            labels={"revenue": "Revenue ($)", "period": "Period"},
        )
        st.plotly_chart(fig_trend, use_container_width=True)

# ======================================================
# TAB 2 — CUSTOMER SEGMENTS
# Correct values (no filters):
#   Customers by segment:
#     At-risk customers          6,155
#     High-value loyal customers 5,397
#     New buyers                 2,950
#     Price-sensitive users      1,766
#   Revenue by segment:
#     High-value loyal customers $1,975,934
#     At-risk customers          $1,304,494
#     New buyers                   $725,305
#     Price-sensitive users        $487,484
# ======================================================

with tab2:

    st.subheader("Customer Segment Distribution")

    # Use seg_lookup filtered to only customers present in current filtered orders
    # This gives correct unique customer counts per segment (not inflated by line items)
    active_customers = filtered["customer_id"].unique()
    seg_counts = (
        seg_lookup[seg_lookup["customer_id"].isin(active_customers)]
        .groupby("segment")["customer_id"]
        .nunique()
        .reset_index()
        .rename(columns={"customer_id": "customers"})
    )

    fig_pie = px.pie(
        seg_counts, names="segment", values="customers",
        title="Customers by Segment",
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("Revenue by Segment")

    # Deduplicate at order level first, then join segment — prevents line-item inflation
    seg_rev = (
        filtered
        .drop_duplicates("order_id")[["order_id", "customer_id", "total_usd"]]
        .merge(seg_lookup, on="customer_id", how="left")
        .dropna(subset=["segment"])
        .groupby("segment")["total_usd"]
        .sum()
        .reset_index()
        .rename(columns={"total_usd": "revenue"})
        .sort_values("revenue", ascending=False)
    )

    fig_seg = px.bar(
        seg_rev, x="segment", y="revenue",
        color="segment",
        labels={"revenue": "Revenue ($)", "segment": "Segment"},
    )
    st.plotly_chart(fig_seg, use_container_width=True)

# ======================================================
# TAB 3 — RECOMMENDATIONS
# ======================================================

with tab3:

    st.subheader("Recommendation Viewer")

    customer_list     = recommendations["customer_id"].unique()
    selected_customer = st.selectbox("Select Customer", customer_list)

    recs = recommendations[recommendations["customer_id"] == selected_customer]

    # Enrich with product name and category so table is meaningful
    recs_enriched = pd.merge(
        recs,
        products[["product_id", "product_name", "category"]],
        left_on="recommended_product",
        right_on="product_id",
        how="left",
    ).drop(columns=["product_id"], errors="ignore")

    st.dataframe(recs_enriched, use_container_width=True)

# ======================================================
# TAB 4 — TOP PRODUCTS & CATEGORIES
# Correct top 10 products (no filters):
#   1. mouse rosybrown 419           $9,152
#   2. headphones aquamarine 465     $8,997
#   3. webcam lightblue 848          $8,695
#   4. mouse chartreuse 292          $8,444
#   5. smartwatch moccasin 101       $8,238
#   6. tennis racket palegreen 443   $8,191
#   7. cycling helmet darkkhaki 165  $8,109
#   8. hoodie blanchedalmond 225     $8,098
#   9. water bottle gold 746         $7,696
#  10. yoga mat mediumturquoise 462  $7,670
#
# Correct category revenue (no filters):
#   home & kitchen  $781,434
#   sports          $772,686
#   fashion         $767,567
#   electronics     $644,772
#   beauty          $642,435
#   toys            $528,275
#   books           $356,048
# ======================================================

with tab4:

    st.subheader("Top 10 Revenue Products")

    top_products = (
        filtered
        .groupby("product_name")["revenue"]
        .sum()
        .reset_index()
        .sort_values("revenue", ascending=False)
        .head(10)
    )

    fig_prod = px.bar(
        top_products, x="product_name", y="revenue",
        labels={"revenue": "Revenue ($)", "product_name": "Product"},
        title="Top 10 Products by Revenue",
    )
    fig_prod.update_layout(xaxis_tickangle=-35)
    st.plotly_chart(fig_prod, use_container_width=True)

    st.subheader("Revenue by Category")

    cat_rev = (
        filtered
        .groupby("category")["revenue"]
        .sum()
        .reset_index()
        .sort_values("revenue", ascending=False)
    )

    fig_cat = px.bar(
        cat_rev, x="category", y="revenue",
        color="category",
        labels={"revenue": "Revenue ($)", "category": "Category"},
        title="Revenue by Category",
    )
    st.plotly_chart(fig_cat, use_container_width=True)

# ======================================================
# TAB 5 — BUSINESS INSIGHTS
# Correct values (no filters):
#   Top country  : US
#   Top product  : mouse rosybrown 419
#   Top category : home & kitchen
#   Best segment : High-value loyal customers
#   Monthly growth: 0.75%
# ======================================================

with tab5:

    orders_dedup = filtered.drop_duplicates("order_id")

    # Top country — order-level total_usd
    top_country  = orders_dedup.groupby("country")["total_usd"].sum().idxmax()

    # Top product — discount-adjusted line revenue
    top_product  = filtered.groupby("product_name")["revenue"].sum().idxmax()

    # Top category — discount-adjusted line revenue
    top_category = filtered.groupby("category")["revenue"].sum().idxmax()

    # Best segment — deduplicate orders first, then join seg_lookup
    best_segment = (
        filtered
        .drop_duplicates("order_id")[["order_id", "customer_id", "total_usd"]]
        .merge(seg_lookup, on="customer_id", how="left")
        .dropna(subset=["segment"])
        .groupby("segment")["total_usd"]
        .sum()
        .idxmax()
    )

    # Monthly growth — order-level total_usd, deduped
    temp          = orders_dedup.copy()
    temp["month"] = temp["order_time"].dt.to_period("M").astype(str)
    monthly       = temp.groupby("month")["total_usd"].sum()
    growth        = monthly.pct_change().mean() * 100

    st.markdown(f"""
### Key Insights

**Top Revenue Country:** {top_country}

**Top Performing Product:** {top_product}

**Top Revenue Category:** {top_category}

**Highest Revenue Segment:** {best_segment}

**Average Monthly Growth:** {growth:.2f}%
""")

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown("---")
st.caption("Revenue Growth & Personalization Analytics Platform")