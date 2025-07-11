import streamlit as st
import fastf1 as ff1
import pandas as pd
from matplotlib import pyplot as plt
from timple.timedelta import strftimedelta
from fastf1.core import Laps
import seaborn as sns
import fastf1.plotting

st.set_page_config(
    page_title="F1 Analysis Dashboard",
    layout="wide"
)

st.sidebar.title("Analysis Options")

with st.sidebar.form("global_filters_form"):
    year = st.number_input("Year:", min_value=2018, max_value=2025)
    gp = st.text_input("Race Name:", placeholder="Enter the Race Name", value="Belgium")
    
    confirm_button = st.form_submit_button("Confirm Selection")

if confirm_button:
    st.session_state.data_confirmed = True
    st.sidebar.success(f"Confirmed: {year} {gp}")

st.title("F1 Data Analysis")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Qualifying Delta", "Sector Times Analysis", "Qualifying Head-to-Head", "Race Lap Distribution", "Acceleration Times"])

if 'data_confirmed' in st.session_state:
    race = ff1.get_session(year, gp, 'R')
    quali = ff1.get_session(year, gp, 'Q')


with tab1:
        st.header(f"Qualifying Delta ({year} {gp} Grand Prix)")
        st.markdown("This plot shows the qualifying gap for each driver to the fastest driver.")

        if st.button("Generate Qualifying Plot"): 
            if 'data_confirmed' not in st.session_state:
                st.warning("Select the Year and the Race Name before generating a plot.")
            else:
                with st.spinner(f"Loading {year} {gp} Qualifying data..."):
                    try:
                        
                        plt.style.use('dark_background')
                        quali.load(telemetry=False, weather=False, messages=False)

                        list_fastest_laps = []
                        for drv in pd.unique(quali.laps['Driver']):
                            drvs_fastest_lap = quali.laps.pick_drivers(drv).pick_fastest()
                            list_fastest_laps.append(drvs_fastest_lap)

                        fastest_laps = Laps(list_fastest_laps).sort_values(by='LapTime').reset_index(drop=True)
                        pole_lap = fastest_laps.pick_fastest()

                        if pd.isna(pole_lap['LapTime']):
                            st.warning("No valid fastest laps found for this session.")
                        else:
                            fastest_laps['LapTimeDelta'] = fastest_laps['LapTime'] - pole_lap['LapTime']
                            team_colors = [ff1.plotting.get_team_color(lap['Team'], session=quali) for _, lap in fastest_laps.iterlaps()]

                            fig, ax = plt.subplots(figsize=(10, 7))
                            ax.barh(fastest_laps.index, fastest_laps['LapTimeDelta'], color=team_colors, edgecolor='grey')
                            ax.set_yticks(fastest_laps.index)
                            ax.set_yticklabels(fastest_laps['Driver'])
                            ax.invert_yaxis()
                            ax.set_axisbelow(True)
                            ax.xaxis.grid(True, which='major', linestyle='--', color='black', zorder=-1000)
                            ax.tick_params(labelsize=12)

                            lap_time_string = strftimedelta(pole_lap['LapTime'], '%m:%s.%ms')
                            plt.suptitle(f"{quali.event['EventName']} {quali.event.year} Qualifying\n"
                                        f"Fastest Lap: {lap_time_string} ({pole_lap['Driver']})")

                            st.session_state.qualifying_delta_plot = fig

                    except Exception as e:
                        st.error(f"An error occurred during plot generation: {e}")
                        st.warning("Ensure the race name is spelled correctly, GP exists and it has been completed for the selected year.")
        
        if 'qualifying_delta_plot' in st.session_state:
            st.pyplot(st.session_state.qualifying_delta_plot)


