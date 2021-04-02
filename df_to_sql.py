# Functions for transferring data from csvs/dataframes into sql tables
import pandas as pd
import psycopg2

def convert_df_to_sql_command(table_name, df1):
    """
        Function that takes a data frame and generates an SQL command for
        creating the table with the given table name.
        
        Attributes:  
        table_name | str  
        A name for the table that you want to create for the database.
        
        df1 | pandas.core.frame.DataFrame  
        The data frame that you want to make an SQL table out of.
        
        Returns:  
        A string containing the SQL command for creating the table from the
        given data frame.
    """
    # This is the dictionary between Python types and SQL types
    df_to_sql_dict = {
        "bool": "boolean",
        "datetime64[ns]": "date",
        "int64": "integer",
        "float64": "decimal (6, 3)",
        "object": "text"
    }
    # Get the data types of every column
    type_list = []
    for i in range(df1.shape[1]):
        type_list.append(df1.dtypes[i].name)
    # Convert the data types into sql data types
    sql_types = [df_to_sql_dict[data_type] for data_type in type_list]
    
    # Get the length of the largest column name
    max_num = len(max(df1.columns, key = len))
    
    # Create the commands for SQL to create the table
    
    command_lines = ["DROP TABLE IF EXISTS " + table_name + ";",
                     "CREATE TABLE " + table_name + " ("]
    for i in range(df1.shape[1]):
        # Using this to align the second column which is the sql data type
        spaces = " " * (1 + max_num - len( df1.columns[i] ))
        
        # Logic to make sure last line doesn't have comma
        if i == (df1.shape[1] - 1):
            comma_string = ""
        else:
            comma_string = ","
        
        command_string = ("    " + df1.columns[i] + spaces + sql_types[i] +
                          comma_string)
        
        command_lines.append(command_string)
    command_lines.append(");")
    
    full_command = '\n'.join(command_lines)
    return full_command

def import_csv_to_sql(database_connection, path_to_csv, table_name):
    
    cursor = database_connection.cursor()
    # Load the csv file
    csv_file = open(path_to_csv, 'r')
    # Skip the header row
    next(csv_file, None)
    # Add the csv values into the SQL table
    try:
        cursor.copy_from(csv_file, table = table_name, sep = ",",
                         null = "NULL")
        database_connection.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: {}".format(error))
        database_connection.rollback()
        cursor.close()

    print("csv file values imported into sql table: {}.".format(table_name))
    cursor.close()
        
    

# Resources
# https://naysan.ca/2020/06/21/pandas-to-postgresql-using-psycopg2-copy_from/