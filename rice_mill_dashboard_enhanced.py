import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def format_currency(x):
    """Format number as Indian currency"""
    return f"₹ {x:,.0f}"


def format_percentage(x):
    """Format number as percentage"""
    return f"{x:.1f}%"


def calculate_comprehensive_financials(inputs):
    """Calculate all financial metrics with comprehensive details"""
    
    # ===== CAPITAL COST BREAKDOWN =====
    capital_costs = {
        "Land": inputs.get("land_cost", 0),
        "Building & Civil Works": inputs.get("building_cost", 0),
        "Plant & Machinery": inputs.get("machinery_cost", 0),
        "Electrical Installation": inputs.get("electrical_cost", 0),
        "Pre-operative Expenses": inputs.get("preoperative_cost", 0),
        "Miscellaneous Fixed Assets": inputs.get("misc_fixed_assets", 0),
    }
    total_fixed_capital = sum(capital_costs.values())
    working_capital = inputs.get("working_capital", 0)
    total_project_cost = total_fixed_capital + working_capital
    
    # ===== FINANCING DETAILS =====
    loan_amount = inputs.get("loan_amount", 0)
    equity_amount = total_project_cost - loan_amount
    loan_interest_rate = inputs.get("loan_interest_rate", 12.0) / 100.0
    loan_tenure_years = inputs.get("loan_tenure", 10)
    
    # Calculate EMI
    if loan_amount > 0 and loan_interest_rate > 0:
        monthly_rate = loan_interest_rate / 12
        num_payments = loan_tenure_years * 12
        emi = loan_amount * monthly_rate * (1 + monthly_rate)**num_payments / ((1 + monthly_rate)**num_payments - 1)
        annual_loan_payment = emi * 12
    else:
        emi = 0
        annual_loan_payment = 0
    
    # ===== PRODUCTION PARAMETERS =====
    tph = 3.0  # tonnes per hour
    hours_per_day = inputs["hours_per_day"]
    days_per_month = inputs["days_per_month"]
    working_days_per_year = days_per_month * 12
    recovery_rate = inputs["recovery_rate"] / 100.0
    
    # Production calculations
    paddy_tonnes_day = tph * hours_per_day
    paddy_tonnes_month = paddy_tonnes_day * days_per_month
    paddy_tonnes_year = paddy_tonnes_day * working_days_per_year
    
    rice_tonnes_year = paddy_tonnes_year * recovery_rate
    rice_kg_year = rice_tonnes_year * 1000
    
    # By-products (typical for rice mills)
    bran_rate = 0.08  # 8% bran
    husk_rate = 0.20  # 20% husk
    broken_rice_rate = 0.07  # 7% broken rice
    
    bran_tonnes_year = paddy_tonnes_year * bran_rate
    husk_tonnes_year = paddy_tonnes_year * husk_rate
    broken_rice_tonnes_year = paddy_tonnes_year * broken_rice_rate
    
    # ===== REVENUE CALCULATIONS =====
    rice_sale_price = inputs["sale_price_per_kg"]
    bran_sale_price = inputs.get("bran_price_per_kg", 15.0)
    husk_sale_price = inputs.get("husk_price_per_kg", 2.0)
    broken_rice_price = inputs.get("broken_rice_price_per_kg", 20.0)
    
    annual_revenue_rice = rice_kg_year * rice_sale_price
    annual_revenue_bran = bran_tonnes_year * 1000 * bran_sale_price
    annual_revenue_husk = husk_tonnes_year * 1000 * husk_sale_price
    annual_revenue_broken = broken_rice_tonnes_year * 1000 * broken_rice_price
    total_annual_revenue = annual_revenue_rice + annual_revenue_bran + annual_revenue_husk + annual_revenue_broken
    
    # ===== OPERATING COSTS =====
    
    # 1. Raw Material Cost (Paddy procurement)
    paddy_purchase_price = inputs.get("paddy_price_per_quintal", 2000.0)  # per quintal (100kg)
    annual_paddy_cost = (paddy_tonnes_year * 10) * paddy_purchase_price  # Convert tonnes to quintals
    
    # 2. Manpower Costs
    manpower_costs = {
        "Manager": inputs.get("manager_salary", 30000) * 12,
        "Supervisor": inputs.get("supervisor_salary", 20000) * 12,
        "Skilled Workers": inputs.get("skilled_workers_salary", 15000) * inputs.get("num_skilled_workers", 4) * 12,
        "Unskilled Workers": inputs.get("unskilled_workers_salary", 10000) * inputs.get("num_unskilled_workers", 6) * 12,
        "Watchman": inputs.get("watchman_salary", 8000) * 12,
    }
    total_manpower_cost = sum(manpower_costs.values())
    
    # 3. Utilities
    power_cost_per_month = inputs.get("power_cost_monthly", 50000)
    water_cost_per_month = inputs.get("water_cost_monthly", 5000)
    fuel_cost_per_month = inputs.get("fuel_cost_monthly", 10000)
    annual_utilities = (power_cost_per_month + water_cost_per_month + fuel_cost_per_month) * 12
    
    # 4. Maintenance & Repairs
    annual_maintenance = inputs.get("maintenance_percentage", 3.0) / 100.0 * total_fixed_capital
    
    # 5. Insurance
    annual_insurance = inputs.get("insurance_percentage", 1.0) / 100.0 * total_fixed_capital
    
    # 6. Administrative & Other Expenses
    admin_expenses = inputs.get("admin_expenses_monthly", 15000) * 12
    
    # 7. Packing & Transportation
    packing_cost_per_kg = inputs.get("packing_cost_per_kg", 0.50)
    transport_cost_per_kg = inputs.get("transport_cost_per_kg", 1.0)
    annual_packing_cost = rice_kg_year * packing_cost_per_kg
    annual_transport_cost = rice_kg_year * transport_cost_per_kg
    
    # Total Operating Costs
    total_operating_costs = (
        annual_paddy_cost +
        total_manpower_cost +
        annual_utilities +
        annual_maintenance +
        annual_insurance +
        admin_expenses +
        annual_packing_cost +
        annual_transport_cost
    )
    
    # ===== DEPRECIATION =====
    # Straight line depreciation
    building_depreciation_rate = 0.05  # 5% per year
    machinery_depreciation_rate = 0.10  # 10% per year
    other_assets_depreciation_rate = 0.15  # 15% per year
    
    annual_depreciation = (
        capital_costs["Building & Civil Works"] * building_depreciation_rate +
        capital_costs["Plant & Machinery"] * machinery_depreciation_rate +
        capital_costs["Electrical Installation"] * machinery_depreciation_rate +
        (capital_costs["Pre-operative Expenses"] + capital_costs["Miscellaneous Fixed Assets"]) * other_assets_depreciation_rate
    )
    
    # ===== INTEREST ON LOAN =====
    # Simplified: Average interest over the year
    annual_interest = loan_amount * loan_interest_rate
    
    # ===== PROFIT CALCULATIONS =====
    gross_profit = total_annual_revenue - annual_paddy_cost
    ebitda = total_annual_revenue - total_operating_costs
    ebit = ebitda - annual_depreciation
    pbt = ebit - annual_interest  # Profit Before Tax
    
    # Tax calculation
    tax_rate = inputs.get("tax_rate", 30.0) / 100.0
    tax_amount = max(0, pbt * tax_rate)
    pat = pbt - tax_amount  # Profit After Tax
    
    # Cash flow = PAT + Depreciation - Loan Principal Repayment
    principal_repayment = annual_loan_payment - annual_interest if annual_loan_payment > 0 else 0
    annual_cash_flow = pat + annual_depreciation - principal_repayment
    
    # ===== PROFITABILITY RATIOS =====
    gross_margin = (gross_profit / total_annual_revenue * 100) if total_annual_revenue > 0 else 0
    ebitda_margin = (ebitda / total_annual_revenue * 100) if total_annual_revenue > 0 else 0
    net_margin = (pat / total_annual_revenue * 100) if total_annual_revenue > 0 else 0
    
    # ROI and Payback
    roi_percent = (pat / total_project_cost * 100) if total_project_cost > 0 else 0
    payback_years = total_project_cost / annual_cash_flow if annual_cash_flow > 0 else None
    
    # ===== BREAK-EVEN ANALYSIS =====
    # Fixed costs include manpower, utilities (considered semi-fixed), depreciation, interest
    annual_fixed_costs = total_manpower_cost + annual_utilities + annual_maintenance + annual_insurance + admin_expenses + annual_depreciation + annual_interest
    
    # Variable costs include raw materials and packing/transport
    variable_cost_per_unit = (annual_paddy_cost + annual_packing_cost + annual_transport_cost) / rice_kg_year if rice_kg_year > 0 else 0
    
    # Revenue per unit (considering all products)
    revenue_per_kg_rice = total_annual_revenue / rice_kg_year if rice_kg_year > 0 else 0
    
    # Break-even quantity
    contribution_per_unit = revenue_per_kg_rice - variable_cost_per_unit
    breakeven_kg = annual_fixed_costs / contribution_per_unit if contribution_per_unit > 0 else 0
    breakeven_revenue = breakeven_kg * revenue_per_kg_rice
    
    # ===== 5-YEAR PROJECTIONS =====
    annual_growth = inputs.get("annual_growth_rate", 5.0) / 100.0
    years = list(range(1, 6))
    yearly_data = []
    cumulative_cash = -total_project_cost
    loan_balance = loan_amount
    
    for year in years:
        growth_factor = (1 + annual_growth) ** (year - 1)
        
        # Revenue grows
        yr_revenue = total_annual_revenue * growth_factor
        yr_operating_costs = total_operating_costs * growth_factor
        yr_depreciation = annual_depreciation
        
        # Interest reduces as loan is repaid
        if loan_balance > 0:
            yr_interest = loan_balance * loan_interest_rate
            yr_principal = min(annual_loan_payment - yr_interest, loan_balance)
            loan_balance -= yr_principal
        else:
            yr_interest = 0
            yr_principal = 0
        
        yr_ebitda = yr_revenue - yr_operating_costs
        yr_ebit = yr_ebitda - yr_depreciation
        yr_pbt = yr_ebit - yr_interest
        yr_tax = max(0, yr_pbt * tax_rate)
        yr_pat = yr_pbt - yr_tax
        yr_cash_flow = yr_pat + yr_depreciation - yr_principal
        
        cumulative_cash += yr_cash_flow
        
        yearly_data.append({
            "Year": year,
            "Revenue": yr_revenue,
            "Operating Costs": yr_operating_costs,
            "EBITDA": yr_ebitda,
            "Depreciation": yr_depreciation,
            "EBIT": yr_ebit,
            "Interest": yr_interest,
            "PBT": yr_pbt,
            "Tax": yr_tax,
            "PAT": yr_pat,
            "Cash Flow": yr_cash_flow,
            "Cumulative Cash": cumulative_cash,
            "Loan Balance": loan_balance
        })
    
    # Monthly calculations for display
    monthly_revenue = total_annual_revenue / 12
    monthly_operating_costs = total_operating_costs / 12
    monthly_depreciation = annual_depreciation / 12
    monthly_interest = annual_interest / 12
    monthly_profit = pat / 12
    
    return {
        # Capital costs
        "capital_costs": capital_costs,
        "total_fixed_capital": total_fixed_capital,
        "working_capital": working_capital,
        "total_project_cost": total_project_cost,
        
        # Financing
        "loan_amount": loan_amount,
        "equity_amount": equity_amount,
        "loan_interest_rate": loan_interest_rate * 100,
        "emi": emi,
        "annual_loan_payment": annual_loan_payment,
        
        # Production
        "paddy_tonnes_year": paddy_tonnes_year,
        "rice_tonnes_year": rice_tonnes_year,
        "rice_kg_year": rice_kg_year,
        "bran_tonnes_year": bran_tonnes_year,
        "husk_tonnes_year": husk_tonnes_year,
        "broken_rice_tonnes_year": broken_rice_tonnes_year,
        
        # Revenue
        "annual_revenue_rice": annual_revenue_rice,
        "annual_revenue_bran": annual_revenue_bran,
        "annual_revenue_husk": annual_revenue_husk,
        "annual_revenue_broken": annual_revenue_broken,
        "total_annual_revenue": total_annual_revenue,
        
        # Operating costs breakdown
        "annual_paddy_cost": annual_paddy_cost,
        "manpower_costs": manpower_costs,
        "total_manpower_cost": total_manpower_cost,
        "annual_utilities": annual_utilities,
        "annual_maintenance": annual_maintenance,
        "annual_insurance": annual_insurance,
        "admin_expenses": admin_expenses,
        "annual_packing_cost": annual_packing_cost,
        "annual_transport_cost": annual_transport_cost,
        "total_operating_costs": total_operating_costs,
        
        # Profitability
        "annual_depreciation": annual_depreciation,
        "annual_interest": annual_interest,
        "gross_profit": gross_profit,
        "ebitda": ebitda,
        "ebit": ebit,
        "pbt": pbt,
        "tax_amount": tax_amount,
        "pat": pat,
        "annual_cash_flow": annual_cash_flow,
        
        # Ratios
        "gross_margin": gross_margin,
        "ebitda_margin": ebitda_margin,
        "net_margin": net_margin,
        "roi_percent": roi_percent,
        "payback_years": payback_years,
        
        # Break-even
        "breakeven_kg": breakeven_kg,
        "breakeven_revenue": breakeven_revenue,
        "revenue_per_kg_rice": revenue_per_kg_rice,
        "variable_cost_per_unit": variable_cost_per_unit,
        "contribution_per_unit": contribution_per_unit,
        
        # Monthly
        "monthly_revenue": monthly_revenue,
        "monthly_operating_costs": monthly_operating_costs,
        "monthly_depreciation": monthly_depreciation,
        "monthly_interest": monthly_interest,
        "monthly_profit": monthly_profit,
        
        # Projections
        "yearly_data": yearly_data
    }


