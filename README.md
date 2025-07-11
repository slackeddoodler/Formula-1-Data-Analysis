# Formula-1-Data-Analysis

### 1. Project Overview
This project is an interactive data analysis tool built to explore and visualize Formula 1 race data. It leverages the FastF1 library to fetch detailed session information, including lap times, telemetry, and qualifying results. The application is built with Streamlit, providing a user-friendly web interface with multiple analysis tabs.
The core of the application allows users to select a specific race and year. Once confirmed, the tool loads the necessary data and enables the user to generate a series of detailed visualizations across different tabs, each focusing on a unique aspect of driver and team performance.
### 2. Technologies Used
- Data Fetching & F1 API: ```fastf1```
- Data Manipulation & Analysis: ```pandas```
- Web Application Framework: ```streamlit```
- Data Visualization: ```matplotlib, seaborn```
- Handling Time Data: ```timple.timedelta``` (for time-based calculations)
### 3. Visualizations
The application generates five distinct visualizations, each in its own tab.
#### 3.1. Qualifying Delta
- Purpose: To visualize the time gap between each driver and the pole-sitter in a qualifying session.
- Implementation: A horizontal bar chart showing each driver's delta to the fastest time. Bars are colored according to the driver's team color using Fast F1.
  
  <img width="1852" height="947" alt="image" src="https://github.com/user-attachments/assets/8e364814-663a-49b1-92e2-834285c525c9" />

#### 3.2. Sector Times
- Purpose: To compare the theoretical best lap of drivers by combining their fastest individual sector times.
- Implementation: A bar chart that breaks down each driver's theoretical best lap into its three sector components, allowing for analysis of where on the track a driver is strongest.

  <img width="1850" height="945" alt="image2" src="https://github.com/user-attachments/assets/3c0ca043-3fb6-4941-ae51-35de071296d9" />

#### 3.3. Qualifying Head-to-Head
- Purpose: To provide a direct comparison of qualifying performance between teammates over a particular Grand Prix using metrics like Speed(in kmph), Throttle, and Brake application from the fastest lap of the selected drivers.
- Implementation: A visualization containing 3 line plots showing the Speed, Throttle % and the Brake application of the two selected drivers. The two drivers are distinguished by their team color.

  <img width="1847" height="943" alt="image3" src="https://github.com/user-attachments/assets/2894a216-2165-4e58-b021-434509acd8b8" />

#### 3.4. Race Lap Distributions
- Purpose: To analyze the consistency and pace of drivers over a race stint.
- Implementation: A violin plot and swarm plot showing the distribution of all quicklaps (which is 107% of each driver's fastest lap) times for each driver during the race. This visualization makes it easy to compare driver consistency and identify outliers (e.g., laps under safety cars).

  <img width="1852" height="944" alt="image4" src="https://github.com/user-attachments/assets/cf5594f5-29c3-4ffe-b23b-df0605f05560" />

#### 3.5. Acceleration Times
- Purpose: To visualize the calculated 0-100 km/h and 100-200 km/h times for each driver from the race start.
- Implementation: A stacked bar chart, sorted by the total 0-200 km/h time.
	- The bars are colored using team colors.
	- The 100-200 km/h section is shaded with a diagonal hatch pattern for clarity.
	- Labels are placed automatically for a clean and efficient implementation. The 0-100 km/h time is labeled in its section, and the total 0-200 km/h time is labeled on top of the bar.
  
   <img width="1853" height="943" alt="image5" src="https://github.com/user-attachments/assets/400e482e-0200-4616-a8e9-09cb5eeb2d68" />

### 4. How to Run the Application
1. Download the ```f1_analysis.py``` file.
2. Ensure all required libraries are installed: ```pip install fastf1 pandas streamlit matplotlib seaborn timple```
3. Run the application from your terminal: ```streamlit run f1_analysis.py```
