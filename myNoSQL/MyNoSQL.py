import json
import os
import hashlib

class MyNoSQL:
    def __init__(self, db_directory = './myNoSQL/data'):
        self.db_directory = db_directory
        if not os.path.exists(db_directory):
            os.makedirs(db_directory)

    def _get_partition(self, collection):
        # Create a hash of the collection name
        hash_object = hashlib.md5(collection.encode())
        partition_name = hash_object.hexdigest()[:6]  # Use the first 6 characters of the hash
        return os.path.join(self.db_directory, partition_name + ".jsons")

    def insert(self, collection, document):
        partition_path = self._get_partition(collection)
        with open(partition_path, 'a') as f:
            entry = {collection: document}
            f.write(json.dumps(entry) + "\n")

    def find(self, collection, query=None):
        results = []
        partition_path = self._get_partition(collection)
        if not os.path.exists(partition_path):
            return results
        with open(partition_path, 'r') as f:
            for line in f:
                entry = json.loads(line)
                if collection not in entry:
                    continue
                if not query or all(item in entry[collection].items() for item in query.items()):
                    results.append(entry[collection])
        return results

    def update(self, collection, query, new_values):
        partition_path = self._get_partition(collection)
        temp_file = partition_path + ".tmp"
        if not os.path.exists(partition_path):
            return
        with open(partition_path, 'r') as f, open(temp_file, 'w') as tf:
            for line in f:
                entry = json.loads(line)
                if collection not in entry:
                    continue
                if all(item in entry[collection].items() for item in query.items()):
                    entry[collection].update(new_values)
                tf.write(json.dumps(entry) + "\n")
        os.rename(temp_file, partition_path)

    def delete(self, collection, query):
        partition_path = self._get_partition(collection)
        temp_file = partition_path + ".tmp"
        if not os.path.exists(partition_path):
            return
        with open(partition_path, 'r') as f, open(temp_file, 'w') as tf:
            for line in f:
                entry = json.loads(line)
                if collection in entry and not all(item in entry[collection].items() for item in query.items()):
                    tf.write(line)
        os.rename(temp_file, partition_path)


if __name__ == '__main__':
    db = MyNoSQL('myNoSQL')
    db.insert('test_collection', {'aaa' : {'a': 1}})
    db.update('test_collection', {'aaa' : {'a': 1}}, {'aaa' : None})
    # print(db.find('test_collection', {'aaa': 0}))