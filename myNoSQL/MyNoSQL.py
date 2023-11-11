import os
import json
import time
import uuid
import hashlib
import heapq
from collections import defaultdict


class MyNoSQL:
    MEMORY_SIZE = 1000

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
    
    def _get_nested_value(self, entry, key_path):
        """Retrieve a value from a nested dictionary given a key path."""
        for key in key_path.split('.'):
            entry = entry.get(key, {})
        return entry

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

        if not query:
            return partition_paths

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

    def join(self, input_file_paths1, input_file_paths2, join_key):
        def generate_joined_entries():
            for file_path1 in input_file_paths1:
                with open(file_path1, 'r') as file1:
                    for line1 in file1:
                        entry1 = json.loads(line1)
                        # Skip if the join key is not in the first entry
                        if join_key not in entry1:
                            continue

                        for file_path2 in input_file_paths2:
                            with open(file_path2, 'r') as file2:
                                for line2 in file2:
                                    entry2 = json.loads(line2)
                                    # Perform the join if the join key exists in both entries
                                    if join_key in entry2 and entry1[join_key] == entry2[join_key]:
                                        joined_entry = {**entry1, **entry2}
                                        yield json.dumps(joined_entry)

        output_files = self._write_to_chunk(generate_joined_entries())
        return output_files
    
    def group_and_aggregate(self, input_file_paths, group_key, aggregations):
        for file_path in input_file_paths:
            temp_aggregation_data = defaultdict(lambda: defaultdict(float))

            with open(file_path, 'r') as file:
                for line in file:
                    entry = json.loads(line)
                    if group_key in entry:
                        group_value = entry[group_key]

                        # Update the aggregation data for this group_value
                        temp_aggregation_data[group_value]['_count'] += 1  # Count each occurrence
                        for field, agg in aggregations.items():
                            if field in entry:
                                if agg in ['sum', 'avg']:
                                    temp_aggregation_data[group_value][agg] += entry[field]
                                elif agg == 'min':
                                    temp_aggregation_data[group_value][agg] = min(temp_aggregation_data[group_value][agg], entry[field])
                                elif agg == 'max':
                                    temp_aggregation_data[group_value][agg] = max(temp_aggregation_data[group_value][agg], entry[field])

            # Update the aggregation data in the corresponding temp files
            for group_value, aggregation in temp_aggregation_data.items():
                temp_file_path = os.path.join(self.db_directory, f"group_{group_value}.tmp")
                
                if os.path.exists(temp_file_path):
                    with open(temp_file_path, 'r') as temp_file:
                        existing_data = json.loads(temp_file.read())

                    for agg in aggregations.values():
                        if agg in ['sum', 'avg']:
                            aggregation[agg] += existing_data.get(agg, 0)

                    # Combine counts
                    aggregation['_count'] += existing_data.get('_count', 0)
                    aggregation[group_key] = group_value

                    # Update avg if needed
                    if 'avg' in aggregations.values():
                        aggregation['avg'] = aggregation['sum'] / aggregation['_count']

                with open(temp_file_path, 'w') as temp_file:
                    temp_file.write(json.dumps(aggregation))

        # Generate final output
        def generate_final_output():
            for temp_file_name in os.listdir(self.db_directory):
                if temp_file_name.startswith("group_") and temp_file_name.endswith(".tmp"):
                    with open(os.path.join(self.db_directory, temp_file_name), 'r') as temp_file:
                        yield temp_file.read()
                    os.remove(os.path.join(db.db_directory, temp_file_name))
                    

        final_output_files = self._write_to_chunk(generate_final_output())

        return final_output_files
    
    def ordering(self, input_file_paths, sort_keys, ascending=True):
        sorted_temp_files = []

        # Step 1: Sort each file individually and write to a temp file
        for file_index, file_path in enumerate(input_file_paths):
            with open(file_path, 'r') as file:
                data = [json.loads(line) for line in file]
                # Sort the data based on nested keys and order
                data.sort(key=lambda x: tuple(self._get_nested_value(x, k) for k in sort_keys), reverse=not ascending)
                sorted_temp_file_path = os.path.join(self.db_directory, f"sorted_{file_index}.tmp")
                with open(sorted_temp_file_path, 'w') as sorted_temp_file:
                    for entry in data:
                        sorted_temp_file.write(json.dumps(entry) + "\n")
                sorted_temp_files.append(sorted_temp_file_path)

        # Step 2: Merge sorted files using a multi-way merge algorithm
        def merge_sorted_files(sorted_files, sort_keys, ascending):
            merged_file_path = os.path.join(self.db_directory, "merged_output.tmp")
            with open(merged_file_path, 'w') as outfile:
                # Create a priority queue and initialize it with the first line of each file
                pq = []
                files = [open(f, 'r') for f in sorted_files]
                for f in files:
                    line = f.readline()
                    if line:
                        entry = json.loads(line)
                        sort_values = tuple(self._get_nested_value(entry, k) for k in sort_keys)
                        heapq.heappush(pq, (sort_values, line, f))

                # Process the priority queue and write to the merged file
                while pq:
                    _, line, f = heapq.heappop(pq)
                    outfile.write(line)
                    next_line = f.readline()
                    if next_line:
                        next_entry = json.loads(next_line)
                        sort_values = tuple(self._get_nested_value(next_entry, k) for k in sort_keys)
                        heapq.heappush(pq, (sort_values, next_line, f))

                # Close all file handles
                for f in files:
                    f.close()

            return merged_file_path

        # Apply multi-way merge to the sorted temp files
        merged_file_path = merge_sorted_files(sorted_temp_files, sort_keys, ascending)

        # Step 3: Write final output using _write_to_chunk
        def generate_sorted_data():
            with open(merged_file_path, 'r') as file:
                for line in file:
                    yield line.rstrip('\n')

        final_output_files = self._write_to_chunk(generate_sorted_data())
        
        # Cleanup temporary sorted files and merged file
        for temp_file in sorted_temp_files:
            os.remove(temp_file)
        os.remove(merged_file_path)

        return final_output_files

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


    # Clean old data for testing
    for temp_file_name in os.listdir(db.db_directory):
        if temp_file_name.endswith(".json"):
            os.remove(os.path.join(db.db_directory, temp_file_name))


    # db.update('test_collection', {'aaa' : {'a': 1}}, {'aaa' : 'AAAAAAAAAAAAAAAAAAAAAAAAAA'})
    # tmp_files = db.find('test_collection', {
    #                     "aaa": "AAAAAAAAAAAAAAAAAAAAAAAAAA"})
    # tmp_files = db.project(tmp_files, ['_id'])
    # tmp_files = db.ordering(db._get_all_partition_paths(''))
    # db.output_and_cleanup_all_tmp(tmp_files)

    ## test ordering
    # for i in range(100):
    #     db.insert('test_collection', {'a' : {'a': i}})
    # files = db.find('test_collection')
    # files = db.ordering(files, ["a.a"])
    # db.output_and_cleanup_all_tmp(files)

    ## test join
    # for i in range(50):
    #     db.insert('collection1', {'join_key': i, 'collection1_value': f"value1_{i}"})
    # for i in range(50):
    #     db.insert('collection2', {'join_key': i, 'collection2_value': f"value2_{i}"})
    # files1 = db.find('collection1')
    # files2 = db.find('collection2')
    # join_key = "join_key"
    # joined_files = db.join(files1, files2, join_key)
    # final_output_files = db.output_and_cleanup_all_tmp(joined_files)

    ## Test Aggregate & Grouping
    # 生成销售数据
    items = ['item1', 'item2', 'item3']
    for i in range(30):
        db.insert('sales', {
            'item': items[i % len(items)],
            'quantity': i + 1,
            'price': (i + 1) * 10
        })

    # 找到销售数据
    sales_files = db.find('sales')

    # 定义分组键和聚合操作
    group_key = 'item'
    aggregations = {
        'quantity': 'sum',
        'price': 'avg'
    }

    # 进行分组和聚合操作
    grouped_file = db.group_and_aggregate(sales_files, group_key, aggregations)

    # 输出分组和聚合结果，并清理临时文件
    db.output_and_cleanup_all_tmp(grouped_file)

    # print(db.delete('test_collection', {'aaa': 0}))
