from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.config import (  # noqa: E402
    DIM_CUSTOMER_FILE,
    DIM_DATE_FILE,
    DIM_PRODUCT_FILE,
    FACT_SALES_FILE,
    VALIDATION_REPORT_FILE,
)


PROJECT_NAME = "Retail Sales Intelligence Platform"
PROJECT_SUBTITLE = (
    "Retail analytics warehouse, business KPI layer, and interactive reporting surface for "
    "data analyst and data engineer portfolios."
)


st.set_page_config(
    page_title=PROJECT_NAME,
    layout="wide",
)


@st.cache_data(show_spinner=False)
def load_model_data() -> dict[str, pd.DataFrame]:
    fact_sales = pd.read_csv(FACT_SALES_FILE, parse_dates=["order_timestamp"])
    dim_product = pd.read_csv(DIM_PRODUCT_FILE)
    dim_customer = pd.read_csv(DIM_CUSTOMER_FILE)
    dim_date = pd.read_csv(DIM_DATE_FILE, parse_dates=["date", "month_start"])

    merged = (
        fact_sales.merge(dim_product, on="product_id", how="left")
        .merge(dim_customer.rename(columns={"city": "customer_city", "segment": "customer_segment"}), on="customer_id", how="left")
        .merge(dim_date, on="date_key", how="left")
    )
    merged["order_date"] = merged["order_timestamp"].dt.date
    merged["order_hour"] = merged["order_timestamp"].dt.hour
    merged["customer_type"] = merged.groupby("customer_id")["order_id"].transform("nunique").gt(1).map(
        {True: "Repeat Customer", False: "One-Time Customer"}
    )

    validation = pd.read_csv(VALIDATION_REPORT_FILE) if VALIDATION_REPORT_FILE.exists() else pd.DataFrame()
    return {
        "fact_sales": fact_sales,
        "merged": merged,
        "validation": validation,
    }


def filter_selector(label: str, options: list[str], key_prefix: str) -> list[str]:
    with st.sidebar.expander(label, expanded=False):
        use_all = st.checkbox(f"Use all {label.lower()}", value=True, key=f"{key_prefix}_all")
        if use_all:
            st.caption(f"{len(options)} selected")
            return options
        selected = st.multiselect(
            f"Choose {label.lower()}",
            options=options,
            default=options[: min(5, len(options))],
            key=f"{key_prefix}_selected",
        )
        return selected or options


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filters")

    min_date = pd.to_datetime(df["date"]).min().date()
    max_date = pd.to_datetime(df["date"]).max().date()
    selected_dates = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
        start_date, end_date = selected_dates
    else:
        start_date = end_date = selected_dates

    segments = filter_selector(
        "Customer Segments",
        sorted(df["segment"].dropna().unique()),
        "segments",
    )
    cities = filter_selector(
        "Cities",
        sorted(df["city"].dropna().unique()),
        "cities",
    )
    categories = filter_selector(
        "Product Categories",
        sorted(df["category"].dropna().unique()),
        "categories",
    )

    filtered = df[
        (pd.to_datetime(df["date"]).dt.date >= start_date)
        & (pd.to_datetime(df["date"]).dt.date <= end_date)
        & (df["segment"].isin(segments))
        & (df["city"].isin(cities))
        & (df["category"].isin(categories))
    ].copy()
    filtered.attrs["selected_start"] = pd.Timestamp(start_date)
    filtered.attrs["selected_end"] = pd.Timestamp(end_date)

    st.sidebar.caption(
        f"{len(filtered):,} orders | {filtered['customer_id'].nunique():,} customers | {filtered['product_id'].nunique():,} products"
        if not filtered.empty
        else "No matching records"
    )
    return filtered


def format_currency(value: float) -> str:
    absolute_value = abs(value)
    if absolute_value >= 10_000_000:
        return f"Rs {value / 10_000_000:,.1f} Cr"
    if absolute_value >= 100_000:
        return f"Rs {value / 100_000:,.1f} L"
    return f"Rs {value:,.0f}"


