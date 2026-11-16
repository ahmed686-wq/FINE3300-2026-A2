
import csv
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# =====================================================
# 1. FILE SETTINGS
# =====================================================

# Folder containing this Python file
FOLDER = Path(__file__).resolve().parent

# Your downloaded Bank of Canada CSV file
CSV_FILE = FOLDER / "STATIC_INFLATIONCALC.csv"

# Name of the graph to be saved
GRAPH_FILE = FOLDER / "cpi_graph.png"

# Bank of Canada CPI base level (2002 = 100)
BASE_CPI = 100.0


# =====================================================
# 2. READ CPI DATA USING PANDAS
# =====================================================

def load_cpi_data():

    # Check whether CSV file exists
    if not CSV_FILE.exists():
        raise FileNotFoundError(
            f"Cannot find {CSV_FILE.name} in {FOLDER}"
        )

    # Find the header containing the actual observations
    # Bank of Canada CSV files contain metadata at the top.
    header_row = None

    with open(CSV_FILE, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file)

        for row_number, row in enumerate(reader):
            if row and row[0].strip().lower() == "date":
                header_row = row_number
                break

    if header_row is None:
        raise ValueError("Could not find the date header in the CSV.")

    # Load the CSV into a Pandas DataFrame
    df = pd.read_csv(
        CSV_FILE,
        skiprows=header_row,
        encoding="utf-8-sig"
    )

    df.columns = df.columns.str.strip()

    # Identify the CPI column
    if "STATIC_INFLATIONCALC" in df.columns:
        cpi_column = "STATIC_INFLATIONCALC"
    elif "CPI" in df.columns:
        cpi_column = "CPI"
    else:
        raise ValueError("Could not find the CPI column.")

    # Keep only the date and CPI columns
    df = df[["date", cpi_column]].copy()

    df.columns = ["Date", "CPI"]

    # Convert columns into appropriate data types
    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    df["CPI"] = pd.to_numeric(
        df["CPI"],
        errors="coerce"
    )

    # Remove missing or invalid observations
    df = df.dropna(subset=["Date", "CPI"])

    df = df[df["CPI"] > 0]

    # Convert dates to the first day of their month
    df["Date"] = (
        df["Date"].dt.to_period("M").dt.to_timestamp()
    )

    # Sort by date
    df = df.sort_values("Date")

    # Remove duplicate months
    df = df.drop_duplicates(subset="Date")

    if df.empty:
        raise ValueError("No valid CPI observations found.")

    # Set date as the DataFrame index
    df = df.set_index("Date")

    # Create a monthly time series
    df = df.asfreq("MS")

    # Annual inflation:
    # Compare each month's CPI against 12 months earlier
    df["Annual_Inflation"] = (
        (df["CPI"] / df["CPI"].shift(12) - 1) * 100
    )

    return df


# =====================================================
# 3. CREATE CPI GRAPH USING MATPLOTLIB
# =====================================================

def create_graph(df):

    fig, ax1 = plt.subplots(figsize=(13, 7))

    # Plot CPI time series on left Y-axis
    cpi_line, = ax1.plot(
        df.index,
        df["CPI"],
        color="blue",
        linewidth=2,
        label="Consumer Price Index (CPI)"
    )

    ax1.set_xlabel("Year", fontsize=12)

    ax1.set_ylabel(
        "Consumer Price Index (CPI)",
        fontsize=12,
        color="blue"
    )

    ax1.tick_params(axis="y", labelcolor="blue")

    # Dotted line passing through CPI base level
    base_line = ax1.axhline(
        y=BASE_CPI,
        color="gray",
        linestyle=":",
        linewidth=2,
        label="CPI Base Level (2002 = 100)"
    )

    # Create a second Y-axis on the right
    ax2 = ax1.twinx()

    # Plot annual percentage change
    inflation_line, = ax2.plot(
        df.index,
        df["Annual_Inflation"],
        color="red",
        linewidth=1.5,
        label="Annual Percentage Change in CPI"
    )

    ax2.set_ylabel(
        "Annual Percentage Change (%)",
        fontsize=12,
        color="red"
    )

    ax2.tick_params(axis="y", labelcolor="red")

    # Graph title
    ax1.set_title(
        "Canadian Consumer Price Index and Annual Inflation Rate",
        fontsize=15,
        fontweight="bold"
    )

    # Grid
    ax1.grid(
        True,
        linestyle="--",
        alpha=0.3
    )

    # Legend
    ax1.legend(
        handles=[cpi_line, inflation_line, base_line],
        loc="upper left"
    )

    # Improve layout
    fig.tight_layout()

    # Save graph as PNG
    plt.savefig(
        GRAPH_FILE,
        dpi=300,
        bbox_inches="tight"
    )

    print("\nCPI graph successfully created!")
    print(f"Graph saved as: {GRAPH_FILE.name}")

    # Display graph
    plt.show()

    plt.close(fig)


