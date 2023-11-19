### key requirements ###
- You should assume you have a limited memory to perform operations. If your datasize is 5MB and your memory assumption is 1MB, then your dataset should be divided into 5 different chunks and then perform operations
- Best approach for this project is to store data as chunks rather than reading as chunks using builtin methods like read_csv(n_chunks = ...). So that you have control over data processing as chunks. You can also store intermediate results on disk and construct final results from intermediate results again by reading them from the disk
- Design a query language like human conversations with some keywords and map them to process the query using programming languages
- You cannot use any of the existing databases like firebase, sql, etc to store data


### assumptions ###   
- queries are case sensitive
- memory size > reading one line from each chunk file


### next steps ###
- ppt
- memory usage (especially k-way merge) & legal use of panda/csv module
- (support calling multiple operations in one query)
- (query "update netflix_originals set Title = Bright Forces where Title = Dark Forces") 
- (allow for matching diff row names in join)


### query language for relational db (outdated) ###
- Projection: "get [col1_name, col2_name, col3_name, ...] from [table_name]"
- Filtering: "find [table_name] that have a [col_name] of at [least / most] [numeric_value]", "find [table_name] that [col_name] is [value]"
- Ordering: "order [table_name] by [col_name] in [descending / ascending] order"
- Aggregation: "calculate the [sum / average] of [col_name] for [table_name]"
- Grouping: "group [table_name] by [col1_name] and calculate the [sum / average] of [col2_name]"
  - only support grouping with aggregation
- Inner Join: "combine rows from [table1_name] and [table2_name] where their [col_name] values match"   
    

### data modification operations for relatioal db (outdated)###
- insert [row_value] into [table_name]
- delete from [table_name] where [col_name] = [value]
- update [table_name] set [col_name] = [new_value] where [col_name] = [old_value]
- create table [table_name] ([col1_name]:[col1_type], [col2_name]:[col2_type], [col3_name]:[col3_type])