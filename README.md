# Better Spread
A wrapper around gspread with cell and row level functionalities

## Sheet

```python
from betterspread import Sheet, Connection

con = Connection(credentials_path="./credentials.json")
sheet = Sheet(connection=con, sheet_name="Better Sheet")
tab = await sheet.get_tab('Sheet1')
```
`Sheet` is a subclass of gsprad's `Spreadsheet`

### get all values
```python
await tab.values() # returns a list of rows
```

### Row
row is a subclass of list, with functionalities like `update` and `clear`
```python
row = await tab.get_row(1) # returns a Row
print(row)
```

### update row
```python
await row.update(['new', 'values'])
await row.clear() # clear all value of the row
```
### Cell
cell is a subclass of string, with additional functionalities like `update` and `clear`
```python
cell = await tab.get_cell('A1') # returns a Cell
cell = row[0] # same as above
```

### update cell
```python
await cell.update('New cell value')
await cell.clear() # clear value of the cell
```