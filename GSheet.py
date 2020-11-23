import gspread

gc = gspread.service_account(filename='credentials.json')

Book = gc.open('Chess_Tourney')
sheet = Book.get_worksheet(0)
sheet.update_cell(4, 3, 'p')
print(len(sheet.col_values(1)))
try:
    Cell = sheet.find("Rainey")
    print(f"{Cell.row},{Cell.col}")
except:
    print("nooooo")