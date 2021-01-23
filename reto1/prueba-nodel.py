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
    # METHOD #1
    # create_autogenerated_pivot_table(sheet)

    # METHOD #2
    # create new sheet
    create_new_sheet(sheet, 'result2-test')
    create_pivot_table_using_query(sheet)
    # fill empty space with zeros, due to the function COUNTA leaves black cells
    


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
        "select Col3, Col4, Col5, Col6, Col7, Col8, Col9, Col10, Col11, Col12, Col13, Col14, Col15, Col16, Col17, Col18 offset 1"; 0)); "Falso"; "Verdadero"))'


    requests.append({
        'updateCells': {
            'rows': [
                {
                    "values": [
                        {
                            'userEnteredValue': {
                            'formulaValue': query_header
                        }
                    } 
                    ]
                }
            ],
            'start': {
                'sheetId': '999999',
                'rowIndex': 1,
                'columnIndex': 0
            },
            'fields': 'userEnteredValue'
        }
    })

    requests.append({
        'updateCells': {
            'rows': [
                {
                    "values": [
                        {
                            'userEnteredValue': {
                            'formulaValue': query_grouped_columns
                        }
                    } 
                    ]
                }
            ],
            'start': {
                'sheetId': '999999',
                'rowIndex': 2,
                'columnIndex': 0
            },
            'fields': 'userEnteredValue'
        }
    })

    requests.append({
        'updateCells': {
            'rows': [
                {
                    "values": [
                        {
                            'userEnteredValue': {
                            'formulaValue': query_values
                        }
                    } 
                    ]
                }
            ],
            'start': {
                'sheetId': '999999',
                'rowIndex': 2,
                'columnIndex': 2
            },
            'fields': 'userEnteredValue'
        }
    })


    body = {
        'requests': requests
    }

    response = sheetService.batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()


def create_pivot_table_manually(sheetService):

    requests = []

    query_to_generate_pivot_tables = '={query(Reto1!A1:D; "select A, B, count(A) where A is not null group by A, B pivot C";1)\ \
    query(Reto1!A1:D; "select A, B, count(A) where A is not null  group by A, B pivot D";1)}'
    


    requests.append({
        'updateCells': {
            'rows': {
                'values': [
                    {
                        'pivotTable': {
                            'source': {
                                'sheetId': 0,
                                'startRowIndex': 0,
                                'startColumnIndex': 0
                            },
                            'rows': [
                                {
                                    'sourceColumnOffset': 0,
                                    'showTotals': False,
                                    'sortOrder': 'ASCENDING',
                                },
                                {
                                    'sourceColumnOffset': 1,
                                    'showTotals': False,
                                    'sortOrder': 'ASCENDING',
                                },

                            ],
                            'columns': [
                                {
                                    'sourceColumnOffset': 2,
                                    'sortOrder': 'ASCENDING',
                                    'showTotals': False,

                                }
                            ],
                            'values': [
                                {
                                    'summarizeFunction': 'CUSTOM',
                                    'formula': '=IF(COUNTA(Country)>0; "Verdadero"; "Falso")'
                                }
                            ],
                            'valueLayout': 'HORIZONTAL'
                        }
                    }
                ]
            },
            'start': {
                'sheetId': '1844551335',
                'rowIndex': 0,
                'columnIndex': 0
            },
            'fields': 'pivotTable'
        }
    })
    
    requests.append(requestToUpdateCells)
    body = {
        'requests': requests
    }
    #sheet.batchUpdate(spreadsheetId=SAMPLE_SPREADSHEET_ID, body=body).execute()

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