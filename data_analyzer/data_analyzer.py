import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
#color for tables 
#======================================================================================
st.markdown("""
    <style>
        /* Table background and text color */
        .dataframe {
            background-color: #021024; /* Dark navy background */
            color: #FFFFFF; /* White text */
        }
        /* Table header color */
        .dataframe th {
            background-color: #052659; /* Sidebar/card color */
            color: #FFFFFF;
        }
        /* Table cell borders */
        .dataframe td, .dataframe th {
            border: 1px solid #5483B3; /* Mid blue accent */
        }
    </style>
""", unsafe_allow_html=True)
#======================================================================================

#gradient colour for the app 
#======================================================================================
page_bg_css = """                                                                     
<style>
/* App background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(to bottom, #021024, #052659, #5483B3, #7DA0C4, #C1E8FF);
    color: white;
}

/* Sidebar background */
[data-testid="stSidebar"] {
    background: rgba(0,0,0,0.5);
    color: white;
}

/* Make all text white */
html, body, [class*="css"] {
    color: white !important;
}
</style>
"""
st.markdown(page_bg_css, unsafe_allow_html=True)
#metric do over 
#=================================================================================
st.markdown("""
<style>
div[data-testid="stMetric"]{
    background-color: #052659;   /* Dark blue background */
    border: 0.5px solid #7DA0C4;     /* Thin white border */
    border-radius: 20px;         /* Curved corners */
    padding: 15px;
    margin: 10px 0;
    color: white;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

    #title===========================================================================================================
#metric callout value 
#======================================================================================
st.markdown("""
<style>
div[data-testid="stMetric"] {
    background-color: #052659;   /* Dark blue background */
    border: 0.5px solid #7DA0C4; /* Thin border, light blue */
    border-radius: 20px;         /* More curved corners */
    padding: 15px;
    margin: 10px 5px;
    text-align: center;          /* Center everything */
}

/* Style the metric label */
div[data-testid="stMetric"] label {
    color: white !important;     /* White text */
    font-size: 22px !important;  /* Bigger font size */
    font-weight: bold;           /* Bold for emphasis */
    display: block;
    text-align: center;          /* Center the label */
    margin-bottom: 5px;
}

/* Style the metric value and delta */
div[data-testid="stMetric"] span {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

    #file uploader=====================================================================================================

st.title("Data Analyzer")
uploaded_file = st.file_uploader("Upload your excel file" , type=["xlsx" , "xls"])
if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
    except Exception as exc:
        st.error(f"Unable to read the uploaded Excel file: {exc}")
        st.stop()

    if df is None or df.empty:
        st.error("The uploaded file is empty. Please upload an Excel file with data.")
        st.stop()

    if df.columns.empty:
        st.error("The uploaded file has no columns to analyze.")
        st.stop()
    

    #calculate kpi =====================================================================================================
    st.markdown(
        "<h3 style='font-size:27px;'>Dataset Overview</h3>",
        unsafe_allow_html=True)
    
    totalrows = len(df)
    totlcolumns = len(df.columns)
    missingvalues = df.isnull().sum().sum()
    col1 , col2 , col3 = st.columns(3)
    
    with col1:
        # st.write("---") 
        st.metric("Total Rows" , totalrows)
        # st.write("---")

    with col2:
        # st.write("---")
        st.metric("total columns".capitalize() , totlcolumns)  
        # st.write("---")  
    with col3:
        # st.write("---") 
        st.metric("missing values".capitalize() , missingvalues)
        # st.write("---")
    
    
    #data preview =====================================================================================================
    st.markdown(
        "<h3 style='font-size:27px;'>Preview of Data</h3>",
        unsafe_allow_html=True)
    st.dataframe(df.head(), hide_index=True)

    # Detect and extract date column early for trend analysis
    date_keywords = ["date", "order_date", "invoice_date"]
    date_col = None
    for col in df.columns:
        if any(keyword.lower() in col.lower() for keyword in date_keywords):
            date_col = col
            break

    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df = df.dropna(subset=[date_col])
        df['year'] = df[date_col].dt.year   
        df['month'] = df[date_col].dt.month

    
    #basic info by column  ============================================================================================
    st.markdown(
        "<h3 style='font-size:27px;'>Column Summary</h3>",
        unsafe_allow_html=True)
    summary = st.selectbox("select a column to view summary" , df.columns)
    if summary:
        st.write(f"summary of **{summary}**")
        st.write(df[summary].describe())


    #metrics ====================================================================================================================
    st.markdown(
        "<h3 style='font-size:27px;'>Key Performance Indicators (KPIs)</h3>",
        unsafe_allow_html=True)
    # st.write("---")
    possible_kw = {
        "Sales" : ["sales" , "total_sales" , "order_amount" , "salesamount" , "total_price" , "totalprice" , "sale" , "ordervlaue" , "order value"],
        "Quantity" : ["quantity" , "total_quantity" , "sold_quantity"],
        "Profit" : ["total_profit" , 'net_profit' , "profit"]
        }
    detected_cols = {}
    for metric , kws in possible_kw.items():
        for col in df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in kws):
                detected_cols[metric] = col
                break

    selected_kpi_year = None
    year_options = None
    kpi_df = df.copy()
    if "year" in df.columns:
        year_options = sorted(df["year"].dropna().astype(int).unique())
        if year_options:
            selected_kpi_year = st.selectbox("Select Year for KPI Indicators", year_options, key="kpi_year")
            kpi_df = df[df["year"] == selected_kpi_year].copy()

    def get_numeric_series(dataframe, column_name):
        return pd.to_numeric(dataframe[column_name], errors="coerce")

    def format_metric_value(metric_name, value):
        if pd.isna(value):
            return "N/A"
        if "margin" in metric_name.lower() or "%" in metric_name:
            return f"{value:.2f}%"
        return f"{value:,.2f}" if isinstance(value, float) and not float(value).is_integer() else f"{value:,.0f}"

    # Calculate number of columns needed for metrics display
    num_metrics = len(detected_cols)

    # Add profit margin if both Sales and Profit exist
    has_profit_margin = False
    if "Sales" in detected_cols and "Profit" in detected_cols:
        num_metrics += 1
        has_profit_margin = True

    cols = st.columns(num_metrics)
    col_idx = 0
    
    # Display basic metrics (Total Sales, Total Quantity, Total Profit)
    for metric, colname in detected_cols.items():
        metric_series = get_numeric_series(kpi_df, colname)
        if metric_series.notna().any():
            total_value = metric_series.sum()
            cols[col_idx].metric(f"Total {metric}", f'{total_value:,.0f}')
            col_idx += 1
    
    # Display Profit Margin if available
    if has_profit_margin:
        sales_col_name = detected_cols["Sales"]
        profit_col_name = detected_cols["Profit"]
        total_sales = get_numeric_series(kpi_df, sales_col_name).sum()
        total_profit = get_numeric_series(kpi_df, profit_col_name).sum()
        
        if total_sales > 0:
            profit_margin = (total_profit / total_sales) * 100
            cols[col_idx].metric("Profit Margin %", f'{profit_margin:.2f}%')
            col_idx += 1

    extra_metric_options = {
        "Sum": "sum",
        "Average": "mean",
        "Maximum": "max",
        "Minimum": "min",
        "Median": "median",
        "Count": "count",
        "Unique Count": "nunique"
    }

    numeric_columns = [
        column_name for column_name in kpi_df.columns
        if pd.to_numeric(kpi_df[column_name], errors="coerce").notna().any()
    ]
    all_columns = list(df.columns)

    with st.expander("More Metrics"):
        st.caption("Advanced KPI metrics")
        growth_selector_col1, growth_selector_col2 = st.columns(2)
        with growth_selector_col1:
            growth_date_column = st.selectbox(
                "Growth Date Column",
                all_columns,
                index=all_columns.index(date_col) if date_col in all_columns else 0,
                key="growth_date_column"
            )
        with growth_selector_col2:
            growth_value_column = st.selectbox(
                "Growth Value Column",
                numeric_columns if numeric_columns else all_columns,
                index=(numeric_columns.index(detected_cols["Sales"]) if "Sales" in detected_cols and detected_cols["Sales"] in numeric_columns else 0),
                key="growth_value_column"
            )

        growth_dates = pd.to_datetime(df[growth_date_column], errors="coerce")
        growth_values = pd.to_numeric(df[growth_value_column], errors="coerce")
        growth_df = pd.DataFrame({"date": growth_dates, "value": growth_values}).dropna()

        monthly_growth_value = np.nan
        yoy_growth_value = np.nan
        if not growth_df.empty:
            if selected_kpi_year is not None:
                monthly_growth_df = growth_df[growth_df["date"].dt.year == selected_kpi_year].copy()
                yoy_current_year = selected_kpi_year
            else:
                monthly_growth_df = growth_df.copy()
                yoy_current_year = int(growth_df["date"].dt.year.max())

            monthly_totals = monthly_growth_df.groupby(monthly_growth_df["date"].dt.to_period("M"))["value"].sum().sort_index()
            if len(monthly_totals) >= 2 and monthly_totals.iloc[-2] != 0:
                monthly_growth_value = ((monthly_totals.iloc[-1] - monthly_totals.iloc[-2]) / monthly_totals.iloc[-2]) * 100

            current_year_total = growth_df[growth_df["date"].dt.year == yoy_current_year]["value"].sum()
            previous_year_total = growth_df[growth_df["date"].dt.year == (yoy_current_year - 1)]["value"].sum()
            if previous_year_total != 0:
                yoy_growth_value = ((current_year_total - previous_year_total) / previous_year_total) * 100

        advanced_metric_cols = st.columns(2)
        advanced_metric_cols[0].metric(
            "Monthly Growth %",
            format_metric_value("Monthly Growth %", monthly_growth_value)
        )
        advanced_metric_cols[1].metric(
            "YoY Growth %",
            format_metric_value("YoY Growth %", yoy_growth_value)
        )

        st.caption("Choose a metric and a column to show one more KPI card.")
        selector_col1, selector_col2 = st.columns(2)
        with selector_col1:
            selected_metric_question = st.selectbox(
                "Metric Question",
                list(extra_metric_options.keys()),
                key="more_metrics_question"
            )
        with selector_col2:
            selected_metric_column = st.selectbox(
                "Column Selectbox",
                numeric_columns if numeric_columns else list(kpi_df.columns),
                key="more_metrics_column"
            )

        if numeric_columns:
            selected_series = get_numeric_series(kpi_df, selected_metric_column).dropna()
            if selected_series.empty:
                metric_value = np.nan
            else:
                metric_action = extra_metric_options[selected_metric_question]
                if metric_action == "count":
                    metric_value = selected_series.count()
                elif metric_action == "nunique":
                    metric_value = selected_series.nunique()
                else:
                    metric_value = getattr(selected_series, metric_action)()

            extra_metric_col = st.columns(1)[0]
            extra_metric_col.metric(
                f"{selected_metric_question} of {selected_metric_column}",
                format_metric_value(selected_metric_question, metric_value)
            )
        else:
            st.info("No numeric columns are available for additional metrics.")
    
    # st.write("---")
                 

    #sales trend==================================================================================================================
    st.markdown("<h3 style='font-size:27px;'>Monthly Sales/Profit Trend </h3>",
        unsafe_allow_html=True)
    sales_keywords = ["sales", "salesamount" ,  "amount", "total", "price", "revenue", "order_amount", "totalprice" , "orderamount"]
    sales_col = None

    for col in df.columns:
        if any(keyword.lower() in col.lower() for keyword in sales_keywords):
            sales_col = col
            break

    if not sales_col:
        st.error("No sales column detected automatically")
        sales_col = st.selectbox("select column to analyze" , df.columns)
    else:
        st.info(f"Auto-detected column: {sales_col}")
        sales_col = st.selectbox("Override auto‑detected column (Sales/Profit/etc.)(optional)", df.columns, index=df.columns.get_loc(sales_col))
    
    # Check if date column was detected earlier
    if not date_col:
        st.error("No date column detected.")
        st.stop()

    # Convert sales column to numeric
    df[sales_col] = pd.to_numeric(df[sales_col] , errors="coerce")

    # Year slicer
    selected_year = st.selectbox("Select Year", sorted(df['year'].dropna().unique()))
    

    df_filtered = df[df['year'] == selected_year]

    # Monthly aggregation
    monthly_sales = df_filtered.groupby('month')[sales_col].sum()

    # Ensure all months are present
    all_months = pd.Series(index=range(1, 13))
    monthly_sales = all_months.add(monthly_sales, fill_value=0)

    # Month names
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


    # Plot
    fig, ax = plt.subplots()
    ax.plot(month_names, monthly_sales.values, marker='o',color="#C6D7EE",
            alpha=0.9,
            markerfacecolor="#021024")
    
    # ax.set_xlabel("Month" , color="black")
    ax.set_ylabel("Total Sales" , color="white")
    ax.set_title(f"Monthly {sales_col} Trend - {selected_year}" , color="white")
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.tick_params(axis='x', colors="white")
    ax.tick_params(axis='y', colors="white")

    
    fig.patch.set_facecolor("#021024")
    ax.set_facecolor("#021024")
    for spine in ax.spines.values():
        spine.set_edgecolor("white")
        spine.set_linewidth(0.8)

    st.pyplot(fig)  

    #Show data
    with st.expander(f"show {sales_col} monthly table"):
      result_df = pd.DataFrame({
        "Month": month_names,
        "Sales": monthly_sales.values
      })
    
      st.dataframe(result_df, hide_index=True)






    #QNA USING GROUP BY  =====================================================================================================
    
    st.markdown("<h3 style='font-size:27px;'>Sales & Profit Performance Queries </h3>",
        unsafe_allow_html=True)
    
    #Example questions
    with st.expander("Example Questions"):
     st.markdown("""
    <div style="background-color: #052659; padding: 15px; border-radius: 10px; border: 0.5px solid #7DA0C4;">
        • What's the top selling product?<br>
        • Which customer has highest sales?<br>
        • Average quantity by product<br>
        • Lowest sales by region
        </p>
      </div>
     """, unsafe_allow_html=True)
    
    #Year slicer and visualization options for Q&A section
    qa_filter_col1, qa_filter_col2 = st.columns(2)
    with qa_filter_col1:
        selected_year_qa = st.selectbox("Select Year for Analysis", sorted(df['year'].dropna().unique()), key="qa_year")
    with qa_filter_col2:
        viz_type = st.selectbox("Choose Visualization Type", ["Bar Chart", "Pie Chart"])

    df_qa = df[df['year'] == selected_year_qa]
    
    question = st.text_input("ask question about your data".capitalize()).strip()
    
    if question:
        if df_qa.empty:
            st.warning("No data is available for the selected year.")
        else:
            q = question.lower()
            matched_cols = [col for col in df_qa.columns if col.lower() in q]

            if len(matched_cols) < 2:
                st.warning("Please include one category column and one numeric column in your question, like 'highest sales by region'.")
            else:
                cat_cols = [col for col in matched_cols if df_qa[col].dtype == "object"]
                num_cols = [col for col in matched_cols if pd.api.types.is_numeric_dtype(df_qa[col])]

                if not cat_cols or not num_cols:
                    st.warning("I matched some columns, but I need one text column and one numeric column to answer that question.")
                else:
                    group_col = cat_cols[0]
                    value_col = num_cols[0]

                    if "average" in q or "avg" in q or "mean" in q:
                        summary = df_qa.groupby(group_col)[value_col].mean().sort_values(ascending=False)
                        agg_type = "Average"
                    elif "min" in q or "lowest" in q or "least" in q:
                        summary = df_qa.groupby(group_col)[value_col].sum().sort_values(ascending=True)
                        agg_type = "Lowest Total"
                    elif "max" in q or "highest" in q or "top" in q:
                        summary = df_qa.groupby(group_col)[value_col].sum().sort_values(ascending=False)
                        agg_type = "Highest Total"
                    else:
                        summary = df_qa.groupby(group_col)[value_col].sum().sort_values(ascending=False)
                        agg_type = "Total"

                    if summary.empty:
                        st.warning("I could not generate a result for that question with the selected year.")
                    else:
                        with st.expander(f"total {value_col} by {group_col}"):
                            st.dataframe(summary)

                        top_entity = summary.idxmax()
                        top_value = summary.max()
                        low_entity = summary.idxmin()
                        low_value = summary.min()

                        st.write(f"🏆 Top {group_col}: **{top_entity}** ({top_value})")
                        st.write(f"⬇️ Lowest {group_col}: **{low_entity}** ({low_value})")

                        # Show visualization based on selected type
                        if viz_type == "Pie Chart":
                            fig, ax = plt.subplots(figsize=(8, 6))
                            # Use numpy linspace to get better distributed blue shades
                            colors = plt.cm.Blues(np.linspace(0.4, 0.95, len(summary)))
                            summary.plot(kind="pie", autopct='%1.1f%%', ax=ax, colors=colors, textprops={'color': 'white'})
                            ax.set_ylabel("")
                            ax.set_title(f"{agg_type} {value_col} by {group_col}", color="white", fontsize=14, fontweight="bold")
                            fig.patch.set_facecolor("#021024")
                            ax.set_facecolor("#021024")
                            st.pyplot(fig)
                        
                        else:  # Bar Chart (default)
                            fig, ax = plt.subplots()
                            summary.plot(kind="bar", color="#D7E4F7", edgecolor="#185DBE", alpha=0.7, ax=ax)
                            ax.set_ylabel("value", color="white")
                            ax.xaxis.label.set_visible(False)
                            ax.set_title(f"{agg_type} {value_col} by {group_col}", color="white")
                            ax.spines["right"].set_visible(False)
                            ax.spines["top"].set_visible(False)
                            for patch in ax.patches:
                                patch.set_capstyle("round")
                                patch.set_joinstyle("round")
                            fig.patch.set_facecolor("#021024")
                            ax.set_facecolor("#021024")
                            for spine in ax.spines.values():
                                spine.set_edgecolor("white")
                                spine.set_linewidth(0.8)
                            ax.tick_params(axis='x', colors="white")
                            ax.tick_params(axis='y', colors="white")
                            st.pyplot(fig)

   



     