# =====================================================
# 4. VALIDATE USER PRICE INPUT
# =====================================================

def get_price():

    while True:

        user_input = input(
            "\nEnter the original price in CAD: "
        ).strip()

        # Remove optional dollar signs and commas
        cleaned_input = user_input.replace("$", "")
        cleaned_input = cleaned_input.replace(",", "")
        cleaned_input = cleaned_input.replace(" ", "")

        if cleaned_input.upper().startswith("CAD"):
            cleaned_input = cleaned_input[3:]

        try:
            price = float(cleaned_input)

            # Reject infinite values or NaN
            if not np.isfinite(price):
                print("Error: Enter a valid finite number.")
                continue

            # Reject negative prices
            if price < 0:
                print("Error: Price cannot be negative.")
                continue

            return price

        except ValueError:
            print("Invalid price. Please enter a number.")
            print("Example: 1000 or 1250.50")


# =====================================================
# 5. VALIDATE USER DATE INPUT
# =====================================================

def get_date(message, df):

    # Find available dataset date range
    first_date = df["CPI"].first_valid_index()
    last_date = df["CPI"].last_valid_index()

    while True:

        user_input = input(message).strip()

        # Require YYYY-MM format
        if (
            len(user_input) != 7
            or user_input[4] != "-"
            or not user_input[:4].isdigit()
            or not user_input[5:].isdigit()
        ):
            print("Invalid format. Please use YYYY-MM.")
            print("Example: 2020-01")
            continue

        # Extract year and month
        year = int(user_input[:4])
        month = int(user_input[5:7])

        # Validate month and year
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

        # Check data range
        if selected_date < first_date or selected_date > last_date:

            print("\nError: Date is outside available CPI data.")

            print(
                f"Available dates: "
                f"{first_date:%Y-%m} to {last_date:%Y-%m}"
            )

            continue

        # Check whether CPI exists for selected date
        if pd.isna(df.loc[selected_date, "CPI"]):
            print("CPI data is unavailable for this month.")
            continue

        return selected_date


# =====================================================
# 6. CALCULATE INFLATION
# =====================================================

def calculate_inflation(price, start_date, end_date, df):

    # Extract the CPI for each selected month
    start_cpi = float(df.loc[start_date, "CPI"])
    end_cpi = float(df.loc[end_date, "CPI"])

    # Inflation-adjusted price
    adjusted_price = price * (end_cpi / start_cpi)

    # Dollar difference
    dollar_difference = adjusted_price - price

    # Total percentage change
    percentage_change = (
        (end_cpi / start_cpi) - 1
    ) * 100

    # Difference in months
    months_difference = (
        (end_date.year - start_date.year) * 12
        + (end_date.month - start_date.month)
    )

    # Difference in years
    years_difference = months_difference / 12

    # Compound annual rate of change
    # Signed time difference handles forward and reverse dates
    if months_difference == 0:
        annual_rate = 0.0
    else:
        annual_rate = (
            np.power(
                end_cpi / start_cpi,
                12 / months_difference
            ) - 1
        ) * 100

    return {
        "original_price": price,
        "adjusted_price": adjusted_price,
        "dollar_difference": dollar_difference,
        "percentage_change": percentage_change,
        "months_difference": months_difference,
        "years_difference": years_difference,
        "annual_rate": annual_rate,
        "start_cpi": start_cpi,
        "end_cpi": end_cpi,
        "start_date": start_date,
        "end_date": end_date
    }


# =====================================================
# 7. DISPLAY RESULTS
# =====================================================

