import streamlit as st
from plotly import graph_objects as go
import pandas as pd

st.markdown("""# How many people meet your partner criteria where you live?

There are many fish in the sea right? Well if you have too many criteria for your match, you are probably excluding a large number of those fish. Or maybe there are more fish than you expect!

Use this app to discover how many people match your criteria where you live. Data is available for the **100 metro areas with the largest populations** in the United States.

Data was collected from the [US Census American Community Survey](https://www.census.gov/data/developers/data-sets/acs-1year.html). This app originally appeared on [datafantic](https://datafantic.com/are-you-being-too-picky-in-a-partner).
""")

##
## Load data
##
msa = pd.read_csv("msa.csv")
education = pd.read_csv("education.csv")
age_race_gender = pd.read_csv("age_race_gender.csv")

##
## Setup options
##
locations = sorted(age_race_gender['msa'].unique())
races = sorted(age_race_gender['race'].dropna().unique())
ages = ['18 and 19','20-24','25-29','30-34','35-44','45-54','55-64','65-74','75-84']
genders = ['Male','Female']
edus = ['GED or alternative credential', 'Regular high school diploma',
        'Some college, no degree', "Associate's degree",
        "Bachelor's degree", 'Graduate or professional degree']

##
## Convenience functions
##
def string_formatter(item):
    return item.title()

def check_input():
    if len(location) == 0:
        return False
    elif len(edu) == 0:
        return False
    elif len(race) == 0:
        return False
    elif len(age) == 0:
        return False
    else:
        return True

def calculate_funnel(location, gender, edu, race, age, msa, education, age_race_gender):
    # MSA Total Population
    total_pop = msa[msa['NAME'] == location]['population'].iat[0]

    # Population of MSA with specific race.
    msa_race_pop = age_race_gender[(age_race_gender['gender'].isna()) & 
                                   (age_race_gender['age'].isna()) & 
                                   (age_race_gender['msa'] == location) &
                                   (age_race_gender['race'].isin(race))]['value'].sum()

    # Population of MSA with race and gender
    msa_race_gender_pop = age_race_gender[(age_race_gender['gender'] == gender) & 
                                          (age_race_gender['age'].isna()) & 
                                          (age_race_gender['msa'] == location) &
                                          (age_race_gender['race'].isin(race))]['value'].sum()

    # Population of MSA with race, gender, and age
    msa_focused_pop = age_race_gender[(age_race_gender['gender'] == gender) & 
                                      (age_race_gender['age'].isin(age)) & 
                                      (age_race_gender['msa'] == location) &
                                      (age_race_gender['race'].isin(race))]['value'].sum()
    
    # Determine ratio of those above 24 years with specified MSA, gender, race, and education.
    edu_pop = education[(education['msa'] == location) & 
                        (education['gender'] == gender) & 
                        (education['race'].isin(race)) &
                        (education['edu'].isin(edu))]['population'].sum()
    edu_total = education[(education['msa'] == location) & 
                          (education['gender'] == gender) & 
                          (education['race'].isin(race)) &
                          (education['edu'].isna())]['population'].sum()
    ratio = edu_pop / edu_total
    final_pop = round(msa_focused_pop * ratio, 0)
    pop_list = [total_pop, msa_race_pop, msa_race_gender_pop, msa_focused_pop, final_pop]
    return pop_list, ratio

def plot_funnel(pop_list, ratio):
    layout = go.Layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        boxgap=0.25,
        margin=dict(l=0, r=0, t=0, b=0),
        font=dict(
            size=20,  # Set the font size here
        )
    )

    fig = go.Figure(go.Funnel(
            y=['Race', 'Race+Gender', 
            'Race+Gender+Age', 'Race+Gender+Age+Education'],
            x=pop_list[1:],
            textposition = "auto",
            textinfo = "value+text",
            hoverinfo = 'none',
            marker = {"color": "#0048f1"}
            #marker = {"color": "#1f77b4"}
            
            ), 
        layout
        )
    fig.update_traces(texttemplate="%{value:,d}")
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


##
## Layout and text
##
col1, col2 = st.columns(2)

with col1:
    location = st.selectbox(label="City/Metro Area", options=locations, index=58)
    gender = st.selectbox(label='Gender', options=genders)
    edu = st.multiselect(label='Education Level(s)', options=edus)

with col2:
    race = st.multiselect(label='Race(s)', options=races, format_func=string_formatter)
    age = st.multiselect(label='Age Range(s)', options=ages)
    st.text("")
    st.text("")
    button = st.button("Calculate!")

if button:
    if check_input():
        pop_list, ratio = calculate_funnel(location, gender, edu, race, age, msa, education, age_race_gender)
        if 0 in pop_list:
            st.markdown("Woops, it looks like your criteria didn't match enough people. This doesn't mean they don't exist, just that the population is small enough that the Census Bureau doesn't track it.")
        else:
            fig = plot_funnel(pop_list, ratio)
            st.text("")
            st.markdown("---")
            st.markdown("## Your match funnel")
            st.markdown(f"{pop_list[-1]:,.0f} people match your criteria in the {location} from a total population of {pop_list[0]:,.0f}.")

            st.plotly_chart(fig, config= dict(displayModeBar = False), use_container_width=True)


            st.markdown("## Funnel breakdown")
            st.markdown(f"""- {pop_list[0]:,.0f}: Total population of the {location}.""")
            st.markdown(f"""- {pop_list[1]:,.0f}: Population from above that is {" **or** ".join([x.title() for x in race])}.""")
            st.markdown(f"""- {pop_list[2]:,.0f}: Population from above that is also {gender}.""")
            st.markdown(f"""- {pop_list[3]:,.0f}: Population from above that is also {" **or** ".join([x.title() for x in age])}.""")
            st.markdown(f"""- {pop_list[4]:,.0f}: Population from above that also has education of {" **or** ".join([x.capitalize() for x in edu])}. This is estimated to be {round(ratio * 100, 0)}% of the population from above.""")
            st.markdown("""> Note: Education population estimates are derived for those above the age of 24. If your age range(s) include ages below 24, this might not be accurate estimate.""")

            st.markdown("## How does this app work?")
            st.markdown("""Census Bureau creates estimates of the US population for various critieria and at various geographic levels (county, city, and metro areas). This app uses those estimates and filters based on metro area, race, gender, and age ranges.""")
            st.markdown("""For education, detailed estimates by age are not available. To derive these population numbers, I take the percentage of the population (in that location and that matches your selected race(s)) who are over the age of 24 that have your selected education level(s). I then multiply the filtered population (race, gender, and age ranges) by that percentage to estimate the population that have attained your selected education level(s).""")
    else:
        st.markdown("*It looks like you didn't fill in every criteria. Please select at least one option for each criteria.*")



