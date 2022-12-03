import streamlit as st
from streamlit_folium import st_folium
import folium
import pandas as pd
import geopandas as gpd
from folium.plugins import HeatMap
from time import sleep
import os
import matplotlib.pyplot as plt
import numpy as np
#from bsf_package.bsf_logic.heatmap import search_venue
from bsf_package.bsf_logic.design_streamlit import set_page_container_style
from bsf_package.bsf_logic.maps import search_venue, heatmap_venues
from bsf_package.bsf_logic.filterdata import filtercategory

dir_name = os.path.abspath(os.path.dirname(__file__))
location = os.path.join(dir_name, 'clean_b1_veryfinal_categories.csv')
location2 = os.path.join(dir_name, 'neighbourhoods.geojson')

#import data and geojson
data = pd.read_csv(location)
geo_neighbourhoods = gpd.read_file(location2)

#first step streamlit
st.set_page_config(
    page_title='Shopify',
    layout='wide',
    page_icon=':rocket:'
)

# padding
set_page_container_style(
        max_width = 1100, max_width_100_percent = True,
        padding_top = 0, padding_right = 0, padding_left = 0, padding_bottom = 0
)

# Initialize session state for the button
if 'button_on' not in st.session_state:
    st.session_state.button_on = False
if 'gap_on' not in st.session_state:
    st.session_state.gap_on = False

# function for placeholder
def empty():
    placeholder.empty()
    sleep(0.01)

st.title('Clothify')
#st.sidebar.header('Settings')

st.sidebar.header('Explore shop types in Berlin')
choice_district = st.sidebar.selectbox('Choose a district',  ('Berlin', 'Steglitz - Zehlendorf', 'Mitte', 'Friedrichshain-Kreuzberg',
       'Pankow', 'Charlottenburg-Wilm.', 'Tempelhof - Schöneberg',
       'Neukölln', 'Reinickendorf', 'Spandau', 'Marzahn - Hellersdorf',
       'Treptow - Köpenick', 'Lichtenberg')) # District: list of 13 including Berlin
choice_shop = st.sidebar.selectbox('Choose a shop type', ('Baby clothing', 'Bag shop','Beauty supplies','Bridal store', "Children's clothing",'Costume store','Department store',
 'Emboidery & Clothing alternation','Fashion accessories','Footwear','Formal wear','General clothing store','Hat shop','Home supplies','Jeans shop', 'Jewelry store', 'Leather store','Maternity store',"Men's clothing",'Optical store','Outlet store','Pet store','Plus size clothing','Second hand clothing','Shopping mall','Sportswear','Swimwear','T-shirt shop','Underwear','Vintage clothing store','Wholesalers',"Women's clothing",'Work clothing','Youth clothing'))

if st.sidebar.button("Show results"):
    st.session_state.button_on = True
    st.session_state.gap_on = False

st.sidebar.header('Calculate')
choice_shop2 = st.sidebar.selectbox('Shop type', ('Baby clothing', 'Bag shop','Beauty supplies','Bridal store', "Children's clothing",'Costume store','Department store', 'Emboidery & Clothing alternation','Fashion accessories','Footwear','Formal wear','General clothing store','Hat shop','Home supplies','Jeans shop', 'Jewelry store', 'Leather store','Maternity store',"Men's clothing",'Optical store','Outlet store','Pet store','Plus size clothing','Second hand clothing','Shopping mall','Sportswear','Swimwear','T-shirt shop','Underwear','Vintage clothing store','Wholesalers',"Women's clothing",'Work clothing','Youth clothing'))

if st.sidebar.button('Show gap analysis'):
    st.session_state.gap_on = True
    st.session_state.button_on = False

if st.sidebar.button("Back to Home"):
    st.session_state.button_on = False
    st.session_state.gap_on = False

placeholder = st.empty()

# Main Page
with placeholder.container():
    m= folium.Map(location=[52.5200, 13.405], zoom_start=12) # show map if no button pressed
    st_folium(m, width=1500, height=600)

