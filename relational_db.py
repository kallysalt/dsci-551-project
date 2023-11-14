import csv
import re
import pandas as pd
import sys
import os
import glob
from tabulate import tabulate
import json
import typing

from my_ql_parser import MyQLParser

memory_size = 512 # bytes

class RelationalDB:
    def __init__(self):
        pass
    
    def _print_df(self, df, i):
        header = True if i == 0 else False
        print(df.to_csv(index = False, header = header))
    
    def _write_dict_to_file(self, data_dict, file_path):
        with open(file_path, 'w') as file:
            json.dump(data_dict, file)

    def _read_dict_from_file(self, file_path):
        with open(file_path, 'r') as file:
            return json.load(file)

    def _aggregate_data(self, df, col1_name, calculation, col2_name):
        aggregation_dict = {}
        for _, row in df.iterrows():
            key = row[col1_name]
            value = row[col2_name]
            if calculation == 'sum':
                aggregation_dict[key] = aggregation_dict.get(key, 0) + value
            elif calculation == 'avg':
                if key in aggregation_dict:
                    sum_, count_ = aggregation_dict[key]
                    aggregation_dict[key] = (sum_ + value, count_ + 1)
                else:
                    aggregation_dict[key] = (value, 1)
        return aggregation_dict
    
    def _bubble_sort(self, data, col_name, ascending = True):
        n = len(data)
        for i in range(n):
            for j in range(0, n-i-1):
                if (data[j][col_name] > data[j+1][col_name] and ascending) or \
                   (data[j][col_name] < data[j+1][col_name] and not ascending):
                    data[j], data[j+1] = data[j+1], data[j]
    
    def _sort_individual_files(self, table_name, col_name, ascending):
        pattern = f'rdb/{table_name}_*.csv'
        files = glob.glob(pattern)
        for file_path in files:
            df = pd.read_csv(file_path)
            data_list = df.to_dict('records')
            # sort the list using bubble sort
            self._bubble_sort(data_list, col_name, ascending)
            # convert the sorted list of dictionaries back to a DataFrame
            df_sorted = pd.DataFrame(data_list)
            # saving the sorted DataFrame with a .tmp extension
            tmp_file_path = f"{file_path}.tmp"
            df_sorted.to_csv(tmp_file_path, index=False)

    def _merge_and_print(self, sorted_temp_files, col_name, ascending):
        # open file handles for all sorted temporary files
        file_handles = [open(f, 'r') for f in sorted_temp_files]
        readers = [pd.read_csv(fh, iterator=True) for fh in file_handles]
        # fetch the first row from each file
        current_rows = [next(reader) for reader in readers]
        # merge and print
        while any(rows is not None for rows in current_rows):
            # determine the next row to print
            next_index = None
            next_value = None
            for i, row in enumerate(current_rows):
                if row is not None:
                    value = row[col_name].iloc[0]
                    if (next_value is None or (ascending and value < next_value) or (not ascending and value > next_value)):
                        next_index = i
                        next_value = value
            # print the next row
            if next_index is not None:
                print(current_rows[next_index].to_csv(header=False, index=False).strip())
                try:
                    current_rows[next_index] = next(readers[next_index])
                except StopIteration:
                    current_rows[next_index] = None
                    file_handles[next_index].close()  # close the file handle when done
        # close any remaining open files and delete temporary files
        for fh in file_handles:
            fh.close()
        for f in sorted_temp_files:
            os.remove(f)
    
    def query(self, args):
        if args:
            if args[0] == "\"" and args[-1] == "\"":
                args = args[1:-1]
            self.parse_query(args) 
        else:
            print("No query provided")
        
    def parse_query(self, query):
        if query.startswith("get"):
            col_names, table_name = MyQLParser.parse_projection(query)
            self.projection(col_names, table_name)
            
        elif query.startswith("find"):
            col_name, table_name, value, criteria = MyQLParser.parse_filtering(query)
            self.filtering(col_name, table_name, value, criteria)
            
        elif query.startswith("order"):
            table_name, col_name, ascending = MyQLParser.parse_ordering(query)
            self.ordering(table_name, col_name, ascending)
            
        elif query.startswith("group"):
            table_name, col1_name, calculation, col2_name = MyQLParser.parse_grouping(query)
            self.grouping(table_name, col1_name, calculation, col2_name)
            
        elif query.startswith("calculate"):
            table_name, col_name, order = MyQLParser.parse_aggregation(query)
            self.aggregation(table_name, col_name, order)
        
        elif query.startswith("combine"):
            table1_name, table2_name, col_name = MyQLParser.parse_inner_join(query)
            self.inner_join(table1_name, table2_name, col_name)
        
        elif query.startswith("insert"):
            row_value, table_name = MyQLParser.parse_insert(query)
            self.insert(row_value, table_name)
        
        elif query.startswith("delete"):
            table_name, col_name, value = MyQLParser.parse_delete(query)
            self.delete(table_name, col_name, value)
        
        elif query.startswith("update"):
            table_name, col_name, new_val, old_val = MyQLParser.parse_update(query)
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
        files = glob.glob(pattern)
        files.sort() # ASK
        # check if table exists
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
              
    def filtering(self, col_name, table_name, value, criteria):
        pattern = f'rdb/{table_name}_*.csv'
        files = glob.glob(pattern)
        files.sort() # ASK
        # check if table exists
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
        # sort all files individually and store in temporary .tmp files
        self._sort_individual_files(table_name, col_name, order)
        # perform external merge sort on all the sorted .tmp files
        pattern = f'rdb/{table_name}_*.csv.tmp'
        temp_files = glob.glob(pattern)
        if temp_files:
            # print the header
            df = pd.read_csv(f'rdb/{table_name}_0.csv', nrows=0)
            print(','.join(df.columns))
        self._merge_and_print(temp_files, col_name, order)
        
    def inner_join(self, table1_name, table2_name, col_name):
        # fn = f'rdb/{table_name}_{n}.csv'
        # not sure how to implement
        pass 

    # TODO: max, min, count
    def grouping(self, table_name, col1_name, calculation, col2_name):
        # iterate thru all files
        # store aggregation result in a dictionary
        # if dictionary exceed memory size, store in tmp file
        memory_size = 64
        pattern = f'rdb/{table_name}_*.csv'
        files = glob.glob(pattern)
        if not files:
            print(f"Error: Table {table_name} does not exist.")
            return
        aggregated_data = {}
        tmp_files = []
        for file in files:
            df = pd.read_csv(file)
            new_aggregated_data = self._aggregate_data(df, col1_name, calculation, col2_name)
            # check the size of the aggregated data, if it exceeds memory size, write to temp file
            if (sum([len(str(v)) for v in aggregated_data.values()]) + sum([len(str(v)) for v in new_aggregated_data.values()])) > memory_size:
                tmp_file_path = f'rdb/{table_name}_temp_{len(tmp_files)}.json'
                self._write_dict_to_file(aggregated_data, tmp_file_path)
                tmp_files.append(tmp_file_path)
                aggregated_data = new_aggregated_data
            else:
                for key, value in new_aggregated_data.items():
                    if key in aggregated_data:
                        if calculation == 'sum':
                            aggregated_data[key] += value
                        elif calculation == 'avg':
                            sum_, count_ = aggregated_data[key]
                            aggregated_data[key] = (sum_ + value, count_ + 1)
                    else:
                        aggregated_data[key] = value
        # final aggregation from tmp files
        for tmp_file in tmp_files:
            tmp_aggregated_data = self._read_dict_from_file(tmp_file)
            for key, value in tmp_aggregated_data.items():
                if key in aggregated_data:
                    if calculation == 'sum':
                        aggregated_data[key] += value
                    elif calculation == 'avg':
                        sum_, count_ = aggregated_data[key]
                        aggregated_data[key] = (sum_ + value[0], count_ + value[1])
                else:
                    aggregated_data[key] = value
        # if calculation is 'avg', compute the final average
        if calculation == 'avg':
            for key, (sum_, count_) in aggregated_data.items():
                aggregated_data[key] = sum_ / count_
        # output the result
        if calculation == 'avg':
            for key in aggregated_data.keys():
                sum_, count_ = aggregated_data[key]
                aggregated_data[key] = sum_ / count_
            df_result = pd.DataFrame(list(aggregated_data.items()), columns=[col1_name, f'average_of_{col2_name}'])
        else:
            df_result = pd.DataFrame(list(aggregated_data.items()), columns=[col1_name, f'sum_of_{col2_name}'])
        # clean up temporary files
        for tmp_file in tmp_files:
            os.remove(tmp_file)
        # print the result as a table
        print(df_result.to_string(index=False))
        
    # TODO: max, min
    def aggregation(self, type, col_name, table_name):
        try:
            pattern = f'rdb/{table_name}_*.csv'
            files = glob.glob(pattern)
            # check if table exists
            if not files:
                print(f"Error: Table {table_name} does not exist.")
            else:
                aggregated_value = 0
                aggregated_count = 0
                for file in files:
                    df = pd.read_csv(file)
                    aggregated_value += df[col_name].sum()
                    if type != 'avg':
                        aggregated_count += len(df)
                # print aggregated value
                if type == 'sum':
                    print(aggregated_value)
                elif type == 'count':
                    print(aggregated_count)
                elif type == 'avg' and aggregated_count == 0:
                    print(0)
                elif type == 'avg' and aggregated_count > 0:
                    print(aggregated_value / aggregated_count)
        except ValueError:
            print(f"Error: Column {col_name} in table {table_name} contains non-numeric value.")

    # TODO: check for duplicates
    # TODO: check for data type
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
                    # set column names
                    new_df = pd.DataFrame(columns = first_file_df.columns)
                    # insert row
                    new_df.loc[0] = row_values
                    new_df.to_csv(new_file, index = False)
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
                    # delete matching record(s)
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
                # update matching record(s)
                if old_value in df[col_name].values:
                    df[col_name] = df[col_name].replace(old_value, new_value)
                    df.to_csv(file, index = False)
            print("Update operation completed successfully.")
    
    # TODO: specify data type
    def create(self, table_name, col_names):
        fn = f'rdb/{table_name}_0.csv'
        if os.path.exists(fn):
            print(f"Error: Table '{table_name}' already exists.")
        else:
            with open(fn, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(col_names)
            print(f"Table {table_name} created.")
