import csv
import pandas as pd
import os
import glob
import json
import heapq
import json

from MyRDBParser import MyRDBParser

# csv.reader: a lazy iterator that reads and processes the file line by line
# csv.DictReader & csv.DictWriter: read from and write to CSV files using dictionaries
# select col(s): df[col_names]

class MyRDB:
    def __init__(self):
        # assupmtion: max file size is half of memeory size
        self.max_file_size = 4096 # bytes
        
    # note: sorted by file name
    def _get_all_partition_paths(self, table_name):
        pattern = f'rdb/{table_name}/{table_name}_*.csv'
        files = glob.glob(pattern)
        if not files:
            print(f'Error: Table {table_name} does not exist.')
        files.sort()
        return files
    
    # note: truncate if data string is too long 
    def _print_df(self, df, is_first_file, cnt, limit):
        header = True if is_first_file else False
        max_width = 25
        df.isnull().any(axis = 0)
        formatters = {column: lambda x: f'{str(x)[:max_width]:<{max_width}}' for column in df.columns}
        if cnt + len(df) < limit:
            # print all
            print(df.to_string(index = False, header = header, justify='left', formatters = formatters, na_rep=''))
            cnt += len(df)
        else: 
            # print only up to the limit
            rows_to_print = limit - cnt
            print(df.iloc[:rows_to_print].to_string(index = False, header = header, justify = 'left', formatters = formatters, na_rep = ''))
            cnt = limit
        return cnt
        
    def _print_csv_files(self, files, limit = 15):
        is_first_file = True
        cnt = 0
        if files:
            for file in files:
                df = pd.read_csv(file)
                cnt = self._print_df(df, is_first_file, cnt, limit)
                is_first_file = False
                if cnt >= limit:
                    return
        
    def _delete_files(self, files):
        for file in files:
            os.remove(file)
    
    def _delete_tmp_files(self):
        pattern = f'rdb/*/*.tmp'
        files = glob.glob(pattern)
        for file in files:
            os.remove(file)
    
    def _to_number(self, value):
        try:
            return int(value)
        except ValueError:
            try:
                return float(value) 
            except ValueError:
                raise ValueError(f"Error: The value '{value}' is not a number.")
    
    def _append_row(self, row_values, file):
        row_string = ','.join(str(value) for value in row_values)
        total_bytes = os.path.getsize(file) + len(row_string.encode('utf-8'))
        # check if adding this row would exceed the max file size
        if total_bytes > self.max_file_size:
            # create a new file
            suffix = file.split('.')[-1]
            prefix = file.split('.')[0]
            index = prefix.split('_')[-1]
            prefix = prefix.split(index)[0]
            new_file = f'{prefix}{int(index) + 1}.{suffix}'
            # get header from prev file
            with open(file, 'r') as f: 
                reader = csv.reader(f)
                header = next(reader)  
            # write header and row to new file
            with open(new_file, 'a', newline = '') as f:
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerow(row_values)
            file = new_file
        else:
            # append row to current file
            with open(file, 'a', newline = '') as f:
                writer = csv.writer(f)
                writer.writerow(row_values)
        return file
    
    def _bubble_sort(self, data_list, col_name, ascending):
        n = len(data_list)
        for i in range(n):
            for j in range(0, n-i-1):
                if (data_list[j][col_name] > data_list[j+1][col_name] and ascending) or \
                   (data_list[j][col_name] < data_list[j+1][col_name] and not ascending):
                    data_list[j], data_list[j+1] = data_list[j+1], data_list[j]
    
    def _sort_individual_files(self, table_name, col_name, ascending):
        files = self._get_all_partition_paths(table_name)
        sorted_files = []
        for file in files:
            data_list = pd.read_csv(file).to_dict('records')
            # sort the list using bubble sort
            self._bubble_sort(data_list, col_name, ascending)
            tmp_file = file.replace('.csv', '.tmp')
            pd.DataFrame(data_list).to_csv(tmp_file, index = False)
            sorted_files.append(tmp_file)
        return sorted_files
    
    def _insert_into_pq(self, pq, reader, unique_id_counter, col_name, ascending):
        try:
            row = next(reader)
            val = self._to_number(row[col_name])
            # since heapq is a min heap, we need to convert to negative if descending
            if not ascending:
                val = -val
            heapq.heappush(pq, ((val, unique_id_counter), row, reader))
        except StopIteration: 
            pass # ignore exhausted files
        except ValueError:
            raise ValueError(f"Error: Column {col_name} contains non-numeric value.")

    def _k_way_merge(self, sorted_files, table_name, col_name, ascending):
        merged_files = []
        file_pointers = [open(file, 'r') for file in sorted_files]
        csv_readers = [csv.DictReader(fp) for fp in file_pointers] 
        # push first row from each file into pq
        pq = []
        unique_id_counter = 0
        for reader in csv_readers:
            self._insert_into_pq(pq, reader, unique_id_counter, col_name, ascending)
            unique_id_counter += 1  
        # create _merged_0.tmp file
        current_file = f'rdb/{table_name}/{table_name}_merged_0.tmp'
        col_names = csv_readers[0].fieldnames        
        with open(current_file, 'w', newline = '') as f:
            writer = csv.writer(f)
            writer.writerow(col_names)
        while pq:
            # pop smallest row from the heap and append to _merged_{n}.tmp file 
            _, row, reader = heapq.heappop(pq)
            new_file = self._append_row(row.values(), current_file)
            if new_file != current_file:
                # a new file was created
                merged_files.append(new_file)
                current_file = new_file
            # push the next row from the same file into pq
            self._insert_into_pq(pq, reader, unique_id_counter, col_name, ascending)
            unique_id_counter += 1  
        # close file pointers
        for fp in file_pointers:
            fp.close()
        return merged_files
    
    
    def query(self, args):
        if args:
            if args[0] == "\"" and args[-1] == "\"":
                args = args[1:-1]
            self.parse_query(args) 
        else:
            print("No query provided")
        
        
    def parse_query(self, query):
        if query.startswith("get"):
            col_names, table_name, limit = MyRDBParser.parse_projection(query)
            tmp_files = self.projection(col_names, table_name)
            if limit:
                self._print_csv_files(tmp_files, limit)
            else:
                self._print_csv_files(tmp_files)
            self._delete_files(tmp_files)
            
        elif query.startswith("find"):
            col_name, table_name, value, criteria, limit = MyRDBParser.parse_filtering(query)
            tmp_files = self.filtering(col_name, table_name, value, criteria)
            if limit:
                self._print_csv_files(tmp_files, limit)
            else:
                self._print_csv_files(tmp_files)
            self._delete_files(tmp_files)
            
        elif query.startswith("order"):
            table_name, col_name, ascending, limit = MyRDBParser.parse_ordering(query)
            tmp_files = self.ordering(table_name, col_name, ascending)
            if limit:
                self._print_csv_files(tmp_files, limit)
            else:
                self._print_csv_files(tmp_files)
            self._delete_tmp_files()

        # limit not implemented
        elif query.startswith("group"):
            table_name, col1_name, calculation, col2_name = MyRDBParser.parse_grouping(query)
            self.grouping(table_name, col1_name, calculation, col2_name)
            
        elif query.startswith("give me"):
            calculation, col_name, table_name = MyRDBParser.parse_aggregation(query)
            self.aggregation(calculation, col_name, table_name)
        
        elif query.startswith("combine"):
            table1_name, table2_name, col_name, limit = MyRDBParser.parse_inner_join(query)
            tmp_files = self.inner_join(table1_name, table2_name, col_name)
            if limit:
                self._print_csv_files(tmp_files, limit)
            else:
                self._print_csv_files(tmp_files)
            self._delete_files(tmp_files)
            for file in glob.glob(f'rdb/*.tmp'):
                os.remove(file)
        
        elif query.startswith("insert"):
            row_value, table_name = MyRDBParser.parse_insert(query)
            self.insert(row_value, table_name)
        
        elif query.startswith("delete"):
            table_name, col_name, value = MyRDBParser.parse_delete(query)
            self.delete(table_name, col_name, value)
        
        elif query.startswith("update"):
            table_name, col_name, new_val, old_val = MyRDBParser.parse_update(query)
            self.update(table_name, col_name, new_val, old_val)
            
        elif query.startswith("create"):
            table_name, col_names = MyRDBParser.parse_create(query)
            self.create(table_name, col_names)
            
        elif query.startswith("load"):
            file_path = MyRDBParser.parse_load(query)
            self.load_large_csv_file(file_path)
        
        else:
            raise ValueError("Unrecognized command")
    
    
    def projection(self, col_names, table_name):
        try:
            tmp_files = []
            files = self._get_all_partition_paths(table_name)
            if files:
                for file in files:
                    df = pd.read_csv(file)  
                    df = df[col_names]  
                    tmp_fn = file.replace('.csv', '.tmp')
                    df.to_csv(tmp_fn, index = False)
                    tmp_files.append(tmp_fn)
            return tmp_files
        except KeyError:
            print(f"Error: Column {col_names} does not exist in table {table_name}.")
            return []
                
                
    def filtering(self, col_name, table_name, value, criteria):
        try:
            tmp_files = []
            files = self._get_all_partition_paths(table_name)
            if files:
                for file in files:
                    df = pd.read_csv(file)
                    # abort if col_name does not exist
                    if not col_name in df.columns: # okay to use df.columns?
                        print(f"Error: Column {col_name} does not exist.")
                        return tmp_files
                    # get filtered results for each csv file
                    if criteria == '=': 
                        if df[col_name].dtype == 'object': 
                            # value is text
                            df = df[df[col_name] == value] 
                        else: 
                            # value is numeric
                            df = df[df[col_name] == self._to_number(value)]
                    elif criteria == '>=': 
                        df = df[df[col_name] >= value]
                    elif criteria == '<=': 
                        df = df[df[col_name] <= value] 
                    # store filtered results in tmp file
                    tmp_fn = file.replace('.csv', '.tmp')
                    if not df.empty:
                        df.to_csv(tmp_fn, index = False)
                        tmp_files.append(tmp_fn)
                # print something if no matching record found
                if not tmp_files:
                    print("No matching record found.")
            return tmp_files        
        except KeyError:
            print(f"Error: Column {col_name} does not exist in table {table_name}.")
            return []


    # note: only support numeric values
    def ordering(self, table_name, col_name, ascending):
        try: 
            files = self._get_all_partition_paths(table_name)
            if files:
                # sort all files individually and store in temporary .tmp files
                sorted_files = self._sort_individual_files(table_name, col_name, ascending)
                # perform external merge sort on sorted .tmp files
                merged_files = self._k_way_merge(sorted_files, table_name, col_name, ascending)
            return merged_files
        except KeyError:
            print(f"Error: Column {col_name} does not exist in table {table_name}.")
            return []
        
        
    def inner_join(self, table1_name, table2_name, col_name):
        try:
            # initialize variables
            current_file = f"rdb/{table1_name}_joined_with_{table2_name}_0.tmp"
            header_written = False
            joined_files = []
            # prepare for writing into current_filex
            with open(current_file, 'w', newline = '') as cf:
                writer = csv.writer(cf)
            # load entire table 1 into memory
            for file1 in self._get_all_partition_paths(table1_name):
                df1 = pd.read_csv(file1)
                # read table 2 line by line
                for file2 in self._get_all_partition_paths(table2_name):
                    with open(file2, 'r') as f2:
                        reader2 = csv.DictReader(f2) # an iterator that processes the file line by line
                        for row in reader2:
                            # check if the value in col_name exists in df1
                            if row[col_name] in df1[col_name].values:
                                # get all rows from df1 that match the current value
                                matching_rows_df1 = df1[df1[col_name] == row[col_name]]
                                # For each matching row, add the information from the second table's current row
                                for _, matching_row in matching_rows_df1.iterrows():
                                    combined_row = {**matching_row.to_dict(), **row}
                                    row_values = list(combined_row.values())
                                    # write the header if not written yet
                                    if not header_written:
                                        with open(current_file, 'w', newline='') as f:
                                            writer = csv.writer(f)
                                            writer.writerow(combined_row.keys())  # Writing the header
                                            header_written = True
                                    # append row
                                    current_file = self._append_row(row_values, current_file)
                                    if current_file not in joined_files:
                                        joined_files.append(current_file)
            return joined_files
        except KeyError:
            print(f"Error: Column {col_name} does not exist in both tables.")
            json_files = glob.glob(f'rdb/*.json')
            return []
    

    # pending: not store aggregation result in json file
    def grouping(self, table_name, col1_name, calculation, col2_name):
        # write aggregation result for each group to one json file
        try:
            files = self._get_all_partition_paths(table_name)
            for file in files:
                df = pd.read_csv(file)
                for _, row in df.iterrows(): 
                    key = row[col1_name]
                    value = row[col2_name]
                    # create key file if not exist
                    key_file = f"rdb/{table_name}/{key}.json"
                    if not os.path.isfile(key_file):
                        with open(key_file, 'w') as f:
                            data = { 'count': 0, 'sum': 0 }
                            json.dump(data, f)
                    # perform aggregation    
                    if calculation == 'sum':
                        # get current sum from key file
                        with open(key_file, 'r') as f:
                            data = json.load(f)
                        with open(key_file, 'w') as f:    
                            data['sum'] += value
                            json.dump(data, f)
                    elif calculation == 'count':
                        with open(key_file, 'r') as f:
                            data = json.load(f)
                        with open(key_file, 'w') as f:  
                            data['count'] += 1
                            json.dump(data, f)
                    elif calculation == 'average':
                        with open(key_file, 'r') as f:
                            data = json.load(f)
                        with open(key_file, 'w') as f:  
                            data['sum'] += value
                            data['count'] += 1
                            json.dump(data, f)
            # print aggregation results
            pattern = f'rdb/{table_name}/*.json'
            key_files = glob.glob(pattern)
            for key_file in key_files:
                key = os.path.splitext(os.path.basename(key_file))[0]
                if calculation == 'sum':
                    # print sum from key file
                    with open(key_file, 'r') as f:
                        data = json.load(f)
                        print(f'{key}: ', data['sum'])
                    # delete json file
                    os.remove(key_file)
                elif calculation == 'count':
                    # print count from key file
                    with open(key_file, 'r') as f:
                        data = json.load(f)
                        print(f'{key}: ', data['count'])
                    # delete json file
                    os.remove(key_file)
                elif calculation == 'average':
                    # calculate average from key file
                    with open(key_file, 'r') as f:
                        data = json.load(f)
                        avg = data['sum'] / data['count']
                        print(f'{key}: ', f"{avg:.2f}")
                    # delete json file
                    os.remove(key_file)
        except KeyError as e:
            print(f"Error: Column {col1_name} or {col2_name} does not exist in table {table_name}.")
        except ValueError:
            print(f"Error: Column {col2_name} contains non-numeric value.")

        
    def aggregation(self, calculation, col_name, table_name):
        try:
            files = self._get_all_partition_paths(table_name)
            if files:
                try:
                    aggregated_value = 0
                    aggregated_count = 0
                    for file in files:
                        df = pd.read_csv(file)
                        # abort if col_name does not exist
                        if not col_name in df.columns: 
                            print(f"Error: Column {col_name} does not exist in table {table_name}.")
                            return
                        # calculate aggregated value
                        if calculation == 'count':
                            aggregated_count += len(df[col_name]) 
                        elif calculation == 'sum':
                            for value in df[col_name]:
                                aggregated_value += value
                        elif calculation == 'average':
                            aggregated_count += len(df[col_name]) 
                            for value in df[col_name]:
                                aggregated_value += value
                    # print aggregated value
                    if calculation == 'sum':
                        print(aggregated_value)
                    elif calculation == 'count':
                        print(aggregated_count)
                    elif calculation == 'average' and aggregated_count == 0:
                        print(0)
                    elif calculation == 'average':
                        avg = aggregated_value / aggregated_count
                        print(f"{avg:.2f}")
                except Exception:
                    print(f"Error: Column {col_name} in table {table_name} contains non-numeric value.")
        except KeyError:
            print(f"Error: Column {col_name} does not exist in table {table_name}.")


    def insert(self, row_values, table_name):
        files = self._get_all_partition_paths(table_name)
        if files:
            # check if record length is valid
            first_file_df = pd.read_csv(files[0])
            if len(row_values) != len(first_file_df.columns): 
                print("Error: Invalid record length.")
            else:
                # find the "last" csv file
                current_file = files[-1]
                current_file = self._append_row(row_values, current_file)
                print("Insert operation completed successfully.")
            
            
    # note: does not delete file if no more rows left
    def delete(self, table_name, col_name, value):
        files = self._get_all_partition_paths(table_name)
        if files:
            found = False
            for file in files:
                df = pd.read_csv(file)
                # abort if col_name does not exist
                if not col_name in df.columns:
                    print(f"Error: Column {col_name} does not exist in table {table_name}.")
                    return
                # delete matching record(s)
                if value in df[col_name].values:
                    found = True
                    df = df[df[col_name] != value]
                    df.to_csv(file, index = False)
            if found:
                print("Delete operation completed successfully.")
            else:
                print("No matching record found.")


    def update(self, table_name, col_name, new_value, old_value):
        found = False
        files = self._get_all_partition_paths(table_name)
        if not files:
            print(f"No files found for table {table_name}.")
            return
        for file in files:
            updated_rows = []
            with open(file, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                if col_name not in reader.fieldnames:
                    print(f"Error: Column {col_name} does not exist in table {table_name}.")
                    return
                for row in reader:
                    if row[col_name] == old_value:
                        row[col_name] = new_value
                        found = True
                    updated_rows.append(row)
            # write the updated data back to the file
            with open(file, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames = reader.fieldnames)
                writer.writeheader()
                writer.writerows(updated_rows)
        if found:
            print("Update operation completed successfully.")
        else:
            print("No matching record found.")


    def create(self, table_name, col_names):
        folder_name = fn = f'rdb/{table_name}'
        if os.path.isdir(folder_name):
            print(f"Error: Table '{table_name}' already exists.")
        else:
            os.mkdir(folder_name)
            fn = f'rdb/{table_name}/{table_name}_0.csv'
            with open(fn, 'w', newline = '') as file:
                writer = csv.writer(file)
                writer.writerow(col_names)
            print(f"Table {table_name} created.")
            
    
    # split a large csv file into smaller chunks
    def load_large_csv_file(self, file_path):
        table_name = os.path.splitext(os.path.basename(file_path))[0]
        output_directory = f'rdb/{table_name}'  
        if os.path.exists(output_directory):
            # clear all files in output directory
            pattern = f'rdb/{table_name}/{table_name}_*.csv'
            files = glob.glob(pattern)
            for f in files:
                os.remove(f)
        else:
            # create output directory
            os.makedirs(output_directory)
        with open(file_path, 'r') as csv_file:
            reader = csv.reader(csv_file)
            header = next(reader)  
            current_file_index = 0
            current_file_size = 0
            current_file_name = os.path.join(output_directory, f'{table_name}_{current_file_index}.csv')
            output_file = open(current_file_name, 'w', newline = '')
            writer = csv.writer(output_file)
            writer.writerow(header) 
            for record in reader:
                record_size = len(','.join(record)) + len(os.linesep)
                # create a new file if adding this record would exceed the max file size
                if current_file_size + record_size > self.max_file_size:
                    output_file.close() 
                    current_file_index += 1
                    current_file_name = os.path.join(output_directory, f'{table_name}_{current_file_index}.csv')
                    output_file = open(current_file_name, 'w', newline = '')
                    writer = csv.writer(output_file)
                    writer.writerow(header)  
                    current_file_size = 0
                # write the record to the new file
                writer.writerow(record)
                current_file_size += record_size