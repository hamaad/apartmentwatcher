# apartments.py
import requests
import sqlalchemy

class Apartment:
    def __init__(self, complex, bedrooms, unit, price, sqft, date):
        self.complex = complex
        self.bedrooms = bedrooms
        self.unit = unit
        self.price = price
        self.sqft = sqft
        self.date = date

        self.person_1_price = int(self.price * 0.4)
        self.person_2_price = int(self.price * 0.6)

    def __str__(self):
        return ("%s - The %sbd apartment unit (%s) is listing for $%s with %ssqft. It's available on %s. Person1 would pay $%s, Person2 would pay $%s"
        %(self.complex, self.bedrooms, self.unit, self.price, self.sqft, self.date, self.person_1_price, self.person_2_price))

def send_emails(potential_apartments, changed_apartments, off_market_apartments, new_apartments):
    message = ""

    if len(new_apartments) > 0:
        message += ("There are " + str(len(new_apartments)) + " new apartments! :)\n")
        for apartment in new_apartments:
            message += (str(apartment) + "\n")
        message += "\n"

    if len(changed_apartments) > 0:
        message += ("There are " + str(len(changed_apartments)) + " apartments with a price change! :|\n")
        for apartment in changed_apartments:
            message += (apartment + "\n")
        message += "\n"

    if len(off_market_apartments) > 0:
        message += ("There are " + str(len(off_market_apartments)) + " apartments taken off the market! :(\n")
        for apartment in off_market_apartments:
            message += (apartment + "\n")
        message += "\n"

    message += "Here's a list of all currently available apartments!\n"
    for apartment in potential_apartments:
        message += (str(apartment) + "\n")

    url = "<private_mailgun_api_url>"
    mailgun_api_key = "<private_mailgun_api_key>"
    email_from = "Apartment Watcher <projectemail@gmail.com>"
    subject = "Twice Daily Update for Apartment Watcher"

    requests.post(url, auth=("api", mailgun_api_key), data={"from": email_from, "to": "Person 1 <person1@gmail.com>", "subject": subject, "text": message})
    requests.post(url, auth=("api", mailgun_api_key), data={"from": email_from, "to": "Person 2 <person2@gmail.com>", "subject": subject, "text": message})

def get_excelsior_apartment_data():
    url = 'https://excelsiorseattle.com/floorplans/'
    data = {'action': 'available-units',
                'building': 1}
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://excelsiorseattle.com',
        'Referer': 'https://excelsiorseattle.com/floorplans/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }

    response = requests.post(url, data=data, headers=headers)

    potential_apartments = []
    for apartment in response.json():
        potential_apartments.append(
            Apartment(
                'Excelsior',
                apartment['bedroom'],
                apartment['unit'],
                apartment['max_rent'],
                apartment['sq_ft'],
                apartment['availability'][0:10],
            )
        )
    return potential_apartments

def get_modera_apartment_data():
    url = 'https://sightmap.com/app/api/v1/k9zw4m9zw87/sightmaps/13969'
    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "en-US,en;q=0.9",
        "sec-ch-ua": "\"Google Chrome\";v=\"105\", \"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"105\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-requested-with": "XMLHttpRequest",
        "cookie": "_ga=GA1.2.1581924043.1652929528; _gid=GA1.2.1441928259.1668469723; _gat=1",
        "Referer": "https://sightmap.com/embed/m1ywyl30pq0?enable_api=1&origin=https://www.moderabroadway.com",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }

    response = requests.get(url, headers=headers)
    response_json = response.json()

    floor_plans = {}
    for floor_plan in response_json['data']['floor_plans']:
        floor_plans[floor_plan['id']] = floor_plan['bedroom_count']

    potential_apartments = []
    for apartment in response_json['data']['units']:
        potential_apartments.append(
            Apartment(
                'Modera',
                floor_plans[apartment['floor_plan_id']],
                apartment['unit_number'],
                apartment['price'],
                apartment['area'],
                apartment['available_on'],
            )
        )
    return potential_apartments

def get_ava_apartment_data():
    url = 'https://api.avalonbay.com/json/reply/ApartmentSearch?communityCode=WA026'
    headers = {}

    response = requests.get(url, headers=headers)
    response_json = response.json()

    potential_apartments = []
    # 1 bedroom
    for available_floor_plan in response_json['results']['availableFloorPlanTypes'][0]['availableFloorPlans']:
        for apartment in available_floor_plan['finishPackages'][0]['apartments']:
            print(str(apartment['apartmentNumber']) + str(apartment['pricing']['effectiveRent']))
            if apartment['apartmentNumber'] != "5":
                potential_apartments.append(
                    Apartment(
                        'AVA',
                        apartment['beds'],
                        apartment['apartmentNumber'],
                        apartment['pricing']['effectiveRent'],
                        apartment['apartmentSize'],
                        apartment['pricing']['availableDate'],
                    )
                )

     # 2 bedrooms
    for available_floor_plan in response_json['results']['availableFloorPlanTypes'][1]['availableFloorPlans']:
        for apartment in available_floor_plan['finishPackages'][0]['apartments']:
            print(str(apartment['apartmentNumber']) + str(apartment['pricing']['effectiveRent']))
            if apartment['apartmentNumber'] != "5":
                potential_apartments.append(
                    Apartment(
                        'AVA',
                        apartment['beds'],
                        apartment['apartmentNumber'],
                        apartment['pricing']['effectiveRent'],
                        apartment['apartmentSize'],
                        apartment['pricing']['availableDate'],
                    )
                )
    return potential_apartments

