import csv
import re
import pandas as pd
import sys
import os

import utils
from query_parser import QueryParser

class RelationalDB:
    
    def __init__(self):
        pass
    
    
    def query(self, args):
        # print(f"Querying Relational database with: {args}")
        if args:
            # print(args)
            if args[0] == "\"" and args[-1] == "\"":
                args = args[1:-1]
            self.parse_query(args) 
        else:
            print("No query provided")
        

    def parse_query(self, query):
        query = query.lower()
        
        if query.startswith("get"):
            cols, table = QueryParser.parse_projection(query)
            self.projection(cols, table)
        
        elif query.startswith("find"):
            col, table, value, criteria = QueryParser.parse_filtering(query)
            self.filtering(col, table, value, criteria)
            
        elif query.startswith("order"):
            table, col, order = QueryParser.parse_ordering(query)
            self.ordering(table, col, order)

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
    def projection(self, cols, table):
    
        fn = f'{table}.csv'
        
        # determine chunk size
        total_rows = sum(1 for _ in open(fn, 'r', encoding = 'utf-8')) - 1  # Minus 1 for the header
        chunk_size = max(1, total_rows // 10)  # Ensure at least 1 row per chunk to avoid division by zero

        # read specified csv file, 10% at a time
        for i, chunk in enumerate(pd.read_csv(fn, usecols = cols, chunksize = chunk_size)):
            tmp_fn = f"{table}_chunk.csv"
            chunk.to_csv(tmp_fn, index = False)
            utils.print_df(chunk, i)
            os.remove(tmp_fn)
        

    # TODO: create chunks based on memory size vs. file soze instead of 10% rule        
    # TODO: we are not allowed to use chunk size parameter provided by pandas        
    def filtering(self, col, table, value, criteria):

        fn = f'{table}.csv'
        
        # determine chunk size
        total_rows = sum(1 for _ in open(fn, 'r', encoding = 'utf-8')) - 1  # Minus 1 for the header
        chunk_size = max(1, total_rows // 10)  # Ensure at least 1 row per chunk to avoid division by zero
        
        # read specified csv file, 10% at a time
        for i, chunk in enumerate(pd.read_csv(fn, chunksize = chunk_size)):
            # filter chunk file based on criteria
            if criteria == '=':
                chunk = chunk[chunk[col] == value]
            elif criteria == '>=':
                chunk = chunk[chunk[col] >= value]
            elif criteria == '<=':
                chunk = chunk[chunk[col] <= value]
            else:
                print("Invalid criteria")
                return
            if chunk.empty:
                continue
            
            tmp_fn = f"{table}_chunk.csv"
            chunk.to_csv(tmp_fn, index = False)
            utils.print_df(chunk, i)
            os.remove(tmp_fn)
            

    # TODO: create chunks based on memory size vs. file soze instead of 10% rule        
    # TODO: we are not allowed to use chunk size parameter provided by pandas      
    # TODO: we are not allowed to use sort_values() function provided by pandas
    # TODO: incorrect sorting results -> need to sort each chunk and then combine             
    def ordering(self, table, col, order):
    
        fn = f'{table}.csv'
        
        # determine chunk size
        total_rows = sum(1 for _ in open(fn, 'r', encoding = 'utf-8')) - 1  # Minus 1 for the header
        chunk_size = max(1, total_rows // 10)  # Ensure at least 1 row per chunk to avoid division by zero
        
        # read specified csv file, 10% at a time
        for i, chunk in enumerate(pd.read_csv(fn, usecols = [col], chunksize = chunk_size)):
            
            if order == 'ascending':
                chunk = chunk.sort_values(by=col, ascending=True)
            elif order == 'descending':
                chunk = chunk.sort_values(by=col, ascending=False)
            else:
                print("Invalid order")
                return
            
            tmp_fn = f"{table}_chunk.csv"
            chunk.to_csv(tmp_fn, index = False)
            utils.print_df(chunk, i)
            os.remove(tmp_fn)
    

    def inner_join(query):
        pass 

    def grouping(query):
        pass  

    def aggregation(query):
        pass