with tab2:
    st.header(f"Sector Times ({year} {gp} Grand Prix - Qualifying)")
    st.markdown("This plot shows the sector times for each driver across 3 sectors.")

    if st.button("Generate Sector Times Plot"):

        if 'data_confirmed' not in st.session_state:
            st.warning("Select the Year and the Race Name before generating a plot.")
        else:
            with st.spinner(f"Loading Sector Times Data..."):
                try:

                    quali.load()

                    def format_timedelta(td):
                        if pd.isna(td):
                            return ""
                        seconds = td.components.seconds
                        milliseconds = td.components.milliseconds
                        return f"{seconds:01d}.{milliseconds:03d}"

                    quali_laps = quali.laps

                    personal_bests = quali_laps.groupby('Driver').agg({
                        'Sector1Time': 'min',
                        'Sector2Time': 'min',
                        'Sector3Time': 'min',
                    }
                    )

                    sector_1 = personal_bests['Sector1Time'].sort_values()
                    sector_2 = personal_bests['Sector2Time'].sort_values()
                    sector_3 = personal_bests['Sector3Time'].sort_values()


                    driver_colors = {driver: ff1.plotting.get_team_color(quali_laps[quali_laps['Driver'] == driver].iloc[0]['Team'], session=quali)
                                    for driver in quali_laps['Driver'].unique()}

                    s1_colors = [driver_colors[driver] for driver in sector_1.index]
                    s2_colors = [driver_colors[driver] for driver in sector_2.index]
                    s3_colors = [driver_colors[driver] for driver in sector_3.index]


                    plt.style.use('dark_background')

                    x_positions = range(len(sector_1))
                    
                    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15, 12))

                    ax1.set_ylim(bottom=sector_1.dt.total_seconds().min() - 0.2, top=sector_1.dt.total_seconds().max() + 0.2)
                    ax1_container = ax1.bar(sector_1.index, sector_1.dt.total_seconds(), color=s1_colors, width=0.75)

                    fastest_s1_time = sector_1.iloc[0]
                    s1_deltas = sector_1 - fastest_s1_time
                    s1_formatted_times = s1_deltas.apply(format_timedelta)
                    ax1.bar_label(ax1_container, labels=s1_formatted_times, color='white', padding=2, fontsize=11)

                    ax1.set_title("Sector 1", fontsize=14)
                    ax1.set_ylabel("Time (seconds)", fontsize=17, labelpad=15)
                    ax1.spines['top'].set_visible(False)
                    ax1.spines['right'].set_visible(False)
                    ax1.set_xticks(x_positions)
                    ax1.set_xticklabels(sector_1.index, fontsize=12, weight='bold')
                    ax1.tick_params(axis='y', labelsize=15)
                


                    ax2.set_ylim(bottom=sector_2.dt.total_seconds().min() - 0.2, top=sector_2.dt.total_seconds().max() + 0.2)
                    ax2_container = ax2.bar(sector_2.index, sector_2.dt.total_seconds(), color=s2_colors)

                    fastest_s2_time = sector_2.iloc[0]
                    s2_deltas = sector_2 - fastest_s2_time
                    s2_formatted_times = s2_deltas.apply(format_timedelta)
                    ax2.bar_label(ax2_container, labels=s2_formatted_times, color='white', padding=2, fontsize=11)

                    ax2.set_title("Sector 2", fontsize=14)
                    ax2.set_ylabel("Time (seconds)", fontsize=17, labelpad=15)
                    ax2.spines['top'].set_visible(False)
                    ax2.spines['right'].set_visible(False)
                    ax2.set_xticks(x_positions)
                    ax2.set_xticklabels(sector_2.index, fontsize=12, weight='bold')
                    ax2.tick_params(axis='y', labelsize=15)

                
                    ax3.set_ylim(bottom=sector_3.dt.total_seconds().min() - 0.2, top=sector_3.dt.total_seconds().max() + 0.2)
                    ax3_container = ax3.bar(sector_3.index, sector_3.dt.total_seconds(), color=s3_colors)

                    fastest_s3_time = sector_3.iloc[0]
                    s3_deltas = sector_3 - fastest_s3_time
                    s3_formatted_times = s3_deltas.apply(format_timedelta)
                    ax3.bar_label(ax3_container, labels=s3_formatted_times, color='white', padding=2, fontsize=11)

                    ax3.set_title("Sector 3", fontsize=14)
                    ax3.set_ylabel("Time (seconds)", fontsize=17, labelpad=15)
                    ax3.spines['top'].set_visible(False)
                    ax3.spines['right'].set_visible(False)
                    ax3.set_xticks(x_positions)
                    ax3.set_xticklabels(sector_3.index, fontsize=12, weight='bold')
                    ax3.tick_params(axis='y', labelsize=15)

                
                    fig.suptitle(f"{quali.event['EventName']} {quali.event.year} {quali.name} - Personal Best Sector Times", fontsize=20, fontweight='bold', y=0.98)
                    plt.tight_layout(rect=[0, 0, 1, 0.96])
                    
                    st.session_state.sector_analysis = fig
                
                except Exception as e:
                    st.error(f"An error has occured during plot generation: {e}")
                    st.warning("Ensure the race name is spelled correctly, GP exists and it has been completed for the selected year.")
    
    if 'sector_analysis' in st.session_state:
        st.pyplot(st.session_state.sector_analysis)


