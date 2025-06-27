import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

@st.cache_data
def load_sp500_tickers():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    tables = pd.read_html(url)
    df = tables[0]
    return df[['Symbol', 'Security', 'GICS Sector', 'GICS Sub-Industry']]

@st.cache_data
def fetch_stock_data(tickers):
    data = []
    for symbol in tickers:
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            data.append({
                'Symbol': symbol,
                'Name': info.get('shortName', ''),
                'Sector': info.get('sector', ''),
                'Industry': info.get('industry', ''),
                'Price': info.get('regularMarketPrice', None),
                'Volume': info.get('volume', None),
                'Market Cap': info.get('marketCap', None),
                'P/E Ratio': info.get('trailingPE', None),
                'Forward P/E': info.get('forwardPE', None),
                'EPS': info.get('trailingEps', None),
                'Dividend Yield': info.get('dividendYield', None),
                '52W High': info.get('fiftyTwoWeekHigh', None),
                '52W Low': info.get('fiftyTwoWeekLow', None),
                'Beta': info.get('beta', None),
                'Price/Book': info.get('priceToBook', None),
                'ROE': info.get('returnOnEquity', None),
                'Debt/Equity': info.get('debtToEquity', None),
                'Revenue': info.get('totalRevenue', None),
                'Gross Margin': info.get('grossMargins', None),
                'Operating Margin': info.get('operatingMargins', None),
                'Free Cash Flow': info.get('freeCashflow', None),
                'Next Earnings': info.get('earningsDate', None),
                'Exchange': info.get('exchange', ''),
                'Country': info.get('country', ''),
                'Website': info.get('website', '')
            })
        except Exception:
            continue
    return pd.DataFrame(data)

def main():
    st.markdown("""
    <h1 style='text-align: center; color: #00BFFF;'>S&amp;P 500 Stock Screener</h1>
    <p style='text-align: center;'>Filter S&amp;P 500 stocks by various metrics. Download your results as CSV.</p>
    """, unsafe_allow_html=True)

    sp500 = load_sp500_tickers()
    tickers = sp500['Symbol'].tolist()

    with st.sidebar:
        st.header('Filters')
        with st.expander('General'):
            sector = st.multiselect('Sector', options=sp500['GICS Sector'].unique())
            industry = st.multiselect('Industry', options=sp500['GICS Sub-Industry'].unique())
        with st.expander('Valuation'):
            min_price, max_price = st.slider('Price Range', 0.0, 2000.0, (0.0, 2000.0))
            min_pe, max_pe = st.slider('P/E Ratio Range', 0.0, 100.0, (0.0, 100.0))
            min_fpe, max_fpe = st.slider('Forward P/E Range', 0.0, 100.0, (0.0, 100.0))
            min_pb, max_pb = st.slider('Price/Book Range', 0.0, 50.0, (0.0, 50.0))
        with st.expander('Performance'):
            min_eps, max_eps = st.slider('EPS Range', -50.0, 50.0, (-50.0, 50.0))
            min_roe, max_roe = st.slider('ROE Range', -1.0, 2.0, (-1.0, 2.0))
            min_beta, max_beta = st.slider('Beta Range', -2.0, 4.0, (-2.0, 4.0))
        with st.expander('Dividends & Margins'):
            min_div, max_div = st.slider('Dividend Yield (%)', 0.0, 10.0, (0.0, 10.0))
            min_gm, max_gm = st.slider('Gross Margin (%)', 0.0, 1.0, (0.0, 1.0))
            min_om, max_om = st.slider('Operating Margin (%)', 0.0, 1.0, (0.0, 1.0))
        with st.expander('Other'):
            min_52wlow, max_52whigh = st.slider('52W Price Range', 0.0, 2000.0, (0.0, 2000.0))
            min_de, max_de = st.slider('Debt/Equity', 0.0, 10.0, (0.0, 10.0))

    if st.button('Run Screener'):
        data = fetch_stock_data(tickers)
        if sector:
            data = data[data['Sector'].isin(sector)]
        if industry:
            data = data[data['Industry'].isin(industry)]
        data = data[(data['Price'] >= min_price) & (data['Price'] <= max_price)]
        data = data[(data['P/E Ratio'] >= min_pe) & (data['P/E Ratio'] <= max_pe)]
        data = data[(data['Forward P/E'] >= min_fpe) & (data['Forward P/E'] <= max_fpe)]
        data = data[(data['Price/Book'] >= min_pb) & (data['Price/Book'] <= max_pb)]
        data = data[(data['EPS'] >= min_eps) & (data['EPS'] <= max_eps)]
        data = data[(data['ROE'] >= min_roe) & (data['ROE'] <= max_roe)]
        data = data[(data['Beta'] >= min_beta) & (data['Beta'] <= max_beta)]
        data = data[(data['Dividend Yield'] >= min_div/100) & (data['Dividend Yield'] <= max_div/100)]
        data = data[(data['Gross Margin'] >= min_gm) & (data['Gross Margin'] <= max_gm)]
        data = data[(data['Operating Margin'] >= min_om) & (data['Operating Margin'] <= max_om)]
        data = data[(data['52W Low'] >= min_52wlow) & (data['52W High'] <= max_52whigh)]
        data = data[(data['Debt/Equity'] >= min_de) & (data['Debt/Equity'] <= max_de)]
        # Format columns
        data['Dividend Yield'] = data['Dividend Yield'] * 100
        data['Gross Margin'] = data['Gross Margin'] * 100
        data['Operating Margin'] = data['Operating Margin'] * 100
        # Format Next Earnings
        data['Next Earnings'] = data['Next Earnings'].apply(lambda x: x.strftime('%Y-%m-%d') if isinstance(x, (datetime, pd.Timestamp)) else x)
        # Make Website clickable
        data['Website'] = data['Website'].apply(lambda x: f"[Link]({x})" if x else "")
        st.dataframe(data, use_container_width=True)
        st.download_button('Download CSV', data.to_csv(index=False), file_name='sp500_screened.csv', mime='text/csv')
    else:
        st.info('Set your filters and click "Run Screener".')

if __name__ == '__main__':
    main() 
