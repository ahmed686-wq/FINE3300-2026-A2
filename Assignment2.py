
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class InflationCalculator:

    # Step 1: Import CPI data from the CSV file downloaded from the Bank of Canada website

    def __init__(self):

        # Read the CSV file into a Pandas DataFrame - it skips the first 8 rows which contain metadata and not actual data
        self.df = pd.read_csv("STATIC_INFLATIONCALC.csv", skiprows=8)

        # now it selects only the columns we need, which are the date and the CPI values
        self.df = self.df[["date", "STATIC_INFLATIONCALC"]]

        # I renamed the columns to make them easier to work with while writing rest of the code
        self.df.columns = ["Date", "CPI"]

        # Step 2: Now we will organize CPI data

        # Convert dates to datetime format since the csv data shows dates in YYYY-MM-DD format
        self.df["Date"] = pd.to_datetime(self.df["Date"])

        # Sort the data from oldest to newest
        self.df = self.df.sort_values("Date")

        # Set the Date column as the index
        self.df = self.df.set_index("Date")

        # Now we will calculate annual percentage change for graphing
        # Each row represents one month, so shift(12) compares the current month with the same month one year earlier
        self.df["Annual_Inflation"] = (
            (self.df["CPI"] / self.df["CPI"].shift(12) - 1) * 100
        )


    # Step 3: Get and validate the original value

    def get_value(self):

        while True:

            value = input("\nEnter the original value in CAD: ").strip()

            # Remove dollar signs and commas
            value = value.replace("$", "").replace(",", "")

            try:
                value = float(value)

                if not np.isfinite(value) or value < 0:
                    print("Please enter a valid non-negative value.")
                    continue

                return value

            except ValueError:
                print("Invalid value. Please enter a number.")


    # Step 4: Validate dates entered by the user

    def get_date(self, message):

        while True:
            date = input(message).strip()

            try:
                selected_date = pd.to_datetime(date, format="%Y-%m")

                if selected_date in self.df.index:
                    return selected_date

                print("Date is not available in the CPI dataset.")

            except ValueError:
                print("Invalid date format. Use YYYY-MM.")


    # Step 5: Calculate inflation

    def calculate_inflation(self):

        print("\nCanadian Inflation Calculator")

        first_available = self.df["CPI"].first_valid_index()
        last_available = self.df["CPI"].last_valid_index()

        print(
            f"Available dates: "
            f"{first_available:%Y-%m} to {last_available:%Y-%m}"
        )

        # Get and validate the original value
        value = self.get_value()

        # Get and validate the two dates
        first_date = self.get_date(
            "\nEnter the first date (YYYY-MM): "
        )

        second_date = self.get_date(
            "\nEnter the second date (YYYY-MM): "
        )

        # Get CPI values for the selected months
        first_cpi = float(self.df.loc[first_date, "CPI"])
        second_cpi = float(self.df.loc[second_date, "CPI"])

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
                (second_cpi / first_cpi) ** (12 / abs(months)) - 1
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


    # Step 6: Generate CPI graph

    def plot(self):

        # Create figure and left Y-axis
        fig, ax1 = plt.subplots(figsize=(12, 6))

        # Plot CPI
        ax1.plot(
            self.df.index,
            self.df["CPI"],
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
            self.df.index,
            self.df["Annual_Inflation"],
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

        # Save and display the graph
        fig.tight_layout()
        fig.savefig("cpi_graph.png", dpi=300)

        print("\nGraph saved as cpi_graph.png")

        plt.show()
        plt.close(fig)


    # Step 7: This is for the main menu

    def main_menu(self):

        while True:

            print("\nMain Menu")
            print("1. Inflation Calculator")
            print("2. Generate CPI Graph")
            print("3. Exit")

            choice = input("\nEnter your choice (1-3): ").strip()

            # Option 1: this is for the inflation calculator
            if choice == "1":
                self.calculate_inflation()

            # Option 2: CPI Graph
            elif choice == "2":
                self.plot()

            # Option 3: Exit
            elif choice == "3":
                print("\nProgram ended.")
                break

            else:
                print("Invalid option. Please choose 1, 2, or 3.")


# Step 8: Start the program

if __name__ == "__main__":

    calculator = InflationCalculator()
    calculator.main_menu()
