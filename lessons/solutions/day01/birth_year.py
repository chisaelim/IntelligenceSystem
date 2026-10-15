name = input("Your name: ")
age = int(input("Your age: "))
this_year = int(input("What year is it now? "))

birth_year = this_year - age
print(f"{name}, you were born around {birth_year}.")