with tab3:
    st.header(f"Telemetry Analysis ({year} {gp} Grand Prix - Qualifying)")
    st.markdown("This plot shows the qualifying head-to-head between two drivers.")

    if 'data_confirmed' not in st.session_state:
        st.warning("Select the Year and the Race Name before generating a plot.")
    else:
        try:

            quali.load()

            drivers_list = pd.unique(quali.laps['Driver']).tolist()

            col1, col2 = st.columns(2)
            with col1:
                driver1 = st.selectbox("Select Driver 1", options=drivers_list, index=0, key="d1_h2h")
            with col2:
                driver2 = st.selectbox("Select Driver 2", options=drivers_list, index=1, key="d2_h2h")

        except Exception as e:
            st.sidebar.error("Could not load driver list.")
            driver1 = None
            driver2 = None

        if st.button("Generate Head-to-Head Plot"):
            if driver1 and driver2 and driver1 != driver2:
                with st.spinner(f"Loading data for {driver1} vs {driver2}..."):
                    try:

                        lap_driver1 = quali.laps.pick_drivers(driver1).pick_fastest()
                        lap_driver2 = quali.laps.pick_drivers(driver2).pick_fastest()

                        telemetry_driver1 = lap_driver1.get_car_data().add_distance()
                        telemetry_driver2 = lap_driver2.get_car_data().add_distance()

                        color_d1 = ff1.plotting.get_team_color(lap_driver1['Team'], session=quali)
                        color_d2 = ff1.plotting.get_team_color(lap_driver2['Team'], session=quali)

                        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15, 12), sharex=True)

                        
                        ax1.plot(telemetry_driver1['Distance'], telemetry_driver1['Speed'], label=driver1, color=color_d1, linewidth=1.9)
                        ax1.plot(telemetry_driver2['Distance'], telemetry_driver2['Speed'], label=driver2, color=color_d2, linewidth=1.9)
                        ax1.legend(loc='lower left', fontsize=10)
                        ax1.set_ylabel('Speed (Km/h)', fontsize=15, labelpad=15)
                        ax1.tick_params(axis='y', labelsize=13)

                        
                        ax2.plot(telemetry_driver1['Distance'], telemetry_driver1['Throttle'], label=driver1, color=color_d1, linewidth=1.9)
                        ax2.plot(telemetry_driver2['Distance'], telemetry_driver2['Throttle'], label=driver2, color=color_d2, linewidth=1.9)
                        ax2.set_ylabel('Throttle (%)', fontsize=15, labelpad=15)
                        ax2.tick_params(axis='y', labelsize=13)

                        
                        ax3.plot(telemetry_driver1['Distance'], telemetry_driver1['Brake'], label=driver1, color=color_d1, linewidth=1.9)
                        ax3.plot(telemetry_driver2['Distance'], telemetry_driver2['Brake'], label=driver2, color=color_d2, linewidth=1.9)
                        ax3.set_ylabel('Brake', fontsize=15, labelpad=15)
                        ax3.set_xlabel('Distance (m)', labelpad=20)
                        ax3.tick_params(axis='y', labelsize=13)


                        plt.suptitle(f"{driver1} vs {driver2} ({year} {gp} Telemetry Analysis)", fontsize=20, fontweight='bold', y=0.95)

                        plt.subplots_adjust(top=0.90)

                        st.session_state.quali_h2h = fig

                    except Exception as e:
                        st.error(f"An error has occured during plot generation: {e}")
            else:
                st.error(f"An error has occured during plot generation {e}")
                st.warning("Ensure the race name is spelled correctly, GP exists and it has been completed for the selected year.")
    
    if 'quali_h2h' in st.session_state:
        st.pyplot(st.session_state.quali_h2h)


