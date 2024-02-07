# Standard Library Imports
import sys
import json

# Define constants
CATALOG_PATH = r'catalog/catalog.md'

'''
TEST CASES:
    - COMPLETE: TEST_1: All Normal, no Other Use Cases
    - COMPLETE: TEST_2: Other Check Selected, No Other FreeText populated
    - COMPLETE: TEST_3: Other Not Checked, FreeText Populated
    - COMPLETE: TEST_4: Other checked, Freetext populated
    - COMPLETE: TEST_5: Handle case where only OTHER is selected with no freetext populated
    - COMPLETE: TEST_6: Where only Other(s) is selected from Covered Use Cases and Freetext is populated
'''

def transform_use_cases(use_cases: str) -> str:
    use_cases = use_cases.strip()

    use_cases_selected = [value.strip('- [X] ') for value in use_cases.split('\n') if "[X]" in value]

    return ', '.join(use_cases_selected)

def transform_email_address(email: str) -> str:
    email = f'[Email](mailto:{email})'
    return email

def append_other_use_cases(use_cases: str, other_use_cases: str,  remove_others: bool) -> dict:
    if remove_others:
        if ', Other(s)' in use_cases:
            use_cases = use_cases.replace(', Other(s)', '')
            use_cases += ', ' + other_use_cases
        else:
            use_cases = use_cases.replace('Other(s)', '')
            use_cases = other_use_cases
    
    return use_cases

def main():
    # Store github_context payload
    # payload_dict: dict = json.loads(sys.argv[1])

    # LOCAL TESTING BLOCK
    payload_dict: dict = {}
    with open(sys.argv[1]) as fin:
        payload_dict = json.load(fin)

    # Select Issue body from JSON Dictionary
    issue_body: list = payload_dict["event"]["issue"]["body"].split('###')[1:]

    # Compose ordered dictionary of form answer : responses
    insert_dict = {key:value for key, value in [item.strip().split('\n\n') for item in issue_body]}

    # Remove confirm submission from insert dict, as we don't write that to the table
    del insert_dict['Confirm Submission?']

    # Perform Transformations
    insert_dict['Primary Point of Contact Email'] = transform_email_address(insert_dict['Primary Point of Contact Email'])

    insert_dict['Covered Use Cases'] = transform_use_cases(insert_dict['Covered Use Cases'])

    # Process Other Uses Case(s)
    if insert_dict['Other Use Case(s)'] != '_No response_':
        if 'Other(s)' in insert_dict['Covered Use Cases']:
            # Remove 'Other(s)' and append 'Other Use Case(s)' to 'Covered Use Cases'
            insert_dict['Covered Use Cases'] = append_other_use_cases(insert_dict['Covered Use Cases'], insert_dict['Other Use Case(s)'], True)
        else:
            # Just append 'Other Use Case(s)' to 'Covered Use Cases'
            insert_dict['Covered Use Cases'] = append_other_use_cases(insert_dict['Covered Use Cases'], insert_dict['Other Use Case(s)'], False)

    # Delete 'Other Use Case(s)' from insert_dict
    del insert_dict['Other Use Case(s)']

    # Transform dictionary values to list
    insert_list = list(insert_dict.values())

    # Transform list into pip delimited string, for insertion into markdown table
    insert_row = '| ' + ' | '.join(insert_list) + ' |'

    # Open catalog.md and write row to bottom of file
    with open(CATALOG_PATH, 'r+') as fin:
        lines = fin.read()
        if lines[-1] in ['\n', '\r\n', '']:
            fin.write(insert_row)
        else: 
            fin.write('\n'+insert_row)

if __name__ == "__main__":
    main()