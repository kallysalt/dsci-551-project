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
- query "get type, title from tests"
- query "find tests that have a release_year of at most 2020" 
- query "find tests that have a release_year of at least 2020"
- query "find tests that release_year is 2020"
- query "find tests that director is Kirsten Johnson" 
- query "order tests by release_year in descending order" 
- query "order tests by release_year in ascending order"  
- query "find tests that col_not_exist is 2020"
- ...  
- query "calculate the sum of release_year for tests"
- query "calculate the average of release_year for tests" 
- query "group tests by show_id and calculate the sum of test_aggr"
- query "group machine_learning_youtube_videos by Channel and calculate the sum of Likes"
- query "group machine_learning_youtube_videos by Channel and calculate the average of Likes"
- query "combine rows from tests_left and tests_right_partial where their show_id values match"
- query "combine rows from tests_left and machine_learning_youtube_videos where their show_id values match" 
- query "combine rows from tests_left and tests_right_partial where their hhh values match"
- query "insert s16, TV Show, Dear White People, , 2021, TV-MA, 4 Seasons into tests"
- query "delete from tests where title = Falsa identidad"
- query "update tests set title = Bangkok where title = Bangkok Breaking"
- query "create table demo (col1_name, col2_name)"


### next steps ###
- support inner join (need to prep csv files first)
- support calling multiple queries in one line
- add limit
- link
- update query language