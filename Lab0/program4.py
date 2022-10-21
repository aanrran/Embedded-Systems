# reference https://codereview.stackexchange.com/questions/238047/dictionary-of-names-and-birthdays
birthdays = {'Jon': 'July 17', 'Shauna': 'Jan 27', 'Lynette': 'July 10'}


print("Welcome to the birthday dictionary. We know the birthdays of:")
for name in birthdays:
    print(name)
name = input("Whose birthday do you want to look up? ")

if name in birthdays:
    print(name + "'s birthday is  " + birthdays[name])
else:
    print("I don't have that person's name in my archives.")
