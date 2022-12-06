import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
from streamlit_folium import st_folium
import folium
import geopandas as gpd
from folium.plugins import HeatMap
from folium import plugins
from time import sleep

from bsf_package.bsf_logic.design_streamlit import set_page_container_style
from bsf_package.bsf_logic.maps import search_venue, heatmap_venues, display_district
from bsf_package.bsf_logic.filterdata import filtercategory
from bsf_package.bsf_logic.plots import plot_rating_berlin, plot_price_berlin,  plot_hist, plot_count_district

dir_name = os.path.abspath(os.path.dirname(__file__))
location = os.path.join(dir_name, 'clean_b1_veryfinal_categories.csv')
location2 = os.path.join(dir_name, 'neighbourhoods.geojson')

#import data and geojson
data = pd.read_csv(location)
geo_neighbourhoods = gpd.read_file(location2)

def search_venue(df):
    return list(zip(df['lat'], df['lon']))

def heatmap_venues(data):
    map = folium.Map(location=[52.5200, 13.4050], zoom_start=12)
    boroughs_style = lambda x: {'color': 'black', 'opacity': 0.9, 'fillColor': 'green', 'weight': 0.6}
    folium.GeoJson(
      geo_neighbourhoods.geometry,
      style_function=boroughs_style,
      name='geojson'
      ).add_to(map)
    HeatMap(data).add_to(map)
    return map

# problem with loc
# pin map NOT WORKING
def display_district(data, neighbourhood_var):
    if neighbourhood_var == 'Berlin':
        district_df = data
    else:
        district_df = data[data.neighbourhood_group == neighbourhood_var]
        # Create an initial map of Berlin
        # Berlin latitude and longitude values

    latitude = 52.520008
    longitude = 13.404954
    # create map and display it
    berlin_map_district = folium.Map(location=[latitude, longitude], zoom_start=12)
    for i in range(0,len(district_df)):
        folium.Marker(
        location=[district_df.iloc[i]['lat'], district_df.iloc[i]['lon']].add_to(berlin_map_district))
        #popup=district_df.iloc[i]['title'], tooltip='Click for more information').add_to(berlin_map_district)
    return berlin_map_district

# Calculate the amount of store categories per district
def shops_per_district(data, district):
    data = data[data["neighbourhood_group"] == district]
    data["categories_list"] = data.final_categories.apply(lambda x: x[1:-1].split(','))
    data.reset_index(inplace=True)
    data.drop(columns=['index'])
    all_categories = []
    for i in range(len(data)):
        for x in range(len(data.categories_list[i])):
            all_categories.append([data.categories_list[i][x]])
    for i in range(len(all_categories)):
        all_categories[i][0].strip()
        all_categories[i][0] = all_categories[i][0].strip()
    shop_count = {}
    for i in range(len(all_categories)):
        for shop in all_categories[i]:
            if shop in shop_count:
                shop_count[shop] = shop_count[shop] + 1
            else:
                shop_count[shop] = 1

    # TURN THE DICTIONARY INTO A DATAFRAME BEFORE PLOTTING IT

    # Turn the shop_count dictionary into a dataframe
    df = pd.DataFrame.from_dict(shop_count, orient='index')
    # Turn the store category into a column and reset index
    df = df.reset_index(names=['Store Category'])
    # Change the name for the column of Number of stores
    df.rename(columns = {0:'Number of stores'}, inplace = True)
    # Replace unnecessary characters from the dataframe
    df['Store Category'] = df['Store Category'].apply(lambda x: str(x).replace("'", ""))
    df['Store Category'] = df['Store Category'].apply(lambda x: str(x).replace('"', ""))
    # If you want the df in aphabetical order uncomment the next line
    # df.sort_values('Store Category', ascending=True)
    # If you want the df in ascending order (based on Number of stores) uncomment the next line
    df.sort_values('Number of stores', ascending = True)
    # If you want the df in descending order (based on Number of stores) uncomment the next line
    # df.sort_values('Number of stores', ascending = False)

    # NOW PLOT THE DATAFRAME
    store_category = df['Store Category']
    num_stores = df['Number of stores']
    # Figure Size
    fig, ax = plt.subplots(figsize =(16, 9))
    # Horizontal Bar Plot
    ax.barh(store_category, num_stores)
    # Remove axes splines
    for s in ['top', 'bottom', 'left', 'right']:
        ax.spines[s].set_visible(False)
    # Remove x, y Ticks
    ax.xaxis.set_ticks_position('none')
    ax.yaxis.set_ticks_position('none')
    # Add padding between axes and labels
    ax.xaxis.set_tick_params(pad = 5)
    ax.yaxis.set_tick_params(pad = 10)
    # Add x, y gridlines
    ax.grid(b = True, color ='grey',
            linestyle ='-.',
            linewidth = 0.5,
            alpha = 0.2)
    # Show top values
    #ax.invert_yaxis()

    # Add annotation to bars
    for i in ax.patches:
        plt.text(i.get_width()+0.2, i.get_y()+0.2,
                 str(round((i.get_width()), 2)),
                 fontsize = 10, fontweight ='bold',
                 color ='grey')

    # Add Plot Title
    ax.set_title(f"Number of store categories in district",
                 loc ='center' )

    # Show Plot
    plt.show()
    return st.pyplot(plt)

