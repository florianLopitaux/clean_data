import os

# -----------------------------------------------------------------------------

FILE_PATH = os.path.join("raw_data", "games.csv")

# -----------------------------------------------------------------------------

def parse_and_format_file(file_path: str, delimeter_searched: chr = ',', delimeter_expected: chr = ';') -> str:
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
    new_file_content = file_content.replace("<strong>", "")
    new_file_content = file_content.replace("</strong>", "")
    new_file_content = file_content.replace("<br>", "")
    
    # replace null values '\N' by None value
    new_file_content = file_content.replace("\N", "")

    return new_file_content

# -----------------------------------------------------------------------------


if __name__ == "__main__":
    if not os.path.isfile(FILE_PATH):
        print(f"Error, the file : '{FILE_PATH}' doesn't exist !")
        exit(1)

    # replace all delimter commas by semi-colons
    file_content = parse_and_format_file(FILE_PATH)

    # remove useless elements like html tags or '\N' for null values
    file_content = remove_useless_elements(file_content)

    # write in output the new file data
    output_path = os.path.join("clean_data", f"clean_{os.path.basename(FILE_PATH)}")
    with open(output_path, mode='w', encoding='utf-8') as output_file:
        output_file.write(file_content)
