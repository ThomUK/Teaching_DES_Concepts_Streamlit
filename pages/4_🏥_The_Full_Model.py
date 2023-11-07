'''
A Streamlit application based on Monks and 

Allows users to interact with an increasingly more complex treatment simulation 
'''
import streamlit as st
import pandas as pd

from helper_functions import read_file_contents, add_logo, mermaid
from model_classes import Scenario, multiple_replications
from output_animation_functions import reshape_for_animations, animate_queue_activity_bar_chart, animate_activity_log
# from st_pages import show_pages_from_config, add_page_title
import plotly.express as px

st.set_page_config(
     page_title="The Full Model",
     layout="wide",
     initial_sidebar_state="expanded",
 )

# Initialise session state
if 'session_results' not in st.session_state:
    st.session_state['session_results'] = []

# add_page_title()

# show_pages_from_config()

add_logo()

with open("style.css") as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

## We add in a title for our web app's page
st.title("Discrete Event Simulation Playground")
st.subheader("How can we optimise the full system?")



tab1, tab2, tab3, tab4 = st.tabs(["Introduction", "Exercises", "Playground", "Compare Scenario Outputs"])
with tab1:
    st.markdown("""
                So now we have explored every component of the model:
                - Generating arrivals
                - Generating and using resources
                - Sending people down different paths 
                
                So now let's create a version of the model that uses all of these aspects. 

                For now, we won't consider nurses separately - we will assume that each nurse on shift has one room that is theirs to always use.
                """
                )
    
    mermaid(height=600, code=
    """
    %%{ init: { 'flowchart': { 'curve': 'step' } } }%%
    %%{ init: {  'theme': 'base', 'themeVariables': {'lineColor': '#b4b4b4'} } }%%
    flowchart LR
        A[Arrival] --> BX[Triage]
        BX -.-> T([Triage Bay\n<b>RESOURCE</b>])
        T -.-> BX

        BX --> BY{Trauma or non-trauma}
        BY ----> B1{Trauma Pathway} 
        BY ----> B2{Non-Trauma Pathway}
        
        B1 --> C[Stabilisation]
        C --> E[Treatment]
      
        B2 --> D[Registration]
        D --> G[Examination]

        G --> H[Treat?]
        H ----> F 

        H --> I[Non-Trauma Treatment]
        I --> F 

        C -.-> Z([Trauma Room\n<b>RESOURCE</b>])
        Z -.-> C

        E -.-> Y([Cubicle - 1\n<b>RESOURCE</b>])
        Y -.-> E

        D -.-> X([Clerks\n<b>RESOURCE</b>])
        X -.-> D

        G -.-> W([Exam Room\n<b>RESOURCE</b>])
        W -.-> G

        I -.-> V([Cubicle - 2\n<b>RESOURCE</b>])
        V -.-> I

        E ----> F[Discharge]

        classDef ZZ1 fill:#8B5E0F,font-family:lexend, color:#FFF
        classDef ZZ2 fill:#5DFDA0,font-family:lexend
        classDef ZZ2a fill:#02CD55,font-family:lexend, color:#FFF
        classDef ZZ3 fill: #D45E5E,font-family:lexend
        classDef ZZ3a fill: #932727,font-family:lexend, color:#FFF
        classDef ZZ4 fill: #611D67,font-family:lexend, color:#FFF
        classDef ZZ5 fill:#47D7FF,font-family:lexend
        classDef ZZ5a fill:#00AADA,font-family:lexend

        class A ZZ1
        class C,E ZZ2
        class D,G ZZ3
        class X,W ZZ3a
        class Z,Y ZZ2a
        class I,V ZZ4
        class BX ZZ5
        class T ZZ5a
        ;
    """
)
    
with tab2:
    st.header("Things to Try")

    st.markdown(
        """
        - Try changing the number of resources you have available so that your system has an average utilisation of over 80% while meeting the 4 hour target 90% of the time.
        - Imagine you have a maximum of 15 rooms and cubicles. With a probability that a new arrival is a trauma patient of 0.3, and the probability that a non-trauma patient will need treament of 0.7, what is the best configuration of rooms you can find to keep the average treatment time low across both pathways?
        """
    )

