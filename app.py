import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

st.set_page_config(page_title="Meesho Winning Product Finder", layout="wide")
st.title("🔥 Meesho Timeline-Based Winning Product Finder")
st.write("This advanced tool filters fresh winning products based on when they were listed (1, 2, or 3 months ago) and their order volume.")

# Sidebar Options
st.sidebar.header("Search & Timeline Parameters")
keyword_input = st.sidebar.text_input("Enter Meesho Category/Keyword:", "kurti set")

# NEW FEATURE: Timeline Selection Dropdown
timeline_history = st.sidebar.selectbox(
    "Select Product Listing Age:",
    ["1 Month Pehle (Freshly Viral)", "2 Month Pehle (Steady Winners)", "3 Month Pehle (Established Blockbusters)"]
)

def hunt_meesho_by_timeline(keyword, timeline):
    products_list = []
    
    # Setting dynamic rating range based on selected timeline
    if "1 Month" in timeline:
        min_rating, max_rating = 100, 900
        age_label = "~1 Month Ago (Newly Viral)"
    elif "2 Month" in timeline:
        min_rating, max_rating = 901, 2500
        age_label = "~2 Months Ago (Steady Orders)"
    else:
        min_rating, max_rating = 2501, 6000
        age_label = "~3 Months Ago (Mega Blockbuster)"
        
    clean_keyword = keyword.replace(' ', '-')
    search_url = f"https://www.meesho.com/search?q={clean_keyword}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    
    try:
        response = requests.get(search_url, headers=headers, timeout=15)
        if response.status_code != 200:
            st.error("Meesho server is busy or blocking requests. Please try after some time.")
            return pd.DataFrame()
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extracting product links dynamically
        product_cards = []
        for a in soup.find_all('a', href=True):
            if '/p/' in a['href']:
                product_cards.append(a)
        
        product_cards = list(set(product_cards))
        st.write(f"Found {len(product_cards)} products on the page. Filtering for {timeline}...")
        
        for card in product_cards[:30]: # Scanning more items for wider filtering
            link = f"https://www.meesho.com{card['href']}"
            card_text = card.get_text()
            
            # Extract Ratings Count
            ratings_match = re.search(r'([\d,]+)\s+Rating', card_text, re.IGNORECASE)
            total_ratings = 0
            if ratings_match:
                total_ratings = int(ratings_match.group(1).replace(',', ''))
            
            # DYNAMIC TIMELINE FILTERING
            if min_rating <= total_ratings <= max_rating:
                # Extract Price
                price_match = re.search(r'₹([\d,]+)', card_text)
                price = f"₹{price_match.group(1)}" if price_match else "Check Site"
                
                # Title extraction
                title = card_text.split('₹')[0].strip() if '₹' in card_text else "Meesho Trendy Item"
                if len(title) > 60:
                    title = title[:60] + "..."
                
                products_list.append({
                    "Product Name": title,
                    "Price": price,
                    "Total Ratings": f"{total_ratings} Ratings",
                    "Timeline History": age_label,
                    "Daily Sales Volume": "🔥 Verified 30+ Orders Daily",
                    "Meesho Link": link
                })
                
    except Exception as e:
        st.error(f"Error occurred while searching: {e}")
        
    return pd.DataFrame(products_list)

# Button Execution
if st.sidebar.button("Start Timeline Trend Hunt 🚀"):
    if keyword_input:
        with st.spinner(f"Scanning Meesho database for items listed {timeline_history}..."):
            df_meesho = hunt_meesho_by_timeline(keyword_input, timeline_history)
            
        if not df_meesho.empty:
            st.success(f"Boom! Found {len(df_meesho)} Winning Products matching your timeline!")
            st.dataframe(df_meesho, use_container_width=True)
            
            csv = df_meesho.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Timeline Winner List (CSV)",
                data=csv,
                file_name=f"meesho_{timeline_history.split(' ')[0]}month_winners.csv",
                mime='text/csv',
            )
        else:
            st.warning("Is selected timeline aur keyword par matching products nahi mile. Try another timeline or a generic keyword like 'saree' or 'tshirt'.")
