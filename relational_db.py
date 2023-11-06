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
            pass
        elif query.startswith("aggregate"):
            pass
        elif query.startswith("join"):
            pass
        else:
            raise ValueError("Unrecognized command")
    
    # TODO: create chunks based on memory size vs. file soze instead of 10% rule        
    # TODO: we are not allowed to use chunk size parameter provided by pandas
    def projection(self, col_names, table_name):
        fn = f'data/{table_name}.csv'
        # determine chunk size
        total_rows = sum(1 for _ in open(fn, 'r', encoding = 'utf-8')) - 1  # Minus 1 for the header
        chunk_size = max(1, total_rows // 10)  # Ensure at least 1 row per chunk to avoid division by zero
        # read specified csv file, 10% at a time
        for i, chunk in enumerate(pd.read_csv(fn, usecols = col_names, chunksize = chunk_size)):
            tmp_fn = f"{table_name}_chunk.csv"
            chunk.to_csv(tmp_fn, index = False)
            utils.print_df(chunk, i)
            os.remove(tmp_fn)
        
    # TODO: create chunks based on memory size vs. file soze instead of 10% rule        
    # TODO: we are not allowed to use chunk size parameter provided by pandas        
    def filtering(self, col_name, table_name, value, criteria):
        fn = f'data/{table_name}.csv'
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
            tmp_fn = f"data/{table_name}_chunk.csv"
            chunk.to_csv(tmp_fn, index = False)
            utils.print_df(chunk, i)
            os.remove(tmp_fn)

    # TODO: create chunks based on memory size vs. file size instead of 10% rule        
    # TODO: we are not allowed to use chunk size parameter provided by pandas      
    # TODO: we are not allowed to use sort_values() function provided by pandas
    # TODO: incorrect sorting results -> need to sort each chunk and then combine             
    def ordering(self, table_name, col_name, order):
        fn = f'data/{table_name}.csv'
        # determine chunk size
        total_rows = sum(1 for _ in open(fn, 'r', encoding = 'utf-8')) - 1  # Minus 1 for the header
        chunk_size = max(1, total_rows // 10)  # Ensure at least 1 row per chunk to avoid division by zero
        # read specified csv file, 10% at a time
        for i, chunk in enumerate(pd.read_csv(fn, usecols = [col_name], chunksize = chunk_size)):
            if order == 'ascending':
                chunk = chunk.sort_values(by=col_name, ascending=True)
            elif order == 'descending':
                chunk = chunk.sort_values(by=col_name, ascending=False)
            else:
                print("Invalid order")
                return
            tmp_fn = f"{table_name}_chunk.csv"
            chunk.to_csv(tmp_fn, index = False)
            utils.print_df(chunk, i)
            os.remove(tmp_fn)

    def inner_join(query):
        # fn = f'data/{table_name}.csv'
        
        pass 

    def grouping(query):
        pass  

    def aggregation(query):
        pass
    
    def insert(query):
        # insert record into end of csv file
        
        pass 

    def update(query):
        # read csv file (chunk by chunk)
        # locate & update record
        pass  

    def delete(query):
        # read csv file (chunk by chunk)
        # locate & update record
        pass