with tab3:
    
    # n_triage: int
    #         The number of triage cubicles

    # n_reg: int
    #     The number of registration clerks

    # n_exam: int
    #     The number of examination rooms

    # n_trauma: int
    #     The number of trauma bays for stablisation

    # n_cubicles_1: int
    #     The number of non-trauma treatment cubicles

    # n_cubicles_2: int
    #     The number of trauma treatment cubicles

    # non_trauma_treat_p: float
    #     Probability non trauma patient requires treatment

    # prob_trauma: float
    #     probability that a new arrival is a trauma patient.
    

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.subheader("Triage")
        n_triage = st.slider("Number of Triage Cubicles", 1, 10, step=1, value=3)
        prob_trauma = st.slider("Probability that a new arrival is a trauma patient", 0.0, 1.0, step=0.01, value=0.3)

    with col2:
        st.subheader("Trauma Pathway")
        n_trauma = st.slider("Number of Trauma Bays for Stabilisation", 1, 10, step=1, value=6)
        n_cubicles_2 = st.slider("Number of Treatment Cubicles for Trauma", 1, 10, step=1, value=6)

    with col3:
        st.subheader("Non-Trauma Pathway")
        n_reg = st.slider("Number of Registration Cubicles", 1, 10, step=1, value=2)
        n_exam = st.slider("Number of Examination Rooms for non-trauma patients", 1, 10, step=1, value=3)

    with col4: 
        st.subheader("Non-trauma Treatment")
        n_cubicles_1 = st.slider("Number of Treatment Cubicles for Non-Trauma", 1, 10, step=1, value=2)
        non_trauma_treat_p = st.slider("Probability that a non-trauma patient will need treatment", 0.0, 1.0, step=0.01, value=0.7)

    st.write("Total rooms in use is {}".format(n_cubicles_1+n_cubicles_2+n_exam+n_trauma+n_triage+n_reg))

    args = Scenario(
        random_number_set=42,
                 n_triage=n_triage,
                 n_reg=n_reg,
                 n_exam=n_exam,
                 n_trauma=n_trauma,
                 n_cubicles_1=n_cubicles_1,
                 n_cubicles_2=n_cubicles_2,
                 non_trauma_treat_p=non_trauma_treat_p,
                 prob_trauma=prob_trauma)

    n_reps = 8

    # A user must press a streamlit button to run the model
    button_run_pressed = st.button("Run simulation")
    
    
    if button_run_pressed:

        # add a spinner and then display success box
        with st.spinner('Simulating the minor injuries unit...'):
            # run multiple replications of experment
            detailed_outputs = multiple_replications(
                args,
                n_reps=n_reps,
                rc_period=30*60*24,
                return_detailed_logs=True
            )

            results = pd.concat([detailed_outputs[i]['results']['summary_df'].assign(rep= i+1)
                                        for i in range(n_reps)]).set_index('rep')
            
            full_event_log = pd.concat([detailed_outputs[i]['results']['full_event_log'].assign(rep= i+1)
                                        for i in range(n_reps)])
            

            # print(len(st.session_state['session_results']))
            # results_for_state = pd.DataFrame(results.median()).T.drop(['Rep'], axis=1)
            results_for_state = results
            original_cols = results_for_state.columns.values
            results_for_state['Triage\nCubicles'] = args.n_triage
            results_for_state['Registration\nClerks'] = args.n_reg
            results_for_state['Examination\nRooms'] = args.n_exam
            results_for_state['Non-Trauma\nTreatment Cubicles'] = args.n_cubicles_1
            results_for_state['Trauma\nStabilisation Bays'] = args.n_trauma
            results_for_state['Trauma\nTreatment Cubicles'] = args.n_cubicles_2
            results_for_state['Probability patient\nis a trauma patient'] = args.prob_trauma
            results_for_state['Probability non-trauma patients\nrequire treatment'] = args.non_trauma_treat_p
            results_for_state['Model Run'] = len(st.session_state['session_results']) + 1
            results_for_state['Random Seed'] = args.random_number_set

            # Reorder columns
            column_order = ['Model Run', 'Triage\nCubicles', 'Registration\nClerks', 'Examination\nRooms',
                            'Non-Trauma\nTreatment Cubicles', 'Trauma\nStabilisation Bays', 
                            'Trauma\nTreatment Cubicles', 'Probability patient\nis a trauma patient',
                            'Probability non-trauma patients\nrequire treatment', 'Random Seed'
                            ] + list(original_cols)

            results_for_state = results_for_state[column_order]


            current_state = st.session_state['session_results']

            current_state.append(results_for_state)

            st.session_state['session_results'] = current_state

            # print(len(st.session_state['session_results']))

            full_utilisation_audit = pd.concat([detailed_outputs[i]['results']['utilisation_audit'].assign(Rep= i+1)
                                    for i in range(n_reps)])
            
            animation_dfs_queue = reshape_for_animations(
                full_event_log[
                    (full_event_log['rep']==1) &
                    ((full_event_log['event_type']=='queue') | (full_event_log['event_type']=='arrival_departure'))
                ]
            )

            animation_dfs_log = reshape_for_animations(
                full_event_log=full_event_log[
                    (full_event_log['rep']==1) &
                    ((full_event_log['event_type']=='queue') | (full_event_log['event_type']=='resource_use')  | (full_event_log['event_type']=='arrival_departure'))
                ],
                every_x_minutes=5
            )
        # st.write(results.reset_index())

        # st.write(pd.wide_to_long(results, stubnames=['util', 'wait'], i="rep", j="metric_type",         
        #                          sep='_', suffix='.*'))

        # st.write(results.reset_index().melt(id_vars="rep").set_index('variable').filter(like="util", axis=0))

        # Add in a box plot showing utilisation
        
        tab_playground_results_1, tab_playground_results_2, tab_playground_results_3, tab_playground_results_4, tab_playground_results_5  = st.tabs(['Utilisation and Wait Metrics',
                                                                                        'Animated Model',
                                                                                        'Animated Resource Utilisation',
                                                                                        'Animated Queue Sizes',
                                                                                        'Utilisation over Time'])
        
        # st.subheader("Look at Average Results Across Replications")

        with tab_playground_results_1:
            

            col_res_1, col_res_2 = st.columns(2)

            with col_res_1:
                st.subheader("Utilisation Metrics")

                st.plotly_chart(px.box(
                    results.reset_index().melt(id_vars="rep").set_index('variable').filter(like="util", axis=0).reset_index(), 
                    y="variable", 
                    x="value",
                    points="all",
                    range_x=[0, 1]),
                    use_container_width=True
                    )
                
                st.write(results.filter(like="util", axis=1).merge(results.filter(like="throughput", axis=1),left_index=True,right_index=True))
                
            with col_res_2:
                st.subheader("Wait Metrics")
                # Add in a box plot showing waits
                st.plotly_chart(px.box(
                    results.reset_index().melt(id_vars="rep").set_index('variable').filter(like="wait", axis=0).reset_index(), 
                    y="variable", 
                    x="value",
                    points="all"),
                    use_container_width=True
                    )

                st.write(results.filter(like="wait", axis=1)
                        .merge(results.filter(like="throughput", axis=1), 
                                left_index=True, right_index=True))


        with tab_playground_results_2:
            
            event_position_df = pd.DataFrame([
                # {'event': 'arrival', 'x':  10, 'y': 250, 'label': "Arrival" },
                
                # Triage - minor and trauma                
                {'event': 'triage_wait_begins', 'x':  160, 'y': 400, 'label': "Waiting for<br>Triage"  },
                {'event': 'triage_begins', 'x':  160, 'y': 315, 'resource':'n_triage', 'label': "Being Triaged" },
            
                # Minors (non-trauma) pathway 
                {'event': 'MINORS_registration_wait_begins', 'x':  310, 'y': 580, 'label': "Waiting for<br>Registration"  },
                {'event': 'MINORS_registration_begins', 'x':  300, 'y': 510, 'resource':'n_reg', 'label':'Being<br>Registered'  },

                {'event': 'MINORS_examination_wait_begins', 'x':  475, 'y': 580, 'label': "Waiting for<br>Examination"  },
                {'event': 'MINORS_examination_begins', 'x':  465, 'y': 510, 'resource':'n_exam', 'label': "Being<br>Examined" },

                {'event': 'MINORS_treatment_wait_begins', 'x':  640, 'y': 580, 'label': "Waiting for<br>Treatment"  },
                {'event': 'MINORS_treatment_begins', 'x':  630, 'y': 510, 'resource':'n_cubicles_1', 'label': "Being<br>Treated" },

                # Trauma pathway
                {'event': 'TRAUMA_stabilisation_wait_begins', 'x': 300, 'y': 90, 'label': "Waiting for<br>Stabilisation" },
                {'event': 'TRAUMA_stabilisation_begins', 'x': 300, 'y': 210, 'resource':'n_trauma', 'label': "Being<br>Stabilised" },

                {'event': 'TRAUMA_treatment_wait_begins', 'x': 630, 'y': 90, 'label': "Waiting for<br>Treatment" },
                {'event': 'TRAUMA_treatment_begins', 'x': 630, 'y': 210, 'resource':'n_cubicles_2', 'label': "Being<br>Treated" }
            ])

            st.plotly_chart(animate_activity_log(
                    animation_dfs_log['full_patient_df'],
                    event_position_df = event_position_df,
                    scenario=args,
                    include_play_button=True,
                    return_df_only=False,
                    plotly_height=900,
                    plotly_width=1600,
                    override_x_max=700,
                    override_y_max=675,
                    icon_and_text_size=24,
                    display_stage_labels=False,
                    wrap_queues_at=10,
                    add_background_image="https://raw.githubusercontent.com/Bergam0t/Teaching_DES_Concepts_Streamlit/main/resources/Full%20Model%20Background%20Image%20-%20Horizontal%20Layout.drawio.png",
            ), 
            use_container_width=False)

            # Uncomment if debugging animated event log
            # st.write(
            #     animate_activity_log(
            #         animation_dfs_log['full_patient_df'],
            #         event_position_df = event_position_df,
            #         scenario=args,
            #         include_play_button=True,
            #         return_df_only=True
            # ).sort_values(['patient', 'minute'])
            # )

            # st.write(
            #          animation_dfs_log['full_patient_df'].sort_values(['patient', 'minute'])
            # )

        # st.write(animation_dfs_log['full_patient_df'].sort_values('minute'))


        with tab_playground_results_3:
            st.markdown("Placeholder")

        with tab_playground_results_4:

            st.plotly_chart(
                
                animate_queue_activity_bar_chart(
                    minute_counts_df_complete=animation_dfs_queue['minute_counts_df_complete'],
                    event_order= ['arrival', 
                                  'triage_wait_begins', 

                                  'MINORS_registration_wait_begins',            
                                  'MINORS_examination_wait_begins',
                                  

                                  'TRAUMA_stabilisation_wait_begins', 
                                  
                                  'MINORS_treatment_wait_begins', 
                                  'TRAUMA_treatment_wait_begins'
                                    ]
                    ),
                    
                    use_container_width=True
                    )
            
            

        with tab_playground_results_5:
            tab1a, tab1b = st.tabs(["Facet by Replication", "Facet by Resource"])

            with tab1a:
                fig_util_line_chart = px.line(full_utilisation_audit,
                        x="simulation_time",
                        y="number_utilised", 
                        color= "resource_name",
                        facet_col="Rep", 
                        facet_col_wrap=2,
                        height=900
                        )
                fig_util_line_chart.update_traces(line=dict(width=0.5))
                # write(results.filter(like="wait", axis=1).merge(results.filter(like="util", axis=1),left_index=True,right_index=True).reset_index().melt(id_vars=["rep"]))

                st.plotly_chart(
                    fig_util_line_chart,
                    use_container_width=True
                )

                with tab1b:
                    fig_util_line_chart = px.line(full_utilisation_audit,
                        x="simulation_time",
                        y="number_utilised", 
                        color= "Rep",
                        facet_col="resource_name", 
                        facet_col_wrap=1,
                        height=900
                        )
                    fig_util_line_chart.update_traces(line=dict(width=0.5))
                    # write(results.filter(like="wait", axis=1).merge(results.filter(like="util", axis=1),left_index=True,right_index=True).reset_index().melt(id_vars=["rep"]))

                    st.plotly_chart(
                        fig_util_line_chart,
                        use_container_width=True
                    )



        

