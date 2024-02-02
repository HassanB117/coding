choice = input("Choice [*,-,+,/,N1,N2]: ")

if choice == '*':
    num1=float(input(("Number 1: ")))
    num2=float(input(("Number 2: ")))
    total = num1 * num2
    print(f"{num1} * {num2} = {total}")

elif choice == '-':
    num1=float(input(("Number 1: ")))
    num2=float(input(("Number 2: ")))
    total = num1 - num2
    print(f"{num1} - {num2} = {total}")

elif choice == '+':
    num1=float(input(("Number 1: ")))
    num2=float(input(("Number 2: ")))
    total = num1 + num2
    print(f"{num1} + {num2} = {total}")

elif choice == '/':
    num1=float(input(("Number 1: ")))
    num2=float(input(("Number 2: ")))
    total = num1 / num2
    print(f"{num1} / {num2} = {total}")

elif choice == 'N1':
    Name1=str(input(("Name 1: ")))
    Name2=str(input(("Name 2: ")))
    total = Name2 + " " + Name2
    print(Name1 + " " + Name2)

elif choice == 'N2':
    print("Please put a space after the first name olny")
    num1=str(input(("Name 1:")))
    num2=str(input(("Name 2:")))
    total = num1 + num2
    print(f"{num1} + {num2} = {total}")

elif choice == 'n1':
    print("Please inter capital N and try again")
elif choice == 'n2':
    print("Please inter capital N and try again")