def create_revenue_breakdown_chart(results, period_divisor=1, period_label="Annual"):
    """Create revenue source breakdown pie chart"""
    labels = ['Rice', 'Bran', 'Husk', 'Broken Rice']
    values = [
        results['annual_revenue_rice'] / period_divisor,
        results['annual_revenue_bran'] / period_divisor,
        results['annual_revenue_husk'] / period_divisor,
        results['annual_revenue_broken'] / period_divisor
    ]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.4,
        marker_colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    )])
    
    fig.update_layout(
        title=f"{period_label} Revenue Breakdown by Product",
        height=400
    )
    
    return fig


def create_cost_breakdown_chart(results, period_divisor=1, period_label="Annual"):
    """Create comprehensive cost breakdown chart"""
    labels = [
        'Raw Material (Paddy)',
        'Manpower',
        'Utilities',
        'Packing',
        'Transport',
        'Maintenance',
        'Insurance',
        'Admin'
    ]
    values = [
        results['annual_paddy_cost'] / period_divisor,
        results['total_manpower_cost'] / period_divisor,
        results['annual_utilities'] / period_divisor,
        results['annual_packing_cost'] / period_divisor,
        results['annual_transport_cost'] / period_divisor,
        results['annual_maintenance'] / period_divisor,
        results['annual_insurance'] / period_divisor,
        results['admin_expenses'] / period_divisor
    ]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.3
    )])
    
    fig.update_layout(
        title=f"{period_label} Operating Cost Breakdown",
        height=400
    )
    
    return fig


