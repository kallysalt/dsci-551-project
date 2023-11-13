import csv
import re
import pandas as pd
import sys
import os
import glob
from tabulate import tabulate

from my_ql_parser import MyQLParser

memory_size = 512 # bytes

class RelationalDB:
    def __init__(self):
        pass
    
    def _print_df(self, df, i):
        if i == 0:
            # Print with column names
            print(tabulate(df, headers='keys', tablefmt='plain', showindex=False, colalign=("left",)))
        else:
            # Print without column names, using an empty list for headers
            print(tabulate(df, headers=[], tablefmt='plain', showindex=False, colalign=("left",)))
    
    def query(self, args):
        if args:
            if args[0] == "\"" and args[-1] == "\"":
                args = args[1:-1]
            self.parse_query(args) 
        else:
            print("No query provided")
        
    def parse_query(self, query):
        # query = query.lower()
        
        if query.startswith("get"):
            col_names, table_name = MyQLParser.parse_projection(query)
            self.projection(col_names, table_name)
            
        elif query.startswith("find"):
            col_name, table_name, value, criteria = MyQLParser.parse_filtering(query)
            self.filtering(col_name, table_name, value, criteria)
            
        elif query.startswith("order"):
            table_name, col_name, order = MyQLParser.parse_ordering(query)
            self.ordering(table_name, col_name, order)
            
        elif query.startswith("group"):
            table_name, col1_name, calculation, col2_name = MyQLParser.parse_grouping(query)
            # print('table_name:', table_name, ', col1_name:', col1_name, ', calculation:', calculation, ', col2_name:', col2_name)
            self.grouping(table_name, col1_name, calculation, col2_name)
            
        elif query.startswith("calculate"):
            table_name, col_name, order = MyQLParser.parse_aggregation(query)
            # print('table_name:', table_name, ', col_name:', col_name, ', order:', order)
            self.aggregation(table_name, col_name, order)
        
        elif query.startswith("combine"):
            table1_name, table2_name, col_name = MyQLParser.parse_inner_join(query)
            # print('table1_name:', table1_name, ', table2_name:', table2_name, ', col_name:', col_name)
            self.inner_join(table1_name, table2_name, col_name)
        
        elif query.startswith("insert"):
            row_value, table_name = MyQLParser.parse_insert(query)
            # print('row_value:', row_value, ', table_name:', table_name)
            self.insert(row_value, table_name)
        
        elif query.startswith("delete"):
            table_name, col_name, value = MyQLParser.parse_delete(query)
            # print('table_name:', table_name, ', col_name:', col_name, ', value:', value)
            self.delete(table_name, col_name, value)
        
        elif query.startswith("update"):
            table_name, col_name, new_val, old_val = MyQLParser.parse_update(query)
            # print('table_name:', table_name, ', col_name:', col_name, ', new_val:', new_val, ', old_val:', old_val)
            self.update(table_name, col_name, new_val, old_val)
            
        elif query.startswith("create"):
            table_name, col_names = MyQLParser.parse_create(query)
            print('table_name:', table_name, ', col_names:', [c for c in col_names])
            self.create(table_name, col_names)
        
        else:
            raise ValueError("Unrecognized command")
    
    # TODO: pretty print
    def projection(self, col_names, table_name):
        pattern = f'rdb/{table_name}_*.csv'
        # check if table exists
        files = glob.glob(pattern)
        files.sort()
        if not files:
            print(f"Error: Table {table_name} does not exist.")
        else:
            i = 0
            for file in files:
                df = pd.read_csv(file, usecols = col_names)
                tmp_fn = f"{file}.tmp"
                df.to_csv(tmp_fn, index = False)
                self._print_df(df, i)
                os.remove(tmp_fn)
                i += 1
              
    # TODO: pretty print
    def filtering(self, col_name, table_name, value, criteria):
        pattern = f'rdb/{table_name}_*.csv'
        # check if table exists
        files = glob.glob(pattern)
        files.sort()
        if not files:
            print(f"Error: Table {table_name} does not exist.")
        else:
            i = 0
            for file in files:
                df = pd.read_csv(file)
                # create tmp file to store filtering results for each csv file
                tmp_fn = f"{file}.tmp"
                if criteria == '=': # can work wih string or numeric
                    df = df[df[col_name] == value]
                elif criteria == '>=': # can only work with numeric
                    df = df[df[col_name] >= value]
                elif criteria == '<=': # can only work with numeric
                    df = df[df[col_name] <= value]
                if df.empty:
                    continue
                df.to_csv(tmp_fn, index = False)
                self._print_df(df, i)
                os.remove(tmp_fn)
                i += 1

    def ordering(self, table_name, col_name, order):
        # fn = f'rdb/{table_name}_{n}.csv'
        # not sure how to implement
        pass

    def inner_join(self, table1_name, table2_name, col_name):
        # fn = f'rdb/{table_name}_{n}.csv'
        # not sure how to implement
        pass 

    def grouping(self, table_name, col1_name, calculation, col2_name):
        # fn = f'rdb/{table_name}_{n}.csv'
        # not sure how to implement
        pass  

    def aggregation(self, calculation, col_name, table_name):
        try:
            pattern = f'rdb/{table_name}_*.csv'
            # check if table exists
            files = glob.glob(pattern)
            if not files:
                print(f"Error: Table {table_name} does not exist.")
            else:
                aggregated_value = 0
                record_count = 0
                for file in files:
                    df = pd.read_csv(file)
                    aggregated_value += df[col_name].sum()
                    if calculation == 'avg':
                        record_count += len(df)
                if calculation == 'avg' and record_count > 0:
                    aggregated_value /= record_count
                print(aggregated_value)
        except ValueError:
            print(f"Error: Column {col_name} in table {table_name} contains non-numeric value.")

    # note: does not check for duplicates
    # TODO: check for duplicates? check for data type?
    def insert(self, row_values, table_name):
        pattern = f'rdb/{table_name}_*.csv'
        files = glob.glob(pattern)
        # check if table exists
        if not files:
            print(f"Error: Table {table_name} does not exist.")
        else:
            # check if record length is valid
            first_file_df = pd.read_csv(files[0])
            if len(row_values) != len(first_file_df.columns):
                print("Error: Invalid record length.")
            else:
                # find and read the "last" csv file
                max_index = max([int(file.split('_')[-1].split('.csv')[0]) for file in files])
                last_file = f'rdb/{table_name}_{max_index}.csv'
                df = pd.read_csv(last_file)
                # check if it's ok to add a new record to this file
                row_string = ','.join(str(value) for value in row_values)
                total_bytes = os.path.getsize(last_file) + len(row_string.encode('utf-8'))
                if total_bytes < memory_size:
                    # write update to existing file
                    df.loc[len(df)] = row_values
                    df.to_csv(last_file, index = False)
                else:
                    # create a new csv file
                    max_index += 1
                    new_file = f'rdb/{table_name}_{max_index}.csv'
                    new_df = pd.DataFrame(columns=first_file_df.columns)
                    new_df.loc[0] = row_values
                    new_df.to_csv(new_file, index=False)
                print("Insert operation completed successfully.")
            
    # note: does not delete file if no more rows left
    def delete(self, table_name, col_name, value):
        pattern = f'rdb/{table_name}_*.csv'
        files = glob.glob(pattern)
        # check if table exists
        if not files:
            print(f'Error: Table {table_name} does not exist.')
        else:
            for file in files:
                df = pd.read_csv(file)
                if value in df[col_name].values:
                    df = df[df[col_name] != value]
                    df.to_csv(file, index=False)
            print("Delete operation completed successfully.")
    
    
    # TODO: check if data type matches 
    def update(self, table_name, col_name, new_value, old_value):
        pattern = f'rdb/{table_name}_*.csv'
        files = glob.glob(pattern)
        # check if table exists
        if not files:
            print(f'Error: Table {table_name} does not exist.')
        else:
            for file in files:
                df = pd.read_csv(file)
                if old_value in df[col_name].values:
                    df[col_name] = df[col_name].replace(old_value, new_value)
                    df.to_csv(file, index=False)
            print("Update operation completed successfully.")
    
    # TODO: specify data type
    def create(self, table_name, col_names):
        fn = f'rdb/{table_name}_0.csv'
        # check if table exists
        if os.path.exists(fn):
            print(f"Error: Table '{table_name}' already exists.")
        else:
            with open(fn, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(col_names)
            print(f"Table {table_name} created.")
