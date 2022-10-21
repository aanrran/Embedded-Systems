import random
list = []
for i in range(1, 10, 1):
    random_number = random.randint(0, 100)
    list.append(random_number)
print('a = ', list)
print('enter number: ')
limit = int(input())
new_list = []
for i in range(0, len(list), 1):
    if list[i] < limit:
        new_list.append(list[i])
print('The new list is ', new_list)