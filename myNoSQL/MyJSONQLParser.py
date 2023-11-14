
import json
import re

from MyNoSQL import MyNoSQL

'''
INSERT INTO <collection> VALUES <document>

Get FROM <collection> whose <query>

UPDATE <collection> SET <new_values> whose <query>

DELETE FROM <collection> whose <query>
'''

class MyJSONQLParser:
    def __init__(self, db: MyNoSQL):
        self.db = db

    def _parse_condition(self, condition_str):
        """Parse a single condition string into a dictionary."""
        # Assume the format is 'field operator value'
        field, operator, value = re.split(r'\s+', condition_str, maxsplit=2)
        # Convert value to appropriate type (int, float, or leave as string)
        try:
            value = int(value)
        except ValueError:
            try:
                value = float(value)
            except ValueError:
                pass  # leave as string

        op_map = {
            '>': '$gt',
            '<': '$lt',
            '>=': '$gte',
            '<=': '$lte',
            '=': '$eq'
        }
        return {field: {op_map[operator]: value}}

    def _parse_query(self, query_str):
        """Parse a query string into a dictionary."""
        # Simple AND/OR logic for now
        if ' and ' in query_str:
            return {'$and': [self._parse_condition(cond) for cond in query_str.split(' and ')]}
        elif ' or ' in query_str:
            return {'$or': [self._parse_condition(cond) for cond in query_str.split(' or ')]}
        else:
            return self._parse_condition(query_str)
        
    def _parse_aggregations(self, aggregations_str):
        """Parse aggregations from a string."""
        aggregations = {}
        for part in aggregations_str.split(','):
            field, agg = part.strip().split()
            aggregations[field] = agg
        return aggregations

    def execute(self, command):
        if command[-1] == '.':
            command = command[:-1]

        sub_commands = [cmd.strip() for cmd in command.split(';') if cmd.strip()]
        temp_files = None

        for sub_cmd in sub_commands:
            tokens = sub_cmd.split()

            if tokens[0] == "Add" and tokens[1] == "to":
                collection = tokens[2]
                document = json.loads(' '.join(tokens[3:]))
                self.db.insert(collection, document)

            elif tokens[0] == "Update":
                collection = tokens[1]
                query_str = ' '.join(tokens[tokens.index('where') + 1: tokens.index('set')])
                query = self._parse_query(query_str)
                new_values = json.loads(' '.join(tokens[tokens.index('set') + 1:]))
                self.db.update(collection, query, new_values)

            elif tokens[0] == "Delete":
                collection = tokens[1]
                query_str = ' '.join(tokens[tokens.index('where') + 1:])
                query = self._parse_query(query_str)
                self.db.delete(collection, query)

            if tokens[0] == "Get":
                collection = tokens[1]
                temp_files = self.db.find(collection)

            elif 'filter' in tokens:
                query_str = ' '.join(tokens[1:])
                query = self._parse_query(query_str)
                temp_files = self.db.filter(temp_files, query)

            elif 'join' in tokens:
                collection2 = tokens[tokens.index('join') + 1]
                join_key = tokens[tokens.index('by') + 1]
                temp_files2 = self.db.find(collection2)
                temp_files = self.db.join(temp_files, temp_files2, join_key)

            elif 'group' in tokens and 'aggregate' in tokens:
                group_key = tokens[tokens.index('group') + 1]
                aggregations_str = ' '.join(tokens[tokens.index('aggregate') + 1:])
                aggregations = self._parse_aggregations(aggregations_str)
                temp_files = self.db.group_and_aggregate(temp_files, group_key, aggregations)

            elif 'aggregate' in tokens:
                aggregations_str = ' '.join(tokens[tokens.index('aggregate') + 1:])
                aggregations = self._parse_aggregations(aggregations_str)
                temp_files = self.db.group_and_aggregate(temp_files, None, aggregations)

            elif 'sort' in tokens and 'by' in tokens:
                sort_field = tokens[tokens.index('by') + 1]
                ascending = True if 'ascending' in tokens else False
                temp_files = self.db.ordering(temp_files, [sort_field], ascending)

            elif tokens[0] == 'project':
                projection_string = ''.join(tokens[1:])
                projection_fields = projection_string.split(',')
                print(projection_fields)
                temp_files = self.db.project(temp_files, projection_fields)

        if temp_files:
            self.db.output_and_cleanup_all_tmp(temp_files)
        

if __name__ == '__main__':
    db=MyNoSQL()

    parser = MyJSONQLParser(db)
    # parser.execute("Add to collection1 {\"field1\": \"value1\", \"field2\": \"value2\"}.")
    # parser.execute("Get collection1.")
    # parser.execute("Get collection1; aggregate test.test_value avg.")
    # parser.execute("Get collection1; filter test.test_value >= 40 and test.test_value <= 45.")
    # parser.execute("Get collection1; join collection2 by join_key; filter collection1_value > value1_40.")
    # parser.execute("Get sales; group item aggregate quantity sum, price avg; sort by sum ascending.")
    # parser.execute("Delete collection1 where test.test_value < 5.")
    # parser.execute("Update collection1 where field1 = value1 or test.test_value < 7 set {\"field1\": \"new_updated_value\", \"test\": \"test\"}.")
    # parser.execute("Update collection1 where test.test_value = 7 set {\"test\": null}.")
    # parser.execute("Get collection1; project test,_id.")