# filter shop within list
def filtercategory(data, choice_shop):
    if choice_shop == 'All shops':
        df = df
    else:
        mask = data.final_categories.apply(lambda x: any(item for item in \
            choice_shop if item in x)) # filter df if any category matching
        df = data[mask]
    return df


### HERE THE APP BEGINS ###
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
if choice_district == 'Berlin':
    choice_shop = st.sidebar.selectbox('Choose a shop type', ('Baby clothing store', 'Bag store','Beauty supplies store','Bridal store',"Children's clothing store",
 'Costume store','Department store','Emboidery & Clothing alternation store','Fashion accessories store','Footwear store','Formal wear store',
 'General clothing store','Hat store','Home supplies store','Jeans store','Jewelry store','Leather store','Maternity store',
 "Men's clothing store",'Optical store','Outlet store','Pet store','Plus size clothing store','Second hand clothing store',
 'Shopping mall','Sportswear store','Swimwear store','T-shirt store','Underwear store','Vintage clothing store',
 'Wholesalers store',"Women's clothing store",'Work clothing store','Youth clothing store'))
else:
    choice_shop = st.sidebar.selectbox('Choose a shop type', ('Baby clothing store', 'Bag store','Beauty supplies store','Bridal store',"Children's clothing store",
 'Costume store','Department store','Emboidery & Clothing alternation store','Fashion accessories store','Footwear store','Formal wear store',
 'General clothing store','Hat store','Home supplies store','Jeans store','Jewelry store','Leather store','Maternity store',
 "Men's clothing store",'Optical store','Outlet store','Pet store','Plus size clothing store','Second hand clothing store',
 'Shopping mall','Sportswear store','Swimwear store','T-shirt store','Underwear store','Vintage clothing store',
 'Wholesalers store',"Women's clothing store",'Work clothing store','Youth clothing store', 'All shops'))

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
    m = folium.Map(location=[52.5200, 13.405], zoom_start=12) # show map if no button pressed
    st_folium(m, width=1500, height=600)

