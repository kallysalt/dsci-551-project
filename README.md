### key requirements ###
- You should assume you have a limited memory to perform operations. If your datasize is 5MB and your memory assumption is 1MB, then your dataset should be divided into 5 different chunks and then perform operations
- Best approach for this project is to store data as chunks rather than reading as chunks using builtin methods like read_csv(n_chunks = ...). So that you have control over data processing as chunks. You can also store intermediate results on disk and construct final results from intermediate results again by reading them from the disk
- Design a query language like human conversations with some keywords and map them to process the query using programming languages
- You cannot use any of the existing databases like firebase, sql, etc to store data

   
### assumptions ###   
- queries are case sensitive (including col_name)
- memory size > reading one line from each chunk file
- encoded in utf-8 (unicode)


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
   
### demo queries ###
- data manipulation:
- query "insert Fire in Paradise, Documentary, 39, 7.4, English into netflix_originals" # keep insert until new chunks get created
- query "delete from netflix_originals where Title = Fire in Paradise"
- query "update netflix_originals set Title = Bright Forces where Title = Dark Forces" 
- query "create table demo (col1_name, col2_name)"
- data retrieval:
- query "load rdb/netflix_originals.csv"
- projection:
- query "get Title, Genre, IMDB Score from netflix_originals" # default: limit = 15
- query "get Title, Genre, IMDB Score from netflix_originals, limit 3"
- query "get Age from netflix_originals" # error handling
- filtering:
- query "find netflix_originals that have a IMDB_Score of at most 3" 
- query "find netflix_originals that have a IMDB_Score of at most 5, limit 3" 
- query "find netflix_originals that have a IMDB_Score of at least 6"
- query "find netflix_originals that have a IMDB_Score of at least 6, limit 3"
- query "find netflix_originals that Language is Japanese"
- query "find netflix_originals that Genre is Korean" # error handling
- query "find netflix_originals that Runtime is 120" 
- query "find netflix_originals that Runtime is 120, limit 3" # FIX
- ordering:
- query "order netflix_originals by IMDB_Score in descending order" 
- query "order netflix_originals by IMDB_Score in descending order, limit 100" 
- query "order netflix_originals by IMDB_Score in ascending order"  
- query "order netflix_originals by IMDB_Score in ascending order, limit 100"  
- query "order netflix_originals by Age in ascending order"  # error handling
- aggregation:
- query "give me the sum of Runtime for netflix_originals"
- query "give me the average of Runtime for netflix_originals" 
- query "give me the count of Title for netflix_originals" # ?
- query "give me the sum of Genre for netflix_originals" # error handling
- grouping:
- query "group netflix_originals by Language and give me the sum of Runtime"
- query "group netflix_originals by Language and give me the average of IMDB_Score"
- query "group netflix_originals by Language and give me the count of Title" # ?
- joining (inner join): # TODO: allow for matching of diff row names
- query "combine rows from netflix_originals and netflix_videos where their Title values match"
- query "combine rows from netflix_originals and netflix_videos where their Title values match, limit 5"
- query "combine rows from netflix_originals and netflix_videos where their Age values match" # error handling


### next steps ###
- support calling multiple operations in one query
- query "update netflix_originals set Title = Bright Forces where Title = Dark Forces" 