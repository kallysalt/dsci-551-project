if your datasize is 5MB and your memory assumption is 1MB， your dataset should be divided into 5 different chunks and then perform operations
- our memory assumption: ?  


query language for relational db:
- Projection: "get [col1, col2, col3, ...] from [table]"
- Filtering: "find [table] that have a [col] of at [least / most] [numeric value]", "find [table] that [col] is [value]"
- Ordering: "order [table] by [col] in [descending / ascending] order"
- Aggregation: calculate the [sum / average] of [col] for [table]
- Grouping: "group [table] by [col]"
  - only support grouping with aggregation?
  - e.g. query "calculate the [sum / average] of [col] for [table]" "group by [col]
- Inner Join: "combine rows from [table1] and [table2] where their [col] values match"  


example queries:
- query "get type, title from netflix23"
- query "find netflix23 that have a release_year of at most 2020"
- query "find netflix23 that have a release_year of at least 2020"
- query "find netflix23 that release_year is 2020"
- query "order netflix23 by release_year in descending order"
- query "order netflix23 by release_year in ascending order"
- ...  
