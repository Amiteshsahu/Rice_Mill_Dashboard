import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def format_currency(x):
    """Format number as Indian currency with lakhs and crores"""
    if x < 0:
        return f"-{format_currency(abs(x))}"
    
    x = round(x)
    
    if x >= 10000000:  # 1 crore or more
        crores = x / 10000000
        return f"₹ {crores:.2f} Cr"
    elif x >= 100000:  # 1 lakh or more
        lakhs = x / 100000
        return f"₹ {lakhs:.2f} L"
    elif x >= 1000:  # Use thousands with Indian comma system
        s = str(x)
        if len(s) <= 3:
            return f"₹ {s}"
        result = s[-3:]
        s = s[:-3]
        while s:
            if len(s) <= 2:
                result = s + "," + result
                break
            else:
                result = s[-2:] + "," + result
                s = s[:-2]
        return f"₹ {result}"
    else:
        return f"₹ {x:,.0f}"


def format_currency_full(x):
    """Format number as Indian currency with full digits and Indian comma system"""
    if x < 0:
        sign = "-"
        x = abs(x)
    else:
        sign = ""
    
    x = round(x)
    s = str(x)
    
    if len(s) <= 3:
        return f"{sign}₹ {s}"
    
    result = s[-3:]
    s = s[:-3]
    while s:
        if len(s) <= 2:
            result = s + "," + result
            break
        else:
            result = s[-2:] + "," + result
            s = s[:-2]
    
    return f"{sign}₹ {result}"


def format_percentage(x):
    """Format number as percentage"""
    return f"{x:.1f}%"


def get_financial_glossary():
    """Return dictionary of financial terms and their definitions"""
    return {
        "Gross Profit": {
            "short": "Revenue - Operating Costs",
            "definition": "The profit a company makes after deducting the costs associated with making and selling its products or services. It represents the efficiency of production and pricing.",
            "formula": "Gross Profit = Total Revenue - Total Operating Costs",
            "example": "If revenue is ₹10 Cr and operating costs are ₹8 Cr, Gross Profit = ₹2 Cr"
        },
        "EBITDA": {
            "short": "Earnings Before Interest, Tax, Depreciation & Amortization",
            "definition": "A measure of a company's operating performance. It shows how much profit the business generates from its core operations before accounting for capital structure (interest), taxes, and non-cash expenses (depreciation).",
            "formula": "EBITDA = Total Revenue - Operating Costs",
            "example": "EBITDA is used to compare profitability between companies and industries, as it eliminates the effects of financing and accounting decisions.",
            "why_important": "Shows the true operational profitability without considering how the business is financed or taxed."
        },
        "EBIT": {
            "short": "Earnings Before Interest & Tax",
            "definition": "The operating profit after accounting for depreciation. It shows how much profit the business makes from operations before paying interest on loans and taxes.",
            "formula": "EBIT = EBITDA - Depreciation",
            "example": "If EBITDA is ₹1.5 Cr and depreciation is ₹30 L, then EBIT = ₹1.2 Cr",
            "why_important": "Indicates the profitability of core business operations before considering debt servicing and tax obligations."
        },
        "PBT": {
            "short": "Profit Before Tax",
            "definition": "The profit earned by the company after paying all expenses including interest on loans, but before paying income tax to the government.",
            "formula": "PBT = EBIT - Interest on Loans",
            "example": "If EBIT is ₹1.2 Cr and annual interest is ₹20 L, then PBT = ₹1 Cr",
            "why_important": "Shows profitability after all operating and financing costs, before tax obligations."
        },
        "PAT": {
            "short": "Profit After Tax (Net Profit)",
            "definition": "The final profit that belongs to the business owners after paying all expenses, interest, and taxes. This is the 'bottom line' - the actual money the business gets to keep.",
            "formula": "PAT = PBT - Income Tax",
            "example": "If PBT is ₹1 Cr and tax is ₹25 L, then PAT = ₹75 L (this is your actual profit)",
            "why_important": "This is the real profit available for distribution to owners, reinvestment, or debt repayment."
        },
        "Depreciation": {
            "short": "Reduction in asset value over time",
            "definition": "The decrease in value of machinery, equipment, and buildings over time due to wear and tear. It's a non-cash expense that reduces profit on paper but doesn't involve actual cash outflow.",
            "formula": "Annual Depreciation = Asset Cost ÷ Useful Life",
            "example": "If machinery costs ₹50 L with 10-year life, annual depreciation = ₹5 L",
            "why_important": "Reduces taxable income (saving tax) and helps plan for equipment replacement."
        },
        "ROI": {
            "short": "Return on Investment",
            "definition": "A percentage that shows how much profit you earn compared to the total money invested in the project. Higher ROI means better returns.",
            "formula": "ROI = (Annual PAT ÷ Total Project Cost) × 100",
            "example": "If PAT is ₹75 L and project cost is ₹5 Cr, ROI = 15%",
            "why_important": "Helps compare different investment opportunities and decide if the project is worthwhile."
        },
        "Break-even Point": {
            "short": "Zero profit, zero loss point",
            "definition": "The level of sales or production at which total revenue equals total costs. Below this point, you make losses; above it, you make profits.",
            "formula": "Break-even Volume = Fixed Costs ÷ (Sale Price per unit - Variable Cost per unit)",
            "example": "If you need to produce 3,45,000 kg to cover all costs, that's your break-even point",
            "why_important": "Critical for planning - tells you the minimum sales needed to avoid losses."
        },
        "Debt-Equity Ratio": {
            "short": "Loan amount compared to own investment",
            "definition": "A ratio that compares how much you borrowed (debt) versus how much you invested from your own pocket (equity). Shows the financial risk level.",
            "formula": "Debt-Equity Ratio = Total Loan ÷ Own Investment",
            "example": "If loan is ₹4 Cr and equity is ₹1 Cr, ratio = 4:1 (higher risk)",
            "why_important": "Banks prefer lower ratios (2:1 or 3:1) as it shows you have skin in the game."
        },
        "Working Capital": {
            "short": "Money needed for daily operations",
            "definition": "The funds required to manage day-to-day operations like buying raw materials, paying salaries, utilities, etc. It's the cushion to keep business running smoothly.",
            "formula": "Working Capital = 2-3 months of Operating Expenses",
            "example": "If monthly expenses are ₹30 L, working capital needed = ₹60-90 L",
            "why_important": "Without adequate working capital, business can face cash flow problems even if profitable."
        },
        "EMI": {
            "short": "Equated Monthly Installment",
            "definition": "The fixed amount you pay to the bank every month to repay your loan. It includes both principal repayment and interest charges.",
            "formula": "EMI = [P × R × (1+R)^N] ÷ [(1+R)^N - 1]",
            "example": "For ₹40 L loan at 12% for 10 years, EMI ≈ ₹57,350/month",
            "why_important": "Must ensure business generates enough cash flow to comfortably pay EMI every month."
        },
        "Cash Flow": {
            "short": "Actual cash available after all payments",
            "definition": "The net amount of cash moving in and out of business. Positive cash flow means more cash coming in than going out.",
            "formula": "Cash Flow = PAT + Depreciation - Loan Principal Repayment",
            "example": "If PAT is ₹75 L, depreciation ₹35 L, principal payment ₹30 L, Cash Flow = ₹80 L",
            "why_important": "More important than profit for survival - you can be profitable but run out of cash!"
        },
        "Margin": {
            "short": "Profit as a percentage of revenue",
            "definition": "Shows what percentage of revenue becomes profit. Higher margins mean better profitability and pricing power.",
            "formula": "Net Margin = (PAT ÷ Revenue) × 100",
            "example": "If PAT is ₹75 L and revenue is ₹9.75 Cr, margin = 7.7%",
            "why_important": "Industry comparison tool - helps understand if you're priced competitively and operating efficiently."
        },
        "Capacity Utilization": {
            "short": "Percentage of maximum production used",
            "definition": "How much of your mill's maximum production capacity you're actually using. 100% means running at full capacity.",
            "formula": "Capacity Utilization = (Actual Production ÷ Maximum Capacity) × 100",
            "example": "If you produce 4,500 tonnes but can produce 5,000 tonnes, utilization = 90%",
            "why_important": "Higher utilization means better efficiency and lower per-unit costs (spreading fixed costs)."
        }
    }


def format_indian_number(x, decimals=0):
    """Format number with Indian comma system (no currency symbol)"""
    if x < 0:
        return f"-{format_indian_number(abs(x), decimals)}"
    
    if decimals > 0:
        x_formatted = f"{x:.{decimals}f}"
        int_part, dec_part = x_formatted.split('.')
    else:
        int_part = str(int(round(x)))
        dec_part = None
    
    if len(int_part) <= 3:
        result = int_part
    else:
        s = int_part
        result = s[-3:]
        s = s[:-3]
        while s:
            if len(s) <= 2:
                result = s + "," + result
                break
            else:
                result = s[-2:] + "," + result
                s = s[:-2]
    
    if dec_part:
        result = result + "." + dec_part
    
    return result


