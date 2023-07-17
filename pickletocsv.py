import pandas as pd
#from google.colab import files

# Loading the first pickle file
with open('diseases_names.pkl', 'rb') as f:
    list1 = pd.read_pickle(f)

# Load the second pickle file
with open('skin_diseases_names.pkl', 'rb') as f:
    dict2 = pd.read_pickle(f)

# Creating a dictionary from the list
dict1 = {i: v for i, v in enumerate(list1)}

print(type(dict1))
print(type(dict2))

# Merging the two dictionaries
dict1.update(dict2)

print(dict1)

# Converting the merged dictionary to a dataframe
# df = pd.DataFrame.from_dict(dict1, orient='index', columns=['#DISEASE'])

# Writing the dataframe to a CSV file
#The r before the string is used to indicate that the string is a raw string. This means that the string should be treated as a literal string, without any special characters being interpreted.
#Otherwise it will interpret it as \.. with some functionality like \n or \t
# df.to_csv(r'C:\Users\Urmil Pawar\Documents\Google Solution Challenge\diseases_names_combined.csv',index=False, index_label='INDEX')

df = pd.DataFrame.from_dict(dict1, orient='index', columns=['DISEASE'])

# Writing the dataframe to a CSV file
# The r before the string is used to indicate that the string is a raw string.
# This means that the string should be treated as a literal string, without any special characters being interpreted.
# Otherwise, it will interpret it as \.. with some functionality like \n or \t
df.to_csv(r'C:\Users\Urmil Pawar\Documents\Google Solution Challenge\diseases_names_combined.csv', index=False, header=['#DISEASE'])

