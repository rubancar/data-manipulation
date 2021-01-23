from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a table_nodel spreadsheet in Google account
SPREADSHEET_ID = '1zhGVw3hQY1I8EnyrQGNLYtMM3zOlVOzdlmwMyJJxSeY'
# Give access to all cells in sheet Reto1
RANGE = 'Reto1!A1:Z1000'

def main():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()

    # create new sheet
    create_new_sheet(sheet, 'results')
    create_pivot_table_using_query(sheet)
    


def create_pivot_table_using_query(sheetService):
    requests = []

    query_to_generate_pivot_tables = '={query(Reto1!A1:D; "select A, B, count(A) where A is not null group by A, B pivot C";1)\ \
    query(Reto1!A1:D; "select count(A) where A is not null  group by A, B pivot D";1)}'


    query_header = '=query({query(Reto1!A1:D; "select A, B, count(A) where A is not null group by A, B pivot C";1)\ \
    query(Reto1!A1:D; "select count(A) where A is not null  group by A, B pivot D";1)}; "select * limit 0")'

    query_grouped_columns = '=query(query(Reto1!A1:D; "select A, B, count(A) where A is not null group by A, B";1);\
        "select Col1, Col2 offset 1"; 0)'

    query_values = '=ARRAYFORMULA(if(ISBLANK(query(     {query(Reto1!A1:D; "select A, B, count(A) where A is not null group by A, B pivot C";1)\ \
        query(Reto1!A1:D; "select count(A) where A is not null  group by A, B pivot D";1)};\
        "select Col3, Col4, Col5, Col6, Col7, Col8, Col9, Col10, Col11, Col12, Col13, Col14, Col15, Col16, Col17, Col18 offset 1"; 0)); "FALSE"; "TRUE"))'


    requests.append(insert_data_into_sheet(0, 2, 999999, [
                        {
                            'userEnteredValue': {
                            'stringValue': "Countries"
                        }
                    } 
                    ]))

    requests.append(insert_data_into_sheet(0, 13, 999999, [
                    {
                        'userEnteredValue': {
                        'stringValue': "Theme"
                    }
                } 
                ]))

    requests.append(insert_data_into_sheet(1, 0, 999999, [
                        {
                            'userEnteredValue': {
                            'formulaValue': query_header
                        }
                    } 
                    ]))

    requests.append(insert_data_into_sheet(2, 0, 999999, [
                        {
                            'userEnteredValue': {
                            'formulaValue': query_grouped_columns
                        }
                    } 
                    ]))
    
    # fill empty space with zeros, due to the query with pivot leaves black cells
    requests.append(insert_data_into_sheet(2, 2, 999999, [
                        {
                            'userEnteredValue': {
                            'formulaValue': query_values
                        }
                    } 
                    ]))


    body = {
        'requests': requests
    }

    response = sheetService.batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()

def insert_data_into_sheet(rowIndex, colIndex, sheetId, values):
    request = {
        'updateCells': {
            'rows': [
                {
                    "values": values
                }
            ],
            'start': {
                'sheetId': sheetId,
                'rowIndex': rowIndex,
                'columnIndex': colIndex
            },
            'fields': 'userEnteredValue'
        }
    }

    return request

def create_new_sheet(sheetService, sheetName):
    # check if sheet exists
    requests = []
    spreadsheet = sheetService.get(spreadsheetId=SPREADSHEET_ID).execute()
    sheets_data = [ (sheet['properties']['title'], sheet['properties']['sheetId']) for sheet in spreadsheet['sheets']]
    for sheet in sheets_data:
        # if sheet exists, simply delete
        if sheet[0] == sheetName:
            requests.append(
                {
                    'deleteSheet': {
                        'sheetId': sheet[1]
                    }
                }
            )
    
    # create a new sheet
    requests.append(
        {
            'addSheet': {
                'properties': {
                    'title': sheetName,
                    'sheetId': 999999
                }
            }
        }
    )
        
    body = {
        'requests': requests
    }

    sheetService.batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()


if __name__ == '__main__':
    main()