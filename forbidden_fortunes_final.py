import streamlit as st
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import yfinance as yf
import random

flag=False


def fetch_gold_price():
    """
    Fetches gold price data from a financial data provider.
    """
    try:
        # Fetch real gold prices from the goldapi.io API
        url = "https://www.goldapi.io/api/XAU/INR"
        headers = {"x-access-token": "goldapi-1j97x5sluz3pdeu-io"}  
        response = requests.get(url, headers=headers)
        data = response.json()
        gold_price = data["price"]
        return gold_price
    except Exception as e:
        st.error(f"Error fetching gold price data: {str(e)}")
        return None

def fetch_fd_interest_rates():
    # Fixed interest rate of 7.5% for all tenures
    rates = {"Bank": {"1 Year": 7.5, "2 Years": 7.5, "3 Years": 7.5}}
    return rates

def fetch_nifty50_data():
    try:
        nifty_data = yf.download("^NSEI", start=datetime.now() - timedelta(days=365), end=datetime.now())
        return nifty_data
    except Exception as e:
        st.error(f"Error fetching Nifty 50 data: {str(e)}")
        return None

def calculate_returns(investment_amounts, fd_rates, gold_price):
    gold_return = (investment_amounts["gold"] / gold_price) * (gold_price * 1.05)
    fd_returns = 0
    for bank, rates in fd_rates.items():
        for tenure, rate in rates.items():
            if tenure in investment_amounts["fd"][bank]:
                fd_returns += investment_amounts["fd"][bank][tenure] * (1 + rate / 100)
    nifty_return = investment_amounts["nifty50"] * 1.10
    total_investment = investment_amounts["gold"] + fd_returns + investment_amounts["nifty50"]
    total_return = gold_return + fd_returns + nifty_return
    return total_investment, total_return

def display_investment_allocation(investment_amounts):
    labels = ["Gold", "Fixed Deposits", "NIFTY 50"]
    fd_total = sum(sum(amounts.values()) for amounts in investment_amounts["fd"].values())
    sizes = [investment_amounts["gold"], fd_total, investment_amounts["nifty50"]]
    colors = ["gold", "lightblue", "darkgreen"]
    plt.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%")
    st.pyplot(plt)


def investment1_calculator():
    
    # User input for investment amounts
    gold_investment = st.number_input("Gold investment", min_value=0.0)
    fd_investments = {
        "Bank": {
            "1 Year": st.number_input("Short Term FD investment", min_value=0.0),
            "2 Years": st.number_input("Medium Term FD investment", min_value=0.0),
            "3 Years": st.number_input("Long Term FD investment", min_value=0.0),
        }
    }
    nifty50_investment = st.number_input("NIFTY50 investment", min_value=0.0)
    
    st.header("Current Gold Price")
    gold_price = fetch_gold_price()
    st.write(f"Gold Price: ₹{gold_price}")
    
    # Fixed Deposits (FDs) interest rates
    fd_rates = fetch_fd_interest_rates()
    st.header("Fixed Deposits Interest Rates")
    for bank, rates in fd_rates.items():
        st.subheader(f"{bank} FD Interest Rates")
        for tenure, rate in rates.items():
            st.write(f"{tenure}: {rate}%")
    
    # Stocks (Nifty 50) data
    nifty_data = fetch_nifty50_data()
    st.header("NIFTY50 Stocks Data")
    st.write(nifty_data)
    
    if st.button("Calculate Returns"):
        investment_amounts = {
            "gold": gold_investment,
            "fd": fd_investments,
            "nifty50": nifty50_investment,
        }
        
        total_investment, total_return = calculate_returns(investment_amounts, fd_rates, gold_price)
        st.write(f"Total investment: ₹{total_investment:,.2f}")
        st.write(f"Expected return: ₹{total_return:,.2f}")
        try:
            display_investment_allocation(investment_amounts)
        except:
            st.write("No values entered")
    


def split_predictor(risk_score, amount):
    st.header("Suggested split based on Risk Profile")

    if(1<=risk_score<2):
        rfd=round(random.uniform(0.7,1),2)
        rg=round(random.uniform(0,0.3),2)
        rs=1-rfd-rg

    elif(2<=risk_score<3):
        rfd=round(random.uniform(0.6,1),2)
        rg=round(random.uniform(0.1,0.4),2)
        rs=1-rfd-rg

    elif(3<=risk_score<4):
        rg=round(random.uniform(0.2,0.4),2)
        rs=round(random.uniform(0.4,0.5),2)
        rfd=1-rg-rs

    elif(4<=risk_score<5):
        rg=round(random.uniform(0.25,0.5),2)
        rs=round(random.uniform(0.5,0.6),2)
        rfd=1-rg-rs

    elif(5<=risk_score<6):        
        rg=round(random.uniform(0.3,0.6),2)
        rs=round(random.uniform(0.6,0.75),2)
        rfd=1-rg-rs

    stock_split=amount*rs
    fd_split=amount*rfd
    gold_split=amount*rg

    investment_amounts = {
            "gold": gold_split,
            "fd": fd_split,
            "nifty50": stock_split,
        }
    return investment_amounts
    


