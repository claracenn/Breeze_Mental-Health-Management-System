import pandas as pd


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



        




