import streamlit as st
from streamlit_option_menu import option_menu
import mysql.connector
import pandas as pd

# MySQL Connection Setup
con = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Kloud@123",
    autocommit=True,
    auth_plugin='mysql_native_password'
)

mycursor = con.cursor()
mycursor.execute("USE REDBUS")

query = "SELECT * FROM bus_routes;"

# Load data into a dataframe
try:
    df = pd.read_sql_query(query, con)
except Exception as e:
    st.error("Error loading data from database: {}".format(e))
finally:
    con.close()

# Sidebar menu
with st.sidebar:
    selected = option_menu(
        menu_title="Menu",
        options=["Home", "Select Bus"],
        icons=["house-door-fill", "bus-front"],
        menu_icon="columns-gap",
        default_index=0
    )

st.logo("/home/blockchain/Downloads/Redbus project/RedBus Logo.png")

if selected == "Home":
    st.header("Welcome to Redbus Guvi Project")
    st.image("/home/blockchain/Downloads/Redbus project/Beautifully Simple.gif")


elif selected == "Select Bus":
    st.header("Select a Bus")

    if not df.empty:
        # Dropdown for AC/Non-AC
        ac_types = ["All", "AC", "Non AC"]
        col1, col2, col3 = st.columns(3)

        with col3:
            selected_ac_type = st.selectbox("Select AC Type", ac_types)

        # Dropdown for Sleeper/Seater/Semisleeper
        allowed_bus_types = ["Sleeper", "Seater", "Semisleeper"]
        filtered_bus_types = ["All"] + allowed_bus_types

        with col2:
            selected_bus_type = st.selectbox("Select seat Type", filtered_bus_types)

        # Dropdown for route selection
        unique_bus_names = df['route_name'].dropna().unique()

        with col1:
            selected_bus = st.selectbox("Choose a Bus", unique_bus_names)

        # Set the min and max price based on the selected bus
        if selected_bus:
            filtered_data = df[df['route_name'] == selected_bus]

            # Get the min and max prices for the selected bus route
            min_price = filtered_data['price'].min()
            max_price = filtered_data['price'].max()

            # Set the slider with dynamic min and max values
            with col2:
                selected_price = st.slider("Select price range", min_value=min_price, max_value=max_price, value=(min_price, max_price))

        # Additional filters for rating, seat types, and other criteria
        with col1:
            bus_rating = ["All", "1-2", "2-3", "3-4", "4-5"]
            selected_rating = st.selectbox("Select rating", bus_rating)

        # Filter data based on selections
        if selected_bus:
            filtered_data = df[df['route_name'] == selected_bus]

            # Filter based on AC/Non-AC
            if selected_ac_type != "All":
                if selected_ac_type == "AC":
                    filtered_data = filtered_data[filtered_data['bustype'].str.contains("AC", case=False) & ~filtered_data['bustype'].str.contains("Non AC", case=False)]
                elif selected_ac_type == "Non AC":
                    filtered_data = filtered_data[filtered_data['bustype'].str.contains("Non AC", case=True)]

            # Filter based on Sleeper/Seater/Semisleeper
            if selected_bus_type != "All":
                filtered_data = filtered_data[filtered_data['bustype'].str.contains(selected_bus_type, case=False)]

            # Rating filter logic
            if selected_rating != "All":
                if selected_rating == "1-2":
                    filtered_data = filtered_data[(filtered_data['star_rating'] >= 1) & (filtered_data['star_rating'] < 2)]
                elif selected_rating == "2-3":
                    filtered_data = filtered_data[(filtered_data['star_rating'] >= 2) & (filtered_data['star_rating'] < 3)]
                elif selected_rating == "3-4":
                    filtered_data = filtered_data[(filtered_data['star_rating'] >= 3) & (filtered_data['star_rating'] < 4)]
                elif selected_rating == "4-5":
                    filtered_data = filtered_data[(filtered_data['star_rating'] >= 4) & (filtered_data['star_rating'] <= 5)]

            # Price filter logic
            if selected_price:
                min_price, max_price = selected_price
                filtered_data = filtered_data[(filtered_data['price'] >= min_price) & (filtered_data['price'] <= max_price)]

            # Display results
            if not filtered_data.empty:
                st.write("**Details for selected bus:**")
                
                # Extract the route link and display it
                route_link = filtered_data['route_link'].iloc[0]
                st.markdown(f"**Link to book bus ticket = [{route_link}]({route_link})**", unsafe_allow_html=True)
                
                # Drop the route_link column before displaying the dataframe
                filtered_data_without_link = filtered_data.drop(columns=['route_link', 'departing_time', 'reaching_time', 'id'])
                st.dataframe(filtered_data_without_link)
            else:
                st.warning("No data matches the selected criteria.")
    else:
        st.warning("No data available in the table.")
