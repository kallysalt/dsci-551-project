#### Insert

```
query "insert Fire in Paradise, Documentary, 39, 7.4, English into netflix_originals" # keep insert until new chunks get created
```

#### Delete

```
query "delete from netflix_originals where Title = Fire in Paradise"
```

#### Update

```
query "update netflix_originals set Title = Bright Forces where Title = Dark Forces" 
```

#### Create

```
query "create table demo (col1_name, col2_name)"
```

#### Load Data

```
query "load rdb/netflix_originals.csv"
```

#### Projection

```
query "get Title, Genre, IMDB Score from netflix_originals" (default: limit = 15)
query "get Title, Genre, IMDB Score from netflix_originals, limit 3"
query "get Age from netflix_originals" (error handling)
```

#### Filtering

```
query "find netflix_originals that have a IMDB_Score of at most 3" (default: limit = 15)
query "find netflix_originals that have a IMDB_Score of at most 5, limit 3" 
query "find netflix_originals that have a IMDB_Score of at least 6"
query "find netflix_originals that have a IMDB_Score of at least 6, limit 3"
query "find netflix_originals that Language is Japanese"
query "find netflix_originals that Language is Japanese, limit 3"
query "find netflix_originals that Genre is Korean" (error handling)
query "find netflix_originals that Runtime is 120" 
query "find netflix_originals that Runtime is 120, limit 3"
```

#### Ordering

```
query "order netflix_originals by IMDB_Score in descending order" (default: limit = 15)
query "order netflix_originals by IMDB_Score in descending order, limit 100" 
query "order netflix_originals by IMDB_Score in ascending order"  
query "order netflix_originals by IMDB_Score in ascending order, limit 100"  
query "order netflix_originals by Age in ascending order"  (error handling)
```

#### Aggregation

```
query "give me the sum of Runtime for netflix_originals"
query "give me the average of Runtime for netflix_originals" 
query "give me the count of Title for netflix_originals"
query "give me the sum of Genre for netflix_originals" (error handling)
```

#### Grouping

```
query "group netflix_originals by Language and give me the sum of Runtime"
query "group netflix_originals by Language and give me the average of IMDB_Score"
query "group netflix_originals by Language and give me the count of Title"
```

#### Joining (inner join)

```
query "combine rows from netflix_originals and netflix_videos where their Title values match" (default: limit = 15)
query "combine rows from netflix_originals and netflix_videos where their Title values match, limit 5"
query "combine rows from netflix_originals and netflix_videos where their Age values match" (error handling)
```