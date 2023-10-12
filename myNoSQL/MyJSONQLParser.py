
import json

'''
INSERT INTO <collection> VALUES <document>

FIND FROM <collection> WHERE <query>

UPDATE <collection> SET <new_values> WHERE <query>

DELETE FROM <collection> WHERE <query>
'''

class MyJSONQLParser:
    def __init__(self, db):
        self.db = db

    def execute(self, command):
        tokens = command.split()
        if tokens[0] == "INSERT":
            collection = tokens[2]
            document = json.loads(' '.join(tokens[4:]))

            print(collection, document)

            self.db.insert(collection, document)
            return "Document inserted."

        elif tokens[0] == "FIND":
            collection = tokens[2]
            query = json.loads(' '.join(tokens[4:]))
            return self.db.find(collection, query)

        elif tokens[0] == "UPDATE":
            collection = tokens[1]
            new_values = json.loads(tokens[3])
            query = json.loads(tokens[5])
            self.db.update(collection, query, new_values)
            return "Documents updated."

        elif tokens[0] == "DELETE":
            collection = tokens[2]
            query = json.loads(' '.join(tokens[4:]))
            self.db.delete(collection, query)
            return "Documents deleted."

        else:
            return "Invalid command."
