Project Description:

This project consists of a python based inflation calculator using historical CPI data provided from the Bank of Canada website. This program essentially allows the user to input an original monetary value amount and then select 2 dates which include a year and month to calculate how the value has changed due to inflation.

The calculator provides the inflation-adjusted value, total percentage change, difference in years, annualized rate of change, and CPI values for both selected periods. It replicates the features from the Bank of Canada calculator on their website, but instead provides a more accurate result as the project calculator uses data from months. It also includes input validation to ensure users enter valid monetary values and dates within the available dataset. Input validations include checking for dollar signs, commas, and incorrect formats for the dates.

The project uses Pandas to organize and analyze CPI data, NumPy for numerical validation, and Matplotlib to visualize historical CPI levels and annual inflation rates. A simple menu allows users to run the inflation calculator, generate the CPI graph, or exit the program. It uses a modular coding approach to have more effective and simple structure for the code.

Project Files

File

Description

Assignment2.py

Main Python program containing the inflation calculator, input validation, calculations, and graphing functions.

STATIC_INFLATIONCALC.csv

Historical monthly Canadian CPI data downloaded from the Bank of Canada website.

cpi_graph.png

Graph generated using Matplotlib showing historical Canadian CPI levels and annual inflation rates.

README.md

Project description, instructions, CPI graph analysis, and sample calculator output.

How to Run the Program

Install Python and open the project folder in VS Code.

Download the monthly CPI dataset from the Bank of Canada.

Save the downloaded file as STATIC_INFLATIONCALC.csv in the same folder as the Python program. The code automatically skips the first eight rows containing metadata.

Open the VS Code terminal and install the required libraries:

pip install numpy pandas matplotlib

Run the Python program:

python Assignment2.py

The following menu will appear:

Main Menu
1. Inflation Calculator
2. Generate CPI Graph
3. Exit

Select Option 1 to use the inflation calculator. Enter an original monetary value in Canadian dollars, followed by two dates in YYYY-MM format. The calculator will display the inflation-adjusted value, percentage change, difference in years, annualized rate of change, and CPI values for both dates.

Select Option 2 to generate the CPI graph. The graph will be displayed and automatically saved as cpi_graph.png.

Select Option 3 to exit the program