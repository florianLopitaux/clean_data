import os
import csv
import json
from io import StringIO

# -----------------------------------------------------------------------------

FILE_PATH = os.path.join("raw_data", "games.csv")
FINAL_DELIMETER = ';'

# -----------------------------------------------------------------------------

def parse_and_format_file(file_path: str, delimeter_searched: chr = ',', delimeter_expected: chr = FINAL_DELIMETER) -> str:
    new_file_content = ""

    with open(file_path, mode='r', encoding='utf-8') as input_file:
        inside_quotes = False
        previous_char = None

        while (current_char := input_file.read(1)):
            if current_char == '"' and previous_char != '\\':
                inside_quotes = not inside_quotes

            elif current_char == delimeter_searched and not inside_quotes:
                current_char = delimeter_expected
            
            new_file_content += current_char
            previous_char = current_char

    return new_file_content


def remove_useless_elements(file_content: str) -> str:
    # remove all <strong>, </strong> and <br> html tags
    new_file_content = file_content.replace("<strong>*", "")
    new_file_content = new_file_content.replace("<strong>", "")
    new_file_content = new_file_content.replace("</strong>", "")
    new_file_content = new_file_content.replace("<br>", "")
    
    # replace null values '\N' by None value
    new_file_content = new_file_content.replace("\\N", "")

    return new_file_content


def parse_csv_data(csv_content: str, csv_delimeter: str = FINAL_DELIMETER) -> str:
    csv_formatted = list()
    reader = csv.DictReader(StringIO(csv_content), delimiter=csv_delimeter)
    
    for row in reader:
        row_formatted = row
        if len(row_formatted['is_free']) > 0:
                row_formatted['is_free'] = int(row_formatted['is_free'])

        if len(row['price_overview']) > 0:
            # loads json data of price overview column
            value_formatted = row['price_overview'].replace('"{', '{')
            value_formatted = value_formatted[:2] + '"' + value_formatted[2:]
            value_formatted = value_formatted.replace('\\"', '"').replace('}"', '}')

            price_data = json.loads(value_formatted)
        
            # get interesting data from price overview
            del row_formatted['price_overview']
            row_formatted['currency'] = price_data['currency']

            final_price = ""
            find_numbers = False
            for char in price_data['final_formatted']:
                if str(char).isdigit() or (find_numbers and (char == ',' or char == '.')):
                    final_price += char
                    find_numbers = True
                elif find_numbers:
                    break

            # transform number string to int and add the row to the list
            if '.' in final_price:
                final_price = final_price.replace(',', '')
            else:
                final_price = final_price.replace(',', '.')

            try:
                row_formatted['price'] = float(final_price)
            except:
                row_formatted['price'] = None

        else:
            del row_formatted['price_overview']
            row_formatted['price'] = None
            row_formatted['currency'] = None

        csv_formatted.append(row_formatted)

    return csv_formatted

# -----------------------------------------------------------------------------


if __name__ == "__main__":
    if not os.path.isfile(FILE_PATH):
        print(f"Error, the file : '{FILE_PATH}' doesn't exist !")
        exit(1)

    # replace all delimter commas by semi-colons
    print(f"Parse csv file and re-format them (long process) ...")
    file_content = parse_and_format_file(FILE_PATH)
    print(f"Parsing done")

    # remove useless elements like html tags or '\N' for null values
    print("Search and delete useless elements ...")
    file_content = remove_useless_elements(file_content)
    print("End of removing")

    # parse csv data to get just interesting data and reformat other
    print("Parse csv data ...")
    csv_content = parse_csv_data(file_content)
    csv_column_names = ["app_id", "type", "name", "release_date", "is_free", "price", "currency", "languages"]
    print("Finish to parse price data")

    # write in output the new file data
    output_path = os.path.join("clean_data", f"clean_{os.path.basename(FILE_PATH)}")
    with open(output_path, mode='w', encoding='utf-8') as output_file:
        writer = csv.DictWriter(output_file, delimiter=FINAL_DELIMETER, fieldnames=csv_column_names)
        writer.writeheader()
        writer.writerows(csv_content)

    print(f"Csv file : '{output_path}' successfully created.")