if st.session_state.button_on:
    empty()
    if choice_district == 'Berlin':
        choice_shop = [choice_shop] #need it in list format for function filtercategory
        df = filtercategory(data, choice_shop)
        choice_shop = choice_shop[0] #take only string
        amount_shops = len(df) # amount of shops of that type in the selected district and category
        header = f'{amount_shops} establishments are classified as {choice_shop.capitalize()} in Berlin.'
        title = f'<p style="font-family:sans-serif; color:Black; font-size: 30px;"><b>{header}<b></p>'
        st.markdown(title, unsafe_allow_html=True)

        dist = search_venue(df)
        heat = heatmap_venues(dist)
        st_folium(heat,width=1400, height=400)
        #pin = display_district(df, choice_district)
        #st_folium(pin,width=1000, height=400)
        st.checkbox('Change to pinmap')

        #col3, col4 = st.columns([5,5]) # here adjust width of columns

        #with col3:
        red = df[['neighbourhood_group','our_rating']].groupby('neighbourhood_group', as_index = False).mean()
        #plot_rating_berlin(red, choice_shop)
        fig = plt.figure(figsize=(15, 10))
        sns.set(font_scale=2)
        sns.set_theme(style="white",font="sans-serif", palette="Set2", rc={"font.size":20,"axes.titlesize":30})
        sns.barplot(y = 'neighbourhood_group', x = 'our_rating', data = red, ci=False, orient = 'h').set(title=f'Mean rating of {choice_shop.capitalize()}s in each district',xlabel ="", ylabel = "")
        plt.xlim(0, 5)
        plt.tick_params(axis='both', which='major', labelsize=20)
        st.pyplot(fig)

        #with col4:
         #   plot_price_berlin(df, choice_shop)
         #plot the price (#### dont plot if 0!!!)
        df['€'] = df.price.map({"€": 1,"€€":0,"€€€":0}).fillna(0)
        df['€€'] = df.price.map({"€": 0,"€€":1,"€€€":0}).fillna(0)
        df['€€€'] = df.price.map({"€": 0,"€€":0,"€€€":1}).fillna(0)
        x_price = df.neighbourhood_group.unique().tolist()
        y_price_cheap = df.groupby(['neighbourhood_group'],as_index=False).sum()['€'].tolist()
        y_price_med = df.groupby(['neighbourhood_group'],as_index=False).sum()['€€'].tolist()
        y_price_exp = df.groupby(['neighbourhood_group'],as_index=False).sum()['€€€'].tolist()
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

    else: # if choose a district


        if choice_shop == 'All shops':
            df = data[data["neighbourhood_group"] == choice_district]
            choice_shop = [choice_shop] #need it in list format for function filtercategory
            choice_shop = choice_shop[0] #take only string
            amount_shops = len(df) # amount of shops of that type in the selected district and category
            #col1, col2 = st.columns([10,1])
            #with col1:
            #st.header(f'{amount_shops} establishments categorize as clothing shops in {choice_district}') # uppercase the shop type
            st.info(f'{amount_shops} establishments categorize as clothing shops in {choice_district}.')

            dist = search_venue(df)
            heat = heatmap_venues(dist)
            st_folium(heat,width=1400, height=400)
            shops_per_district(data, choice_district)

        if choice_shop != 'All shops':
            df = data[data["neighbourhood_group"] == choice_district]
            choice_shop = [choice_shop] #need it in list format for function filtercategory
            df = filtercategory(df, choice_shop)
            choice_shop = choice_shop[0] #take only string
            amount_shops = len(df) # amount of shops of that type in the selected district and category

            if amount_shops > 0:
                #col1, col2 = st.columns([6,2]) # here adjust width of columns
                #with col1:
                #header = f'{amount_shops} establishments are classified as {choice_shop.capitalize()} in {choice_district}.'
                #title = f'<p style="font-family:sans-serif; color:Black; font-size: 30px;"><b>{header}<b></p>'
                #st.markdown(title, unsafe_allow_html=True)
                if amount_shops > 1:
                    st.info(f'{amount_shops} establishments are classified as {choice_shop.capitalize()} in {choice_district}.')
                elif amount_shops == 1:
                    st.info(f'{amount_shops} establishment is classified as {choice_shop.capitalize()} in {choice_district}.')


                dist = search_venue(df)
                heat = heatmap_venues(dist)
                st_folium(heat,width=1400, height=400)

                #with col2:
                mean_rat = np.round(df['our_rating'].mean(),2)

                #message1 = f'- The mean rating for {choice_shop.capitalize()}s in {choice_district} is of {mean_rat} stars.'
                #title1 = f'<p style="font-family:sans-serif; color:Black; font-size: 20px;">{message1}</p>'
                #st.markdown(title1, unsafe_allow_html=True)
                st.success(f'- The mean rating for {choice_shop.capitalize()}s in {choice_district} is of {mean_rat} stars.')

                # price info
                cheap_shops = len(df[df['price'] == '€'])
                med_shops = len(df[df['price'] == '€€'])
                exp_shops = len(df[df['price'] == '€€€'])
                rest = df['price'].isna().sum()

                message2 = f'- There are {cheap_shops} low-price shops, {med_shops} medium-price shops and {exp_shops} high-price shops in the district. (Price information is not yet available for {rest} shops.)'
                #title2 = f'<p style="font-family:sans-serif; color:Black; font-size: 20px;">{message2}</p>'
                #st.markdown(title2, unsafe_allow_html=True)
                st.warning(message2)

                #plot_hist(df, choice_shop, choice_district)
                col1, col2 = st.columns([5,5]) # here adjust width of columns

                with col1:
                    fig = plt.figure(figsize=(4, 3))
                    sns.set_theme(style="white",font="sans-serif", palette="Set2", rc={"font.size":20,"axes.titlesize":30})
                    sns.distplot(df['our_rating'], bins = 5, kde=False, hist_kws={'range':(0,5)}, color = 'blue')
                #sns.title(f'Distribution of ratings of establishments selling {choice_shop.capitalize()}s in {choice_district}', fontsize=35)
                    st.pyplot(fig)


            else:
                st.info(f'There are no establishments categorized as {choice_shop.capitalize()} in {choice_district}.')


if st.session_state.gap_on:
    empty()
    st.markdown("Gap analysis in here")
