import csv
import pandas as pd
import sys
import os
import glob
import json
import heapq

from my_ql_parser import MyQLParser

class RelationalDB:
    def __init__(self):
        self.memory_limit = 512 # bytes
        
    # note: sorted by file name
    def _get_all_partition_paths(self, table_name):
        pattern = f'rdb/{table_name}/{table_name}_*.csv'
        files = glob.glob(pattern)
        if not files:
            print(f'Error: Table {table_name} does not exist.')
        files.sort()
        return files
    
    # note: truncate if data string is too long 
    def _print_df(self, df, is_first_file):
        header = True if is_first_file else False
        max_width = 25
        df.isnull().any(axis = 0)
        formatters = {column: lambda x: f'{str(x)[:max_width]:<{max_width}}' for column in df.columns}
        print(df.to_string(index = False, header = header, justify='left', formatters = formatters, na_rep=''))
        
    # TODO: limit
    def _print_csv_files(self, files):
        is_first_file = True
        if files:
            for file in files:
                df = pd.read_csv(file)
                self._print_df(df, is_first_file)
                is_first_file = False
            
    def _delete_files(self, files):
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
    
    def _write_dict_to_file(self, data_dict, file_path):
        with open(file_path, 'w') as file:
            json.dump(data_dict, file)

    def _read_dict_from_file(self, file_path):
        with open(file_path, 'r') as file:
            return json.load(file)

    def _aggregate_data(self, df, col1_name, calculation, col2_name):
        aggregation_dict = {}
        for _, row in df.iterrows():
            key = row[col1_name]
            value = row[col2_name]
            if calculation == 'sum':
                aggregation_dict[key] = aggregation_dict.get(key, 0) + value
            elif calculation == 'average':
                if key in aggregation_dict:
                    sum_, count_ = aggregation_dict[key]
                    aggregation_dict[key] = (sum_ + value, count_ + 1)
                else:
                    aggregation_dict[key] = (value, 1)
        return aggregation_dict
    
    def _bubble_sort(self, data_list, col_name, ascending):
        n = len(data_list)
        for i in range(n):
            for j in range(0, n-i-1):
                if (data_list[j][col_name] > data_list[j+1][col_name] and ascending) or \
                   (data_list[j][col_name] < data_list[j+1][col_name] and not ascending):
                    data_list[j], data_list[j+1] = data_list[j+1], data_list[j]
    
    def _sort_individual_files(self, table_name, col_name, ascending):
        pattern = f'rdb/{table_name}/{table_name}_*.csv'
        files = glob.glob(pattern)
        sorted_files = []
        for file in files:
            df = pd.read_csv(file)
            data_list = df.to_dict('records')
            # sort the list using bubble sort
            self._bubble_sort(data_list, col_name, ascending)
            # convert the sorted list of dictionaries back to a DataFrame
            df_sorted = pd.DataFrame(data_list)
            # saving the sorted DataFrame with a .tmp extension
            tmp_file_path = file.replace('.csv', '.tmp')
            df_sorted.to_csv(tmp_file_path, index = False)
            sorted_files.append(tmp_file_path)
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

    # note: only support numeric values
    # TODO: what if cannot read all sorted files at once
    def _k_way_merge(self, sorted_files, table_name, col_name, ascending):
        # initialize pq, file pointers, csv readers
        pq = []
        unique_id_counter = 0
        file_pointers = [open(file, 'r') for file in sorted_files]
        csv_readers = [csv.DictReader(fp) for fp in file_pointers]
        
        # populate pq with the first row from each file
        for reader in csv_readers:
            self._insert_into_pq(pq, reader, unique_id_counter, col_name, ascending)
            unique_id_counter += 1  
        
       # write to merged file
        merged_file = f'rdb/{table_name}/{table_name}_merged.tmp'
        with open(merged_file, 'w', newline='') as f_out:
            writer = None
            while pq:
                # pop smallest row from the heap
                _, row, reader = heapq.heappop(pq)
                # write the row to the output file
                if writer is None:
                    writer = csv.DictWriter(f_out, fieldnames = row.keys())
                    writer.writeheader()
                writer.writerow(row)
                self._insert_into_pq(pq, reader, unique_id_counter, col_name, ascending)
                unique_id_counter += 1  
                
        # close file pointers and delete tmp files
        for fp in file_pointers:
            fp.close()
        self._delete_files(sorted_files)
        # print and return the merged file
        df = pd.read_csv(f'rdb/{table_name}/{table_name}_merged.tmp')
        self._print_df(df, True)
        return merged_file

    
    def query(self, args):
        if args:
            if args[0] == "\"" and args[-1] == "\"":
                args = args[1:-1]
            self.parse_query(args) 
        else:
            print("No query provided")
        
        
    def parse_query(self, query):
        if query.startswith("get"):
            col_names, table_name = MyQLParser.parse_projection(query)
            tmp_files = self.projection(col_names, table_name)
            self._print_csv_files(tmp_files)
            self._delete_files(tmp_files)
            
        elif query.startswith("find"):
            col_name, table_name, value, criteria = MyQLParser.parse_filtering(query)
            tmp_files = self.filtering(col_name, table_name, value, criteria)
            self._print_csv_files(tmp_files)
            self._delete_files(tmp_files)
            
        # TODO
        elif query.startswith("order"):
            table_name, col_name, ascending = MyQLParser.parse_ordering(query)
            self.ordering(table_name, col_name, ascending)

        # TODO
        elif query.startswith("group"):
            table_name, col1_name, calculation, col2_name = MyQLParser.parse_grouping(query)
            self.grouping(table_name, col1_name, calculation, col2_name)
            
        elif query.startswith("calculate"):
            calculation, col_name, table_name = MyQLParser.parse_aggregation(query)
            self.aggregation(calculation, col_name, table_name)
        
        elif query.startswith("combine"):
            table1_name, table2_name, col_name = MyQLParser.parse_inner_join(query)
            self.inner_join(table1_name, table2_name, col_name)
        
        elif query.startswith("insert"):
            row_value, table_name = MyQLParser.parse_insert(query)
            self.insert(row_value, table_name)
        
        elif query.startswith("delete"):
            table_name, col_name, value = MyQLParser.parse_delete(query)
            self.delete(table_name, col_name, value)
        
        elif query.startswith("update"):
            table_name, col_name, new_val, old_val = MyQLParser.parse_update(query)
            self.update(table_name, col_name, new_val, old_val)
            
        elif query.startswith("create"):
            table_name, col_names = MyQLParser.parse_create(query)
            self.create(table_name, col_names)
        
        else:
            raise ValueError("Unrecognized command")
    
    
    # completed
    def projection(self, col_names, table_name):
        tmp_files = []
        files = self._get_all_partition_paths(table_name)
        if files:
            for file in files:
                df = pd.read_csv(file, usecols = col_names) # okay to use usecols?
                # save result to tmp file
                tmp_fn = file.replace('.csv', '.tmp')
                df.to_csv(tmp_fn, index = False)
                tmp_files.append(tmp_fn)
        return tmp_files
                
                
    # MAYBE: handle null value
    # completed
    def filtering(self, col_name, table_name, value, criteria):
        tmp_files = []
        files = self._get_all_partition_paths(table_name)
        if files:
            for file in files:
                df = pd.read_csv(file)
                # abort if col_name does not exist
                if not col_name in df.columns:
                    print(f"Error: Column {col_name} does not exist.")
                    return tmp_files
                # get filtered results for each csv file
                if criteria == '=': 
                    if df[col_name].dtype == 'object': # value is text
                        df = df[df[col_name] == value]
                    else: # value is numeric
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


    # TODO
    # MAYBE: handle null value
    def ordering(self, table_name, col_name, ascending):
        files = self._get_all_partition_paths(table_name)
        if files:
            # sort all files individually and store in temporary .tmp files
            sorted_files = self._sort_individual_files(table_name, col_name, ascending)
            # perform external merge sort on sorted .tmp files
            merged_files = self._k_way_merge(sorted_files, table_name, col_name, ascending)
        
        
    # TODO
    # MAYBE: handle null value
    def inner_join(self, table1_name, table2_name, col_name):
        # fn = f'rdb/{table_name}_{n}.csv'
        # not sure how to implement
        pass 
    
    
    # TODO
    # MAYBE: handle null value
    def grouping(self, table_name, col1_name, calculation, col2_name):
        files = self._get_all_partition_paths(table_name)
        aggregation_results = {}
        for file in files:
            df = pd.read_csv(file)
            for _, row in df.iterrows():
                key = row[col1_name]
                value = row[col2_name]
                
                # Check memory usage and write to temp file if needed
                if sys.getsizeof(aggregation_results) > self.memory_limit:
                    temp_file_name = f"temp_aggregation_{temp_file_index}.json"
                    with open(temp_file_name, 'w') as temp_file:
                        json.dump(aggregation_results, temp_file)
                    aggregation_results.clear()
                    temp_file_index += 1
                    
                if calculation == 'sum':
                    aggregation_results[key] = aggregation_results.get(key, 0) + value
                elif calculation == 'count':
                    aggregation_results[key] = aggregation_results.get(key, 0) + 1
                elif calculation == 'average':
                    # For average, store a tuple of (sum, count)
                    sum_, count_ = aggregation_results.get(key, (0, 0))
                    aggregation_results[key] = (sum_ + value, count_ + 1)
        
                # check if the dictionary size exceeds memory size
                # if so, write to a temporary file and clear the dictionary
                # This part is not implemented here, but you would need to add this check

        # Print or return the aggregation results
        for key, value in aggregation_results.items():
            if calculation == 'average':
                # Compute the average
                sum_, count_ = value
                value = sum_ / count_ if count_ else 'Undefined'
            print(f"{key}: {value}")

        
    # MAYBE: max, min
    # MAYBE: handle null value
    # completed
    def aggregation(self, calculation, col_name, table_name):
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
                        aggregated_count += len(df[col_name]) # okay to use len?
                    elif calculation == 'sum':
                        for value in df[col_name]:
                            aggregated_value += value
                    elif calculation == 'average':
                        aggregated_count += len(df[col_name]) # okay to use len?
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


    # completed
    def insert(self, row_values, table_name):
        files = self._get_all_partition_paths(table_name)
        if files:
            # check if record length is valid
            first_file_df = pd.read_csv(files[0])
            if len(row_values) != len(first_file_df.columns):
                print("Error: Invalid record length.")
            else:
                # find the "last" csv file
                max_index = max([int(file.split('_')[-1].split('.csv')[0]) for file in files])
                last_file = files[-1]
                df = pd.read_csv(last_file)
                # check if it's ok to add a new record to this file
                row_string = ','.join(str(value) for value in row_values)
                total_bytes = os.path.getsize(last_file) + len(row_string.encode('utf-8'))
                if total_bytes < self.memory_limit:
                    # write update to existing file
                    df.loc[len(df)] = row_values
                    df.to_csv(last_file, index = False)
                else:
                    # create a new csv file
                    max_index += 1
                    new_file = f'rdb/{table_name}/{table_name}_{max_index}.csv'
                    # set column names
                    new_df = pd.DataFrame(columns = first_file_df.columns)
                    # insert row
                    new_df.loc[0] = row_values
                    new_df.to_csv(new_file, index = False)
                print("Insert operation completed successfully.")
            
            
    # completed
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
                
    
    # TODO: support delete (drop) entire table?
    
    
    # completed
    def update(self, table_name, col_name, new_value, old_value):
        files = self._get_all_partition_paths(table_name)
        if files:
            found = False
            for file in files:
                df = pd.read_csv(file)
                # abort if col_name does not exist
                if not col_name in df.columns:
                    print(f"Error: Column {col_name} does not exist in table {table_name}.")
                    return
                # update matching record(s)
                if old_value in df[col_name].values:
                    found = True
                    df[col_name] = df[col_name].replace(old_value, new_value) # okay to use replace?
                    df.to_csv(file, index = False)
            if found:
                print("Update operation completed successfully.")
            else:
                print("No matching record found.")


    # completed
    def create(self, table_name, col_names):
        folder_name = fn = f'rdb/{table_name}'
        if os.path.isdir(folder_name):
            print(f"Error: Table '{table_name}' already exists.")
        else:
            os.mkdir(folder_name)
            fn = f'rdb/{table_name}/{table_name}_0.csv'
            with open(fn, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(col_names)
            print(f"Table {table_name} created.")
            
    
    # TODO: add to db parser
    # split a csv file into chunks within memory limit
    def load_large_csv_file(self, file_path):
        table_name = os.path.splitext(os.path.basename(file_path))[0]
        output_directory = f'rdb/{table_name}'  
        if os.path.exists(output_directory):
            # clear everything within this directory
            for file in os.listdir(output_directory):
                os.remove(file)
        else:
            # create output directory
            os.makedirs(output_directory)
        # create chunks
        with open(file_path, 'r') as csv_file:
            reader = csv.reader(csv_file)
            header = next(reader)  
            current_file_index = 0
            current_file_size = 0
            current_file_name = os.path.join(output_directory, f'{table_name}_{current_file_index}.csv')
            output_file = open(current_file_name, 'w', newline = '')
            writer = csv.writer(output_file)
            writer.writerow(header) 
            for row in reader:
                row_size = len(','.join(row)) + len(os.linesep)
                # create a new file if adding this row would exceed the max file size
                if current_file_size + row_size > self.memory_limit:
                    output_file.close() 
                    current_file_index += 1
                    current_file_name = os.path.join(output_directory, f'{table_name}_{current_file_index}.csv')
                    output_file = open(current_file_name, 'w', newline = '')
                    writer = csv.writer(output_file)
                    writer.writerow(header)  
                    current_file_size = 0
                # write the row to the new file
                writer.writerow(row)
                current_file_size += row_size