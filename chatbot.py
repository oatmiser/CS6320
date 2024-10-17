class UserPlan:
    def __init__(self, name:str, budget:float):
        self.name = name
        self.budget = budget
    def setIngredients(self, food:list):
        pass
    def display(self):
        s = f"Plan {self.name}:\n"
        #print(s + f"\tbudget {self.budget}")
        for attr in dir(self):
            if not callable(getattr(self, attr)) and not attr.startswith("__"):
                s += f"\t{attr} {getattr(self, attr)}\n"
        print(s)

plans = dict()
def addPlan(name:str, budget:float):
    global plans
    plans[name] = UserPlan(name, budget)

if __name__ == "__main__":
    while (True):
        user_choice = input("Command: ")
        if user_choice == "QUIT":
            break
        elif user_choice == "NEW":
            args = input("Enter a name and budget: ")
            name = " ".join(args.split(" ")[0:-1])
            budget = float(args.split(" ")[-1])
            addPlan(name, budget)
        elif user_choice == "EDIT":
            pass
        elif user_choice == "SHOW":
            for p in plans.values():
                p.display()
