
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
df = df[["date", "STATIC_INFLATIONCALC"]].copy()

# Rename the columns
df.columns = ["Date", "CPI"]


# Step 2: Clean and organize CPI data

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


# Step 3: Calculate annual percentage change

# Compare each month's CPI to the same month in the previous year
df["Annual_Inflation"] = (
    (df["CPI"] / df["CPI"].shift(12) - 1) * 100
)


# Step 4: Validate the user's price

def get_price():

    while True:

        price = input("\nEnter the original price in CAD: ").strip()

        # Remove optional dollar signs and commas
        price = price.replace("$", "").replace(",", "")

        if price.upper().startswith("CAD"):
            price = price[3:].strip()

        try:
            price = float(price)

            # Check that the price is a valid number
            if not np.isfinite(price):
                print("Please enter a valid numerical amount.")
                continue

            # Check that the price is not negative
            if price < 0:
                print("Price cannot be negative.")
                continue

            return price

        except ValueError:
            print("Invalid price. Please enter a number.")


# Step 5: Validate the user's dates

def get_date(message):

    # Find the first and last available dates
    first_date = df["CPI"].first_valid_index()
    last_date = df["CPI"].last_valid_index()

    while True:

        date = input(message).strip()

        # Check if the date follows YYYY-MM format
        if (
            len(date) != 7
            or date[4] != "-"
            or not date[:4].isdigit()
            or not date[5:].isdigit()
        ):
            print("Invalid date format. Please use YYYY-MM.")
            continue

        # Extract the year and month
        year = int(date[:4])
        month = int(date[5:7])

        # Check if the month and year are valid
        if year < 1 or month < 1 or month > 12:
            print("Invalid month or year.")
            continue

        try:
            selected_date = pd.Timestamp(
                year=year,
                month=month,
                day=1
            )

        except (ValueError, OverflowError):
            print("Invalid date.")
            continue

        # Check if the date is within the dataset
        if selected_date < first_date or selected_date > last_date:

            print("Date is outside the available CPI data.")
            print(
                f"Available dates: "
                f"{first_date:%Y-%m} to {last_date:%Y-%m}"
            )
            continue

        # Check if CPI data exists for the selected month
        if pd.isna(df.loc[selected_date, "CPI"]):
            print("CPI data is unavailable for this month.")
            continue

        return selected_date


# Step 6: Calculate inflation

def calculate_inflation(price, first_date, second_date):

    # Find the CPI value for each period
    first_cpi = float(df.loc[first_date, "CPI"])
    second_cpi = float(df.loc[second_date, "CPI"])

    # Calculate the adjusted price
    adjusted_price = price * (second_cpi / first_cpi)

    # Calculate the difference in price
    price_difference = adjusted_price - price

    # Calculate the percentage change
    percentage_change = (
        (second_cpi / first_cpi) - 1
    ) * 100

    # Calculate the difference in months
    months = (
        (second_date.year - first_date.year) * 12
        + (second_date.month - first_date.month)
    )

    # Calculate the difference in years
    years = months / 12

    # Calculate the annual rate of change
    if months == 0:
        annual_rate = 0
    else:
        annual_rate = (
            np.power(
                second_cpi / first_cpi,
                12 / abs(months)
            ) - 1
        ) * 100

    # Display the results
    print("\nCanadian Inflation Calculator Results")

    print(f"\nFirst Period: {first_date:%B %Y}")
    print(f"Second Period: {second_date:%B %Y}")

    print("\nPrice Comparison")

    print(f"Original Price: CAD ${price:,.2f}")
    print(f"Adjusted Price: CAD ${adjusted_price:,.2f}")
    print(f"Price Difference: CAD ${price_difference:+,.2f}")

    print("\nInflation Statistics")

    print(f"Percentage Change: {percentage_change:+.2f}%")
    print(f"Difference in Months: {months}")
    print(f"Difference in Years: {years:.2f}")
    print(f"Annual Rate of Change: {annual_rate:+.2f}%")

    print("\nConsumer Price Index")

    print(f"CPI for First Period: {first_cpi:.2f}")
    print(f"CPI for Second Period: {second_cpi:.2f}")


# Step 7: Run the inflation calculator

def run_calculator():

    print("\nCanadian Inflation Calculator")

    # Find the available CPI date range
    first_date = df["CPI"].first_valid_index()
    last_date = df["CPI"].last_valid_index()

    print(
        f"Available CPI dates: "
        f"{first_date:%Y-%m} to {last_date:%Y-%m}"
    )

    print("When prompted for dates, enter them using YYYY-MM format.")

    # Get the three user inputs
    price = get_price()

    first_date = get_date(
        "\nEnter the first date (YYYY-MM): "
    )

    second_date = get_date(
        "\nEnter the second date (YYYY-MM): "
    )

    # Calculate and display inflation
    calculate_inflation(price, first_date, second_date)


# Step 8: Create the CPI graph

def create_graph():

    # Create the graph and left Y-axis
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Plot CPI on the left Y-axis
    cpi_line, = ax1.plot(
        df.index,
        df["CPI"],
        color="blue",
        label="Consumer Price Index"
    )

    ax1.set_xlabel("Year")
    ax1.set_ylabel("Consumer Price Index (CPI)", color="blue")
    ax1.tick_params(axis="y", labelcolor="blue")

    # Add a dotted line at the CPI base level
    base_line = ax1.axhline(
        y=100,
        color="gray",
        linestyle=":",
        label="CPI Base Level (2002 = 100)"
    )

    # Create the right Y-axis
    ax2 = ax1.twinx()

    # Plot annual percentage change on the right Y-axis
    inflation_line, = ax2.plot(
        df.index,
        df["Annual_Inflation"],
        color="red",
        label="Annual Percentage Change"
    )

    ax2.set_ylabel("Annual Percentage Change (%)", color="red")
    ax2.tick_params(axis="y", labelcolor="red")

    # Add the graph title
    ax1.set_title(
        "Canadian Consumer Price Index and Annual Inflation"
    )

    # Add the legend
    ax1.legend(
        handles=[cpi_line, inflation_line, base_line],
        loc="upper left"
    )

    # Add the grid
    ax1.grid(True, linestyle="--", alpha=0.3)

    # Save the graph as a PNG file
    plt.tight_layout()
    plt.savefig("cpi_graph.png", dpi=300)

    print("\nGraph saved as cpi_graph.png")

    # Display the graph
    plt.show()
    plt.close(fig)


# Step 9: Main menu

def main():

    while True:

        print("\nMain Menu")
        print("1. Inflation Calculator")
        print("2. Generate CPI Graph")
        print("3. Exit")

        choice = input("\nEnter your choice (1-3): ").strip()

        if choice == "1":
            run_calculator()

        elif choice == "2":
            create_graph()

        elif choice == "3":
            print("\nProgram ended.")
            break

        else:
            print("Invalid option. Please choose 1, 2, or 3.")


# Step 10: Start the program

if __name__ == "__main__":
    main()