with tab4:
    st.header(f"Race Lap Distribution ({year} {gp} Grand Prix)")
    st.markdown("This plot shows the lap time distribution for the top 10 finishers.")

    if st.button("Generate Race Plot"):
        if 'data_confirmed' not in st.session_state:
            st.warning("Select the Year and the Race Name before generating a plot.")
        else:
            with st.spinner(f"Loading {year} {gp} Race data..."):
                try:

                    race.load()

                    point_finishers = race.drivers[:10]
                    
                    driver_laps = race.laps.pick_drivers(point_finishers).pick_quicklaps()
                    driver_laps = driver_laps.reset_index()

                    finishing_order = [race.get_driver(i)['Abbreviation'] for i in point_finishers]
                
                    fig, ax = plt.subplots(figsize=(13, 7))

                    driver_laps["LapTime(s)"] = driver_laps["LapTime"].dt.total_seconds()
                    
                    
                    sns.violinplot(data=driver_laps,
                                x="Driver",
                                y="LapTime(s)",
                                hue="Driver",
                                inner=None,
                                density_norm="area",
                                order=finishing_order,
                                palette=ff1.plotting.get_driver_color_mapping(session=race)
                                )
                    
                    
                    sns.swarmplot(data=driver_laps,
                                x="Driver",
                                y="LapTime(s)",
                                order=finishing_order,
                                hue="Compound",
                                palette=ff1.plotting.get_compound_mapping(session=race),
                                hue_order=["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"],
                                linewidth=0,
                                size=3.5,
                                )
                    
                    
                    ax.set_xlabel('Driver', fontsize=15, labelpad=15)
                    ax.tick_params(labelsize=13)
                    ax.set_ylabel('Lap Times', fontsize=15, labelpad=15)
                    ax.legend(loc="upper left", fontsize=8)
                    plt.suptitle(f"{race.event['EventName']} {race.event.year} Race Lap Time Distributions", fontsize=20, fontweight='bold', y=0.97)
                    
                    st.session_state.race_dist = fig

                except Exception as e:
                    st.error(f"An error has occurred during plot generation: {e}")
                    st.warning("Ensure the race name is spelled correctly, GP exists and it has been completed for the selected year.")

    if 'race_dist' in st.session_state:
        st.pyplot(st.session_state.race_dist)


