import requests
import json

def get_drug_info(medication, limit=1):
    """
    Retrieves drug information for a given indication from the OpenFDA API.
    
    :param indication: The medical condition or symptom to query.
    :param limit: The maximum number of results to return.
    :return: A JSON object with the drug information or an error message.
    """
    api_key = 'SnxC8nr4Si3zQhI5zgAGOXK2BumHgbnJxtEa3SGV'
    base_url = 'https://api.fda.gov/drug/event.json'
    query = medication
    request_url = f'{base_url}?search={query}&limit={limit}&api_key={api_key}'
    print(request_url)
    
    response = requests.get(request_url)
    
    if response.status_code == 200:
        result = response.json()
        manufacturer_name = result["results"][0]["patient"]["drug"][0]["openfda"]["manufacturer_name"][0]
        return manufacturer_name
    else:
        return f'Error: {response.status_code} - {response.text}'

result = get_drug_info('Lyrica')


print("Manufacturer Name:", result)

