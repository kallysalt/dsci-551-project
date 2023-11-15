#### Load Data:

```
load cards.json into cards
load rulings.json into rulings
```

#### Get

```
Get cards.
```

#### Get, Project

```
Get cards; project id, name.
```

####Get, Filter, Project

```
Get cards; filter games has paper and set = atq and colors has B and cmc = 3; project id, name.
```

#### Get, Filter, Join, Project

```
Get cards; filter games has paper and set = atq and colors has B and cmc = 3; join rulings by oracle_id; project id, name, comment.
```

#### Get, Group, Aggregate, Sort, Limit

```
Get cards; group set aggregate prices.usd avg; sort by avg descending; limit 3.
```

#### 

#### Add

```
Add to cards {"object": "card", "id": "d778cdec-8fc7-4174-bae1-4c8e8ccdfab3", "oracle_id": "d4cde3d5-eb13-4ad5-8178-08780dc85d39", "name": "Radstorm", "lang": "en", "released_at": "2024-03-08", "set": "pip", "set_name": "Fallout"}
```

#### Update

```
Update cards where id = d778cdec-8fc7-4174-bae1-4c8e8ccdfab3 set {"name": "NEW_NAME"}
```

#### **Get, Filter**

```
Get cards; filter id = d778cdec-8fc7-4174-bae1-4c8e8ccdfab3
```

#### Delete

```
Delete cards where id = d778cdec-8fc7-4174-bae1-4c8e8ccdfab3
```

#### **Get, Filter**

```
Get cards; filter id = d778cdec-8fc7-4174-bae1-4c8e8ccdfab3
```

#### 