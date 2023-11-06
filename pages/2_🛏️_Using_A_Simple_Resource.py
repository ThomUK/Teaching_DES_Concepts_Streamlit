'''
A Streamlit application based on Monks and 

Allows users to interact with an increasingly more complex treatment simulation 
'''
import streamlit as st

from helper_functions import read_file_contents, add_logo, mermaid
from model_classes import *
# from st_pages import show_pages_from_config, add_page_title

# Set page parameters
st.set_page_config(
     page_title="Using a Simple Resource",
     layout="wide",
     initial_sidebar_state="expanded",
 )

# add_page_title()

# show_pages_from_config()

# Add the logo
add_logo()
# Import the stylesheet
with open("style.css") as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)


st.title("Discrete Event Simulation Playground")
st.subheader("Using a Simple Resource: Sending Patients to be Treated")

tab1, tab2, tab3 = st.tabs(["Introduction", "Exercise", "Playground"])

with tab1:

    st.markdown(
        """
        Now, it's all well and good having patients arrive, but at the moment there is no-one and nowhere to see them!

    We need to add our first resource.

    Resources exist inside our simulation, and can be nurses, rooms, ambulances - whatever we need them to be. 

    When someone reaches the front of the queue, they will be allocated to a resource that is currently free.
    They will hold onto this resource for as long as they need it, and then they will let go of it and move on to the next part of the process.

    This means resources can continue to be reused again and again in the system, unlike our arrivals.

    So for now, let's make it so that when someone arrives, they need to be treated, and to do this they will need a resource.
    For now, we're keeping it simple - let's assume each nurse has a room that they treat people in. They always stay in this room, and as soon as a patient has finished being treated, the patient will leave and the nurse (and room) will become available again.

    This means we just have one type of resource to worry about. 
    """
    )

    mermaid(height=175, code=
    """
            %%{ init: { 'flowchart': { 'curve': 'step' } } }%%
            %%{ init: {  'theme': 'base', 'themeVariables': {'lineColor': '#b4b4b4'} } }%%
            flowchart LR
            A[Arrival]----> B[Treatment]
            B -.-> C([Nurse/Cubicle\n<b>RESOURCE</b>])
            C -.-> B
            B ----> F[Discharge]

            classDef default font-size:18pt,font-family:lexend;
            linkStyle default stroke:white;
        """
    )

    st.markdown(read_file_contents('resources/first_simple_resource.md'))

with tab2:
    st.markdown(read_file_contents('resources/first_simple_resource_exercise.md'))


with tab3:
    col1, col2 = st.columns([0.5, 1.5])

    with col1:
        nurses = st.slider("How Many Rooms/Nurses Are Available?", 1, 50, step=1, value=5)

        consult_time = st.slider("How long (in minutes) does a consultation take on average?",
                                    5, 60, step=5, value=20)

        consult_time_sd = st.slider("How much (in minutes) does the time for a consultation usually vary by?",
                                    5, 30, step=5, value=10)

        
        with st.expander("Previous Parameters"):

            st.markdown("If you like, you can edit these parameters too!")

            seed = st.number_input("Set a random number for the computer to start from",
                            1, 100000,
                            step=1, value=42)
            
            n_reps = st.slider("How many times should the simulation run?",
                            1, 50,
                            step=1, value=10)
            run_time_days = st.slider("How many days should we run the simulation for each time?",
                                    1, 100,
                                    step=1, value=15)

        
            mean_arrivals_per_day = st.slider("How many patients should arrive per day on average?",
                                            10, 1000,
                                            step=5, value=300)

    with col2:
        st.text("Placeholder")

