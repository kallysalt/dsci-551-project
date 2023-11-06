from tabulate import tabulate
import re

def to_number(value):
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            raise ValueError(f"The value '{value}' is not a number.")
    
def print_df(df, i):
    if i == 0:
        # Print with column names
        print(tabulate(df, headers='keys', tablefmt='plain', showindex=False, colalign=("left",)))
    else:
        # Print without column names, using an empty list for headers
        print(tabulate(df, headers=[], tablefmt='plain', showindex=False, colalign=("left",)))