def investment_calculator():
    """
    This function creates a Streamlit app to gather user input for investment planning with scoring.
    """
    with st.form("Investment Planning"):
        
        # Title
        st.title("Investment Planning Assistant")
        st.write("The predictions made are based on historical data and is by no means foolproof. Investments are subjected to market risks")


        # Income score
        income_options = {
            "Less than 5 lakhs": 1,
            "5-10 lakhs": 2,
            "10-20": 3,
            "20-30": 4,
            "30-40": 5,
            "40 above": 6,
        }
        income = st.selectbox("What is your annual income?", list(income_options.keys()))
        income_score = income_options[income]

        # Age score
        age_options = {
            "20-30": 6,
            "30-40": 4,
            "40-50": 2,
            "50 above": 1,
        }
        age = st.selectbox("What is your current age?", list(age_options.keys()))
        age_score = age_options[age]


        #Investment amount
        amount= st.number_input("How much money do you want to invest? ", min_value=1000.0)
        val=[2.5,5.5,15.5,25.5,35.5,40]
        percent=(amount/val[income_score-1])*100
        if 5<=percent<10 :
            investment_percentage_score=1
        elif 10<=percent<15 :
            investment_percentage_score=2
        elif 15<=percent<20 :
            investment_percentage_score=3
        elif 20<=percent<25 :
            investment_percentage_score=4
        elif 25<=percent<30 :
            investment_percentage_score=5
        elif percent>=30:
            investment_percentage_score=6


        # Investment goals score
        investment_goals_options = {
            "Retirement planning": 4.5,
            "Major purchase": 5.5,
            "Child's education": 6,
            "Building wealth": 4,
            "Generating income": 5,
        }
        investment_goals = st.selectbox("What are your investment goals?", list(investment_goals_options.keys()))
        investment_goals_score = investment_goals_options[investment_goals]

        # Timeframe score (dummy values for now, replace with actual scores based on your strategy)
        timeframe_options = ["Short Term", "Medium Term", "Long term"]
        timeframe = st.selectbox("What is your investment timeframe?", timeframe_options)
        timeframe_score = 3  # Placeholder score for timeframe

        # Risk tolerance score
        risk_tolerance_options = {
            "No tolerance for losses": -6,
            "Minimize losses": 0,
            "Moderate fluctuations": 3,
            "Significant fluctuations": 4,
        }
        risk_tolerance = st.selectbox("What is your risk tolerance?", list(risk_tolerance_options.keys()))
        risk_tolerance_score = risk_tolerance_options[risk_tolerance]

        # Debt score
        debt_options = {
            "Nil": 6,
            "More": 2,
            "Some": 4,
        }
        debts = st.selectbox("Do you have any outstanding debts?", list(debt_options.keys()))
        debt_score = debt_options[debts]

        # Emergency fund score
        emergency_fund_options = {
            "Nil": 6,
            "Medium": 3,
            "More": 0,
        }
        emergency_fund = st.selectbox("Do you have an emergency fund?", list(emergency_fund_options.keys()))
        emergency_fund_score = emergency_fund_options[emergency_fund]

        # Job security score
        job_security_options = {
            "Secure": 6,
            "Mildly secure": 3,
            "Insecure": 0,
        }
        job_security = st.selectbox("How secure is your current job?", list(job_security_options.keys()))
        job_security_score = job_security_options[job_security]

        # Total score calculation
        total_score = (
            income_score + age_score + investment_percentage_score +
            investment_goals_score + timeframe_score + risk_tolerance_score +
            debt_score + emergency_fund_score + job_security_score
        )/9

        submitted = st.form_submit_button("Calculate Score")
        if submitted:
            st.write("Your total investment score is:", round(total_score,2))
            st.write("(1- Risk Averse, 6- High Risk Tolerance)")
            global flag
            flag = True


        return (total_score,amount)

if __name__ == "__main__":

    with st.container(border = True):
            
            risk_score,amount = investment_calculator()
    with st.container(border = True):
        if flag==True:

            investment_amounts = split_predictor(risk_score,amount)
            labels = ["Gold", "Fixed Deposits", "NIFTY 50"]
            sizes = [abs(investment_amounts["gold"]), abs(investment_amounts["fd"]), abs(investment_amounts["nifty50"])]
            colors = ["gold", "lightblue", "darkgreen"]
            plt.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%")
            st.pyplot(plt)
            st.write(f"Recommended invest amount for Gold: ₹{investment_amounts['gold']:,.2f}")
            st.write(f"Reccommended invest amount for Stocks: ₹{investment_amounts['nifty50']:,.2f}")
            st.write(f"Reccommended invest amount for Fixed Deposits: ₹{investment_amounts['fd']:,.2f}")
    
            

        
    with st.container(border = True):
        st.title('Customize your Split!')
        investment1_calculator()
    
