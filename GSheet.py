import gspread

gc = gspread.service_account(filename='credentials.json')

Book = gc.open('Chess_Tourney')
sheet = Book.get_worksheet(0)
print(sheet.row_values(2))
try:
    Cell = sheet.find("Rainey")
    print(f"{Cell.row},{Cell.col}")
except:
    print("nooooo")