def create_profitability_waterfall(results, period_divisor=1, period_label="Annual"):
    """Create waterfall chart showing profit calculation"""
    fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=["relative", "relative", "relative", "relative", "relative", "total"],
        x=["Revenue", "Operating Costs", "Depreciation", "Interest", "Tax", "Net Profit (PAT)"],
        y=[
            results['total_annual_revenue'] / period_divisor,
            -results['total_operating_costs'] / period_divisor,
            -results['annual_depreciation'] / period_divisor,
            -results['annual_interest'] / period_divisor,
            -results['tax_amount'] / period_divisor,
            results['pat'] / period_divisor
        ],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
    ))
    
    fig.update_layout(
        title=f"{period_label} Profitability Waterfall Chart",
        showlegend=False,
        height=400
    )
    
    return fig


def create_projection_chart(yearly_data):
    """Create comprehensive 5-year projection chart"""
    df = pd.DataFrame(yearly_data)
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Revenue, EBITDA & PAT", "Cumulative Cash Flow"),
        vertical_spacing=0.12,
        row_heights=[0.6, 0.4]
    )
    
    # Top chart: Revenue and Profits
    fig.add_trace(
        go.Bar(name="Revenue", x=df["Year"], y=df["Revenue"], marker_color="#1f77b4"),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(name="EBITDA", x=df["Year"], y=df["EBITDA"], marker_color="#ff7f0e"),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(name="PAT", x=df["Year"], y=df["PAT"], 
                   mode='lines+markers', line=dict(color='#2ca02c', width=3)),
        row=1, col=1
    )
    
    # Bottom chart: Cumulative cash flow
    fig.add_trace(
        go.Scatter(
            name="Cumulative Cash",
            x=df["Year"],
            y=df["Cumulative Cash"],
            mode='lines+markers',
            line=dict(color='#9467bd', width=3),
            fill='tozeroy'
        ),
        row=2, col=1
    )
    
    fig.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.5, row=2, col=1)
    
    fig.update_xaxes(title_text="Year", row=2, col=1)
    fig.update_yaxes(title_text="Amount (₹)", row=1, col=1)
    fig.update_yaxes(title_text="Cumulative Cash (₹)", row=2, col=1)
    
    fig.update_layout(
        height=700,
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


def main():
    st.set_page_config(
        page_title="3 TPH Rice Mill - Comprehensive Financial Plan",
        page_icon="🌾",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: 700;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        .sub-header {
            font-size: 1.2rem;
            color: #666;
            text-align: center;
            margin-bottom: 2rem;
        }
        .section-header {
            background-color: #f0f2f6;
            padding: 0.5rem 1rem;
            border-left: 4px solid #1f77b4;
            margin: 1rem 0;
            font-weight: 600;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown('<div class="main-header">🌾 Rice Mill Comprehensive Financial Plan</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">3 TPH Capacity — Complete Project Report</div>', unsafe_allow_html=True)

    # Sidebar with all inputs
    with st.sidebar:
        st.header("📊 Financial Inputs")
        
        with st.expander("💰 Capital Costs", expanded=False):
            land_cost = st.number_input("Land Cost (₹)", value=500000.0, step=50000.0)
            building_cost = st.number_input("Building & Civil Works (₹)", value=1500000.0, step=50000.0)
            machinery_cost = st.number_input("Plant & Machinery (₹)", value=3000000.0, step=50000.0)
            electrical_cost = st.number_input("Electrical Installation (₹)", value=500000.0, step=50000.0)
            preoperative_cost = st.number_input("Pre-operative Expenses (₹)", value=300000.0, step=10000.0)
            misc_fixed_assets = st.number_input("Miscellaneous Fixed Assets (₹)", value=200000.0, step=10000.0)
            working_capital = st.number_input("Working Capital (₹)", value=1000000.0, step=50000.0)
        
        with st.expander("🏦 Financing Details", expanded=False):
            total_proj = land_cost + building_cost + machinery_cost + electrical_cost + preoperative_cost + misc_fixed_assets + working_capital
            loan_amount = st.number_input("Loan Amount (₹)", value=total_proj * 0.7, step=50000.0, max_value=total_proj)
            loan_interest_rate = st.number_input("Interest Rate (%)", value=12.0, step=0.5)
            loan_tenure = st.slider("Loan Tenure (Years)", 5, 15, 10)
        
        with st.expander("🏭 Production Parameters", expanded=True):
            hours_per_day = st.slider("Operating Hours/Day", 1, 24, 8)
            days_per_month = st.slider("Operating Days/Month", 1, 31, 26)
            recovery_rate = st.slider("Rice Recovery Rate (%)", 50, 80, 65)
        
        with st.expander("💵 Pricing", expanded=True):
            sale_price_per_kg = st.number_input("Rice Sale Price (₹/kg)", value=35.0, step=0.5)
            paddy_price_per_quintal = st.number_input("Paddy Purchase Price (₹/quintal)", value=2000.0, step=50.0)
            bran_price_per_kg = st.number_input("Bran Price (₹/kg)", value=15.0, step=0.5)
            husk_price_per_kg = st.number_input("Husk Price (₹/kg)", value=2.0, step=0.1)
            broken_rice_price_per_kg = st.number_input("Broken Rice Price (₹/kg)", value=20.0, step=0.5)
        
        with st.expander("👥 Manpower Costs", expanded=False):
            manager_salary = st.number_input("Manager Salary (₹/month)", value=30000, step=1000)
            supervisor_salary = st.number_input("Supervisor Salary (₹/month)", value=20000, step=1000)
            skilled_workers_salary = st.number_input("Skilled Worker Salary (₹/month)", value=15000, step=1000)
            num_skilled_workers = st.number_input("Number of Skilled Workers", value=4, step=1)
            unskilled_workers_salary = st.number_input("Unskilled Worker Salary (₹/month)", value=10000, step=1000)
            num_unskilled_workers = st.number_input("Number of Unskilled Workers", value=6, step=1)
            watchman_salary = st.number_input("Watchman Salary (₹/month)", value=8000, step=1000)
        
        with st.expander("⚡ Utilities & Other Costs", expanded=False):
            power_cost_monthly = st.number_input("Power Cost (₹/month)", value=50000, step=5000)
            water_cost_monthly = st.number_input("Water Cost (₹/month)", value=5000, step=500)
            fuel_cost_monthly = st.number_input("Fuel Cost (₹/month)", value=10000, step=1000)
            maintenance_percentage = st.number_input("Maintenance (% of Fixed Assets)", value=3.0, step=0.5)
            insurance_percentage = st.number_input("Insurance (% of Fixed Assets)", value=1.0, step=0.1)
            admin_expenses_monthly = st.number_input("Admin Expenses (₹/month)", value=15000, step=1000)
            packing_cost_per_kg = st.number_input("Packing Cost (₹/kg)", value=0.5, step=0.1)
            transport_cost_per_kg = st.number_input("Transport Cost (₹/kg)", value=1.0, step=0.1)
        
        with st.expander("📈 Other Parameters", expanded=False):
            tax_rate = st.number_input("Tax Rate (%)", value=30.0, step=1.0)
            annual_growth_rate = st.slider("Annual Growth Rate (%)", -10.0, 50.0, 5.0, 0.5)
    
    # Prepare inputs
    inputs = {
        "land_cost": land_cost,
        "building_cost": building_cost,
        "machinery_cost": machinery_cost,
        "electrical_cost": electrical_cost,
        "preoperative_cost": preoperative_cost,
        "misc_fixed_assets": misc_fixed_assets,
        "working_capital": working_capital,
        "loan_amount": loan_amount,
        "loan_interest_rate": loan_interest_rate,
        "loan_tenure": loan_tenure,
        "hours_per_day": hours_per_day,
        "days_per_month": days_per_month,
        "recovery_rate": recovery_rate,
        "sale_price_per_kg": sale_price_per_kg,
        "paddy_price_per_quintal": paddy_price_per_quintal,
        "bran_price_per_kg": bran_price_per_kg,
        "husk_price_per_kg": husk_price_per_kg,
        "broken_rice_price_per_kg": broken_rice_price_per_kg,
        "manager_salary": manager_salary,
        "supervisor_salary": supervisor_salary,
        "skilled_workers_salary": skilled_workers_salary,
        "num_skilled_workers": num_skilled_workers,
        "unskilled_workers_salary": unskilled_workers_salary,
        "num_unskilled_workers": num_unskilled_workers,
        "watchman_salary": watchman_salary,
        "power_cost_monthly": power_cost_monthly,
        "water_cost_monthly": water_cost_monthly,
        "fuel_cost_monthly": fuel_cost_monthly,
        "maintenance_percentage": maintenance_percentage,
        "insurance_percentage": insurance_percentage,
        "admin_expenses_monthly": admin_expenses_monthly,
        "packing_cost_per_kg": packing_cost_per_kg,
        "transport_cost_per_kg": transport_cost_per_kg,
        "tax_rate": tax_rate,
        "annual_growth_rate": annual_growth_rate,
    }
    
    # Calculate comprehensive financials
    results = calculate_comprehensive_financials(inputs)
    
    # ===== PROJECT COST SUMMARY =====
    st.markdown("## 💰 Project Cost Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Fixed Capital", format_currency(results['total_fixed_capital']))
    with col2:
        st.metric("Working Capital", format_currency(results['working_capital']))
    with col3:
        st.metric("Total Project Cost", format_currency(results['total_project_cost']))
    with col4:
        debt_equity_ratio = results['loan_amount'] / results['equity_amount'] if results['equity_amount'] > 0 else 0
        st.metric("Debt-Equity Ratio", f"{debt_equity_ratio:.2f}:1")
    
    # Capital cost breakdown table
    with st.expander("📋 Detailed Capital Cost Breakdown", expanded=False):
        capital_df = pd.DataFrame([
            {"Component": k, "Amount (₹)": format_currency(v)} 
            for k, v in results['capital_costs'].items()
        ])
        st.dataframe(capital_df, use_container_width=True, hide_index=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Financing Structure**")
            st.write(f"- Loan Amount: {format_currency(results['loan_amount'])}")
            st.write(f"- Equity/Own Funds: {format_currency(results['equity_amount'])}")
            st.write(f"- Interest Rate: {results['loan_interest_rate']:.1f}%")
            st.write(f"- Tenure: {loan_tenure} years")
        with col2:
            st.markdown("**Loan Repayment**")
            st.write(f"- Monthly EMI: {format_currency(results['emi'])}")
            st.write(f"- Annual Payment: {format_currency(results['annual_loan_payment'])}")
    
    st.markdown("---")
    
    # ===== VIEW SELECTOR =====
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        view_mode = st.radio(
            "📊 Select View Mode:",
            options=["Monthly Summary", "Annual Summary"],
            horizontal=True,
            help="Switch between monthly and annual financial views"
        )
    
    is_monthly = view_mode == "Monthly Summary"
    period_label = "Monthly" if is_monthly else "Annual"
    period_divisor = 12 if is_monthly else 1
    
    st.markdown("---")
    
    # ===== PRODUCTION OVERVIEW =====
    st.markdown(f"## 🏭 Production Overview ({period_label})")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(f"{period_label} Paddy Processed", f"{results['paddy_tonnes_year']/period_divisor:,.1f} tonnes")
    with col2:
        st.metric(f"{period_label} Rice Produced", f"{results['rice_tonnes_year']/period_divisor:,.1f} tonnes")
    with col3:
        st.metric(f"{period_label} Bran", f"{results['bran_tonnes_year']/period_divisor:,.1f} tonnes")
    with col4:
        st.metric(f"{period_label} Husk", f"{results['husk_tonnes_year']/period_divisor:,.1f} tonnes")
    
    st.markdown("---")
    
    # ===== REVENUE & COST ANALYSIS =====
    st.markdown(f"## 📊 Revenue & Cost Analysis ({period_label})")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_revenue_breakdown_chart(results, period_divisor, period_label), use_container_width=True)
        
        st.markdown(f"**{period_label} Revenue Details**")
        revenue_details = pd.DataFrame([
            {"Product": "Rice", "Amount": format_currency(results['annual_revenue_rice']/period_divisor)},
            {"Product": "Bran", "Amount": format_currency(results['annual_revenue_bran']/period_divisor)},
            {"Product": "Husk", "Amount": format_currency(results['annual_revenue_husk']/period_divisor)},
            {"Product": "Broken Rice", "Amount": format_currency(results['annual_revenue_broken']/period_divisor)},
            {"Product": "**Total Revenue**", "Amount": format_currency(results['total_annual_revenue']/period_divisor)},
        ])
        st.dataframe(revenue_details, use_container_width=True, hide_index=True)
    
    with col2:
        st.plotly_chart(create_cost_breakdown_chart(results, period_divisor, period_label), use_container_width=True)
        
        st.markdown(f"**{period_label} Cost Details**")
        cost_details = pd.DataFrame([
            {"Component": "Raw Material (Paddy)", "Amount": format_currency(results['annual_paddy_cost']/period_divisor)},
            {"Component": "Manpower", "Amount": format_currency(results['total_manpower_cost']/period_divisor)},
            {"Component": "Utilities", "Amount": format_currency(results['annual_utilities']/period_divisor)},
            {"Component": "Packing", "Amount": format_currency(results['annual_packing_cost']/period_divisor)},
            {"Component": "Transport", "Amount": format_currency(results['annual_transport_cost']/period_divisor)},
            {"Component": "Maintenance", "Amount": format_currency(results['annual_maintenance']/period_divisor)},
            {"Component": "Insurance", "Amount": format_currency(results['annual_insurance']/period_divisor)},
            {"Component": "Admin", "Amount": format_currency(results['admin_expenses']/period_divisor)},
            {"Component": "**Total Operating Costs**", "Amount": format_currency(results['total_operating_costs']/period_divisor)},
        ])
        st.dataframe(cost_details, use_container_width=True, hide_index=True)
    
    # Manpower breakdown
    with st.expander(f"👥 Detailed Manpower Cost Breakdown ({period_label})"):
        manpower_df = pd.DataFrame([
            {"Position": k, f"{period_label} Cost (₹)": format_currency(v/period_divisor)} 
            for k, v in results['manpower_costs'].items()
        ])
        st.dataframe(manpower_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # ===== PROFITABILITY ANALYSIS =====
    st.markdown(f"## 💹 Profitability Analysis ({period_label})")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Gross Profit", format_currency(results['gross_profit']/period_divisor))
    with col2:
        st.metric("EBITDA", format_currency(results['ebitda']/period_divisor))
    with col3:
        st.metric("EBIT", format_currency(results['ebit']/period_divisor))
    with col4:
        st.metric("PBT", format_currency(results['pbt']/period_divisor))
    with col5:
        st.metric("PAT (Net Profit)", format_currency(results['pat']/period_divisor))
    
    # Profitability waterfall - now shows for both monthly and annual
    st.plotly_chart(create_profitability_waterfall(results, period_divisor, period_label), use_container_width=True)
    
    # Profit & Loss Statement
    with st.expander(f"📄 Detailed Profit & Loss Statement ({period_label})"):
        pl_data = [
            {"Particulars": "Revenue from Operations", "Amount (₹)": format_currency(results['total_annual_revenue']/period_divisor)},
            {"Particulars": "Less: Operating Expenses", "Amount (₹)": format_currency(results['total_operating_costs']/period_divisor)},
            {"Particulars": "EBITDA", "Amount (₹)": format_currency(results['ebitda']/period_divisor)},
            {"Particulars": "Less: Depreciation", "Amount (₹)": format_currency(results['annual_depreciation']/period_divisor)},
            {"Particulars": "EBIT", "Amount (₹)": format_currency(results['ebit']/period_divisor)},
            {"Particulars": "Less: Interest", "Amount (₹)": format_currency(results['annual_interest']/period_divisor)},
            {"Particulars": "Profit Before Tax (PBT)", "Amount (₹)": format_currency(results['pbt']/period_divisor)},
            {"Particulars": "Less: Tax", "Amount (₹)": format_currency(results['tax_amount']/period_divisor)},
            {"Particulars": "Profit After Tax (PAT)", "Amount (₹)": format_currency(results['pat']/period_divisor)},
            {"Particulars": "Add: Depreciation", "Amount (₹)": format_currency(results['annual_depreciation']/period_divisor)},
            {"Particulars": "Less: Loan Principal Repayment", "Amount (₹)": format_currency((results['annual_loan_payment'] - results['annual_interest'])/period_divisor)},
            {"Particulars": "Net Cash Flow", "Amount (₹)": format_currency(results['annual_cash_flow']/period_divisor)},
        ]
        pl_df = pd.DataFrame(pl_data)
        st.dataframe(pl_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # ===== KEY RATIOS & METRICS =====
    st.markdown("## 📈 Key Financial Ratios & Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Profitability Ratios**")
        st.metric("Gross Margin", format_percentage(results['gross_margin']))
        st.metric("EBITDA Margin", format_percentage(results['ebitda_margin']))
        st.metric("Net Profit Margin", format_percentage(results['net_margin']))
    
    with col2:
        st.markdown("**Investment Returns**")
        st.metric("Annual ROI", format_percentage(results['roi_percent']))
        if results['payback_years']:
            st.metric("Payback Period", f"{results['payback_years']:.1f} years")
        else:
            st.metric("Payback Period", "N/A")
    
    with col3:
        st.markdown("**Break-even Analysis**")
        st.metric("Break-even Volume", f"{results['breakeven_kg']:,.0f} kg rice")
        st.metric("Break-even Revenue", format_currency(results['breakeven_revenue']))
        capacity_utilization = (results['breakeven_kg'] / results['rice_kg_year'] * 100) if results['rice_kg_year'] > 0 else 0
        st.metric("Break-even Capacity %", f"{capacity_utilization:.1f}%")
    
    with st.expander("📊 Additional Cost Analytics"):
        st.write(f"**Revenue per kg of Rice (incl. by-products):** {format_currency(results['revenue_per_kg_rice'])}")
        st.write(f"**Variable Cost per kg:** {format_currency(results['variable_cost_per_unit'])}")
        st.write(f"**Contribution per kg:** {format_currency(results['contribution_per_unit'])}")
        st.write(f"**Contribution Margin:** {format_percentage(results['contribution_per_unit']/results['revenue_per_kg_rice']*100 if results['revenue_per_kg_rice'] > 0 else 0)}")
    
    st.markdown("---")
    
    # ===== 5-YEAR PROJECTIONS =====
    st.markdown("## 📅 5-Year Financial Projections")
    
    st.plotly_chart(create_projection_chart(results['yearly_data']), use_container_width=True)
    
    # Detailed projection table
    with st.expander("📋 Detailed 5-Year Projection Table", expanded=True):
        df_proj = pd.DataFrame(results['yearly_data'])
        df_display = df_proj.copy()
        
        for col in ["Revenue", "Operating Costs", "EBITDA", "Depreciation", "EBIT", 
                    "Interest", "PBT", "Tax", "PAT", "Cash Flow", "Cumulative Cash", "Loan Balance"]:
            df_display[col] = df_display[col].apply(lambda x: format_currency(x))
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # Download button
        csv = df_proj.to_csv(index=False)
        st.download_button(
            label="📥 Download 5-Year Projection as CSV",
            data=csv,
            file_name="rice_mill_5year_detailed_projection.csv",
            mime="text/csv",
        )
    
    st.markdown("---")
    
    st.markdown("---")
    
    # ===== INSIGHTS & RECOMMENDATIONS =====
    st.markdown("## 💡 Financial Insights & Recommendations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Project Viability**")
        if results['pat'] > 0:
            st.success(f"✅ **Profitable Project**: Annual PAT of {format_currency(results['pat'])}")
        else:
            st.error(f"❌ **Loss Making**: Annual loss of {format_currency(abs(results['pat']))}")
        
        if results['payback_years'] and results['payback_years'] <= 5:
            st.success(f"✅ **Quick Payback**: {results['payback_years']:.1f} years")
        elif results['payback_years']:
            st.warning(f"⚠️ **Long Payback**: {results['payback_years']:.1f} years")
        
        if results['roi_percent'] > 20:
            st.success(f"✅ **Excellent ROI**: {format_percentage(results['roi_percent'])} per annum")
        elif results['roi_percent'] > 15:
            st.info(f"ℹ️ **Good ROI**: {format_percentage(results['roi_percent'])} per annum")
        elif results['roi_percent'] > 0:
            st.warning(f"⚠️ **Low ROI**: {format_percentage(results['roi_percent'])} per annum")
    
    with col2:
        st.markdown("**Operational Efficiency**")
        if results['net_margin'] > 15:
            st.success(f"✅ **Healthy Profit Margin**: {format_percentage(results['net_margin'])}")
        elif results['net_margin'] > 10:
            st.info(f"ℹ️ **Moderate Margin**: {format_percentage(results['net_margin'])}")
        elif results['net_margin'] > 0:
            st.warning(f"⚠️ **Thin Margin**: {format_percentage(results['net_margin'])}")
        
        capacity_at_breakeven = (results['breakeven_kg'] / results['rice_kg_year'] * 100) if results['rice_kg_year'] > 0 else 0
        if capacity_at_breakeven < 60:
            st.success(f"✅ **Low Break-even Point**: {capacity_at_breakeven:.1f}% capacity")
        elif capacity_at_breakeven < 80:
            st.info(f"ℹ️ **Moderate Break-even**: {capacity_at_breakeven:.1f}% capacity")
        else:
            st.warning(f"⚠️ **High Break-even**: {capacity_at_breakeven:.1f}% capacity")
        
        final_cumulative = results['yearly_data'][-1]['Cumulative Cash']
        if final_cumulative > results['total_project_cost']:
            st.success(f"✅ **Strong Cash Generation**: 5-year cumulative of {format_currency(final_cumulative)}")
        elif final_cumulative > 0:
            st.info(f"ℹ️ **Positive Cash Flow**: 5-year cumulative of {format_currency(final_cumulative)}")
        else:
            st.error(f"❌ **Negative Cash Flow**: 5-year cumulative of {format_currency(final_cumulative)}")


if __name__ == "__main__":
    main()