def get_all_apartment_data():
    full_potential_apartments = []

    full_potential_apartments.extend(get_excelsior_apartment_data())
    full_potential_apartments.extend(get_modera_apartment_data())
    full_potential_apartments.extend(get_ava_apartment_data())

    full_potential_apartments.sort(key=lambda x: (x.complex, x.price))

    return full_potential_apartments

def create_sql_engine():
    connection_name = 'google_cloud_sql_db_connection_name'
    db_name = 'apartments'
    db_user = 'root'
    db_password = 'database_password'
    driver_name = 'mysql+pymysql'
    query_string = dict({"unix_socket": "/cloudsql/{}".format(connection_name)})

    return sqlalchemy.create_engine(
      sqlalchemy.engine.url.URL(
        drivername=driver_name,
        username=db_user,
        password=db_password,
        database=db_name,
        query=query_string,
      ),
      pool_size=5,
      max_overflow=2,
      pool_timeout=30,
      pool_recycle=1800
    )

def run_sql_statement_and_return_result(db, statement):
    try:
        with db.connect() as conn:
            result = conn.execute(statement)
            return result
    except Exception as e:
        error_string = 'Error: {}'.format(str(e))
        print(error_string)
        return error_string

def store_apartment_data_and_get_delta(potential_apartments):
    db = create_sql_engine()
    table_name = 'apartments'

    # Update all apartments in our database to have off_market = true.
    statement = sqlalchemy.text("update {} set {} = {}".format(table_name, 'off_market', True))
    run_sql_statement_and_return_result(db, statement)

    changed_apartments = []
    off_market_apartments = []
    new_apartments = []

    # Create the list of apartments currently in our database.
    statement = sqlalchemy.text("select {} from {}".format('*', table_name))
    apartments_in_db_result = run_sql_statement_and_return_result(db, statement)
    apartments_in_db = []
    for apartment_in_db in apartments_in_db_result:
        apartments_in_db.append(Apartment(
                                    apartment_in_db['complex'],
                                    apartment_in_db['bedrooms'],
                                    apartment_in_db['unit'],
                                    apartment_in_db['price'],
                                    apartment_in_db['sqft'],
                                    apartment_in_db['date']))

    # Go through all apartments returned from our APIs and
    #   compare them to apartments in our database.
    # This is done to update price changes and figure out changed apartments.
    for potential_apartment in potential_apartments:
        found = False
        for apartment_in_db in apartments_in_db:
            if apartment_in_db.unit == potential_apartment.unit and apartment_in_db.complex == potential_apartment.complex:
                found = True
                if apartment_in_db.price != potential_apartment.price:
                    # add apartment to changed_apartments list via string
                    # i.e. 'Apartment X has went from $Y to $Z.'
                    changed_apartments.append(('%s - The %sbd apartment unit (%s) price has changed from $%s to $%s.'
                    %(potential_apartment.complex, potential_apartment.bedrooms, potential_apartment.unit, apartment_in_db.price, potential_apartment.price)))

                    # update DB with new price + off_market = false
                    statement = sqlalchemy.text("update {} set {} = {}, {} = {} where {} = '{}' and {} = '{}'"
                                .format(table_name,
                                        'price', potential_apartment.price,
                                        'off_market', False,
                                        'complex', potential_apartment.complex,
                                        'unit', potential_apartment.unit))
                    result = run_sql_statement_and_return_result(db, statement)
                else:
                    # update DB with off_market = false
                    statement = sqlalchemy.text("update {} set {} = {} where {} = '{}' and {} = '{}'"
                                .format(table_name,
                                        'off_market', False,
                                        'complex', potential_apartment.complex,
                                        'unit', potential_apartment.unit))
                    result = run_sql_statement_and_return_result(db, statement)
        if not found:
            # create record of apartment in DB + off_market = false
            new_apartments.append(potential_apartment)
            statement = sqlalchemy.text("insert into {} ({}) values {}"
                        .format(table_name,
                                'complex, unit, bedrooms, price, sqft, date, off_market',
                                (potential_apartment.complex,
                                    potential_apartment.unit,
                                    potential_apartment.bedrooms,
                                    potential_apartment.price,
                                    potential_apartment.sqft,
                                    potential_apartment.date,
                                    False)))
            result = run_sql_statement_and_return_result(db, statement)

    # query DB for all apartments where off_market = true
    #   if any, add to list of apartments off the market
    statement = sqlalchemy.text("select {} from {} where {}".format('*', table_name, 'off_market = True'))
    result = run_sql_statement_and_return_result(db, statement)
    for off_market_apartment in result:
        off_market_apartments.append(('%s - The %sbd apartment unit (%s) is now off the market. Previously listing for $%s with %ssqft.'
        %(off_market_apartment.complex, off_market_apartment.bedrooms, off_market_apartment.unit, off_market_apartment.price, off_market_apartment.sqft)))
        statement = sqlalchemy.text("delete from {} where {}".format(table_name, 'off_market = True'))
        result = run_sql_statement_and_return_result(db, statement)

    # return list of apartment price changes + apartments off the market
    return changed_apartments, off_market_apartments, new_apartments

# Main code logic
def get_apartment_data_and_send_emails(event, context):
    potential_apartments = get_all_apartment_data()
    changed_apartments, off_market_apartments, new_apartments = store_apartment_data_and_get_delta(potential_apartments)
    send_emails(potential_apartments, changed_apartments, off_market_apartments, new_apartments)

# The line below is just for local testing, the google cloud function should automatically call the function above.
get_apartment_data_and_send_emails(1,1)
