import streamlit as st
import yfinance as yf
import pandas as pd

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
                'EPS': info.get('trailingEps', None)
            })
        except Exception:
            continue
    return pd.DataFrame(data)

def main():
    st.title('S&P 500 Stock Screener')
    st.write('Filter S&P 500 stocks by various metrics.')

    sp500 = load_sp500_tickers()
    tickers = sp500['Symbol'].tolist()

    st.sidebar.header('Filters')
    sector = st.sidebar.multiselect('Sector', options=sp500['GICS Sector'].unique())
    industry = st.sidebar.multiselect('Industry', options=sp500['GICS Sub-Industry'].unique())
    min_price, max_price = st.sidebar.slider('Price Range', 0.0, 2000.0, (0.0, 2000.0))
    min_pe, max_pe = st.sidebar.slider('P/E Ratio Range', 0.0, 100.0, (0.0, 100.0))
    min_eps, max_eps = st.sidebar.slider('EPS Range', -50.0, 50.0, (-50.0, 50.0))

    if st.button('Run Screener'):
        data = fetch_stock_data(tickers)
        if sector:
            data = data[data['Sector'].isin(sector)]
        if industry:
            data = data[data['Industry'].isin(industry)]
        data = data[(data['Price'] >= min_price) & (data['Price'] <= max_price)]
        data = data[(data['P/E Ratio'] >= min_pe) & (data['P/E Ratio'] <= max_pe)]
        data = data[(data['EPS'] >= min_eps) & (data['EPS'] <= max_eps)]
        st.dataframe(data)
    else:
        st.info('Set your filters and click "Run Screener".')

if __name__ == '__main__':
    main() 
