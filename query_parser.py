import re
import utils


class QueryParser:
    
    def __init__(self):
        raise NotImplementedError("StaticClass cannot be instantiated")

    @staticmethod
    def parse_projection(query):
        match = re.match(r"get ([\w\, ]+) from (\w+)", query)
        if match:
            cols, table = match.groups()
            cols = cols.split(',') 
            for i in range(len(cols)):
                cols[i] = cols[i].strip()
            return cols, table
        else:
            raise ValueError("Invalid projection syntax")

    
    @staticmethod
    def parse_filtering(query):
        if "of at least" in query:
            match = re.match(r"find (\w+) that have a (\w+) of at least (\d+)", query)
            if match:
                table, col, value = match.groups()
                value = utils.to_number(value)
                return col, table, value, ">="
            else:
                raise ValueError("Invalid filtering syntax")
        
        elif "of at most" in query:
            match = re.match(r"find (\w+) that have a (\w+) of at most (\d+)", query)
            if match:
                table, col, value = match.groups()
                value = utils.to_number(value)
                return col, table, value, "<="
            else:
                raise ValueError("Invalid filtering syntax")
        
        elif " is " in query:
            match = re.match(r"find (\w+) that (\w+) is (.+)", query)
            if match:
                table, col, value = match.groups()
                value = utils.to_number(value)
                return col, table, value, "="
            else:
                raise ValueError("Invalid filtering syntax")
        
        else:
            raise ValueError("Invalid filtering syntax")
        
        
    @staticmethod
    def parse_ordering(query):
        match = re.match(r"order (\w+) by (\w+) in (descending|ascending) order", query)
        if match:
            table, column, order = match.groups()
            return table, column, order
        else:
            raise ValueError("Invalid ordering syntax")