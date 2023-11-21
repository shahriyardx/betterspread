# Better Spread
A wrapper around gspread with cell and row level functionalities

## Sheet

```python
from betterspread import Sheet, Connection

con = Connection(credentials_path="./credentials.json")
sheet = Sheet(connection=con, sheet_name="Better Sheet")
tab = sheet.get_tab('Sheet1')
```
`Sheet` is a subclass of gsprad's `Spreadsheet`

### get all values
```python
tab.values() # returns a list of rows
```

### Row
row is a subclass of list, with functionalities like `update` and `clear`
```python
row = tab.get_row(1) # returns a Row
print(row)
```

### update row
```python
row.update(['new', 'values'])
row.clear() # clear all value of the row
```
### Cell
cell is a subclass of string, with additional functionalities like `update` and `clear`
```python
cell = tab.get_cell('A1') # returns a Cell
cell = row[0] # same as above
```

### update cell
```python
cell.update('New cell value')
cell.clear() # clear value of the cell
```