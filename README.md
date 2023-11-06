key requirements
- You should assume you have a limited memory to perform operations. If your datasize is 5MB and your memory assumption is 1MB, then your dataset should be divided into 5 different chunks and then perform operations
- Best approach for this project is to store data as chunks rather than reading as chunks using builtin methods like read_csv(n_chunks = ...). So that you have control over data processing as chunks. You can also store intermediate results on disk and construct final results from intermediate results again by reading them from the disk
- Design a query language like human conversations with some keywords and map them to process the query using programming languages
- You cannot use any of the existing databases like firebase, sql, etc to store data


memory assumption: 1MB 

query language for relational db:
- Projection: "get [col1, col2, col3, ...] from [table]"
- Filtering: "find [table] that have a [col] of at [least / most] [numeric value]", "find [table] that [col] is [value]"
- Ordering: "order [table] by [col] in [descending / ascending] order"
- Aggregation: calculate the [sum / average] of [col] for [table]
- Grouping: "group [table] by [col]"
  - only support grouping with aggregation?
  - e.g. query "calculate the [sum / average] of [col] for [table]" "group by [col]
- Inner Join: "combine rows from [table1] and [table2] where their [col] values match"   


data modification operations for relatioal db:
- INSERT [row value] INTO [table name]
- DELETE FROM [table name] WHERE [column name] = [value]
- UPDATE [table name] SET [column name] = [new value] WHERE [column name] = [old value]   


example queries:
- query "get type, title from netflix23"
- query "find netflix23 that have a release_year of at most 2020"
- query "find netflix23 that have a release_year of at least 2020"
- query "find netflix23 that release_year is 2020"
- query "order netflix23 by release_year in descending order"
- query "order netflix23 by release_year in ascending order"
- ...  
