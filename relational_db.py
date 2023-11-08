import csv
import re
import pandas as pd
import sys
import os

import utils
from my_ql_parser import MyQLParser

class RelationalDB:
    def __init__(self):
        pass
    
    def query(self, args):
        if args:
            if args[0] == "\"" and args[-1] == "\"":
                args = args[1:-1]
            self.parse_query(args) 
        else:
            print("No query provided")
        
    # TODO: optimize performance
    def parse_query(self, query):
        query = query.lower()
        
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
        
        else:
            raise ValueError("Unrecognized command")
    
    # TODO: #chunks = file size // memory size 
    # TODO: we are not allowed to use chunk size parameter provided by pandas
    def projection(self, col_names, table_name):
        fn = f'rdb/{table_name}.csv'
        # determine chunk size
        total_rows = sum(1 for _ in open(fn, 'r', encoding = 'utf-8')) - 1  # Minus 1 for the header
        chunk_size = max(1, total_rows // 10)  # Ensure at least 1 row per chunk to avoid division by zero
        # read specified csv file, 10% at a time
        for i, chunk in enumerate(pd.read_csv(fn, usecols = col_names, chunksize = chunk_size)):
            tmp_fn = f"{table_name}_chunk.csv"
            chunk.to_csv(tmp_fn, index = False)
            utils.print_df(chunk, i)
            os.remove(tmp_fn)
        
    # TODO: #chunks = file size // memory size      
    # TODO: we are not allowed to use chunk size parameter provided by pandas        
    def filtering(self, col_name, table_name, value, criteria):
        fn = f'rdb/{table_name}.csv'
        # determine chunk size
        total_rows = sum(1 for _ in open(fn, 'r', encoding = 'utf-8')) - 1  # Minus 1 for the header
        chunk_size = max(1, total_rows // 10)  # Ensure at least 1 row per chunk to avoid division by zero
        # read specified csv file, 10% at a time
        for i, chunk in enumerate(pd.read_csv(fn, chunksize = chunk_size)):
            # filter chunk file based on criteria
            if criteria == '=':
                chunk = chunk[chunk[col_name] == value]
            elif criteria == '>=':
                chunk = chunk[chunk[col_name] >= value]
            elif criteria == '<=':
                chunk = chunk[chunk[col_name] <= value]
            else:
                print("Invalid criteria")
                return
            if chunk.empty:
                continue
            tmp_fn = f"rdb/{table_name}_chunk.csv"
            chunk.to_csv(tmp_fn, index = False)
            utils.print_df(chunk, i)
            os.remove(tmp_fn)

    # TODO: #chunks = file size // memory size      
    # TODO: we are not allowed to use chunk size parameter provided by pandas    
    def ordering(self, table_name, col_name, order):
        # fn = f'rdb/{table_name}.csv'
        # not sure how to implement
        pass

    def inner_join(self, table1_name, table2_name, col_name):
        # fn = f'rdb/{table_name}.csv'
        # not sure how to implement
        pass 

    def grouping(self, table_name, col1_name, calculation, col2_name):
        # fn = f'rdb/{table_name}.csv'
        # read csv file chunk by chunk
        # for each chunk：
        #   store res of each group in dict
        # print result
        pass  

    def aggregation(self, calculation, col_name, table_name):
        # fn = f'rdb/{table_name}.csv'
        # check if sum or avg
        # if neither -> report err 
        # read csv file chunk by chunk, calc sum / avg
        # report err if found non numeric values
        # print result
        pass
    
    # ASK: append record to end of csv file?
    # assumption: noned to check for duplicates
    def insert(self, row_values, table_name):
        fn = f'rdb/{table_name}.csv'
        # check if table exists
        # if not -> report err
        # check if record len is valid
        # if not -> report err
        # append record to end of csv file
        # return ok
        pass 

    # assumption: allow empty records in csv file
    def delete(self, table_name, col_name, value):
        # fn = f'rdb/{table_name}.csv'
        # check if table exists
        # if not -> report err
        # read csv file (chunk by chunk)
        # for each chunk：
        #   check if record can be found
        #   if found -> delete record
        # return ok
        pass
    
    # assumption: does not check if data type matches 
    def update(self, table_name, col1_name, new_value, old_value):
        # fn = f'rdb/{table_name}.csv'
        # check if table exists
        # if not -> report err
        # read csv file (chunk by chunk)
        # for each chunk：
        #   check if record can be found
        #   if found -> update record
        # return ok
        pass  