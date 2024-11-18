import pandas as pd
import json

def read_json(filepath):
    """
    Reads a JSON file and returns its content.
    """
    try:
        with open(filepath, 'r') as file:
            return json.load(file) 
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Invalid JSON format in file: {filepath} - {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
    

def save_json(filepath, data):
    """
    Writes data to a JSON file.
    """
    try:
        with open(filepath, 'w') as file:
            json.dump(data, file, indent=4)
        return True
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"Invalid JSON format in file: {filepath} - {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False


def add_entry(filepath, entry):
    """
    Adds a new entry to a JSON file
    """
    data = read_json(filepath)
    try:
        if isinstance(data, list):
            data.append(entry)
            return save_json(filepath, data)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False


def delete_entry(filepath, index):
    """
    Deletes an entry from a JSON file based on the index of the entry
    """
    data = read_json(filepath)
    
    try:
        if isinstance(data, list):
            if 1 <= index <= len(data):
                del data[index-1]
                return save_json(filepath, data)
            else:
                print(f"Invalid index: {index}")
                return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False


def update_entry(filepath, index, new_entry):
    """
    Updates an entry in a JSON file based on a key value pair
    """
    data = read_json(filepath)
    try:
        if isinstance(data, list):
            if 1 <= index <= len(data):
                data[index-1].update(new_entry)
                return save_json(filepath, data)
            else:
                print(f"Invalid index: {index}")
                return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False


def create_title(title, df, col_widths):
    """
    Create a title for the table we print such that
    it covers the entire length of the table and the title is
    centered
    """
    # calculate the width of the current table including separators
    total_width = sum(col_widths.values()) + 3 * (len(df.columns)-1)

    # center title
    title = title.center(total_width, " ")

    # print dashes and lines
    dash_lines = "".join(["-" for _ in range(total_width)])
    print(dash_lines)
    print(dash_lines)
    print(title)
    print(dash_lines)
    print(dash_lines)


def create_table(data, title="", display_title=False, display_index=False):
    """
    Creates and prints a standardized dataframe using pandas
    Input data must be of type dictionary with 
    Key: String
    Value: List of any type

    e.g
    data = {
            "Patient ID": [4, 3, 2],
            "Name": [Person4, Person3, Person2],
            "Email": [person4@mail.com, person3@mail.com, person2@mail.com], 
            "Emergency Contact": [em_person4@mail.com, em_person3@mail.com, em_person2@mail.com] 
            }

    WARNINGGGGG!!!!!!!!!
    All lists within the dictionary must be of same length due 
    to how pandas operates internally. This should be fine for our usecases.
    """
    # create pandas dataframe and convert its values to strings
    df = pd.DataFrame(data=data).astype(str)

    # add index to the DataFrame if display_index is True
    if display_index:
        df.index = [str(i + 1) for i in range(len(df))]
        df.index.name = "Index" 
        df = df.reset_index() 

    # calculate max_width for each col based on length of each val (headers and data)
    col_widths = {col: max(df[col].str.len().max(), len(col)) for col in df.columns}

    # center align the values in each cell
    for col, width in col_widths.items():
        df[col] = df[col].str.center(width)

    #print title
    if display_title:
        create_title(title, df, col_widths)

    # print headers separately
    headers = [col.center(col_widths[col]) for col in df.columns]
    print(" | ".join(headers))
    print("=+=".join("=" * col_widths[col] for col in df.columns))

    # now print row data (the first parameter is index if needed)
    for _, row in df.iterrows():
        print(" | ".join(row))