def generate_ai_insights(results, inputs):
    """Generate AI-powered insights and recommendations based on financial analysis"""
    insights = {
        'critical': [],
        'warnings': [],
        'recommendations': [],
        'positive': []
    }
    
    # Profitability Analysis
    profit_margin = (results['pat'] / results['total_annual_revenue'] * 100) if results['total_annual_revenue'] > 0 else 0
    
    if profit_margin < 5:
        insights['critical'].append({
            'title': 'Critical: Very Low Profit Margin',
            'message': f"Your net profit margin is only {profit_margin:.1f}%. This is concerning for long-term sustainability.",
            'detail': f"**Understanding Net Profit Margin (NPM):**\n\n"
                     f"📊 **Formula:** NPM = (Net Profit After Tax / Total Revenue) × 100\n\n"
                     f"📈 **Your Numbers:**\n"
                     f"- Net Profit (PAT): {format_currency(results['pat'])}\n"
                     f"- Total Revenue: {format_currency(results['total_annual_revenue'])}\n"
                     f"- NPM: {profit_margin:.2f}%\n\n"
                     f"🏭 **Industry Benchmarks:**\n"
                     f"- Minimum Viable: 8-10%\n"
                     f"- Industry Average: 12-15%\n"
                     f"- Top Performers: 18-22%\n\n"
                     f"⚠️ **Why This Matters:**\n"
                     f"A margin below 5% means you're barely covering costs. Any market fluctuation (paddy price increase, power cost rise, or rice price drop) could push you into losses. Rice mills typically need 10%+ margin to handle seasonal variations and maintain operations sustainably.\n\n"
                     f"💰 **Financial Impact:**\n"
                     f"- To reach 10% margin, you need additional profit of {format_currency((0.10 * results['total_annual_revenue']) - results['pat'])}\n"
                     f"- This equals approximately {((0.10 * results['total_annual_revenue']) - results['pat']) / results['rice_kg_year']:.2f} per kg rice price increase\n"
                     f"- Or cost reduction of {((0.10 * results['total_annual_revenue']) - results['pat']) / results['total_annual_revenue'] * 100:.1f}% across operations",
            'action': "**Immediate Actions Required:**\n\n"
                     "1. **Revenue Enhancement (Quick Wins):**\n"
                     "   - Increase rice sale price by ₹2-3/kg through branding\n"
                     "   - Add value: branded packaging can justify 15-20% premium\n"
                     "   - Target retail/direct sales vs wholesale (better margins)\n"
                     "   - Explore organic certification (30-40% price premium)\n\n"
                     "2. **Cost Reduction (Immediate Impact):**\n"
                     "   - Negotiate paddy prices with farmers (contract farming)\n"
                     "   - Optimize power consumption (LED lighting, efficient motors)\n"
                     "   - Reduce wastage in processing\n"
                     "   - Review manpower deployment efficiency\n\n"
                     "3. **Operational Excellence:**\n"
                     "   - Improve recovery rate by 1-2% through better machinery\n"
                     "   - Maximize by-product sales (bran oil, husk briquettes)\n"
                     "   - Reduce downtime through preventive maintenance"
        })
    elif profit_margin < 10:
        insights['warnings'].append({
            'title': 'Low Profit Margin',
            'message': f"Net profit margin of {profit_margin:.1f}% is below industry average (12-15%).",
            'detail': f"**Net Profit Margin Analysis:**\n\n"
                     f"📊 **Your Performance:**\n"
                     f"- Current NPM: {profit_margin:.2f}%\n"
                     f"- Industry Average: 12-15%\n"
                     f"- Gap to Average: {12 - profit_margin:.2f} percentage points\n\n"
                     f"📈 **Current Profitability:**\n"
                     f"- Annual PAT: {format_currency(results['pat'])}\n"
                     f"- Per kg profit: ₹{results['pat'] / results['rice_kg_year']:.2f}\n"
                     f"- Per tonne profit: ₹{results['pat'] / (results['rice_kg_year']/1000):.0f}\n\n"
                     f"🎯 **To Reach 12% Margin:**\n"
                     f"- Target PAT needed: {format_currency(0.12 * results['total_annual_revenue'])}\n"
                     f"- Additional profit required: {format_currency((0.12 * results['total_annual_revenue']) - results['pat'])}\n"
                     f"- This requires {((0.12 * results['total_annual_revenue']) - results['pat']) / results['rice_kg_year']:.2f}/kg improvement\n\n"
                     f"💡 **Competitive Position:**\n"
                     f"While not critical, your margin leaves little buffer for market volatility. Successful rice mills maintain 12-15% margins to absorb seasonal price fluctuations and invest in growth.",
            'action': "**Strategic Improvements:**\n\n"
                     "1. **Premium Product Mix:**\n"
                     "   - Introduce premium basmati/specialty rice (20-30% higher margin)\n"
                     "   - Develop branded retail packs\n"
                     "   - Target institutional clients (hotels, caterers)\n\n"
                     "2. **Cost Optimization:**\n"
                     "   - Benchmark costs against top performers\n"
                     "   - Implement energy audit and efficiency measures\n"
                     "   - Optimize procurement through bulk buying\n\n"
                     "3. **By-Product Monetization:**\n"
                     "   - Maximize bran sales to oil mills\n"
                     "   - Convert husk to fuel briquettes\n"
                     "   - Sell broken rice to breweries/snack makers"
        })
    elif profit_margin > 15:
        insights['positive'].append({
            'title': 'Excellent Profit Margin',
            'message': f"Your {profit_margin:.1f}% profit margin exceeds industry standards!",
            'detail': f"**Outstanding Profitability Performance:**\n\n"
                     f"🌟 **Your Achievement:**\n"
                     f"- Your NPM: {profit_margin:.2f}%\n"
                     f"- Industry Average: 12-15%\n"
                     f"- You're {profit_margin - 13.5:.2f} points above average!\n\n"
                     f"💰 **Financial Excellence:**\n"
                     f"- Annual PAT: {format_currency(results['pat'])}\n"
                     f"- Profit per kg: ₹{results['pat'] / results['rice_kg_year']:.2f}\n"
                     f"- Profit per tonne: ₹{results['pat'] / (results['rice_kg_year']/1000):.0f}\n\n"
                     f"📊 **What This Means:**\n"
                     f"Your margin puts you in the top 20% of rice mills nationally. This indicates excellent operational efficiency, strong pricing power, or superior quality positioning. Such margins provide:\n"
                     f"- Strong buffer against market volatility\n"
                     f"- Capacity to invest in growth\n"
                     f"- Competitive advantage in the market\n\n"
                     f"🎯 **Value Creation:**\n"
                     f"With this margin, you're generating {format_currency(results['pat'] - (0.12 * results['total_annual_revenue']))} more profit than average mills!",
            'action': "**Leverage Your Success:**\n\n"
                     "1. **Strategic Growth:**\n"
                     "   - Reinvest in capacity expansion (6-7 TPH upgrade)\n"
                     "   - Add automated sorting and grading equipment\n"
                     "   - Invest in modern packaging line for retail market\n\n"
                     "2. **Market Leadership:**\n"
                     "   - Build strong brand presence\n"
                     "   - Expand distribution network\n"
                     "   - Consider contract manufacturing for brands\n\n"
                     "3. **Sustainability & Innovation:**\n"
                     "   - Invest in green energy (solar panels)\n"
                     "   - Implement quality certifications (ISO, FSSAI)\n"
                     "   - Develop premium product lines\n\n"
                     "4. **Financial Prudence:**\n"
                     "   - Build contingency reserves (6-12 months operating costs)\n"
                     "   - Consider prepaying high-interest debt\n"
                     "   - Invest excess in liquid funds"
        })
    
    # Break-even Analysis
    breakeven_capacity = (results['breakeven_kg'] / results['rice_kg_year'] * 100) if results['rice_kg_year'] > 0 else 0
    
    if breakeven_capacity > 80:
        insights['critical'].append({
            'title': 'Critical: High Break-even Point',
            'message': f"You need to operate at {breakeven_capacity:.1f}% capacity to break even. Very risky!",
            'detail': f"**Break-Even Analysis - Critical Situation:**\n\n"
                     f"📊 **Break-Even Metrics:**\n"
                     f"- Break-even capacity: {breakeven_capacity:.1f}%\n"
                     f"- Break-even production: {format_indian_number(results['breakeven_kg'])} kg/year\n"
                     f"- Your planned production: {format_indian_number(results['rice_kg_year'])} kg/year\n"
                     f"- Safety margin: Only {100 - breakeven_capacity:.1f}%\n\n"
                     f"⚠️ **Understanding Break-Even:**\n"
                     f"Break-even point is where Total Revenue = Total Costs (you make ₹0 profit). Operating at {breakeven_capacity:.1f}% capacity means:\n"
                     f"- Fixed costs: {format_currency(results['total_operating_costs'] - (results.get('variable_costs', 0)))}/year (must be paid regardless)\n"
                     f"- Variable costs: {format_currency(results.get('variable_costs', results['annual_paddy_cost']))}/year (linked to production)\n"
                     f"- Total revenue at break-even: {format_currency(results['breakeven_kg'] * inputs['sale_price_per_kg'])}\n\n"
                     f"🚨 **Why This is Critical:**\n"
                     f"1. **Market Risk:** Any demand reduction >20% = losses\n"
                     f"2. **Operational Risk:** Even short stoppages hurt profitability\n"
                     f"3. **Price Risk:** Cannot absorb paddy price increases\n"
                     f"4. **Cash Flow Risk:** Little margin to service loan EMIs\n\n"
                     f"📉 **Impact of Capacity Reduction:**\n"
                     f"- At 75% capacity: Loss of ~{format_currency(0.05 * results['total_annual_revenue'])}\n"
                     f"- At 70% capacity: Loss of ~{format_currency(0.10 * results['total_annual_revenue'])}\n"
                     f"- Below 60% capacity: Severe losses, possible default\n\n"
                     f"💡 **Financial Viability:**\n"
                     f"Healthy mills operate at 50-60% break-even. Above 70% is risky; above 80% is not recommended for funding.",
            'action': "**Urgent Restructuring Required:**\n\n"
                     "1. **Reduce Fixed Costs (Immediate):**\n"
                     "   - Negotiate lower EMI with longer tenure (reduces monthly burden)\n"
                     "   - Increase equity to reduce loan amount and interest cost\n"
                     "   - Consider leasing instead of buying some equipment\n"
                     "   - Optimize manpower - cross-train workers\n\n"
                     "2. **Improve Revenue Per Unit:**\n"
                     "   - Increase sale price by ₹3-5/kg minimum\n"
                     "   - Focus on value-added products\n"
                     "   - Secure long-term contracts at guaranteed prices\n\n"
                     "3. **Enhance Capacity Utilization:**\n"
                     "   - Line up customers before starting\n"
                     "   - Consider contract processing for other mills\n"
                     "   - Increase operating hours/days\n\n"
                     "4. **Financial Restructuring:**\n"
                     "   - Extend loan tenure from 10 to 15 years\n"
                     "   - Seek lower interest rate (PSU banks vs private)\n"
                     "   - Consider government subsidy schemes\n\n"
                     "⚠️ **Recommendation:** Delay project until break-even drops below 70%"
        })
    elif breakeven_capacity > 60:
        insights['warnings'].append({
            'title': 'High Break-even Capacity',
            'message': f"Break-even at {breakeven_capacity:.1f}% capacity leaves little room for market fluctuations.",
            'detail': f"**Break-Even Analysis - Caution Advised:**\n\n"
                     f"📊 **Current Break-Even Position:**\n"
                     f"- Break-even capacity: {breakeven_capacity:.1f}%\n"
                     f"- Break-even volume: {format_indian_number(results['breakeven_kg'])} kg/year\n"
                     f"- Safety margin: {100 - breakeven_capacity:.1f}%\n"
                     f"- Monthly break-even: {format_indian_number(results['breakeven_kg'] / 12)} kg\n\n"
                     f"📈 **Cost Structure:**\n"
                     f"- Fixed costs/year: {format_currency(results['total_operating_costs'] * 0.4)}\n"
                     f"- Variable costs/year: {format_currency(results['total_operating_costs'] * 0.6)}\n"
                     f"- Revenue at break-even: {format_currency(results['breakeven_kg'] * inputs['sale_price_per_kg'])}\n\n"
                     f"⚠️ **Risk Assessment:**\n"
                     f"Break-even above 60% indicates moderate risk:\n"
                     f"- Limited flexibility in pricing\n"
                     f"- Vulnerable to seasonal demand variations\n"
                     f"- Restricted ability to handle operational issues\n"
                     f"- Tight cash flow management needed\n\n"
                     f"🎯 **Industry Comparison:**\n"
                     f"- Your break-even: {breakeven_capacity:.1f}%\n"
                     f"- Recommended: 50-60%\n"
                     f"- Industry average: 55-65%\n"
                     f"- Best-in-class: 40-50%\n\n"
                     f"💰 **Profit at Different Capacities:**\n"
                     f"- At 100% capacity: {format_currency(results['pat'])}\n"
                     f"- At 80% capacity: ~{format_currency(results['pat'] * 0.6)}\n"
                     f"- At 70% capacity: ~{format_currency(results['pat'] * 0.3)}\n"
                     f"- Below {breakeven_capacity:.0f}%: Losses",
            'action': "**Risk Mitigation Strategies:**\n\n"
                     "1. **Build Financial Buffer (Critical):**\n"
                     "   - Maintain working capital for 3-4 months (not 2)\n"
                     "   - Create contingency reserve of {format_currency(results['total_operating_costs'] * 0.25)}\n"
                     "   - Keep credit line arranged with bank\n\n"
                     "2. **Secure Demand (Before Launch):**\n"
                     "   - Lock in contracts for at least {breakeven_capacity:.0f}% capacity\n"
                     "   - Sign MoUs with wholesalers/retailers\n"
                     "   - Arrange advance payment terms\n"
                     "   - Diversify customer base (avoid single buyer dependency)\n\n"
                     "3. **Cost Management:**\n"
                     "   - Negotiate paddy prices with contract farming\n"
                     "   - Optimize power costs (solar/time-of-day tariff)\n"
                     "   - Reduce fixed costs where possible\n\n"
                     "4. **Operational Excellence:**\n"
                     "   - Maximize capacity utilization from day 1\n"
                     "   - Implement preventive maintenance\n"
                     "   - Train workforce for maximum efficiency\n\n"
                     "5. **Financial Planning:**\n"
                     "   - Keep personal/promoter reserves for emergencies\n"
                     "   - Avoid aggressive expansion in first 2 years\n"
                     "   - Monitor cash flow weekly, not monthly"
        })
    else:
        insights['positive'].append({
            'title': 'Strong Break-even Position',
            'message': f"Break-even at only {breakeven_capacity:.1f}% capacity provides good safety margin.",
            'detail': f"**Excellent Break-Even Performance:**\n\n"
                     f"🌟 **Your Strong Position:**\n"
                     f"- Break-even capacity: {breakeven_capacity:.1f}%\n"
                     f"- Safety margin: {100 - breakeven_capacity:.1f}%\n"
                     f"- Break-even volume: {format_indian_number(results['breakeven_kg'])} kg/year\n"
                     f"- Profit zone begins at: {breakeven_capacity:.0f}% capacity\n\n"
                     f"📊 **Financial Strength:**\n"
                     f"Your low break-even means:\n"
                     f"- Can be profitable even at {breakeven_capacity:.0f}% capacity\n"
                     f"- Strong buffer against market downturns\n"
                     f"- Flexibility to offer competitive pricing\n"
                     f"- Room to absorb input cost increases\n\n"
                     f"💰 **Profit Potential:**\n"
                     f"- At 100% capacity: {format_currency(results['pat'])}\n"
                     f"- At 80% capacity: ~{format_currency(results['pat'] * 0.8)}\n"
                     f"- At 70% capacity: ~{format_currency(results['pat'] * 0.65)}\n"
                     f"- Even at {breakeven_capacity:.0f}%: Break-even (no loss)\n\n"
                     f"🎯 **Competitive Advantage:**\n"
                     f"Your {breakeven_capacity:.1f}% break-even vs industry average 60-65% gives you:\n"
                     f"- Pricing power in the market\n"
                     f"- Ability to undercut competitors if needed\n"
                     f"- Security during seasonal slowdowns\n"
                     f"- Confidence for lenders/investors\n\n"
                     f"📈 **What Makes This Possible:**\n"
                     f"- Efficient cost structure\n"
                     f"- Good revenue per kg\n"
                     f"- Balanced fixed vs variable costs\n"
                     f"- Optimized financing terms",
            'action': "**Maximize Your Advantage:**\n\n"
                     "1. **Market Strategy:**\n"
                     "   - Use pricing flexibility to capture market share\n"
                     "   - Can offer volume discounts to secure large orders\n"
                     "   - Build premium brand without fear of losses\n\n"
                     "2. **Growth Opportunities:**\n"
                     "   - Strong foundation for capacity expansion\n"
                     "   - Can add value-added product lines\n"
                     "   - Consider backward integration (paddy farming)\n\n"
                     "3. **Financial Optimization:**\n"
                     "   - Use free cash flow for growth initiatives\n"
                     "   - Build reserves for future opportunities\n"
                     "   - Could increase automation investment\n\n"
                     "4. **Risk Management:**\n"
                     "   - Even with your buffer, maintain 2-3 month working capital\n"
                     "   - Don't become complacent - monitor costs monthly\n"
                     "   - Keep efficiency improvement as ongoing goal"
        })
    
    # Debt-Equity Ratio Analysis
    debt_equity_ratio = results['loan_amount'] / results['equity_amount'] if results['equity_amount'] > 0 else float('inf')
    
    if debt_equity_ratio > 3:
        insights['warnings'].append({
            'title': 'High Debt Burden',
            'message': f"Debt-Equity ratio of {debt_equity_ratio:.2f}:1 is quite high.",
            'detail': f"**Debt-Equity Ratio Analysis:**\n\n"
                     f"📊 **Your Capital Structure:**\n"
                     f"- Total Project Cost: {format_currency(results['total_project_cost'])}\n"
                     f"- Loan (Debt): {format_currency(results['loan_amount'])} ({results['loan_amount']/results['total_project_cost']*100:.1f}%)\n"
                     f"- Equity: {format_currency(results['equity_amount'])} ({results['equity_amount']/results['total_project_cost']*100:.1f}%)\n"
                     f"- D/E Ratio: {debt_equity_ratio:.2f}:1\n\n"
                     f"📈 **Understanding D/E Ratio:**\n"
                     f"This ratio shows how much you're borrowing for every rupee of your own money. Your ratio of {debt_equity_ratio:.2f}:1 means:\n"
                     f"- For every ₹1 of equity, you have ₹{debt_equity_ratio:.2f} of debt\n"
                     f"- Debt is {debt_equity_ratio * 100:.0f}% of equity\n"
                     f"- High leverage = high risk but potentially high returns\n\n"
                     f"⚠️ **Risks of High Leverage:**\n"
                     f"1. **Interest Burden:** Annual interest = {format_currency(results['loan_amount'] * inputs.get('loan_interest_rate', 12)/100)}\n"
                     f"2. **EMI Obligation:** Monthly EMI = {format_currency(results['emi'])}\n"
                     f"3. **Cash Flow Pressure:** Must service debt regardless of profits\n"
                     f"4. **Bank Scrutiny:** Lenders may flag ratio >3 as high risk\n"
                     f"5. **Limited Flexibility:** Difficult to raise more funds\n\n"
                     f"🏦 **Industry Standards:**\n"
                     f"- Your ratio: {debt_equity_ratio:.2f}:1\n"
                     f"- Ideal range: 1.5:1 to 2.5:1\n"
                     f"- Maximum acceptable: 3:1\n"
                     f"- Your deviation: {debt_equity_ratio - 2.5:.2f} points above recommended\n\n"
                     f"💰 **Impact on Returns:**\n"
                     f"While high debt increases risk, ROE (Return on Equity) = {(results['pat'] / results['equity_amount'] * 100):.1f}% is boosted by leverage.",
            'action': "**De-leveraging Strategies:**\n\n"
                     "1. **Increase Equity (Recommended):**\n"
                     f"   - Bring D/E to 2:1 by adding equity of {format_currency((results['loan_amount']/2) - results['equity_amount'])}\n"
                     "   - Consider bringing in partner/investor\n"
                     "   - Explore promoter's additional contribution\n\n"
                     "2. **Reduce Project Cost:**\n"
                     "   - Phase implementation (start smaller, expand later)\n"
                     "   - Lease equipment instead of buying\n"
                     "   - Buy refurbished machinery where feasible\n\n"
                     "3. **Alternate Financing:**\n"
                     "   - Apply for PMFME (Prime Minister Formalisation of Micro food processing Enterprises) subsidy\n"
                     "   - Check state government food processing schemes\n"
                     "   - Explore NABARD financing (better terms)\n\n"
                     "4. **If Proceeding as-is:**\n"
                     "   - Maintain higher working capital reserve\n"
                     "   - Secure advance customer payments\n"
                     "   - Have personal financial backup for 6 months EMI"
        })
    elif debt_equity_ratio < 1:
        insights['recommendations'].append({
            'title': 'Conservative Financing',
            'message': f"Debt-Equity ratio of {debt_equity_ratio:.2f}:1 is very conservative.",
            'detail': f"**Conservative Capital Structure Analysis:**\n\n"
                     f"📊 **Your Financing:**\n"
                     f"- Total Project: {format_currency(results['total_project_cost'])}\n"
                     f"- Equity: {format_currency(results['equity_amount'])} ({results['equity_amount']/results['total_project_cost']*100:.1f}%)\n"
                     f"- Loan: {format_currency(results['loan_amount'])} ({results['loan_amount']/results['total_project_cost']*100:.1f}%)\n"
                     f"- D/E Ratio: {debt_equity_ratio:.2f}:1 (Equity-heavy)\n\n"
                     f"💡 **What This Means:**\n"
                     f"You're using more of your own money than borrowed funds. This means:\n"
                     f"- Very low financial risk\n"
                     f"- Lower interest payments\n"
                     f"- Easy loan approval\n"
                     f"- But: Potentially lower ROE\n\n"
                     f"📈 **Return on Equity Impact:**\n"
                     f"- Current ROE: {(results['pat'] / results['equity_amount'] * 100):.1f}%\n"
                     f"- With 2:1 D/E ratio, ROE could be: ~{(results['pat'] / (results['equity_amount']*0.6) * 100):.1f}%\n"
                     f"- Opportunity cost of blocking extra capital\n\n"
                     f"🎯 **Industry Practice:**\n"
                     f"- Your ratio: {debt_equity_ratio:.2f}:1\n"
                     f"- Typical ratio: 1.5:1 to 2.5:1\n"
                     f"- Banks often fund 60-75% (1.5:1 to 3:1 D/E)\n\n"
                     f"💰 **Financial Optimization:**\n"
                     f"You have {format_currency(results['equity_amount'] - (results['total_project_cost']/2))} excess equity that could be:\n"
                     f"- Freed for other investments\n"
                     f"- Used for working capital optimization\n"
                     f"- Deployed in expansion later",
            'action': "**Optimize Capital Structure:**\n\n"
                     "1. **Leverage Opportunity (Optional):**\n"
                     f"   - Could increase loan to {format_currency(results['total_project_cost'] * 0.65)} (2:1 D/E)\n"
                     f"   - Would free up equity: {format_currency(results['equity_amount'] - (results['total_project_cost'] * 0.35))}\n"
                     "   - At 12% interest, cost is tax-deductible\n\n"
                     "2. **Benefits of Maintaining Conservative Approach:**\n"
                     "   - Peace of mind - no debt stress\n"
                     "   - Flexibility in operations\n"
                     "   - Can take risks in market strategy\n"
                     "   - Easy to get additional credit if needed\n\n"
                     "3. **Strategic Deployment:**\n"
                     "   - Keep excess funds in liquid investments\n"
                     "   - Plan for capacity expansion with available equity\n"
                     "   - Use freed capital for marketing/branding\n\n"
                     "4. **Best Practice:**\n"
                     "   - If comfortable with current structure, maintain it\n"
                     "   - If want to optimize ROE, consider moderate increase in debt\n"
                     "   - Assess tax benefits of interest vs equity returns"
        })
    else:
        insights['positive'].append({
            'title': 'Balanced Financing',
            'message': f"Debt-Equity ratio of {debt_equity_ratio:.2f}:1 is well-balanced.",
            'detail': f"**Optimal Capital Structure:**\n\n"
                     f"🌟 **Your Balanced Financing:**\n"
                     f"- Total Project: {format_currency(results['total_project_cost'])}\n"
                     f"- Equity: {format_currency(results['equity_amount'])} ({results['equity_amount']/results['total_project_cost']*100:.1f}%)\n"
                     f"- Loan: {format_currency(results['loan_amount'])} ({results['loan_amount']/results['total_project_cost']*100:.1f}%)\n"
                     f"- D/E Ratio: {debt_equity_ratio:.2f}:1 ✓ Optimal\n\n"
                     f"📊 **Why This is Ideal:**\n"
                     f"Your ratio falls within the sweet spot (1:1 to 2.5:1), which means:\n"
                     f"- Moderate financial risk\n"
                     f"- Good leverage for ROE\n"
                     f"- Acceptable to all lenders\n"
                     f"- Tax benefits from interest\n"
                     f"- Preserves equity for emergencies\n\n"
                     f"💰 **Financial Efficiency:**\n"
                     f"- ROE: {(results['pat'] / results['equity_amount'] * 100):.1f}%\n"
                     f"- Interest cost: {format_currency(results['loan_amount'] * inputs.get('loan_interest_rate', 12)/100)}/year\n"
                     f"- Tax shield on interest: ~{format_currency(results['loan_amount'] * inputs.get('loan_interest_rate', 12)/100 * 0.25)}\n"
                     f"- Net interest cost: {format_currency(results['loan_amount'] * inputs.get('loan_interest_rate', 12)/100 * 0.75)}/year\n\n"
                     f"🎯 **Industry Comparison:**\n"
                     f"- Your D/E: {debt_equity_ratio:.2f}:1\n"
                     f"- Industry range: 1.5:1 to 2.5:1\n"
                     f"- Your position: Right in the middle ✓\n"
                     f"- Lender preference: Yes ✓\n\n"
                     f"📈 **Strategic Advantage:**\n"
                     f"This structure gives you:\n"
                     f"- Room to borrow more if needed\n"
                     f"- Strong credit profile\n"
                     f"- Flexibility for expansion",
            'action': "**Maintain & Leverage This Strength:**\n\n"
                     "1. **Preserve the Balance:**\n"
                     "   - Don't disturb this optimal structure\n"
                     "   - Future expansions: maintain similar ratio\n"
                     "   - Regular principal payments improve ratio over time\n\n"
                     "2. **Use Credit Wisely:**\n"
                     "   - Your strong D/E opens doors for:\n"
                     "     * Working capital limits\n"
                     "     * Equipment upgrade loans\n"
                     "     * Expansion financing\n"
                     "   - Banks will view you favorably\n\n"
                     "3. **Optimize Tax Benefits:**\n"
                     "   - Interest paid is tax-deductible\n"
                     f"   - Annual tax saving: ~{format_currency(results['loan_amount'] * inputs.get('loan_interest_rate', 12)/100 * 0.25)}\n"
                     "   - Effective interest rate post-tax: lower\n\n"
                     "4. **Financial Discipline:**\n"
                     "   - Make EMI payments on time (builds credit)\n"
                     "   - Consider prepayment in years 4-5 when cash flows improve\n"
                     "   - Keep equity buffer for opportunities"
        })
    
    # Cash Flow Analysis
    annual_cash_flow = results['annual_cash_flow']
    monthly_cash_flow = annual_cash_flow / 12
    
    if annual_cash_flow < 0:
        insights['critical'].append({
            'title': 'Negative Cash Flow',
            'message': f"Annual cash flow is negative at {format_currency(annual_cash_flow)}.",
            'detail': f"**Critical Cash Flow Problem:**\n\n"
                     f"⚠️ **Your Cash Flow Situation:**\n"
                     f"- Annual Cash Flow: {format_currency(annual_cash_flow)} (NEGATIVE)\n"
                     f"- Monthly Average: {format_currency(monthly_cash_flow)}\n"
                     f"- Monthly EMI: {format_currency(results['emi'])}\n"
                     f"- Monthly Deficit: {format_currency(monthly_cash_flow - results['emi'])}\n\n"
                     f"📊 **Understanding the Problem:**\n"
                     f"Cash Flow = PAT + Depreciation + Interest - EMI Principal\n"
                     f"- Your PAT: {format_currency(results['pat'])}\n"
                     f"- Add: Depreciation: {format_currency(results.get('depreciation', 0))}\n"
                     f"- Less: Loan Principal: {format_currency(results['emi'] * 12 - results['loan_amount'] * inputs.get('loan_interest_rate', 12)/100)}\n"
                     f"= Net Cash Flow: {format_currency(annual_cash_flow)}\n\n"
                     f"🚨 **Why This is Critical:**\n"
                     f"Negative cash flow means you're spending more cash than you're generating. You'll need to:\n"
                     f"1. Use working capital every month\n"
                     f"2. Deplete reserves quickly\n"
                     f"3. Risk EMI defaults\n"
                     f"4. Cannot invest in growth\n\n"
                     f"💰 **12-Month Cash Projection:**\n"
                     f"- Working capital at start: {format_currency(results['working_capital'])}\n"
                     f"- Monthly burn: {format_currency(abs(monthly_cash_flow))}\n"
                     f"- Reserves depleted in: {results['working_capital'] / abs(monthly_cash_flow):.1f} months\n"
                     f"- Additional capital needed: {format_currency(abs(annual_cash_flow))}",
            'action': "**Emergency Actions Required:**\n\n"
                     "1. **Restructure Loan (Urgent):**\n"
                     f"   - Extend tenure from {inputs.get('loan_tenure', 10)} to 15 years\n"
                     "   - This reduces EMI and improves cash flow\n"
                     f"   - New EMI will be ~{format_currency(results['emi'] * 0.75)}\n"
                     f"   - Cash flow improvement: {format_currency((results['emi'] - results['emi'] * 0.75) * 12)}/year\n\n"
                     "2. **Increase Working Capital:**\n"
                     f"   - Current: {format_currency(results['working_capital'])}\n"
                     f"   - Recommended: {format_currency(results['working_capital'] + abs(annual_cash_flow) * 2)}\n"
                     "   - Covers 24 months of deficit\n\n"
                     "3. **Improve Profitability Immediately:**\n"
                     "   - Must increase PAT by at least {format_currency(abs(annual_cash_flow))}\n"
                     "   - Through price increase or cost reduction\n\n"
                     "4. **Alternative: Delay Project:**\n"
                     "   - Reconsider project viability\n"
                     "   - Rework numbers until cash flow positive\n"
                     "   - Secure advance payments from customers"
        })
    elif monthly_cash_flow < results['emi']:
        insights['warnings'].append({
            'title': 'Tight Cash Flow',
            'message': "Monthly cash flow is less than EMI payment. Working capital may be strained.",
            'detail': f"**Cash Flow Pressure Analysis:**\n\n"
                     f"📊 **Your Monthly Cash Position:**\n"
                     f"- Monthly Cash Flow: {format_currency(monthly_cash_flow)}\n"
                     f"- Monthly EMI: {format_currency(results['emi'])}\n"
                     f"- Monthly Gap: {format_currency(monthly_cash_flow - results['emi'])}\n"
                     f"- Annual Impact: {format_currency((monthly_cash_flow - results['emi']) * 12)}\n\n"
                     f"📈 **Annual Cash Flow Breakdown:**\n"
                     f"- PAT (Net Profit): {format_currency(results['pat'])}\n"
                     f"- Add: Depreciation (non-cash): {format_currency(results.get('depreciation', 0))}\n"
                     f"- Less: Loan Principal Payment: {format_currency((results['emi'] * 12) - (results['loan_amount'] * inputs.get('loan_interest_rate', 12)/100))}\n"
                     f"- Net Annual Cash Flow: {format_currency(annual_cash_flow)}\n\n"
                     f"⚠️ **The Challenge:**\n"
                     f"While annual cash flow is positive ({format_currency(annual_cash_flow)}), your monthly EMI exceeds monthly cash generation. This means:\n"
                     f"- Need to dip into working capital some months\n"
                     f"- Seasonal variations can cause cash crunches\n"
                     f"- Limited room for unexpected expenses\n\n"
                     f"💡 **Working Capital Runway:**\n"
                     f"- Available working capital: {format_currency(results['working_capital'])}\n"
                     f"- Monthly strain: {format_currency(results['emi'] - monthly_cash_flow)}\n"
                     f"- Buffer lasts: {results['working_capital'] / (results['emi'] - monthly_cash_flow):.1f} months",
            'action': "**Cash Management Strategies:**\n\n"
                     "1. **Optimize Working Capital (Essential):**\n"
                     f"   - Increase from {format_currency(results['working_capital'])} to {format_currency(results['working_capital'] * 1.5)}\n"
                     "   - Provides 50% more buffer\n"
                     "   - Covers 3-4 months of operations comfortably\n\n"
                     "2. **Improve Payment Terms:**\n"
                     "   - Negotiate 15-day advance from customers\n"
                     "   - Request 30-day credit from paddy suppliers\n"
                     "   - This improves cash cycle by 45 days\n\n"
                     "3. **Consider EMI Restructuring:**\n"
                     "   - Step-up EMI: Lower for first 2 years\n"
                     "   - Moratorium on principal for 6 months\n"
                     "   - Seasonal EMI structure (lower in lean months)\n\n"
                     "4. **Revenue Acceleration:**\n"
                     "   - Offer small discount for advance payment\n"
                     "   - Reduce credit period from 30 to 15 days\n"
                     "   - Diversify to retail (immediate cash)\n\n"
                     "5. **Monitor Closely:**\n"
                     "   - Track cash position daily\n"
                     "   - Maintain cash reserve for EMI\n"
                     "   - Setup cash flow alerts"
        })
    else:
        insights['positive'].append({
            'title': 'Healthy Cash Flow',
            'message': f"Positive annual cash flow of {format_currency(annual_cash_flow)}.",
            'detail': f"**Strong Cash Flow Position:**\n\n"
                     f"💰 **Your Cash Generation:**\n"
                     f"- Annual Cash Flow: {format_currency(annual_cash_flow)} (POSITIVE)\n"
                     f"- Monthly Average: {format_currency(monthly_cash_flow)}\n"
                     f"- Monthly EMI: {format_currency(results['emi'])}\n"
                     f"- Monthly Surplus: {format_currency(monthly_cash_flow - results['emi'])}\n\n"
                     f"📊 **Cash Flow Composition:**\n"
                     f"- PAT (Net Profit): {format_currency(results['pat'])}\n"
                     f"- Add: Depreciation: {format_currency(results.get('depreciation', 0))}\n"
                     f"- Less: Principal Payment: {format_currency((results['emi'] * 12) - (results['loan_amount'] * inputs.get('loan_interest_rate', 12)/100))}\n"
                     f"- Net Cash Flow: {format_currency(annual_cash_flow)}\n\n"
                     f"🌟 **Why This Matters:**\n"
                     f"Positive cash flow means:\n"
                     f"- Can comfortably service debt\n"
                     f"- Generate {format_currency(monthly_cash_flow - results['emi'])}/month surplus\n"
                     f"- Build reserves for growth\n"
                     f"- Handle unexpected expenses\n"
                     f"- No working capital strain\n\n"
                     f"📈 **Annual Accumulation:**\n"
                     f"After all expenses and EMI:\n"
                     f"- Year 1 surplus: {format_currency(annual_cash_flow)}\n"
                     f"- Year 2 accumulated: {format_currency(annual_cash_flow * 2)}\n"
                     f"- Year 3 accumulated: {format_currency(annual_cash_flow * 3)}\n"
                     f"- 5-Year total: {format_currency(annual_cash_flow * 5)}\n\n"
                     f"🎯 **Cash Flow Coverage Ratio:**\n"
                     f"Your ratio: {(monthly_cash_flow / results['emi']):.2f}x\n"
                     f"(Healthy is >1.2x, Excellent is >1.5x)",
            'action': "**Optimize Your Strong Cash Position:**\n\n"
                     "1. **Strategic Reserves:**\n"
                     f"   - Build emergency fund: {format_currency(results['total_operating_costs'] / 2)}\n"
                     "   - Covers 6 months operations\n"
                     "   - Keep in liquid funds earning 6-7%\n\n"
                     "2. **Growth Investment:**\n"
                     f"   - Surplus in 3 years: {format_currency(annual_cash_flow * 3)}\n"
                     "   - Enough for capacity expansion\n"
                     "   - Or technology upgrades\n"
                     "   - Or market expansion\n\n"
                     "3. **Debt Management:**\n"
                     "   - Consider prepayment after year 3\n"
                     "   - Reduces interest burden\n"
                     f"   - Save up to {format_currency(results['loan_amount'] * 0.12 * 3)} in interest\n\n"
                     "4. **Working Capital Optimization:**\n"
                     "   - Excess cash can reduce working capital needs\n"
                     "   - Invest in income-generating assets\n"
                     "   - Provide trade credit to customers\n\n"
                     "5. **Distribution Strategy:**\n"
                     "   - Year 1-2: Retain all cash (build reserves)\n"
                     "   - Year 3+: Can consider dividend to promoters\n"
                     "   - Maintain 2:1 retention vs distribution ratio"
        })
    
    # Working Capital Analysis
    working_capital_months = (results['working_capital'] / results['total_operating_costs'] * 12) if results['total_operating_costs'] > 0 else 0
    
    if working_capital_months < 1:
        insights['warnings'].append({
            'title': 'Insufficient Working Capital',
            'message': f"Working capital covers only {working_capital_months:.1f} months of operations.",
            'action': "Increase working capital to at least 2-3 months of operating expenses for safety."
        })
    elif working_capital_months > 4:
        insights['recommendations'].append({
            'title': 'Excess Working Capital',
            'message': f"Working capital covers {working_capital_months:.1f} months - may be excessive.",
            'action': "Consider investing excess funds in short-term instruments or reducing initial capital."
        })
    
    # Recovery Rate Analysis
    recovery_rate = inputs['recovery_rate']
    
    if recovery_rate < 62:
        insights['warnings'].append({
            'title': 'Below Average Recovery Rate',
            'message': f"Recovery rate of {recovery_rate}% is below industry standard (65-68%).",
            'action': "Invest in better machinery, training, or quality paddy procurement to improve recovery."
        })
    elif recovery_rate > 68:
        insights['positive'].append({
            'title': 'Excellent Recovery Rate',
            'message': f"Recovery rate of {recovery_rate}% is excellent!",
            'action': "This competitive advantage should be maintained through regular maintenance and quality control."
        })
    
    # Operating Hours Analysis
    hours_per_day = inputs['hours_per_day']
    
    if hours_per_day < 8:
        insights['recommendations'].append({
            'title': 'Underutilized Capacity',
            'message': f"Operating only {hours_per_day} hours/day means unused capacity.",
            'action': "Consider increasing operating hours to spread fixed costs and improve profitability."
        })
    elif hours_per_day > 16:
        insights['warnings'].append({
            'title': 'Intensive Operations',
            'message': f"Operating {hours_per_day} hours/day may lead to higher maintenance costs.",
            'action': "Ensure adequate maintenance budget and schedule regular equipment inspections."
        })
    
    # ROI Analysis (5-year perspective)
    total_5yr_profit = sum([year['PAT'] for year in results['yearly_data']])
    roi_5yr = (total_5yr_profit / results['total_project_cost'] * 100) if results['total_project_cost'] > 0 else 0
    
    if roi_5yr < 50:
        insights['warnings'].append({
            'title': 'Low 5-Year ROI',
            'message': f"5-year ROI of {roi_5yr:.1f}% is below expectations (typically 80-120%).",
            'detail': f"**Return on Investment Analysis:**\n\n"
                     f"📊 **Your ROI Performance:**\n"
                     f"- 5-Year Total PAT: {format_currency(total_5yr_profit)}\n"
                     f"- Total Investment: {format_currency(results['total_project_cost'])}\n"
                     f"- 5-Year ROI: {roi_5yr:.1f}%\n"
                     f"- Annual Average ROI: {roi_5yr/5:.1f}%\n\n"
                     f"📈 **ROI Calculation:**\n"
                     f"ROI = (Total Profit / Total Investment) × 100\n"
                     f"ROI = ({format_currency(total_5yr_profit)} / {format_currency(results['total_project_cost'])}) × 100\n"
                     f"ROI = {roi_5yr:.1f}%\n\n"
                     f"⚠️ **Industry Comparison:**\n"
                     f"- Your 5-yr ROI: {roi_5yr:.1f}%\n"
                     f"- Expected range: 80-120%\n"
                     f"- Gap: {80 - roi_5yr:.1f} percentage points below minimum\n"
                     f"- Minimum acceptable: 60%\n\n"
                     f"💰 **Year-wise Profit Breakdown:**\n"
                     + "\n".join([f"- Year {i+1}: {format_currency(year['PAT'])}" for i, year in enumerate(results['yearly_data'])]) + "\n\n"
                     f"🎯 **To Achieve 80% ROI:**\n"
                     f"- Total profit needed: {format_currency(results['total_project_cost'] * 0.80)}\n"
                     f"- Current projection: {format_currency(total_5yr_profit)}\n"
                     f"- Gap: {format_currency((results['total_project_cost'] * 0.80) - total_5yr_profit)}\n"
                     f"- Requires {((results['total_project_cost'] * 0.80) - total_5yr_profit) / 5 / results['rice_kg_year']:.2f}/kg improvement",
            'action': "**Improve ROI Strategies:**\n\n"
                     "1. **Revenue Enhancement:**\n"
                     "   - Increase sale price by ₹2-3/kg\n"
                     f"   - Impact: Additional {format_currency(results['rice_kg_year'] * 2.5 * 5)} over 5 years\n"
                     "   - Or improve capacity utilization by 10%\n\n"
                     "2. **Cost Reduction:**\n"
                     "   - Reduce operating costs by 5-7%\n"
                     f"   - Saves {format_currency(results['total_operating_costs'] * 0.06 * 5)} over 5 years\n"
                     "   - Focus on power, paddy procurement costs\n\n"
                     "3. **Financing Optimization:**\n"
                     "   - Lower interest rate by 1-2%\n"
                     "   - Longer tenure reduces annual burden\n"
                     "   - Improves profitability significantly\n\n"
                     "4. **Operational Excellence:**\n"
                     "   - Increase recovery rate by 1%\n"
                     "   - Better by-product monetization\n"
                     "   - Reduce wastage and downtime\n\n"
                     "5. **Strategic Review:**\n"
                     "   - If ROI stays below 60%, reconsider project\n"
                     "   - Compare with alternative investments\n"
                     "   - Fixed deposits give 7-8% with zero risk"
        })
    elif roi_5yr > 100:
        insights['positive'].append({
            'title': 'Strong 5-Year ROI',
            'message': f"5-year ROI of {roi_5yr:.1f}% indicates excellent returns!",
            'detail': f"**Outstanding ROI Performance:**\n\n"
                     f"🌟 **Your Investment Returns:**\n"
                     f"- Total Investment: {format_currency(results['total_project_cost'])}\n"
                     f"- 5-Year PAT: {format_currency(total_5yr_profit)}\n"
                     f"- 5-Year ROI: {roi_5yr:.1f}%\n"
                     f"- Annual Average ROI: {roi_5yr/5:.1f}%\n\n"
                     f"📊 **What This Means:**\n"
                     f"Your {roi_5yr:.1f}% ROI means:\n"
                     f"- You'll earn {format_currency(total_5yr_profit)} profit on {format_currency(results['total_project_cost'])} investment\n"
                     f"- More than doubling your money in 5 years!\n"
                     f"- Average annual return: {roi_5yr/5:.1f}% (vs FD ~7%)\n"
                     f"- Exceptional business opportunity\n\n"
                     f"💰 **Year-wise Profit Growth:**\n"
                     + "\n".join([f"- Year {i+1}: {format_currency(year['PAT'])} (Cumulative: {format_currency(sum([results['yearly_data'][j]['PAT'] for j in range(i+1)]))})" for i, year in enumerate(results['yearly_data'])]) + "\n\n"
                     f"🎯 **Comparison with Alternatives:**\n"
                     f"If you invested {format_currency(results['total_project_cost'])} elsewhere:\n"
                     f"- Fixed Deposit @7%: {format_currency(results['total_project_cost'] * 0.07 * 5)}\n"
                     f"- Stock Market @12%: {format_currency(results['total_project_cost'] * 0.12 * 5)}\n"
                     f"- Your Rice Mill: {format_currency(total_5yr_profit)}\n"
                     f"- Your advantage: {format_currency(total_5yr_profit - (results['total_project_cost'] * 0.12 * 5))} more than stocks!\n\n"
                     f"📈 **ROE (Return on Equity):**\n"
                     f"Even better news - ROE focuses on your equity:\n"
                     f"- Your equity: {format_currency(results['equity_amount'])}\n"
                     f"- 5-Year profit: {format_currency(total_5yr_profit)}\n"
                     f"- ROE: {(total_5yr_profit / results['equity_amount'] * 100):.1f}%!",
            'action': "**Maximize This Exceptional Opportunity:**\n\n"
                     "1. **Scale Up Strategy:**\n"
                     f"   - With such strong ROI, consider phased expansion\n"
                     f"   - Year 3-4: Add 2-3 TPH capacity\n"
                     f"   - Use retained profits for growth\n\n"
                     "2. **Risk Mitigation (Despite Good ROI):**\n"
                     "   - Don't get complacent\n"
                     "   - Market conditions can change\n"
                     "   - Maintain quality and efficiency\n"
                     "   - Build contingency reserves\n\n"
                     "3. **Value Creation:**\n"
                     f"   - Your business creating {format_currency(total_5yr_profit/5)}/year value\n"
                     "   - Can attract investors/buyers at premium\n"
                     "   - Consider brand building for exit options\n\n"
                     "4. **Financial Prudence:**\n"
                     "   - Reinvest 60-70% of profits\n"
                     "   - Maintain cash reserves\n"
                     "   - Prepay expensive debt\n"
                     "   - Diversify after achieving stability\n\n"
                     "5. **Proceed with Confidence:**\n"
                     "   - Your numbers are solid\n"
                     "   - ROI >100% is exceptional\n"
                     "   - Execute well and monitor closely"
        })
    
    # Payback Period Estimation
    cumulative_5yr = results['yearly_data'][-1]['Cumulative Cash']
    if cumulative_5yr > results['equity_amount']:
        for i, year_data in enumerate(results['yearly_data'], 1):
            if year_data['Cumulative Cash'] >= results['equity_amount']:
                insights['positive'].append({
                    'title': f'Equity Payback in Year {i}',
                    'message': f"Your equity investment will be recovered in approximately {i} years.",
                    'action': "Quick payback period indicates a financially sound project."
                })
                break
    else:
        insights['warnings'].append({
            'title': 'Long Payback Period',
            'message': "Equity may take more than 5 years to recover fully.",
            'action': "Consider this long-term commitment and ensure adequate financial cushion."
        })
    
    # Price Sensitivity Analysis
    price_per_kg = inputs['sale_price_per_kg']
    paddy_price = inputs.get('paddy_price_per_quintal', 2000)
    
    if price_per_kg < 30:
        insights['warnings'].append({
            'title': 'Low Sale Price',
            'message': f"Rice sale price of ₹{price_per_kg}/kg is on the lower end.",
            'action': "Explore value addition (branding, packaging) or premium varieties for better margins."
        })
    
    # Cost Structure Analysis
    raw_material_percent = (results['annual_paddy_cost'] / results['total_annual_revenue'] * 100)
    
    if raw_material_percent > 70:
        insights['warnings'].append({
            'title': 'High Raw Material Cost',
            'message': f"Raw material is {raw_material_percent:.1f}% of revenue - very high!",
            'action': "Negotiate better paddy prices, consider contract farming, or increase sale prices."
        })
    elif raw_material_percent < 50:
        insights['positive'].append({
            'title': 'Efficient Raw Material Management',
            'message': f"Raw material at {raw_material_percent:.1f}% of revenue shows good cost control.",
            'action': "Maintain this efficiency through strategic procurement and inventory management."
        })
    
    # Manpower Efficiency
    revenue_per_employee = results['total_annual_revenue'] / (
        1 + 1 + inputs.get('num_skilled_workers', 6) + inputs.get('num_unskilled_workers', 8) + 1
    )
    
    if revenue_per_employee < 1000000:
        insights['recommendations'].append({
            'title': 'Review Manpower Productivity',
            'message': f"Revenue per employee is {format_currency(revenue_per_employee)}/year.",
            'action': "Consider automation, training programs, or workflow optimization to improve productivity."
        })
    
    # Seasonal Risk
    days_per_month = inputs['days_per_month']
    if days_per_month < 24:
        insights['recommendations'].append({
            'title': 'Seasonal Operations',
            'message': f"Operating {days_per_month} days/month suggests seasonal business.",
            'action': "Plan for adequate working capital during off-season and diversify product range if possible."
        })
    
    return insights


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
    tph = 5.0  # tonnes per hour
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
    
    # Create custom text with Indian formatting
    text_labels = [format_currency(v) for v in values]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        text=text_labels,
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>Amount: %{text}<br>Share: %{percent}<extra></extra>',
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
    
    # Create custom text with Indian formatting
    text_labels = [format_currency(v) for v in values]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        text=text_labels,
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>Amount: %{text}<br>Share: %{percent}<extra></extra>',
        hole=.3
    )])
    
    fig.update_layout(
        title=f"{period_label} Operating Cost Breakdown",
        height=400
    )
    
    return fig