def show_header() -> None:
    st.title(PROJECT_NAME)
    st.caption(PROJECT_SUBTITLE)


def format_display_frame(
    df: pd.DataFrame,
    rename_map: dict[str, str],
    currency_columns: list[str] | None = None,
    percentage_columns: list[str] | None = None,
    integer_columns: list[str] | None = None,
) -> pd.DataFrame:
    display = df.rename(columns=rename_map).copy()
    for column in currency_columns or []:
        if column in display:
            display[column] = display[column].map(format_currency)
    for column in percentage_columns or []:
        if column in display:
            display[column] = display[column].map(lambda value: f"{value:.1f}%")
    for column in integer_columns or []:
        if column in display:
            display[column] = display[column].map(lambda value: f"{int(round(value)):,}")
    return display


def prepare_monthly_trend(df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    monthly = (
        df.groupby("month_start", as_index=False)
        .agg(
            total_revenue=("revenue", "sum"),
            total_orders=("order_id", "nunique"),
            active_customers=("customer_id", "nunique"),
        )
        .sort_values("month_start")
    )
    if monthly.empty:
        return monthly, "No monthly trend data is available for the current filter selection."

    selected_start = pd.Timestamp(df.attrs.get("selected_start", df["date"].min()))
    selected_end = pd.Timestamp(df.attrs.get("selected_end", df["date"].max()))
    monthly["month_end"] = monthly["month_start"] + pd.offsets.MonthEnd(0)
    monthly["is_complete_month"] = (
        (monthly["month_start"] >= selected_start.normalize())
        & (monthly["month_end"] <= selected_end.normalize())
    )

    complete_months = monthly[monthly["is_complete_month"]].copy()
    if len(complete_months) >= 2:
        excluded_months = monthly.loc[~monthly["is_complete_month"], "month_start"].dt.strftime("%b %Y").tolist()
        note = (
            "Trend charts exclude partial edge months: "
            + ", ".join(excluded_months)
            if excluded_months
            else "Trend charts are using full months only."
        )
        return complete_months, note

    return monthly.copy(), "Current filter selection does not contain at least two full months, so partial months are included."


def show_kpis(df: pd.DataFrame) -> None:
    customer_orders = df.groupby("customer_id")["order_id"].nunique()
    repeat_rate = (customer_orders > 1).mean() * 100 if not customer_orders.empty else 0.0

    metrics = [
        ("Total Revenue", format_currency(df["revenue"].sum())),
        ("Total Orders", f"{df['order_id'].nunique():,}"),
        ("Active Customers", f"{df['customer_id'].nunique():,}"),
        ("Average Order Value", format_currency(df["revenue"].sum() / max(df["order_id"].nunique(), 1))),
        ("Units Sold", f"{int(df['quantity'].sum()):,}"),
        ("Repeat Customer Rate", f"{repeat_rate:.1f}%"),
    ]

    top_row = st.columns(3)
    bottom_row = st.columns(3)
    for column, (label, value) in zip(top_row + bottom_row, metrics):
        column.metric(label, value)


def executive_overview(df: pd.DataFrame) -> None:
    show_kpis(df)
    monthly, trend_note = prepare_monthly_trend(df)

    monthly["revenue_growth_pct"] = monthly["total_revenue"].pct_change() * 100

    category = (
        df.groupby("category", as_index=False)
        .agg(total_revenue=("revenue", "sum"), total_units=("quantity", "sum"))
        .sort_values("total_revenue", ascending=False)
    )
    segment = (
        df.groupby("segment", as_index=False)
        .agg(total_revenue=("revenue", "sum"), active_customers=("customer_id", "nunique"))
        .sort_values("total_revenue", ascending=False)
    )
    st.caption(trend_note)

    left, right = st.columns((1.6, 1))
    with left:
        fig = px.line(
            monthly,
            x="month_start",
            y="total_revenue",
            markers=True,
            title="Monthly Revenue Trend",
            labels={"month_start": "Month", "total_revenue": "Revenue"},
        )
        fig.update_layout(margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with right:
        fig = px.bar(
            category.head(8),
            x="total_revenue",
            y="category",
            orientation="h",
            title="Top Categories by Revenue",
            labels={"total_revenue": "Revenue", "category": "Category"},
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig, use_container_width=True)

    insight_one, insight_two = st.columns(2)
    with insight_one:
        st.subheader("Segment Contribution")
        segment_display = format_display_frame(
            segment,
            rename_map={
                "segment": "Customer Segment",
                "total_revenue": "Total Revenue",
                "active_customers": "Active Customers",
            },
            currency_columns=["Total Revenue"],
            integer_columns=["Active Customers"],
        )
        st.dataframe(segment_display, use_container_width=True, hide_index=True)
    with insight_two:
        growth = monthly["revenue_growth_pct"].dropna()
        strongest_month = monthly.loc[monthly["total_revenue"].idxmax()] if not monthly.empty else None
        avg_growth = growth.mean() if not growth.empty else 0.0
        st.subheader("Current Read")
        if strongest_month is not None:
            st.markdown(
                f"- Best month in the current view: `{strongest_month['month_start']:%b %Y}` with `{format_currency(strongest_month['total_revenue'])}` in revenue."
            )
        st.markdown(f"- Average month-over-month revenue growth: `{avg_growth:.2f}%`.")
        st.markdown(
            f"- Highest-contributing segment: `{segment.iloc[0]['segment']}` based on the current filter context."
            if not segment.empty
            else "- No segment data available for the current filters."
        )


def sales_trends(df: pd.DataFrame) -> None:
    revenue_monthly, trend_note = prepare_monthly_trend(df)
    st.caption(trend_note)

    daily_pattern = (
        df.groupby(["weekday_name", "order_hour"], as_index=False)
        .agg(total_revenue=("revenue", "sum"))
    )
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    heatmap = (
        daily_pattern.assign(weekday_name=pd.Categorical(daily_pattern["weekday_name"], categories=weekday_order, ordered=True))
        .pivot(index="weekday_name", columns="order_hour", values="total_revenue")
        .fillna(0)
        .reindex(weekday_order)
    )

    left, right = st.columns((1.5, 1))
    with left:
        fig = px.bar(
            revenue_monthly,
            x="month_start",
            y="total_orders",
            title="Monthly Order Volume",
            labels={"month_start": "Month", "total_orders": "Orders"},
        )
        fig.update_layout(margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with right:
        fig = px.line(
            revenue_monthly,
            x="month_start",
            y="active_customers",
            markers=True,
            title="Active Customers by Month",
            labels={"month_start": "Month", "active_customers": "Customers"},
        )
        fig.update_layout(margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig, use_container_width=True)

    fig = px.imshow(
        heatmap,
        aspect="auto",
        color_continuous_scale="Blues",
        title="Revenue Heatmap by Weekday and Hour",
        labels={"x": "Order Hour", "y": "Weekday", "color": "Revenue"},
    )
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fig, use_container_width=True)

    peak_hour = daily_pattern.loc[daily_pattern["total_revenue"].idxmax()] if not daily_pattern.empty else None
    best_month = revenue_monthly.loc[revenue_monthly["total_revenue"].idxmax()] if not revenue_monthly.empty else None
    st.subheader("Trend Read")
    if best_month is not None:
        st.markdown(
            f"- Strongest full month: `{best_month['month_start']:%b %Y}` with `{format_currency(best_month['total_revenue'])}` across `{best_month['total_orders']:,}` orders."
        )
    if peak_hour is not None:
        st.markdown(
            f"- Highest-yield demand slot: `{peak_hour['weekday_name']}` at `{int(peak_hour['order_hour']):02d}:00`."
        )


def customer_insights(df: pd.DataFrame) -> None:
    customer_summary = (
        df.groupby(["customer_id", "segment", "city"], as_index=False)
        .agg(order_count=("order_id", "nunique"), total_revenue=("revenue", "sum"), total_units=("quantity", "sum"))
    )
    customer_summary["customer_type"] = customer_summary["order_count"].gt(1).map(
        {True: "Repeat Customer", False: "One-Time Customer"}
    )

    segment_summary = (
        customer_summary.groupby("segment", as_index=False)
        .agg(
            customers=("customer_id", "nunique"),
            avg_orders_per_customer=("order_count", "mean"),
            avg_revenue_per_customer=("total_revenue", "mean"),
            repeat_customer_rate=("customer_type", lambda values: (values == "Repeat Customer").mean() * 100),
        )
        .sort_values("avg_revenue_per_customer", ascending=False)
    )

    left, right = st.columns(2)
    with left:
        fig = px.bar(
            segment_summary,
            x="segment",
            y="avg_revenue_per_customer",
            title="Average Revenue per Customer by Segment",
            labels={"avg_revenue_per_customer": "Revenue per Customer", "segment": "Segment"},
        )
        fig.update_layout(margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with right:
        fig = px.bar(
            segment_summary,
            x="segment",
            y="repeat_customer_rate",
            title="Repeat Customer Rate by Segment",
            labels={"repeat_customer_rate": "Repeat Rate (%)", "segment": "Segment"},
        )
        fig.update_layout(margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig, use_container_width=True)

    top_customers = customer_summary.sort_values("total_revenue", ascending=False).head(15)
    st.subheader("Top Customers in Current View")
    top_customers_display = format_display_frame(
        top_customers,
        rename_map={
            "customer_id": "Customer ID",
            "segment": "Customer Segment",
            "city": "City",
            "order_count": "Orders",
            "total_revenue": "Total Revenue",
            "total_units": "Units Sold",
            "customer_type": "Customer Type",
        },
        currency_columns=["Total Revenue"],
        integer_columns=["Orders", "Units Sold"],
    )
    st.dataframe(top_customers_display, use_container_width=True, hide_index=True)

    if not segment_summary.empty:
        best_segment = segment_summary.iloc[0]
        repeat_leader = segment_summary.sort_values("repeat_customer_rate", ascending=False).iloc[0]
        st.subheader("Customer Read")
        st.markdown(
            f"- Highest revenue per customer comes from `{best_segment['segment']}` at `{format_currency(best_segment['avg_revenue_per_customer'])}`."
        )
        st.markdown(
            f"- Best repeat behavior is in `{repeat_leader['segment']}` with a `{repeat_leader['repeat_customer_rate']:.1f}%` repeat rate."
        )


def product_geography(df: pd.DataFrame) -> None:
    product_summary = (
        df.groupby(["product_name", "category"], as_index=False)
        .agg(total_revenue=("revenue", "sum"), total_units=("quantity", "sum"), total_orders=("order_id", "nunique"))
        .sort_values("total_revenue", ascending=False)
        .head(15)
    )
    product_summary["cumulative_share_pct"] = (
        product_summary["total_revenue"].cumsum() / product_summary["total_revenue"].sum() * 100
    )

    city_summary = (
        df.groupby("city", as_index=False)
        .agg(total_revenue=("revenue", "sum"), total_orders=("order_id", "nunique"), active_customers=("customer_id", "nunique"))
        .sort_values("total_revenue", ascending=False)
        .head(15)
    )

    pareto = go.Figure()
    pareto.add_trace(go.Bar(x=product_summary["product_name"], y=product_summary["total_revenue"], name="Revenue"))
    pareto.add_trace(
        go.Scatter(
            x=product_summary["product_name"],
            y=product_summary["cumulative_share_pct"],
            name="Cumulative Revenue Share (%)",
            yaxis="y2",
            mode="lines+markers",
        )
    )
    pareto.update_layout(
        title="Product Pareto View",
        yaxis=dict(title="Revenue"),
        yaxis2=dict(title="Cumulative Share (%)", overlaying="y", side="right", range=[0, 105]),
        margin=dict(l=10, r=10, t=50, b=10),
    )

    left, right = st.columns((1.4, 1))
    with left:
        st.plotly_chart(pareto, use_container_width=True)
    with right:
        fig = px.scatter(
            city_summary,
            x="active_customers",
            y="total_revenue",
            size="total_orders",
            color="city",
            title="City Revenue vs Active Customers",
            labels={"active_customers": "Active Customers", "total_revenue": "Revenue"},
        )
        fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top Products")
    product_summary_display = format_display_frame(
        product_summary,
        rename_map={
            "product_name": "Product Name",
            "category": "Category",
            "total_revenue": "Total Revenue",
            "total_units": "Units Sold",
            "total_orders": "Orders",
            "cumulative_share_pct": "Cumulative Revenue Share",
        },
        currency_columns=["Total Revenue"],
        percentage_columns=["Cumulative Revenue Share"],
        integer_columns=["Units Sold", "Orders"],
    )
    st.dataframe(product_summary_display, use_container_width=True, hide_index=True)

    if not product_summary.empty and not city_summary.empty:
        top_product = product_summary.iloc[0]
        top_city = city_summary.iloc[0]
        top_five_share = product_summary["total_revenue"].head(5).sum() / product_summary["total_revenue"].sum() * 100
        st.subheader("Portfolio Read")
        st.markdown(
            f"- Highest-revenue product in the current view is `{top_product['product_name']}` at `{format_currency(top_product['total_revenue'])}`."
        )
        st.markdown(
            f"- Top city by revenue is `{top_city['city']}` with `{format_currency(top_city['total_revenue'])}`."
        )
        st.markdown(
            f"- The top five displayed products account for `{top_five_share:.1f}%` of revenue in this Pareto slice."
        )


def data_quality(validation: pd.DataFrame) -> None:
    if validation.empty:
        st.info("Validation outputs are not available yet. Run `python -m src.pipeline` first.")
        return

    status_summary = validation.groupby(["stage", "status"], as_index=False).size()
    fig = px.bar(
        status_summary,
        x="stage",
        y="size",
        color="status",
        barmode="group",
        title="Validation Checks by Stage",
        labels={"stage": "Pipeline Stage", "size": "Check Count"},
        color_discrete_map={"pass": "#2f855a", "fail": "#c53030"},
    )
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fig, use_container_width=True)
    pass_rate = (validation["status"].eq("pass").mean() * 100) if not validation.empty else 0.0
    if pass_rate == 100.0:
        st.success("All pipeline validation checks are currently passing.")
    else:
        st.warning(f"Pipeline validation pass rate is {pass_rate:.1f}%.")

    validation_display = format_display_frame(
        validation,
        rename_map={
            "stage": "Pipeline Stage",
            "check_name": "Check Name",
            "status": "Status",
            "metric_value": "Metric Value",
            "details": "Details",
        },
    )
    st.dataframe(validation_display, use_container_width=True, hide_index=True)


def main() -> None:
    required_files = [FACT_SALES_FILE, DIM_PRODUCT_FILE, DIM_CUSTOMER_FILE, DIM_DATE_FILE]
    missing_files = [path for path in required_files if not path.exists()]
    if missing_files:
        st.error("Warehouse files are missing. Run `python -m src.pipeline` before opening the dashboard.")
        st.code("\n".join(str(path) for path in missing_files))
        return

    show_header()
    model_data = load_model_data()
    filtered = apply_filters(model_data["merged"])
    if filtered.empty:
        st.warning("No records match the current filter selection. Expand the filters to continue.")
        return

    tabs = st.tabs(
        [
            "Executive Overview",
            "Sales Trends",
            "Customer Insights",
            "Product & Geography",
            "Data Quality",
        ]
    )

    with tabs[0]:
        executive_overview(filtered)
    with tabs[1]:
        sales_trends(filtered)
    with tabs[2]:
        customer_insights(filtered)
    with tabs[3]:
        product_geography(filtered)
    with tabs[4]:
        data_quality(model_data["validation"])


if __name__ == "__main__":
    main()
