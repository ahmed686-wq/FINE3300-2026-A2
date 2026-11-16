
import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# Step 1: Import CPI data

# Find where the CPI data begins in the CSV file
with open("STATIC_INFLATIONCALC.csv", "r", encoding="utf-8-sig") as file:
    reader = csv.reader(file)

    header_row = None

    for row_number, row in enumerate(reader):
        if row and row[0].strip().lower() == "date":
            header_row = row_number
            break

if header_row is None:
    raise ValueError("Could not find CPI data in the CSV file.")

# Read the CSV file into a Pandas DataFrame
df = pd.read_csv("STATIC_INFLATIONCALC.csv", skiprows=header_row)

# Select the relevant columns
df = df[["date", "STATIC_INFLATIONCALC"]]

# I renamed the columns to make it easier to work with rather than typing "STATIC_INFLATIONCALC" every time I want to reference the CPI column.
df.columns = ["Date", "CPI"]


# Step 2: This step involves cleaning and organizing CPI data

# Convert dates to datetime format
df["Date"] = pd.to_datetime(df["Date"])

# Convert CPI values to numbers
df["CPI"] = pd.to_numeric(df["CPI"])

# Sort the data from oldest to newest
df = df.sort_values("Date")

# Set the Date column as the index
df = df.set_index("Date")

# Organize the data by month
df = df.asfreq("MS")

# Calculate annual percentage change for graphing
df["Annual_Inflation"] = (
    (df["CPI"] / df["CPI"].shift(12) - 1) * 100
)


# Step 3: Validate the dates for user input error

def get_date(message):

    first_date = df["CPI"].first_valid_index()
    last_date = df["CPI"].last_valid_index()

    while True:
        date = input(message).strip()

        # Check YYYY-MM format. This checks for things like if the lenght is 7 characters, if the 5th character is a dash, and if the year and month are digits.
        if (
            len(date) != 7
            or date[4] != "-"
            or not date[:4].isdigit()
            or not date[5:].isdigit()
        ):
            print("Invalid date format. Use YYYY-MM.")
            continue

        # Now from the inputted date, we will extract the year and month and check if they are valid. For example, if the user inputs 2023-13, it will be invalid because there is no 13th month.
        year = int(date[:4])
        month = int(date[5:7])

        if year < 1 or month < 1 or month > 12:
            print("Invalid month or year.")
            continue

        try:
            selected_date = pd.Timestamp(year, month, 1)
        except (ValueError, OverflowError):
            print("Invalid date.")
            continue

        # Check if the date is within the dataset
        if selected_date < first_date or selected_date > last_date:
            print(
                f"Date must be between "
                f"{first_date:%Y-%m} and {last_date:%Y-%m}."
            )
            continue


        return selected_date


# Step 4: Main menu

while True:

    print("\nMain Menu")
    print("1. Inflation Calculator")
    print("2. Generate CPI Graph")
    print("3. Exit")

    choice = input("\nEnter your choice (1-3): ").strip()

    # Option 1: Inflation Calculator
    if choice == "1":

        print("\nCanadian Inflation Calculator")

        first_available = df["CPI"].first_valid_index()
        last_available = df["CPI"].last_valid_index()

        print(
            f"Available dates: "
            f"{first_available:%Y-%m} to {last_available:%Y-%m}"
        )

        # Get and validate the original value
        while True:

            value = input("\nEnter the original value in CAD: ").strip()

            # Remove dollar signs and commas
            value = value.replace("$", "").replace(",", "")

            try:
                value = float(value)

                if not np.isfinite(value) or value < 0:
                    print("Please enter a valid non-negative value.")
                    continue

                break

            except ValueError:
                print("Invalid value. Please enter a number.")

        # Get and validate the two dates
        first_date = get_date(
            "\nEnter the first date (YYYY-MM): "
        )

        second_date = get_date(
            "\nEnter the second date (YYYY-MM): "
        )

        # Get CPI values for the selected months
        first_cpi = float(df.loc[first_date, "CPI"])
        second_cpi = float(df.loc[second_date, "CPI"])

        # Calculate the adjusted value
        adjusted_value = value * second_cpi / first_cpi

        # Calculate the percentage change
        percentage_change = (second_cpi / first_cpi - 1) * 100

        # Calculate the difference in months
        months = (
            (second_date.year - first_date.year) * 12
            + second_date.month - first_date.month
        )

        # Calculate the difference in years
        years = months / 12

        # Calculate the annual rate of change
        if months == 0:
            annual_rate = 0
        else:
            annual_rate = (
                np.power(second_cpi / first_cpi, 12 / abs(months)) - 1
            ) * 100

        # Display the results
        print("\nCanadian Inflation Calculator Results")

        print(f"\nFirst Period: {first_date:%B %Y}")
        print(f"Second Period: {second_date:%B %Y}")

        print(f"\nOriginal Value: CAD ${value:,.2f}")
        print(f"Adjusted Value: CAD ${adjusted_value:,.2f}")
        print(f"Value Difference: CAD ${adjusted_value - value:+,.2f}")

        print(f"\nPercentage Change: {percentage_change:+.2f}%")
        print(f"Difference in Years: {years:.2f}")
        print(f"Annual Rate of Change: {annual_rate:+.2f}%")

        print(f"\nCPI for First Period: {first_cpi:.2f}")
        print(f"CPI for Second Period: {second_cpi:.2f}")

    # Option 2: CPI Graph
    elif choice == "2":

        # Create figure and left Y-axis
        fig, ax1 = plt.subplots(figsize=(12, 6))

        # Plot CPI
        ax1.plot(
            df.index,
            df["CPI"],
            color="blue",
            label="Consumer Price Index"
        )

        ax1.set_xlabel("Year")
        ax1.set_ylabel("Consumer Price Index (CPI)", color="blue")
        ax1.tick_params(axis="y", labelcolor="blue")

        # Dotted line at the base level
        ax1.axhline(
            y=100,
            color="gray",
            linestyle=":",
            label="CPI Base Level (2002 = 100)"
        )

        # Right Y-axis for annual percentage change
        ax2 = ax1.twinx()

        ax2.plot(
            df.index,
            df["Annual_Inflation"],
            color="red",
            label="Annual Percentage Change"
        )

        ax2.set_ylabel("Annual Percentage Change (%)", color="red")
        ax2.tick_params(axis="y", labelcolor="red")

        # Graph title
        ax1.set_title(
            "Canadian Consumer Price Index and Annual Inflation"
        )

        # Include all graph lines in the legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()

        ax1.legend(
            lines1 + lines2,
            labels1 + labels2,
            loc="lower right"
        )

        # Add grid
        ax1.grid(True, linestyle="--", alpha=0.3)

        # Save and display the graph
        fig.tight_layout()
        fig.savefig("cpi_graph.png", dpi=300)

        print("\nGraph saved as cpi_graph.png")

        plt.show()
        plt.close(fig)

    # Option 3: Exit
    elif choice == "3":
        print("\nProgram ended.")
        break

    else:
        print("Invalid option. Please choose 1, 2, or 3.")
