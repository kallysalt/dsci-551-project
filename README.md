### 1 File Structure

#### 1.1 General

```
cli.py
```

`cli.py` is the entry point for command line interaction, responsible for handling user interactions and command line input/output.



#### 1.2 JSON DB

```
/
│
├── myNoSQL/
│   ├── data/
│   │  
│   ├── MyNoSQL.py
│   └── MyJSONQLParser.py
│
├── cards.json
└── rulings.json
```

`cards.json` and `rulings.json` are two real world datasets.

`myNoSQL/data` is a database file directory, including temporary files and stored chunks data.

`myNoSQL/MyNoSQL.py` is the main DB file, responsible for handling internal database operations.

`myNoSQL/MyJSONQLParser.py` is responsible for parsing Query statements.



#### 1.3 Relation DB





### 2 Commands ###

Below are terminal commands to run our DB.

#### 2.1 General

##### Start the DB client

`python3 cli.py`

##### Choose DB

`json` or `relational`

##### Switch DB

`switch`

##### Exit

`exit` or press `Ctrl + C`



#### 2.2 JSON DB

##### Load Data

```
load cards.json into cards
load rulings.json into rulings
```

##### Get

```
Get cards.
```

##### Get, Project

```
Get cards; project id, name.
```

##### Get, Filter, Project

```
Get cards; filter games has paper and set = atq and colors has B and cmc = 3; project id, name.
```

##### Get, Filter, Join, Project

```
Get cards; filter games has paper and set = atq and colors has B and cmc = 3; join rulings by oracle_id; project id, name, comment.
```

##### Get, Group, Aggregate, Sort, Limit

```
Get cards; group set aggregate prices.usd avg; sort by avg descending; limit 3.
```

##### Add

```
Add to cards {"object": "card", "id": "d778cdec-8fc7-4174-bae1-4c8e8ccdfab3", "oracle_id": "d4cde3d5-eb13-4ad5-8178-08780dc85d39", "name": "Radstorm", "lang": "en", "released_at": "2024-03-08", "set": "pip", "set_name": "Fallout"}
```

##### Update

```
Update cards where id = d778cdec-8fc7-4174-bae1-4c8e8ccdfab3 set {"name": "NEW_NAME"}
```

##### **Get, Filter**

```
Get cards; filter id = d778cdec-8fc7-4174-bae1-4c8e8ccdfab3
```

##### Delete

```
Delete cards where id = d778cdec-8fc7-4174-bae1-4c8e8ccdfab3
```

##### **Get, Filter**

```
Get cards; filter id = d778cdec-8fc7-4174-bae1-4c8e8ccdfab3
```



#### 2.3 Relation DB

##### Load Data

```
load rdb/netflix_originals.csv
```

##### Insert

```
insert Fire in Paradise, Documentary, 39, 7.4, English into netflix_originals
```

##### Delete

```
delete from netflix_originals where Title = Fire in Paradise
```

##### Update

```
update netflix_originals set Title = Bright Forces where Title = Dark Forces 
```

##### Create

```
create table demo (col1_name, col2_name)
```

##### Projection

```
get Title, Genre, IMDB_Score from netflix_originals (default: limit = 15)
get Title, Genre, IMDB_Score from netflix_originals, limit 3
get Age from netflix_originals (error handling)
```

##### Filtering

```
find netflix_originals that have a IMDB_Score of at most 3 (default: limit = 15)
find netflix_originals that have a IMDB_Score of at most 5, limit 3 
find netflix_originals that have a IMDB_Score of at least 6
find netflix_originals that have a IMDB_Score of at least 6, limit 3
find netflix_originals that Language is Japanese
find netflix_originals that Language is Japanese, limit 3
find netflix_originals that Runtime is 120 
find netflix_originals that Runtime is 120, limit 3
find netflix_originals that Genre is Korean (error handling)
```

##### Ordering

```
order netflix_originals by IMDB_Score in descending order (default: limit = 15)
order netflix_originals by IMDB_Score in descending order, limit 100 
order netflix_originals by IMDB_Score in ascending order  
order netflix_originals by IMDB_Score in ascending order, limit 100  
order netflix_originals by Age in ascending order  (error handling)
```

##### Aggregation

```
give me the sum of Runtime for netflix_originals
give me the average of Runtime for netflix_originals 
give me the count of Title for netflix_originals
give me the sum of Genre for netflix_originals (error handling)
```

##### Grouping

```
group netflix_originals by Language and give me the sum of Runtime
group netflix_originals by Language and give me the average of IMDB_Score
group netflix_originals by Language and give me the count of Title
```

##### Joining (inner join)

```
combine rows from netflix_originals and netflix_videos where their Title values match (default: limit = 15)
combine rows from netflix_originals and netflix_videos where their Title values match, limit 5
combine rows from netflix_originals and netflix_videos where their Age values match (error handling)
```