if st.session_state.button_on:
    empty()
    if choice_district == 'Berlin':
        col1, col2 = st.columns([6,5]) # here adjust width of columns
        choice_shop = [choice_shop] #need it in list format
        df = filtercategory(data, choice_shop)
        choice_shop = choice_shop[0] #take only string
        amount_shops = len(df) # amount of shops of that type

        with col1:
            st.markdown(f'There is a total of {amount_shops} {choice_shop.capitalize()}s /shops in Berlin')
            dist = search_venue(df)
            heat = heatmap_venues(dist)
            st_folium(heat,width=1000, height=400)
            st.checkbox('Change to pinmap')

            red = df[['neighbourhood_group','our_rating']].groupby('neighbourhood_group', as_index = False).mean()

            fig = plt.figure(figsize=(15, 15))
            #st.markdown(x)
            x = red['neighbourhood_group']
            y = red['our_rating']

            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', '#ff7f0e','#e377c2']
            plt.xlim(0,5)
            plt.title(f'Mean rating of {choice_shop.capitalize()}s in each district', fontsize=35)
            plt.barh(x,y,color=colors)
            plt.yticks(fontsize = 30)
            plt.xticks(fontsize = 30)
            st.pyplot(fig)

        with col2:
            berlin_price = df
            berlin_price['€'] = df.price.map({"€": 1,"€€":0,"€€€":0}).fillna(0)
            berlin_price['€€'] = df.price.map({"€": 0,"€€":1,"€€€":0}).fillna(0)
            berlin_price['€€€'] = df.price.map({"€": 0,"€€":0,"€€€":1}).fillna(0)
            x_price = berlin_price.neighbourhood_group.unique().tolist()
            y_price_cheap = berlin_price.groupby(['neighbourhood_group'],as_index=False).sum()['€'].tolist()
            y_price_med = berlin_price.groupby(['neighbourhood_group'],as_index=False).sum()['€€'].tolist()
            y_price_exp = berlin_price.groupby(['neighbourhood_group'],as_index=False).sum()['€€€'].tolist()

            x_axis = np.arange(len(x_price))

            fig2 = plt.figure(figsize=(15, 20))
            plt.barh(x_axis - 0.3, y_price_cheap, label="€", height = 0.3)
            plt.barh(x_axis, y_price_med,label="€€", height = 0.3)
            plt.barh(x_axis + 0.3,y_price_exp, label="€€€", height = 0.3    )
            plt.legend(fontsize = 20)
            plt.yticks(x_axis,x_price, fontsize = 30)
            plt.xticks(fontsize = 30)
            plt.title(f'Price level of {choice_shop.capitalize()}s in each district', fontsize=35)
            st.pyplot(fig2)


    else:
        df = data[data["neighbourhood_group"] == choice_district]
        #st.markdown(len(df1))
        col1, col2 = st.columns([6,5])

        with col1:
            amount_shops = len(df)
            st.header(f'There is a total of {amount_shops} shops in {choice_district}') # uppercase the shop type
            dist = search_venue(df)
            heat = heatmap_venues(dist)
            st_folium(heat,width=500, height=500)
            st.checkbox('Change to pinmap')

        with col2:
            #st.header(f"Mean rating of {choice_shop.capitalize()}s in each district")
            red = df[['neighbourhood_group','our_rating']].groupby('neighbourhood_group', as_index = False).mean()

            fig = plt.figure(figsize=(15, 15))
            #st.markdown(x)
            x = red['neighbourhood_group']
            y = red['our_rating']

            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', '#ff7f0e','#e377c2']
            plt.xlim(0,5)
            plt.title(f'Mean rating of {choice_shop.capitalize()}s in {choice_district}', fontsize=35)
            plt.barh(x,y,color=colors)
            plt.yticks(fontsize = 30)
            plt.xticks(fontsize = 30)
            st.pyplot(fig)


            berlin_price = df[['categoryName', 'lat','lon', 'price','price_cont', 'neighbourhood', 'neighbourhood_group']]
            berlin_price['€'] = df.price.map({"€": 1,"€€":0,"€€€":0}).fillna(0)
            berlin_price['€€'] = df.price.map({"€": 0,"€€":1,"€€€":0}).fillna(0)
            berlin_price['€€€'] = df.price.map({"€": 0,"€€":0,"€€€":1}).fillna(0)
            x_price = berlin_price.neighbourhood_group.unique().tolist()
            y_price_cheap = berlin_price.groupby(['neighbourhood_group'],as_index=False).sum()['€'].tolist()
            y_price_med = berlin_price.groupby(['neighbourhood_group'],as_index=False).sum()['€€'].tolist()
            y_price_exp = berlin_price.groupby(['neighbourhood_group'],as_index=False).sum()['€€€'].tolist()

            x_axis = np.arange(len(x_price))

            fig2 = plt.figure(figsize=(15, 20))
            plt.barh(x_axis - 0.3, y_price_cheap, label="€", height = 0.3)
            plt.barh(x_axis, y_price_med,label="€€", height = 0.3)
            plt.barh(x_axis + 0.3,y_price_exp, label="€€€", height = 0.3    )
            plt.legend(fontsize = 20)
            plt.yticks(x_axis,x_price, fontsize = 30)
            plt.xticks(fontsize = 30)
            plt.title(f'Price level of {choice_shop.capitalize()}s in {choice_district}', fontsize=35)
            st.pyplot(fig2)


if st.session_state.gap_on:
    empty()
    st.markdown("Gap analysis in here")
