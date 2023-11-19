import re

class MyQLParser:
    def __init__(self):
        raise NotImplementedError("StaticClass cannot be instantiated")
    
    @staticmethod
    def _to_number(value):
        try:
            return int(value)
        except ValueError:
            try:
                return float(value) 
            except ValueError:
                raise(f"Error: The value '{value}' is not a number.")

    @staticmethod
    def parse_projection(query):
        '''get [col1_name, col2_name, col3_name, ...] from [table_name]'''
        '''get [col1_name, col2_name, col3_name, ...] from [table_name], limit [n]'''
        match = re.match(r"get ([\w\s,]+) from (\w+)(?:, limit (\d+))?", query)
        if match:
            col_names, table_name, limit = match.groups()
            col_names = col_names.split(',') 
            for i in range(len(col_names)):
                col_names[i] = col_names[i].strip()
            limit = int(limit) if limit else None
            return col_names, table_name, limit
        else:
            raise ValueError("Invalid projection syntax")

    @staticmethod
    def parse_filtering(query):
        '''find [table_name] that have a [col] of at [least / most] [numeric_value]'''
        '''find [table_name] that have a [col] of at [least / most] [numeric_value], limit [n]'''
        '''find [table] that [col] is [value]'''
        '''find [table] that [col] is [value], limit [n]'''
        if "of at least" in query:
            match = re.match(r"find (\w+) that have a (\w+) of at least (\d+)(?:, limit (\d+))?", query)
            if match:
                table_name, col_name, value, limit = match.groups()
                # only valid for numeric values
                value = MyQLParser._to_number(value)
                limit = int(limit) if limit else None
                return col_name, table_name, value, ">=", limit
            else:
                raise ValueError("Invalid filtering syntax")
        elif "of at most" in query:
            match = re.match(r"find (\w+) that have a (\w+) of at most (\d+)(?:, limit (\d+))?", query)
            if match:
                table_name, col_name, value, limit = match.groups()
                # only valid for numeric values
                value = MyQLParser._to_number(value)
                limit = int(limit) if limit else None
                return col_name, table_name, value, "<=", limit
            else:
                raise ValueError("Invalid filtering syntax")
        elif " is " in query:
            match = re.match(r"find (\w+) that (\w+) is ([\s\S]+)(?:, limit (\d+))?", query)
            if match:
                table_name, col_name, value, limit = match.groups()
                # valid for both texts and numeric values
                limit = int(limit) if limit else None
                return col_name, table_name, value, "=", limit
            else:
                raise ValueError("Invalid filtering syntax")
        else:
            raise ValueError("Invalid filtering syntax")
        
    @staticmethod
    def parse_ordering(query):
        '''order [table_name] by [col] in [descending / ascending] order'''
        '''order [table_name] by [col] in [descending / ascending] order, limit [n]'''
        match = re.match(r"order (\w+) by (\w+) in (descending|ascending) order(?:, limit (\d+))?", query)
        if match:
            table_name, col_name, order, limit = match.groups()
            asecending = order == "ascending"
            limit = int(limit) if limit else None
            return table_name, col_name, asecending, limit
        else:
            raise ValueError("Invalid ordering syntax")

    @staticmethod
    # limit not implemented
    def parse_grouping(query):
        '''group [table_name] by [col1_name] and give me the [sum / average] of [col2_name]'''
        match = re.match(r"group (\w+) by (\w+) and give me the (sum|average|count) of (\w+)", query)
        if match:
            table_name, col1_name, calculation, col2_name = match.groups()
            return table_name, col1_name, calculation, col2_name
        else:
            raise ValueError("Invalid grouping syntax") 
    
    @staticmethod
    def parse_aggregation(query):
        '''give me the [sum / average ] of [col_name] for [table_name]'''
        # TODO: add parser for count
        match = re.match(r"give me the (sum|average|count) of (\w+) for (\w+)", query)
        if match:
            type, col_name, table_name = match.groups()
            return type, col_name, table_name
        else:
            raise ValueError("Invalid aggregation syntax")
    
    @staticmethod
    def parse_inner_join(query):
        '''combine rows from [table1_name] and [table2_name] where their [col] values match'''
        '''combine rows from [table1_name] and [table2_name] where their [col] values match, limit [n]'''
        match = re.match(r"combine rows from (\w+) and (\w+) where their (\w+) values match(?:, limit (\d+))?", query)
        if match:
            table1_name, table2_name, col_name, limit = match.groups()
            limit = int(limit) if limit else None 
            return table1_name, table2_name, col_name, limit
        else:
            raise ValueError("Invalid insert syntax")
    
    @staticmethod
    def parse_insert(query):
        '''insert [row_value] into [table_name]'''
        match = re.match(r"insert (.+) into (\w+)", query)
        if match:
            row_values, table_name = match.groups()
            row_values = [value.strip() for value in row_values.split(',')]
            return row_values, table_name
        else:
            raise ValueError("Invalid insert syntax")
    
    @staticmethod
    def parse_delete(query):
        '''delete from [table_name] where [col_name] = [value]'''
        match = re.match(r"delete from (\w+) where (\w+) = (.+)", query)
        if match:
            table_name, col_name, value = match.groups()
            return table_name, col_name, value
        else:
            raise ValueError("Invalid delete syntax")
    
    @staticmethod
    def parse_update(query):
        '''update [table_name] set [col_name] = [new_value] where [col_name] = [old_value]'''
        match = re.match(r"update (\w+) set (\w+) = (.+) where (\w+) = (.+)", query)
        if match:
            table_name, col1_name, new_value, col2_name, old_value = match.groups()
            if col1_name != col2_name:
                raise ValueError("Column names do not match for update")
            return table_name, col1_name, new_value, old_value
        else:
            raise ValueError("Invalid update syntax")
        
    @staticmethod
    def parse_create(query):
        '''create table [table_name] ([col1_name], [col2_name], [col3_name], ...)'''
        match = re.match(r"create table (\w+)\s*\(([\w\s,]+)\)", query)
        if match:
            table_name, col_names = match.groups()
            col_names = [c.strip() for c in col_names.split(',') if c.strip()]
            return table_name, col_names
        else:
            raise ValueError("Invalid create table syntax")
        
    
    @staticmethod
    def parse_load(query):
        '''load [file_path]'''
        match = re.match(r"load ([^\s]+)", query)
        if match:
            (file_path,) = match.groups()
            return file_path
        else:
            raise ValueError("Invalid load syntax")