# results_pivoted = pd.concat([results.filter(like="wait", axis=1).reset_index().melt(id_vars=["rep"]).assign(what="Wait"),
#            results.filter(like="util", axis=1).reset_index().melt(id_vars=["rep"]).assign(what="Utilisation")])

# results_pivoted['metric_group'] = results_pivoted['variable'].str.extract("(\d{2})")

# st.plotly_chart(

#             px.box(
#                 results.filter(like="wait", axis=1) \
#                     .merge(results.filter(like="util", axis=1),left_index=True,right_index=True) \
#                     .reset_index() \
#                     .melt(id_vars=["rep"])
                
#             )

#         )


with tab4:
    if len(st.session_state['session_results']) > 0:

        all_run_results = pd.concat(st.session_state['session_results'])

        st.subheader("Look at Average Results Across Replications")
        col_a, col_b = st.columns(2)
        
        with col_a:
            
            # st.write(all_run_results.drop(all_run_results.filter(regex='\d+').columns,axis=1).groupby('Model Run').median().T)
            st.write(all_run_results.groupby('Model Run').median().T)
        with col_b:
            # st.write(all_run_results.filter(regex='\d+', axis=1).groupby('Model Run').median().T)
            st.write("Placeholder")

        col_res_1, col_res_2 = st.columns(2)

        

        with col_res_1:
            st.subheader("Utilisation Metrics")

            st.plotly_chart(px.box(
                all_run_results.reset_index().melt(id_vars=["Model Run", "rep"]).set_index('variable').filter(like="util", axis=0).reset_index(), 
                y="variable", 
                x="value",
                color="Model Run",
                points="all",
                range_x=[0, 1]),
                use_container_width=True
                )
            
            # st.write(all_run_results.filter(like="util", axis=1).merge(all_run_results.filter(like="throughput", axis=1),left_index=True,right_index=True))
            
        with col_res_2:
            st.subheader("Wait Metrics")
            # Add in a box plot showing waits
            st.plotly_chart(px.box(
                all_run_results.reset_index().melt(id_vars=["Model Run", "rep"]).set_index('variable').filter(like="wait", axis=0).reset_index(), 
            #                 left_index=True, right_index=True), 
                y="variable", 
                x="value",
                color="Model Run",
                points="all"),
                use_container_width=True
                )

        col_res_3, col_res_4 = st.columns(2)

        with col_res_3:
            st.subheader("Throughput")
            # Add in a box plot showing waits
            st.plotly_chart(px.box(
                all_run_results.reset_index().melt(id_vars=["Model Run", "rep"]).set_index('variable').filter(like="throughput", axis=0).reset_index(),  
                y="variable", 
                x="value",
                color="Model Run",
                points="all"),
                use_container_width=True
                )

            # st.write(all_run_results.filter(like="wait", axis=1)
            #             .merge(all_run_results.filter(like="throughput", axis=1), 
            #                 left_index=True, right_index=True))
    else:
        st.markdown("No scenarios yet run. Go to the 'Playground' tab and click 'Run simulation'.")