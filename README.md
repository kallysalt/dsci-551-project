### key requirements ###
- You should assume you have a limited memory to perform operations. If your datasize is 5MB and your memory assumption is 1MB, then your dataset should be divided into 5 different chunks and then perform operations
- Best approach for this project is to store data as chunks rather than reading as chunks using builtin methods like read_csv(n_chunks = ...). So that you have control over data processing as chunks. You can also store intermediate results on disk and construct final results from intermediate results again by reading them from the disk
- Design a query language like human conversations with some keywords and map them to process the query using programming languages
- You cannot use any of the existing databases like firebase, sql, etc to store data

   
### memory assumption ###   
1KB (for now)


### query language for relational db ###
- Projection: "get [col1_name, col2_name, col3_name, ...] from [table_name]"
- Filtering: "find [table_name] that have a [col] of at [least / most] [numeric_value]", "find [table] that [col] is [value]"
- Ordering: "order [table_name] by [col] in [descending / ascending] order"
- Aggregation: calculate the [sum / average] of [col] for [table_name]
- Grouping: "group [table_name] by [col1_name] and calculate the [sum / average] of [col2_name]"
  - only support grouping with aggregation
- Inner Join: "combine rows from [table1_name] and [table2_name] where their [col] values match"   
    

### data modification operations for relatioal db (case insensitive) ###
- insert [row_value] into [table_name]
- delete from [table_name] where [col_name] = [value]
- update [table_name] set [col_name] = [new_value] where [col_name] = [old_value]
   

### example queries ###
- query "get type, title from netflix23"
- query "find netflix23 that have a release_year of at most 2020"
- query "find netflix23 that have a release_year of at least 2020"
- query "find netflix23 that release_year is 2020"
- query "order netflix23 by release_year in descending order"
- query "order netflix23 by release_year in ascending order"
- ...  