def create_profitability_waterfall(results, period_divisor=1, period_label="Annual"):
    """Create waterfall chart showing profit calculation"""
    values = [
        results['total_annual_revenue'] / period_divisor,
        -results['total_operating_costs'] / period_divisor,
        -results['annual_depreciation'] / period_divisor,
        -results['annual_interest'] / period_divisor,
        -results['tax_amount'] / period_divisor,
        results['pat'] / period_divisor
    ]
    
    # Create custom text with Indian formatting
    text_labels = [format_currency(abs(v)) for v in values]
    
    fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=["relative", "relative", "relative", "relative", "relative", "total"],
        x=["Revenue", "Operating Costs", "Depreciation", "Interest", "Tax", "Net Profit (PAT)"],
        y=values,
        text=text_labels,
        textposition="outside",
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
        page_title="🌾 5 TPH Rice Mill - Nature's Bounty Financial Dashboard",
        page_icon="🌾",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Enhanced Nature-Inspired Custom CSS
    st.markdown("""
        <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&family=Quicksand:wght@400;500;600;700&display=swap');
        
        /* Global Styles */
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #e8f5e9 100%);
            font-family: 'Poppins', sans-serif;
        }
        
        /* Main Header with Rice Theme */
        .main-header {
            font-size: 3.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #2e7d32 0%, #558b2f 50%, #827717 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-align: center;
            margin-bottom: 0;
            padding: 1rem;
            font-family: 'Quicksand', sans-serif;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            animation: fadeInDown 1s ease-in;
        }
        
        .sub-header {
            font-size: 1.3rem;
            color: #558b2f;
            text-align: center;
            margin-bottom: 1rem;
            font-weight: 500;
            font-family: 'Quicksand', sans-serif;
            animation: fadeInUp 1.2s ease-in;
        }
        
        .tagline {
            font-size: 1rem;
            color: #689f38;
            text-align: center;
            margin-bottom: 2rem;
            font-style: italic;
            font-weight: 300;
            animation: fadeIn 1.5s ease-in;
        }
        
        /* Rice Grain Decorative Elements */
        .rice-decoration {
            text-align: center;
            font-size: 2rem;
            margin: 1rem 0;
            letter-spacing: 10px;
            opacity: 0.6;
            animation: float 3s ease-in-out infinite;
        }
        
        /* Nature-Inspired Cards */
        .metric-card {
            background: linear-gradient(135deg, #ffffff 0%, #f1f8e9 100%);
            padding: 1.5rem;
            border-radius: 15px;
            border-left: 5px solid #7cb342;
            box-shadow: 0 4px 15px rgba(124, 179, 66, 0.2);
            margin: 1rem 0;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(124, 179, 66, 0.3);
        }
        
        /* Section Headers with Natural Feel */
        .section-header {
            background: linear-gradient(90deg, #c5e1a5 0%, #dcedc8 100%);
            padding: 1rem 1.5rem;
            border-radius: 10px;
            border-left: 6px solid #558b2f;
            margin: 2rem 0 1rem 0;
            font-weight: 600;
            font-size: 1.4rem;
            color: #33691e;
            box-shadow: 0 2px 10px rgba(85, 139, 47, 0.15);
            font-family: 'Quicksand', sans-serif;
        }
        
        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f1f8e9 0%, #dcedc8 100%);
            border-right: 3px solid #aed581;
        }
        
        section[data-testid="stSidebar"] .stMarkdown h2,
        section[data-testid="stSidebar"] .stMarkdown h3 {
            color: #33691e;
            font-family: 'Quicksand', sans-serif;
        }
        
        /* Expander Styling */
        .streamlit-expanderHeader {
            background: linear-gradient(90deg, #c5e1a5 0%, #e8f5e9 100%);
            border-radius: 8px;
            border-left: 4px solid #7cb342;
            font-weight: 600;
            color: #2e7d32;
            padding: 0.5rem 1rem;
        }
        
        .streamlit-expanderHeader:hover {
            background: linear-gradient(90deg, #aed581 0%, #c5e1a5 100%);
        }
        
        /* Buttons with Nature Theme */
        .stButton > button {
            background: linear-gradient(135deg, #66bb6a 0%, #4caf50 100%);
            color: white;
            border: none;
            border-radius: 25px;
            padding: 0.6rem 2rem;
            font-weight: 600;
            font-size: 1rem;
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
            transition: all 0.3s ease;
            font-family: 'Poppins', sans-serif;
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%);
            box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
            transform: translateY(-2px);
        }
        
        /* Tabs Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: transparent;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%);
            border-radius: 10px 10px 0 0;
            color: #2e7d32;
            font-weight: 600;
            padding: 0.8rem 1.5rem;
            border: 2px solid #c5e1a5;
            border-bottom: none;
            font-family: 'Quicksand', sans-serif;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: linear-gradient(135deg, #c5e1a5 0%, #dcedc8 100%);
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #7cb342 0%, #9ccc65 100%);
            color: white;
            border-color: #558b2f;
        }
        
        /* Metrics with Natural Look */
        [data-testid="stMetricValue"] {
            color: #2e7d32;
            font-size: 1.8rem;
            font-weight: 700;
            font-family: 'Poppins', sans-serif;
        }
        
        [data-testid="stMetricLabel"] {
            color: #558b2f;
            font-weight: 600;
            font-size: 0.95rem;
            font-family: 'Quicksand', sans-serif;
        }
        
        [data-testid="stMetricDelta"] {
            font-weight: 600;
        }
        
        /* DataFrames */
        .dataframe {
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .dataframe thead tr th {
            background: linear-gradient(135deg, #7cb342 0%, #9ccc65 100%);
            color: white;
            font-weight: 600;
            padding: 1rem;
            font-family: 'Quicksand', sans-serif;
        }
        
        .dataframe tbody tr:nth-child(even) {
            background-color: #f1f8e9;
        }
        
        .dataframe tbody tr:hover {
            background-color: #dcedc8;
            transition: background-color 0.3s ease;
        }
        
        /* Radio Buttons */
        .stRadio > label {
            background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%);
            padding: 0.8rem 1.5rem;
            border-radius: 25px;
            border: 2px solid #c5e1a5;
            font-weight: 600;
            color: #2e7d32;
            cursor: pointer;
            transition: all 0.3s ease;
            font-family: 'Quicksand', sans-serif;
        }
        
        .stRadio > label:hover {
            background: linear-gradient(135deg, #c5e1a5 0%, #dcedc8 100%);
            border-color: #7cb342;
        }
        
        /* Success/Warning/Error Messages with Natural Colors */
        .stSuccess {
            background: linear-gradient(135deg, #c8e6c9 0%, #e8f5e9 100%);
            border-left: 5px solid #4caf50;
            border-radius: 8px;
            padding: 1rem;
            color: #1b5e20;
        }
        
        .stWarning {
            background: linear-gradient(135deg, #fff9c4 0%, #fffde7 100%);
            border-left: 5px solid #fbc02d;
            border-radius: 8px;
            padding: 1rem;
            color: #f57f17;
        }
        
        .stError {
            background: linear-gradient(135deg, #ffccbc 0%, #fbe9e7 100%);
            border-left: 5px solid #f44336;
            border-radius: 8px;
            padding: 1rem;
            color: #b71c1c;
        }
        
        .stInfo {
            background: linear-gradient(135deg, #b3e5fc 0%, #e1f5fe 100%);
            border-left: 5px solid #03a9f4;
            border-radius: 8px;
            padding: 1rem;
            color: #01579b;
        }
        
        /* Divider with Natural Element */
        hr {
            border: none;
            height: 2px;
            background: linear-gradient(90deg, transparent 0%, #7cb342 50%, transparent 100%);
            margin: 2rem 0;
        }
        
        /* Animations */
        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes fadeIn {
            from {
                opacity: 0;
            }
            to {
                opacity: 1;
            }
        }
        
        @keyframes float {
            0%, 100% {
                transform: translateY(0px);
            }
            50% {
                transform: translateY(-10px);
            }
        }
        
        /* Container with Nature Background */
        .nature-container {
            background: linear-gradient(135deg, #ffffff 0%, #f1f8e9 100%);
            border-radius: 15px;
            padding: 2rem;
            margin: 1rem 0;
            box-shadow: 0 4px 20px rgba(124, 179, 66, 0.15);
        }
        
        /* Chart Containers */
        .js-plotly-plot {
            border-radius: 10px;
            box-shadow: 0 2px 15px rgba(0,0,0,0.08);
        }
        
        /* Progress Indicators */
        .stProgress > div > div > div {
            background: linear-gradient(90deg, #7cb342 0%, #9ccc65 100%);
        }
        
        /* Input Fields */
        .stNumberInput > div > div > input,
        .stTextInput > div > div > input {
            border-radius: 8px;
            border: 2px solid #c5e1a5;
            padding: 0.5rem;
            transition: border-color 0.3s ease;
        }
        
        .stNumberInput > div > div > input:focus,
        .stTextInput > div > div > input:focus {
            border-color: #7cb342;
            box-shadow: 0 0 0 2px rgba(124, 179, 66, 0.2);
        }
        
        /* Slider */
        .stSlider > div > div > div {
            background-color: #7cb342;
        }
        
        /* Download Button */
        .stDownloadButton > button {
            background: linear-gradient(135deg, #8bc34a 0%, #689f38 100%);
            color: white;
            border-radius: 25px;
            font-weight: 600;
            padding: 0.6rem 2rem;
            border: none;
            box-shadow: 0 4px 15px rgba(139, 195, 74, 0.3);
        }
        
        .stDownloadButton > button:hover {
            background: linear-gradient(135deg, #689f38 0%, #558b2f 100%);
            box-shadow: 0 6px 20px rgba(139, 195, 74, 0.4);
        }
        
        /* Custom Scroll Bar */
        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f8e9;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #7cb342 0%, #9ccc65 100%);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #689f38 0%, #7cb342 100%);
        }
        </style>
    """, unsafe_allow_html=True)

    # Beautiful Header with Rice Theme
    st.markdown('<div class="rice-decoration">🌾 🍚 🌾 🍚 🌾</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-header">🌾 Nature\'s Bounty Rice Mill</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">5 TPH Premium Rice Processing Plant — Complete Financial Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="tagline">"From Golden Fields to Your Table — Sustainable Rice Processing Excellence"</div>', unsafe_allow_html=True)
    st.markdown('<div class="rice-decoration">🌾 🍚 🌾 🍚 🌾</div>', unsafe_allow_html=True)
    
    # Add helpful introduction
    with st.expander("ℹ️ How to Use This Dashboard & Understanding Financial Terms", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 📊 Dashboard Purpose
            This comprehensive financial planning tool helps you:
            - **Plan** your rice mill investment with realistic projections
            - **Analyze** profitability, break-even, and returns
            - **Understand** financial viability before investing
            - **Present** to banks, investors, or partners
            
            ### 🎯 Quick Start Guide
            1. **Adjust Inputs** in the left sidebar (capital costs, loan details, operations)
            2. **Review Outputs** in the main dashboard (all calculations are automatic)
            3. **Check AI Insights** for personalized recommendations
            4. **Download** projections as CSV for your records
            
            ### 💡 Key Metrics to Watch
            - **PAT (Net Profit)** - Your actual earnings after all expenses
            - **ROI** - Return on investment (target: 15%+)
            - **Break-even** - Minimum production to avoid losses
            - **Cash Flow** - Actual money available each month
            """)
        
        with col2:
            st.markdown("""
            ### 📚 Common Financial Terms (Simple Explanation)
            
            **EBITDA** = Earnings Before Interest, Tax, Depreciation, Amortization
            - *In simple words:* Operating profit before accounting stuff
            - *Why care:* Shows if your rice mill operations are profitable
            
            **PAT** = Profit After Tax (also called Net Profit)
            - *In simple words:* The actual money you take home
            - *Why care:* This is YOUR profit - what's left after everything
            
            **ROI** = Return on Investment
            - *In simple words:* How much profit per ₹100 invested
            - *Why care:* Tells if this project is worth your money
            
            **Break-even** = Zero profit, zero loss point
            - *In simple words:* Minimum sales needed to survive
            - *Why care:* Below this = losses, above this = profits
            
            **Depreciation** = Asset value reduction over time
            - *In simple words:* Machinery loses value as it ages
            - *Why care:* Reduces tax bill (non-cash expense)
            
            **EMI** = Equated Monthly Installment
            - *In simple words:* Monthly loan payment to bank
            - *Why care:* Must ensure cash flow can cover this
            
            *📖 Click "Financial Terms Glossary" in the Profitability section for detailed definitions with examples!*
            """)

    # Sidebar with all inputs
    with st.sidebar:
        st.markdown("### 🌾 Financial Parameters")
        st.markdown("*Customize your rice mill project details*")
        st.markdown("---")
        
        with st.expander("💰 Capital Costs", expanded=False):
            land_cost = st.number_input("Land Cost (₹)", value=800000.0, step=50000.0)
            building_cost = st.number_input("Building & Civil Works (₹)", value=2500000.0, step=50000.0)
            machinery_cost = st.number_input("Plant & Machinery (₹)", value=5000000.0, step=50000.0)
            electrical_cost = st.number_input("Electrical Installation (₹)", value=800000.0, step=50000.0)
            preoperative_cost = st.number_input("Pre-operative Expenses (₹)", value=500000.0, step=10000.0)
            misc_fixed_assets = st.number_input("Miscellaneous Fixed Assets (₹)", value=400000.0, step=10000.0)
            working_capital = st.number_input("Working Capital (₹)", value=1500000.0, step=50000.0)
        
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
            manager_salary = st.number_input("Manager Salary (₹/month)", value=35000, step=1000)
            supervisor_salary = st.number_input("Supervisor Salary (₹/month)", value=25000, step=1000)
            skilled_workers_salary = st.number_input("Skilled Worker Salary (₹/month)", value=18000, step=1000)
            num_skilled_workers = st.number_input("Number of Skilled Workers", value=6, step=1)
            unskilled_workers_salary = st.number_input("Unskilled Worker Salary (₹/month)", value=12000, step=1000)
            num_unskilled_workers = st.number_input("Number of Unskilled Workers", value=8, step=1)
            watchman_salary = st.number_input("Watchman Salary (₹/month)", value=10000, step=1000)
        
        with st.expander("⚡ Utilities & Other Costs", expanded=False):
            power_cost_monthly = st.number_input("Power Cost (₹/month)", value=80000, step=5000)
            water_cost_monthly = st.number_input("Water Cost (₹/month)", value=8000, step=500)
            fuel_cost_monthly = st.number_input("Fuel Cost (₹/month)", value=15000, step=1000)
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
    st.markdown('<div class="section-header">💰 Project Investment Overview</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Fixed Capital", format_currency(results['total_fixed_capital']),
                 help="Total investment in land, building, machinery, and equipment. These are long-term assets.")
    with col2:
        st.metric("Working Capital", format_currency(results['working_capital']),
                 help="Money needed for day-to-day operations like buying paddy, paying salaries, utilities etc. (2-3 months operating expenses)")
    with col3:
        st.metric("Total Project Cost", format_currency(results['total_project_cost']),
                 help="Total investment needed = Fixed Capital + Working Capital. This is what you need to start the business.")
    with col4:
        debt_equity_ratio = results['loan_amount'] / results['equity_amount'] if results['equity_amount'] > 0 else 0
        st.metric("Debt-Equity Ratio", f"{debt_equity_ratio:.2f}:1",
                 help="Loan amount compared to your own investment. Lower ratio means less risk. Banks prefer 2:1 or 3:1.")
    
    # Capital cost breakdown table
    with st.expander("📋 Detailed Capital Cost Breakdown", expanded=False):
        capital_df = pd.DataFrame([
            {"Component": k, "Amount (₹)": format_currency(v)} 
            for k, v in results['capital_costs'].items()
        ])
        st.dataframe(capital_df, width='stretch', hide_index=True)
        
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
            
            # EMI breakdown
            st.markdown("**EMI Breakdown (Annual)**")
            st.write(f"- Interest Portion: {format_currency(results['annual_interest'])}")
            st.write(f"- Principal Portion: {format_currency(results['annual_loan_payment'] - results['annual_interest'])}")
            st.info(f"💡 **Note:** Interest is tax-deductible (reduces taxable income), but principal repayment comes from profit after tax.")
    
    st.markdown("---")
    
    # ===== EMI & CASH FLOW SUMMARY =====
    st.markdown('<div class="section-header">💰 EMI Impact & Cash Flow Analysis</div>', unsafe_allow_html=True)
    
    # Check if there's any loan
    if results['loan_amount'] <= 0 or results['emi'] <= 0:
        st.info("ℹ️ **No Loan Taken:** This project is fully funded by equity (own funds). No EMI payments required. All PAT is available for business use!")
        st.markdown("---")
    else:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Monthly EMI", format_currency(results['emi']),
                     help="Fixed monthly payment to bank. Includes both interest and principal repayment.")
        with col2:
            monthly_pat = results['pat'] / 12
            st.metric("Monthly Profit (PAT)", format_currency(monthly_pat),
                     help="Average monthly profit after all expenses and taxes.")
        with col3:
            monthly_principal = (results['annual_loan_payment'] - results['annual_interest']) / 12
            net_cash_monthly = monthly_pat - monthly_principal
            st.metric("Net Cash After EMI", format_currency(net_cash_monthly),
                     help="Actual cash available each month after paying EMI principal. This is money you can use for business or personal needs.",
                     delta=f"{(net_cash_monthly/results['emi']*100):.1f}% of EMI" if results['emi'] > 0 else None)
        with col4:
            dscr = (monthly_pat + results['annual_depreciation']/12) / results['emi'] if results['emi'] > 0 else 0
            st.metric("DSCR (Debt Coverage)", f"{dscr:.2f}x",
                     help="Debt Service Coverage Ratio. Shows ability to pay EMI. Ideal: >1.5x, Minimum: 1.25x, Below 1.0x: Cannot service debt!")
        
        # Visual cash flow representation
        with st.expander("📊 Detailed EMI & Cash Flow Breakdown", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 💳 Annual EMI Breakdown")
                
                # Calculate percentages safely (handle division by zero)
                if results['annual_loan_payment'] > 0:
                    interest_pct = (results['annual_interest']/results['annual_loan_payment']*100)
                    principal_pct = ((results['annual_loan_payment'] - results['annual_interest'])/results['annual_loan_payment']*100)
                else:
                    interest_pct = 0
                    principal_pct = 0
                
                emi_breakdown = pd.DataFrame([
                    {"Component": "Total EMI Payment", "Amount": format_currency(results['annual_loan_payment'])},
                    {"Component": "  ├─ Interest Portion", "Amount": format_currency(results['annual_interest'])},
                    {"Component": "  └─ Principal Portion", "Amount": format_currency(results['annual_loan_payment'] - results['annual_interest'])},
                    {"Component": "", "Amount": ""},
                    {"Component": "Interest as % of EMI", "Amount": f"{interest_pct:.1f}%"},
                    {"Component": "Principal as % of EMI", "Amount": f"{principal_pct:.1f}%"},
                ])
                st.dataframe(emi_breakdown, width='stretch', hide_index=True)
                
                st.info("""
                **💡 Understanding EMI:**
                - **Interest** reduces your PBT (tax-deductible)
                - **Principal** is paid from PAT (after-tax profit)
                - Early years: High interest, Low principal
                - Later years: Low interest, High principal
                """)
            
            with col2:
                st.markdown("### 💵 Cash Flow After EMI")
                cash_flow_detail = pd.DataFrame([
                    {"Particulars": "Revenue", "Annual": format_currency(results['total_annual_revenue']), "Monthly": format_currency(results['total_annual_revenue']/12)},
                    {"Particulars": "Less: Operating Costs", "Annual": format_currency(results['total_operating_costs']), "Monthly": format_currency(results['total_operating_costs']/12)},
                    {"Particulars": "Less: Interest", "Annual": format_currency(results['annual_interest']), "Monthly": format_currency(results['annual_interest']/12)},
                    {"Particulars": "Less: Depreciation", "Annual": format_currency(results['annual_depreciation']), "Monthly": format_currency(results['annual_depreciation']/12)},
                    {"Particulars": "Less: Tax", "Annual": format_currency(results['tax_amount']), "Monthly": format_currency(results['tax_amount']/12)},
                    {"Particulars": "= PAT (Net Profit)", "Annual": format_currency(results['pat']), "Monthly": format_currency(results['pat']/12)},
                    {"Particulars": "---", "Annual": "---", "Monthly": "---"},
                    {"Particulars": "Less: Loan Principal", "Annual": format_currency(results['annual_loan_payment'] - results['annual_interest']), "Monthly": format_currency((results['annual_loan_payment'] - results['annual_interest'])/12)},
                    {"Particulars": "**= Cash After EMI**", "Annual": format_currency(results['pat'] - (results['annual_loan_payment'] - results['annual_interest'])), "Monthly": format_currency((results['pat'] - (results['annual_loan_payment'] - results['annual_interest']))/12)},
                ])
                st.dataframe(cash_flow_detail, width='stretch', hide_index=True)
                
                # Status indicator
                annual_cash_after_emi = results['pat'] - (results['annual_loan_payment'] - results['annual_interest'])
                if annual_cash_after_emi > results['annual_loan_payment'] * 0.2:  # 20% buffer
                    st.success(f"✅ **Healthy:** Good cash buffer after EMI payments")
                elif annual_cash_after_emi > 0:
                    st.warning(f"⚠️ **Tight:** Limited cash buffer. Monitor carefully.")
                else:
                    st.error(f"❌ **Critical:** Cannot cover EMI from profits! Needs restructuring.")
    
    st.markdown("---")
    
    # ===== VIEW SELECTOR =====
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        view_mode = st.radio(
            "📊 Select View Mode:",
            options=["Daily Summary", "Monthly Summary", "Annual Summary"],
            horizontal=True,
            help="Switch between daily, monthly and annual financial views"
        )
    
    # Set period divisor based on selection
    if view_mode == "Daily Summary":
        period_label = "Daily"
        period_divisor = 365  # Assuming 365 working days per year
    elif view_mode == "Monthly Summary":
        period_label = "Monthly"
        period_divisor = 12
    else:
        period_label = "Annual"
        period_divisor = 1
    
    st.markdown("---")
    
    # ===== PRODUCTION OVERVIEW =====
    st.markdown(f'<div class="section-header">🏭 Production Overview ({period_label})</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(f"{period_label} Paddy Processed", f"{format_indian_number(results['paddy_tonnes_year']/period_divisor, 1)} tonnes")
    with col2:
        st.metric(f"{period_label} Rice Produced", f"{format_indian_number(results['rice_tonnes_year']/period_divisor, 1)} tonnes")
    with col3:
        st.metric(f"{period_label} Bran", f"{format_indian_number(results['bran_tonnes_year']/period_divisor, 1)} tonnes")
    with col4:
        st.metric(f"{period_label} Husk", f"{format_indian_number(results['husk_tonnes_year']/period_divisor, 1)} tonnes")
    
    st.markdown("---")
    
    # ===== REVENUE & COST ANALYSIS =====
    st.markdown(f'<div class="section-header">📊 Revenue & Cost Analysis ({period_label})</div>', unsafe_allow_html=True)
    st.markdown("*Detailed breakdown of income streams and operational expenses*")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_revenue_breakdown_chart(results, period_divisor, period_label), width='stretch')
        
        st.markdown(f"**{period_label} Revenue Details**")
        revenue_details = pd.DataFrame([
            {"Product": "Rice", "Amount": format_currency(results['annual_revenue_rice']/period_divisor)},
            {"Product": "Bran", "Amount": format_currency(results['annual_revenue_bran']/period_divisor)},
            {"Product": "Husk", "Amount": format_currency(results['annual_revenue_husk']/period_divisor)},
            {"Product": "Broken Rice", "Amount": format_currency(results['annual_revenue_broken']/period_divisor)},
            {"Product": "**Total Revenue**", "Amount": format_currency(results['total_annual_revenue']/period_divisor)},
        ])
        st.dataframe(revenue_details, width='stretch', hide_index=True)
        
        # Add EMI and Net Profit Summary
        st.markdown(f"**{period_label} Loan Repayment & Final Profit**")
        emi_summary = pd.DataFrame([
            {"Particulars": "Total Revenue", "Amount": format_currency(results['total_annual_revenue']/period_divisor)},
            {"Particulars": "Less: Operating Costs", "Amount": format_currency(results['total_operating_costs']/period_divisor)},
            {"Particulars": "Less: Depreciation", "Amount": format_currency(results['annual_depreciation']/period_divisor)},
            {"Particulars": "Less: Interest (EMI portion)", "Amount": format_currency(results['annual_interest']/period_divisor)},
            {"Particulars": "Less: Tax", "Amount": format_currency(results['tax_amount']/period_divisor)},
            {"Particulars": "= PAT (Net Profit)", "Amount": format_currency(results['pat']/period_divisor)},
            {"Particulars": "---", "Amount": "---"},
            {"Particulars": "Less: Loan Principal (EMI)", "Amount": format_currency((results['annual_loan_payment'] - results['annual_interest'])/period_divisor)},
            {"Particulars": "**= Net Cash After EMI**", "Amount": format_currency((results['pat'] - (results['annual_loan_payment'] - results['annual_interest']))/period_divisor)},
        ])
        st.dataframe(emi_summary, width='stretch', hide_index=True)
        
        # Visual indicator
        net_cash_after_emi = results['pat'] - (results['annual_loan_payment'] - results['annual_interest'])
        if net_cash_after_emi > 0:
            st.success(f"✅ **Positive Cash Flow:** {format_currency(net_cash_after_emi/period_divisor)} available after all expenses & EMI")
        else:
            st.error(f"⚠️ **Negative Cash Flow:** Shortfall of {format_currency(abs(net_cash_after_emi)/period_divisor)} - Unable to service EMI!")
    
    with col2:
        st.plotly_chart(create_cost_breakdown_chart(results, period_divisor, period_label), width='stretch')
        
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
        st.dataframe(cost_details, width='stretch', hide_index=True)
    
    # Manpower breakdown
    with st.expander(f"👥 Detailed Manpower Cost Breakdown ({period_label})"):
        manpower_df = pd.DataFrame([
            {"Position": k, f"{period_label} Cost (₹)": format_currency(v/period_divisor)} 
            for k, v in results['manpower_costs'].items()
        ])
        st.dataframe(manpower_df, width='stretch', hide_index=True)
    
    st.markdown("---")
    
    # ===== PROFITABILITY ANALYSIS =====
    st.markdown(f'<div class="section-header">💹 Profitability Analysis ({period_label})</div>', unsafe_allow_html=True)
    
    # Add glossary expander at the top
    with st.expander("📚 Financial Terms Glossary - Click to understand key metrics", expanded=False):
        glossary = get_financial_glossary()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 💰 Profitability Metrics")
            for term in ["Gross Profit", "EBITDA", "EBIT", "PBT", "PAT"]:
                info = glossary[term]
                st.markdown(f"**{term}** ({info['short']})")
                st.markdown(f"_{info['definition']}_")
                st.markdown(f"📐 **Formula:** `{info['formula']}`")
                st.markdown(f"💡 **Example:** {info['example']}")
                if 'why_important' in info:
                    st.markdown(f"⭐ **Why Important:** {info['why_important']}")
                st.markdown("---")
        
        with col2:
            st.markdown("### 📊 Key Financial Indicators")
            for term in ["ROI", "Break-even Point", "Debt-Equity Ratio", "Working Capital", "Cash Flow", "Margin"]:
                info = glossary[term]
                st.markdown(f"**{term}** ({info['short']})")
                st.markdown(f"_{info['definition']}_")
                st.markdown(f"📐 **Formula:** `{info['formula']}`")
                st.markdown(f"💡 **Example:** {info['example']}")
                if 'why_important' in info:
                    st.markdown(f"⭐ **Why Important:** {info['why_important']}")
                st.markdown("---")
    
    st.markdown("")  # Spacing
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Gross Profit", format_currency(results['gross_profit']/period_divisor),
                 help="Revenue minus Operating Costs. Shows basic operational profitability.")
    with col2:
        st.metric("EBITDA", format_currency(results['ebitda']/period_divisor),
                 help="Earnings Before Interest, Tax, Depreciation & Amortization. Shows core operating performance.")
    with col3:
        st.metric("EBIT", format_currency(results['ebit']/period_divisor),
                 help="Earnings Before Interest & Tax (EBITDA - Depreciation). Operating profit after accounting for asset wear.")
    with col4:
        st.metric("PBT", format_currency(results['pbt']/period_divisor),
                 help="Profit Before Tax (EBIT - Interest). Profit after all expenses except income tax.")
    with col5:
        st.metric("PAT (Net Profit)", format_currency(results['pat']/period_divisor),
                 help="Profit After Tax. The actual profit you keep after all expenses, interest, and taxes. This is your 'bottom line'.")
    
    # Profitability waterfall - now shows for both monthly and annual
    st.plotly_chart(create_profitability_waterfall(results, period_divisor, period_label), width='stretch')
    
    # Profit & Loss Statement
    with st.expander(f"📄 Detailed Profit & Loss Statement ({period_label})"):
        st.info("💡 **Reading P&L Statement:** This shows how we arrive at final profit (PAT) from revenue. Each line deducts different types of costs/expenses.")
        
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
        st.dataframe(pl_df, width='stretch', hide_index=True)
        
        # Add explanation
        st.markdown("""
        **Understanding the Flow:**
        - **Revenue** - Total income from selling rice, bran, husk, and broken rice
        - **Operating Expenses** - Day-to-day costs (paddy, salaries, utilities, etc.)
        - **EBITDA** - Operating profit before accounting decisions
        - **Depreciation** - Asset value reduction (non-cash expense)
        - **EBIT** - Operating profit after depreciation
        - **Interest** - Cost of borrowing (EMI interest portion)
        - **PBT** - Profit before government tax
        - **Tax** - Income tax paid to government
        - **PAT** - Your final profit! This is what you actually earn
        - **Cash Flow** - Actual cash available (PAT + Depreciation - Loan Principal)
        """)
    
    st.markdown("---")
    
    # ===== KEY RATIOS & METRICS =====
    st.markdown('<div class="section-header">📈 Key Financial Ratios & Performance Metrics</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Profitability Ratios**")
        st.metric("Gross Margin", format_percentage(results['gross_margin']),
                 help="Gross Profit as % of Revenue. Shows how much profit you make before interest, tax, and depreciation.")
        st.metric("EBITDA Margin", format_percentage(results['ebitda_margin']),
                 help="EBITDA as % of Revenue. Indicates operational efficiency - higher is better (industry avg: 15-20%).")
        st.metric("Net Profit Margin", format_percentage(results['net_margin']),
                 help="PAT as % of Revenue. Your final profit after ALL expenses. This is the 'bottom line' percentage (target: 10-15%).")
    
    with col2:
        st.markdown("**Investment Returns**")
        st.metric("Annual ROI", format_percentage(results['roi_percent']),
                 help="Return on Investment: How much profit you earn per year as % of total investment. Higher ROI = better returns (target: 15-25%).")
        if results['payback_years']:
            st.metric("Payback Period", f"{results['payback_years']:.1f} years",
                     help="Time needed to recover your initial investment from profits. Shorter is better (ideal: 3-5 years).")
        else:
            st.metric("Payback Period", "N/A",
                     help="Time needed to recover your initial investment from profits.")
    
    with col3:
        st.markdown("**Break-even Analysis**")
        st.metric("Break-even Volume", f"{format_indian_number(results['breakeven_kg'])} kg rice",
                 help="Minimum rice production needed to cover all costs (zero profit, zero loss). Below this = losses, above = profits.")
        st.metric("Break-even Revenue", format_currency(results['breakeven_revenue']),
                 help="Minimum revenue needed to cover all costs. This is your safety threshold.")
        capacity_utilization = (results['breakeven_kg'] / results['rice_kg_year'] * 100) if results['rice_kg_year'] > 0 else 0
        st.metric("Break-even Capacity %", f"{capacity_utilization:.1f}%",
                 help="Percentage of full capacity needed to break even. Lower is safer (ideal: below 60%).")
    
    with st.expander("📊 Additional Cost Analytics"):
        st.write(f"**Revenue per kg of Rice (incl. by-products):** {format_currency(results['revenue_per_kg_rice'])}")
        st.write(f"**Variable Cost per kg:** {format_currency(results['variable_cost_per_unit'])}")
        st.write(f"**Contribution per kg:** {format_currency(results['contribution_per_unit'])}")
        st.write(f"**Contribution Margin:** {format_percentage(results['contribution_per_unit']/results['revenue_per_kg_rice']*100 if results['revenue_per_kg_rice'] > 0 else 0)}")
    
    st.markdown("---")
    
    # ===== 5-YEAR PROJECTIONS =====
    st.markdown('<div class="section-header">📅 5-Year Financial Growth Projections</div>', unsafe_allow_html=True)
    
    st.plotly_chart(create_projection_chart(results['yearly_data']), width='stretch')
    
    # Detailed projection table
    with st.expander("📋 Detailed 5-Year Projection Table", expanded=True):
        df_proj = pd.DataFrame(results['yearly_data'])
        df_display = df_proj.copy()
        
        for col in ["Revenue", "Operating Costs", "EBITDA", "Depreciation", "EBIT", 
                    "Interest", "PBT", "Tax", "PAT", "Cash Flow", "Cumulative Cash", "Loan Balance"]:
            df_display[col] = df_display[col].apply(lambda x: format_currency(x))
        
        st.dataframe(df_display, width='stretch', hide_index=True)
        
        # Download button
        csv = df_proj.to_csv(index=False)
        st.download_button(
            label="📥 Download 5-Year Projection as CSV",
            data=csv,
            file_name="rice_mill_5year_detailed_projection.csv",
            mime="text/csv",
        )
    
    st.markdown("---")
    
    # ===== AI-POWERED INSIGHTS & RECOMMENDATIONS =====
    st.markdown('<div class="section-header">🤖 AI-Powered Financial Intelligence & Strategic Recommendations</div>', unsafe_allow_html=True)
    st.markdown("*Advanced insights generated by analyzing 15+ financial parameters to guide your decision-making*")
    
    # Generate AI insights
    ai_insights = generate_ai_insights(results, inputs)
    
    # Display insights in organized tabs
    insight_tabs = st.tabs(["🔴 Critical Issues", "⚠️ Warnings", "💡 Recommendations", "✅ Positive Indicators"])
    
    with insight_tabs[0]:  # Critical Issues
        if ai_insights['critical']:
            st.markdown("### Critical Issues Requiring Immediate Attention")
            for idx, insight in enumerate(ai_insights['critical'], 1):
                with st.container():
                    st.markdown(f"#### {idx}. {insight['title']}")
                    st.error(f"**Quick Summary:** {insight['message']}")
                    
                    # Show detailed explanation in expander
                    if 'detail' in insight:
                        with st.expander("📊 View Detailed Analysis & Financial Breakdown"):
                            st.markdown(insight['detail'])
                    
                    st.markdown(f"**💡 Recommended Action Plan:**")
                    st.markdown(insight['action'])
                    st.markdown("---")
        else:
            st.success("✅ No critical issues detected! Your project parameters look solid.")
    
    with insight_tabs[1]:  # Warnings
        if ai_insights['warnings']:
            st.markdown("### Areas of Concern - Consider These Carefully")
            for idx, insight in enumerate(ai_insights['warnings'], 1):
                with st.container():
                    st.markdown(f"#### {idx}. {insight['title']}")
                    st.warning(f"**Quick Summary:** {insight['message']}")
                    
                    # Show detailed explanation in expander
                    if 'detail' in insight:
                        with st.expander("📊 View Detailed Analysis & Financial Breakdown"):
                            st.markdown(insight['detail'])
                    
                    st.markdown(f"**💡 Suggested Action Plan:**")
                    st.markdown(insight['action'])
                    st.markdown("---")
        else:
            st.success("✅ No significant warnings! Your financial structure appears balanced.")
    
    with insight_tabs[2]:  # Recommendations
        if ai_insights['recommendations']:
            st.markdown("### Optimization Opportunities")
            for idx, insight in enumerate(ai_insights['recommendations'], 1):
                with st.container():
                    st.markdown(f"#### {idx}. {insight['title']}")
                    st.info(f"**Quick Summary:** {insight['message']}")
                    
                    # Show detailed explanation in expander
                    if 'detail' in insight:
                        with st.expander("📊 View Detailed Analysis & Financial Breakdown"):
                            st.markdown(insight['detail'])
                    
                    st.markdown(f"**💡 Consider These Actions:**")
                    st.markdown(insight['action'])
                    st.markdown("---")
        else:
            st.info("Your current setup is well-optimized. Monitor performance regularly.")
    
    with insight_tabs[3]:  # Positive Indicators
        if ai_insights['positive']:
            st.markdown("### Strong Points - Your Competitive Advantages")
            for idx, insight in enumerate(ai_insights['positive'], 1):
                with st.container():
                    st.markdown(f"#### {idx}. {insight['title']}")
                    st.success(f"**Quick Summary:** {insight['message']}")
                    
                    # Show detailed explanation in expander
                    if 'detail' in insight:
                        with st.expander("📊 View Detailed Analysis & Financial Breakdown"):
                            st.markdown(insight['detail'])
                    
                    st.markdown(f"**💡 How to Leverage This Strength:**")
                    st.markdown(insight['action'])
                    st.markdown("---")
        else:
            st.info("Focus on addressing the concerns above to improve project viability.")
    
    # Overall AI Assessment
    st.markdown("---")
    st.markdown("### 🎯 Overall AI Assessment")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        critical_count = len(ai_insights['critical'])
        if critical_count == 0:
            st.metric("Critical Issues", "0", delta="Excellent", delta_color="normal")
        else:
            st.metric("Critical Issues", str(critical_count), delta="Needs Attention", delta_color="inverse")
    
    with col2:
        warning_count = len(ai_insights['warnings'])
        if warning_count <= 2:
            st.metric("Warnings", str(warning_count), delta="Manageable", delta_color="normal")
        else:
            st.metric("Warnings", str(warning_count), delta="Review Required", delta_color="inverse")
    
    with col3:
        rec_count = len(ai_insights['recommendations'])
        st.metric("Opportunities", str(rec_count), delta=f"{rec_count} found", delta_color="off")
    
    with col4:
        positive_count = len(ai_insights['positive'])
        if positive_count >= 3:
            st.metric("Strengths", str(positive_count), delta="Strong", delta_color="normal")
        else:
            st.metric("Strengths", str(positive_count), delta="Build More", delta_color="off")
    
    # Final AI Recommendation
    st.markdown("---")
    total_critical_warnings = len(ai_insights['critical']) + len(ai_insights['warnings'])
    total_positive = len(ai_insights['positive'])
    
    if len(ai_insights['critical']) > 0:
        st.error("� **AI Recommendation:** Critical issues detected. Address these before proceeding with the project. Consider revising your financial plan.")
    elif len(ai_insights['warnings']) > 3:
        st.warning("⚠️ **AI Recommendation:** Multiple areas of concern identified. Review and optimize your plan before implementation.")
    elif total_positive > total_critical_warnings:
        st.success("✅ **AI Recommendation:** Project shows strong fundamentals! Proceed with confidence while monitoring the suggested improvements.")
    else:
        st.info("ℹ️ **AI Recommendation:** Project is viable but has room for optimization. Address the recommendations to strengthen your position.")
    
    st.markdown("---")
    
    # Traditional Insights (kept for compatibility)
    with st.expander("📊 Detailed Viability Metrics", expanded=False):
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
