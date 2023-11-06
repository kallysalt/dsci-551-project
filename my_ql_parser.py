import re
import utils

class MyQLParser:
    def __init__(self):
        raise NotImplementedError("StaticClass cannot be instantiated")

    @staticmethod
    def parse_projection(query):
        match = re.match(r"get ([\w\, ]+) from (\w+)", query)
        if match:
            col_names, table_name = match.groups()
            col_names = col_names.split(',') 
            for i in range(len(col_names)):
                col_names[i] = col_names[i].strip()
            return col_names, table_name
        else:
            raise ValueError("Invalid projection syntax")

    @staticmethod
    def parse_filtering(query):
        if "of at least" in query:
            match = re.match(r"find (\w+) that have a (\w+) of at least (\d+)", query)
            if match:
                table_name, col_name, value = match.groups()
                value = utils.to_number(value)
                return col_name, table_name, value, ">="
            else:
                raise ValueError("Invalid filtering syntax")
        elif "of at most" in query:
            match = re.match(r"find (\w+) that have a (\w+) of at most (\d+)", query)
            if match:
                table_name, col_name, value = match.groups()
                value = utils.to_number(value)
                return col_name, table_name, value, "<="
            else:
                raise ValueError("Invalid filtering syntax")
        elif " is " in query:
            match = re.match(r"find (\w+) that (\w+) is (.+)", query)
            if match:
                table_name, col_name, value = match.groups()
                value = utils.to_number(value)
                return col_name, table_name, value, "="
            else:
                raise ValueError("Invalid filtering syntax")
        else:
            raise ValueError("Invalid filtering syntax")
        
    @staticmethod
    def parse_ordering(query):
        match = re.match(r"order (\w+) by (\w+) in (descending|ascending) order", query)
        if match:
            table_name, col_name, order = match.groups()
            return table_name, col_name, order
        else:
            raise ValueError("Invalid ordering syntax")
        
    @staticmethod
    def parse_grouping(query):
        pass
    
    @staticmethod
    def parse_aggregation(query):
        pass
    
    @staticmethod
    def parse_inner_join(query):
        pass
    
    @staticmethod
    def parse_insert(query):
        
        pass
    
    @staticmethod
    def parse_update(query):
        pass
    
    @staticmethod
    def parse_delete(query):
        pass