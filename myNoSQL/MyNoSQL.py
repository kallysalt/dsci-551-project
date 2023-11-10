import os
import json
import time
import uuid


class MyNoSQL:
    MEMORY_SIZE = 200

    def __init__(self, db_directory='./myNoSQL/data'):
        self.db_directory = db_directory
        if not os.path.exists(db_directory):
            os.makedirs(db_directory)

    def _generate_id(self):
        # Generate a unique identifier for a document
        return str(uuid.uuid4())

    def _get_timestamp(self):
        # return current timestamp
        return int(time.time())

    def _get_all_partition_paths(self, collection):
        # Retrieve all partition paths for the collection
        partitions = []
        index = 0
        while True:
            partition_path = os.path.join(
                self.db_directory, f"{collection}.{index}.json")
            if os.path.exists(partition_path):
                partitions.append(partition_path)
                index += 1
            else:
                break
        return partitions

    def _get_partition_path(self, collection, document_size=0):
        # Check partition sizes and increment the partition index until an unfilled partition is found
        index = 0
        partition_path = os.path.join(
            self.db_directory, f"{collection}.{index}.json")
        while os.path.exists(partition_path) and os.path.getsize(partition_path) + document_size > self.MEMORY_SIZE:
            index += 1
            partition_path = os.path.join(
                self.db_directory, f"{collection}.{index}.json")
        return partition_path

    def _write_to_chunk(self, data_generator):
        """Write data to chunk files with a unified naming convention."""
        output_files = []
        temp_data = ""
        temp_size = 0
        chunk_index = 0

        while True:
            chunk_name = f"output.{chunk_index}.tmp"
            chunk_path = os.path.join(self.db_directory, chunk_name)
            for entry_json in data_generator:
                entry_size = len(entry_json.encode('utf-8'))

                if temp_size + entry_size > self.MEMORY_SIZE:
                    with open(chunk_path, 'w') as chunk_file:
                        chunk_file.write(temp_data)
                    output_files.append(chunk_path)

                    chunk_index += 1
                    temp_data = entry_json + "\n"
                    temp_size = entry_size
                    break
                else:
                    temp_data += entry_json + "\n"
                    temp_size += entry_size
            else:
                if temp_data:
                    with open(chunk_path, 'w') as chunk_file:
                        chunk_file.write(temp_data)
                    output_files.append(chunk_path)
                break

        return output_files

    def insert(self, collection, document):
        # Add _id and _updated fields to the document
        if '_id' not in document:
            document['_id'] = self._generate_id()
        document['_updated'] = self._get_timestamp()

        # Convert document to JSON string and get its size
        document_json = json.dumps(document)
        document_size = len(document_json.encode('utf-8'))

        # Get the correct partition path, accounting for the new document size
        partition_path = self._get_partition_path(collection, document_size)

        # Append the new document to the partition file
        with open(partition_path, 'a') as f:
            f.write(document_json + "\n")

    def find(self, collection, query=None):
        partition_paths = self._get_all_partition_paths(collection)

        def generate_entries():
            for partition_path in partition_paths:
                with open(partition_path, 'r') as f:
                    for line in f:
                        entry = json.loads(line)
                        if not query or all(item in entry.items() for item in query.items()):
                            yield json.dumps(entry)

        output_files = self._write_to_chunk(generate_entries())
        return output_files

    def project(self, input_file_paths, projection_fields):
        def generate_projected_entries():
            for file_path in input_file_paths:
                with open(file_path, 'r') as f:
                    for line in f:
                        entry = json.loads(line)
                        # Only include keys that are in the projection fields
                        projected_entry = {
                            key: value for key, value in entry.items() if key in projection_fields}
                        yield json.dumps(projected_entry)

        # Since the _write_to_chunk method writes to the output.*.tmp pattern, we just call it directly.
        output_files = self._write_to_chunk(generate_projected_entries())
        return output_files

    def update(self, collection, query, new_values):
        # Retrieve all partition paths for the collection
        partition_paths = self._get_all_partition_paths(collection)
        update_timestamp = self._get_timestamp()

        # Attempt to update documents in existing partitions
        for partition_path in partition_paths:
            temp_file = partition_path + ".tmp"
            partition_updated = False  # Flag to check if the partition was rewritten
            with open(partition_path, 'r') as f, open(temp_file, 'w') as tf:
                partition_size = 0  # Initialize partition size
                for line in f:
                    entry = json.loads(line)
                    if '_updated' in entry and entry['_updated'] >= update_timestamp:
                        # This document has already been updated, skip it
                        tf.write(line)
                        partition_size += len(line.encode('utf-8'))
                        continue

                    if all(item in entry.items() for item in query.items()):
                        # Document matches query, update it
                        entry.update(new_values)
                        entry['_updated'] = update_timestamp
                        updated_document = json.dumps(entry) + "\n"
                        updated_document_size = len(
                            updated_document.encode('utf-8'))
                        if partition_size + updated_document_size <= self.MEMORY_SIZE:
                            # There is space in the current partition
                            tf.write(updated_document)
                            partition_size += updated_document_size
                        else:
                            # Not enough space in the current partition, write to a new partition
                            new_partition_path = self._get_partition_path(
                                collection, updated_document_size)
                            with open(new_partition_path, 'a') as np:
                                np.write(updated_document)
                        partition_updated = True
                    else:
                        # Document does not match query, write it back
                        tf.write(line)
                        partition_size += len(line.encode('utf-8'))

            # Replace the original partition with the temp file if needed
            if partition_updated:
                os.replace(temp_file, partition_path)
            else:
                os.remove(temp_file)

    def delete(self, collection, query):
        # Retrieve all partition paths for the collection
        partition_paths = self._get_all_partition_paths(collection)

        # Attempt to delete documents in existing partitions
        for partition_path in partition_paths:
            temp_file = partition_path + ".tmp"
            with open(partition_path, 'r') as f, open(temp_file, 'w') as tf:
                for line in f:
                    entry = json.loads(line)
                    # Write the line to temp file only if it does not match the query
                    if not all(item in entry.items() for item in query.items()):
                        tf.write(line)

            # Replace the original partition with the temp file
            os.replace(temp_file, partition_path)

    def output_and_cleanup_all_tmp(self, tmp_files):
        for file_path in tmp_files:
            with open(file_path, 'r') as f:
                for line in f:
                    print(line.strip())

        # Remove all the file ends with .tmp
        # all_files = os.listdir(self.db_directory)
        # for tmp_file in [file for file in all_files if file.endswith('.tmp')]:
        #     tmp_file_path = os.path.join(self.db_directory, tmp_file)
        #     os.remove(tmp_file_path)


if __name__ == '__main__':
    db = MyNoSQL()
    # db.insert('test_collection', {'aaa' : {'a': 1}})
    # db.update('test_collection', {'aaa' : {'a': 1}}, {'aaa' : 'AAAAAAAAAAAAAAAAAAAAAAAAAA'})
    tmp_files = db.find('test_collection', {
                        "aaa": "AAAAAAAAAAAAAAAAAAAAAAAAAA"})
    tmp_files = db.project(tmp_files, ['_id'])
    db.output_and_cleanup_all_tmp(tmp_files)

    # print(db.delete('test_collection', {'aaa': 0}))
