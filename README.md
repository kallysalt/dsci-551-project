### key requirements ###
- You should assume you have a limited memory to perform operations. If your datasize is 5MB and your memory assumption is 1MB, then your dataset should be divided into 5 different chunks and then perform operations
- Best approach for this project is to store data as chunks rather than reading as chunks using builtin methods like read_csv(n_chunks = ...). So that you have control over data processing as chunks. You can also store intermediate results on disk and construct final results from intermediate results again by reading them from the disk
- Design a query language like human conversations with some keywords and map them to process the query using programming languages
- You cannot use any of the existing databases like firebase, sql, etc to store data

   
### assumptions ###   
- memory = 1KB (for now)
- queries are case insensitive (including col_name)


### query language for relational db ###
- Projection: "get [col1_name, col2_name, col3_name, ...] from [table_name]"
- Filtering: "find [table_name] that have a [col_name] of at [least / most] [numeric_value]", "find [table_name] that [col_name] is [value]"
- Ordering: "order [table_name] by [col_name] in [descending / ascending] order"
- Aggregation: "calculate the [sum / average] of [col_name] for [table_name]"
- Grouping: "group [table_name] by [col1_name] and calculate the [sum / average] of [col2_name]"
  - only support grouping with aggregation
- Inner Join: "combine rows from [table1_name] and [table2_name] where their [col_name] values match"   
    

### data modification operations for relatioal db (case insensitive) ###
- insert [row_value] into [table_name]
- delete from [table_name] where [col_name] = [value]
- update [table_name] set [col_name] = [new_value] where [col_name] = [old_value]
- create table [table_name] ([col1_name]:[col1_type], [col2_name]:[col2_type], [col3_name]:[col3_type])
   

### example queries ###
- query "get type, title from test"
- query "get show_id,type,title,director,release_year,rating,duration from test"
- query "find test that have a release_year of at most 2020" 
- query "find test that have a release_year of at least 2020"
- query "find test that release_year is 2020"
- query "order test by release_year in descending order"
- query "order test by release_year in ascending order"
- query "find test that col_not_exist is 2020"
- ...  
- query "calculate the sum of release_year for test"
- query "calculate the average of release_year for test" 
- query "group yt by Channel and calculate the sum of Likes"
- query "group yt by Channel and calculate the average of Likes"
- query "combine rows from table1_name and table2_name where their col_name values match"   
- query "insert s23, Movie,Avvai Shanmughi, K.S. Ravikumar, 1996, TV-PG, 161 min into test"
- query "delete from test where title = Falsa identidad"
- query "update test set title = Dear Yellow People where title = Dear White People"
- query "create table table_name (col1_name, col2_name)"


### next steps ###
- support inner join (need to prep csv files first)
- what happens if there exists null values (e.g. in calculations)
- store chunk files in folders
- use generator & support calling multiple queries in one line
- support type check?
- support insert new column?