def display_results(results):

    start_date = results["start_date"].strftime("%B %Y")
    end_date = results["end_date"].strftime("%B %Y")

    print("\n" + "=" * 60)
    print("               CANADIAN INFLATION CALCULATOR")
    print("=" * 60)

    print(f"\nStarting Date:               {start_date}")
    print(f"Ending Date:                 {end_date}")

    print("\n" + "-" * 60)

    print(
        f"Original Price:              "
        f"CAD ${results['original_price']:,.2f}"
    )

    print(
        f"Inflation-Adjusted Price:    "
        f"CAD ${results['adjusted_price']:,.2f}"
    )

    print(
        f"Price Difference:            "
        f"CAD ${results['dollar_difference']:+,.2f}"
    )

    print("\n" + "-" * 60)

    print(
        f"Total Percentage Change:     "
        f"{results['percentage_change']:+.2f}%"
    )

    print(
        f"Difference in Months:        "
        f"{results['months_difference']}"
    )

    print(
        f"Difference in Years:         "
        f"{results['years_difference']:.2f}"
    )

    print(
        f"Annual Rate of Change:       "
        f"{results['annual_rate']:+.2f}%"
    )

    print("\n" + "-" * 60)

    print(
        f"Starting CPI:                "
        f"{results['start_cpi']:.2f}"
    )

    print(
        f"Ending CPI:                  "
        f"{results['end_cpi']:.2f}"
    )

    print("\nCPI Base Level: 2002 = 100")

    print("=" * 60)


# =====================================================
# 8. RUN INFLATION CALCULATOR
# =====================================================

def run_calculator(df):

    print("\n" + "=" * 60)
    print("                 INFLATION CALCULATOR")
    print("=" * 60)

    first_date = df["CPI"].first_valid_index()
    last_date = df["CPI"].last_valid_index()

    print(
        f"\nAvailable CPI data: "
        f"{first_date:%Y-%m} to {last_date:%Y-%m}"
    )

    print("Please enter dates in YYYY-MM format.")

    # Ask for original price
    price = get_price()

    # Ask for starting date
    start_date = get_date(
        "\nEnter starting date (YYYY-MM): ",
        df
    )

    # Ask for ending date
    end_date = get_date(
        "\nEnter ending date (YYYY-MM): ",
        df
    )

    # Calculate inflation
    results = calculate_inflation(
        price,
        start_date,
        end_date,
        df
    )

    # Show results
    display_results(results)


# =====================================================
# 9. MAIN PROGRAM
# =====================================================

def main():

    print("\n" + "=" * 60)
    print("             CANADIAN CPI ANALYSIS PROJECT")
    print("=" * 60)

    print("\nData Source: Bank of Canada")
    print("CPI Base Level: 2002 = 100")

    # Load local CPI file
    try:
        df = load_cpi_data()

    except Exception as error:
        print("\nError loading CPI data:")
        print(error)
        return

    print("\nCPI data loaded successfully!")

    first_date = df["CPI"].first_valid_index()
    last_date = df["CPI"].last_valid_index()

    print(f"\nTotal CPI Observations: {df['CPI'].count()}")
    print(f"First Observation: {first_date:%Y-%m}")
    print(f"Latest Observation: {last_date:%Y-%m}")

    # Application menu
    while True:

        print("\n" + "=" * 60)
        print("                       MAIN MENU")
        print("=" * 60)

        print("1. Calculate Inflation")
        print("2. Generate CPI Graph")
        print("3. View Recent CPI Data")
        print("4. Exit")

        choice = input(
            "\nEnter your choice (1-4): "
        ).strip()

        if choice == "1":
            run_calculator(df)

        elif choice == "2":
            create_graph(df)

        elif choice == "3":
            print("\nMost Recent 12 Months of CPI Data:\n")

            recent_data = df.dropna(
                subset=["CPI"]
            ).tail(12)

            print(recent_data.round(2).to_string())

        elif choice == "4":
            print("\nThank you for using the Inflation Calculator!")
            break

        else:
            print("\nInvalid choice. Please select 1, 2, 3, or 4.")


# =====================================================
# 10. START PROGRAM
# =====================================================

if __name__ == "__main__":
    main()
