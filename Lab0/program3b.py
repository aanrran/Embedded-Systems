import random
random_number = random.randint(0, 100)
result = False;
for i in range(1, 4, 1):
    your_guess = int(input("Enter your guess:"))
    if your_guess == random_number:
        result = True;

if result:
    print("You win!")
else:
    print("You lose!")