with tab5:
    st.header(f"Acceleration Times ({year} {gp} Grand Prix - Race)")
    st.markdown("This plot shows the acceleration times for each driver during the start of the race.")

    if st.button("Generate Acceleration Times Plot"):

        if 'data_confirmed' not in st.session_state:
            st.warning("Select the Year and the Race Name before generating a plot.")
        else:
            with st.spinner(f"Loading Acceleration Times Data..."):
                try:

                    race.load()

                    all_drivers_telemetry = []

                    for driver in race.drivers:
                        driver_laps = race.laps.pick_drivers(driver)
                        
                        driver_data = driver_laps.pick_laps(1).get_telemetry().loc[:, [ 'Time', 'Speed']]

                        start_index = driver_data['Speed'].idxmin()
                        acc_phase = driver_data.loc[start_index:]
                        dec_phase = acc_phase['Speed'].diff() < 0
                        end_index = dec_phase.idxmax()
                        final_df = driver_data.loc[start_index:end_index].copy()
                        
                        final_df['Driver'] = driver_laps.iloc[0]['Driver']
                        final_df['Team'] = driver_laps.iloc[0]['Team']

                        all_drivers_telemetry.append(final_df)

                    drivers_telemetry = pd.concat(all_drivers_telemetry)


                    def get_time_for_speed(df, target_speed):
                        try:
                            point_before = df[df['Speed'] < target_speed].iloc[-1]
                            point_after = df[df['Speed'] >= target_speed].iloc[0]

                            time_before = point_before['Time']
                            speed_before = point_before['Speed']
                            time_after = point_after['Time']
                            speed_after = point_after['Speed']

                            if speed_after == speed_before:
                                return time_before

                            speed_ratio = (target_speed - speed_before) / (speed_after - speed_before)
                            time_diff = time_after - time_before
                            
                            return time_before + (time_diff * speed_ratio)
                        except IndexError:
                            return None

                    acceleration_results = {}

                    for driver_name in drivers_telemetry['Driver'].unique():
                        driver_df = drivers_telemetry[drivers_telemetry['Driver'] == driver_name].copy()
                        
                        start_index = driver_df['Speed'].idxmin()
                        acceleration_df = driver_df.loc[start_index:]
                        deceleration_series = acceleration_df['Speed'].diff() < 0
                        
                        if deceleration_series.any():
                            end_index = deceleration_series.idxmax()
                            final_df = acceleration_df.loc[start_index:end_index]
                        else:
                            final_df = acceleration_df

                        start_time = final_df.iloc[0]['Time']
                        time_at_100 = get_time_for_speed(final_df, 100)
                        time_at_200 = get_time_for_speed(final_df, 200)

                        if time_at_100 and time_at_200:
                            zero_to_100 = time_at_100 - start_time
                            one_hundred_to_200 = time_at_200 - time_at_100
                            
                            acceleration_results[driver_name] = {
                                '0-100 Time': zero_to_100.total_seconds(),
                                '100-200 Time': one_hundred_to_200.total_seconds(),
                                'Team': driver_df['Team'].iloc[0]
                            }


                    times_df = pd.DataFrame.from_dict(acceleration_results, orient='index')
                    times_df = times_df.sort_values(by='0-100 Time')

                    times_df.reset_index(inplace=True)
                    times_df.rename(columns={'index': 'Driver'}, inplace=True)

                    times_df['0-100 Time'] = times_df['0-100 Time'].round(2)
                    times_df['100-200 Time'] = times_df['100-200 Time'].round(2) 


                    fig, ax = plt.subplots(figsize=(16, 9))

                    times_df['Total Time'] = (times_df['0-100 Time'] + times_df['100-200 Time']).round(2)

                    times_df = times_df.sort_values(by=['Total Time', '0-100 Time'])

                    team_colors = [ff1.plotting.get_team_color(team, session=race) for team in times_df['Team']]

                    bar1 = ax.bar(times_df['Driver'], times_df['0-100 Time'], color=team_colors)

                    bar2 = ax.bar(
                        times_df['Driver'], 
                        times_df['100-200 Time'], 
                        bottom=times_df['0-100 Time'],
                        color=team_colors,
                        hatch='//',
                        edgecolor='white',
                        alpha=0.7
                    )


                    ax.bar_label(bar1, label_type='center', fmt='%.2f', fontweight='bold', color='black', fontsize=12)

                    total_time_labels = [f"{total:.2f}" for total in times_df['Total Time']]
                    ax.bar_label(bar2, labels=total_time_labels, label_type='edge', padding=3, fontweight='bold', fontsize=12)

                    ax.set_ylabel('Time')
                    ax.get_yaxis().set_visible(False)
                    ax.spines[['left', 'top', 'right']].set_visible(False)
                    plt.tight_layout()
                    fig.suptitle(f"Acceleration Times ({year} {gp} Grand Prix - Race)", fontsize=20, fontweight='bold', y=1.1)

                    st.session_state.acceleration_time = fig

                except Exception as e:  
                    st.error(f"An error has occured during plot generation : {e}")
                    st.warning("Ensure the race name is spelled correctly, GP exists and it has been completed for the selected year.")
    
    if 'acceleration_time' in st.session_state:
        st.pyplot(st.session_state.acceleration_time)