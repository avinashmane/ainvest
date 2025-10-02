import json
import streamlit as st
from lib.user import User

# with open(".streamlit/firebase_key.json") as f:
#     firebase_key=json.load(f)

# print(firebase_key['client_email'])
def is_logged_in():
    if 'is_logged_in' in st.user:
        if st.user.is_logged_in:
            return True
        else:
            return False
        
def show_login():
    if not is_logged_in():
        login_screen()
    else:
        logged_in()

def logged_in():
    st.session_state.user=User(getattr(st.user,'email'))
    st.session_state.user.update(**st.session_state.user.get_profile())
    st.markdown(f'<img src="{st.user.picture}" style="border-radius:100%" with="100px"/>',
                           unsafe_allow_html=True)
    st.header(f"Welcome {st.user.given_name or st.user.name}!")

    st.button("Log out", on_click=st.logout)

def st_login():
    return st.login(provider='google')

def login_screen():
    st.subheader("This app is needs a login and it's free.")
    st.button("Log in with Google", 
              on_click=st_login)
    
def please_login():
    st.write("""
    It's fantastic that you're looking to take charge of your financial future! Investing doesn't have to be complicated. It's about putting your money to work so it grows over time.

Here is a guide to help you become a better investor and learn how to earn rewards for taking the right kind of risk.

**👈 First thing...   Please Login. It's FREE**
             
---

## The Basics of Becoming a Better Investor

Investing is simply delaying spending today so you can have more money in the future. The "rewards" you earn are the returns on your investment.

### 1. Master Your Money Mindset

Before you invest a single penny, you need a solid foundation.

* **Pay Yourself First:** Automate a portion of your income (even a small amount!) to go directly into a savings or investment account. Treat this like a non-negotiable bill.
* **Crush High-Interest Debt:** Debt, especially credit card debt, is an *anti-investment*. Its high interest rate is a guaranteed loss that will outpace most investment returns. Pay this off first.
* **Build an Emergency Fund:** Keep $\mathbf{3}$ to $\mathbf{6}$ months' worth of living expenses in a separate, easily accessible savings account. This fund prevents you from having to sell investments at a loss when life throws a curveball.

### 2. Understand Risk: The Price of Reward

Every investment involves risk, but **risk** simply means **uncertainty**. You don't know for sure what your return will be.

| Type of Risk | Definition | How to Mitigate (Lower) It |
| :--- | :--- | :--- |
| **Market Risk** | The value of your investment might go up or down because of general market conditions (e.g., a recession). | **Diversification:** Don't put all your eggs in one basket. Invest across different types of assets (stocks, bonds, real estate). |
| **Inflation Risk** | Your money loses its buying power over time because the cost of goods increases. | **Growth Investing:** Invest in assets (like stocks) that have historically grown *faster* than the rate of inflation. |
| **Individual Stock Risk** | The value of a single company's stock drops due to poor performance or bad news. | **Index Funds/ETFs:** Instead of buying one stock, buy a fund that holds hundreds of stocks, like a whole market index (e.g., S\&P 500). |

**The Right Kind of Risk:** This is **calculated, diversified risk** that has a **long-term time horizon**. The longer your money is invested, the more time it has to recover from market dips and grow, making the risk more manageable.

### 3. Start Simple: Your Core Investment Strategy

You don't need to pick the next hot stock. Most successful investors follow a simple, proven strategy:

* **The Power of Index Funds and ETFs:** These are the best tools for common people. They are baskets of stocks or bonds that track a major market index (like the NIFTY 50, which holds the 50 biggest companies).
    * **Why they're great:** They are **low-cost**, **immediately diversified** (you own tiny pieces of hundreds of companies), and have historically delivered strong long-term returns.
* **Automation and Consistency (Buy-Cost Averaging):** Set up automatic monthly or bi-weekly transfers to buy your chosen investment.
    * This is called **Buy-Cost Averaging (BCA)**. You buy whether the market is up or down. Sometimes you buy high, sometimes you buy low, but over time, you lower your average purchase price and remove emotion from the equation.
* **Reinvest Your Earnings:** When your investments pay out dividends (profits), set them to automatically buy more shares. This is called **compounding**—earning returns on your original investment *plus* on the returns you've already made. This is the **most powerful force in investing.**

---

## Key Steps to Take Today

1.  **Open a Brokerage Account:** Use a reputable, low-cost platform . For retirement, look into a **Tax advantaged accounts** .
2.  **Choose a Simple Investment:** Invest in a **broad, low-cost index fund** that tracks the entire stock market (e.g., a total stock market fund or an NIFTY 50 or SP500 fund).
3.  **Set it and Forget it (Mostly):** Set up your automatic contributions and let time and compounding do the heavy lifting. **Do not check your account balance every day.** Investing is a marathon, not a sprint.

**The Golden Rule:** The best time to invest was yesterday. The second best time is **today**. Don't wait for the "perfect" moment; just start.

***

Do you have a specific goal in mind, like saving for retirement or a down payment on a house? Knowing your goal can help guide your starting investments!
""")
