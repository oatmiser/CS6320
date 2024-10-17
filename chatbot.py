class UserPlan:
    def __init__(self, name:str, budget:float):
        self.name = name
        self.budget = budget

    def display(self):
        str_build = f"Plan {self.name}:\n"
        for attr in dir(self):
            if not callable(getattr(self, attr)) and not attr.startswith("__"):
                str_build += f"\t{attr} {getattr(self, attr)}\n"
        print(str_build)

    def setIngredients(self, food:list):
        pass

    def setGoal(self, desc:str):
        pass

user_plans = dict()
def add_plan(name:str, budget:float):
    global user_plans
    user_plans[name] = UserPlan(name, budget)

if __name__ == "__main__":
    while True:
        user_choice = input("Command: ")
        # don't use a switch so we can break easily?
        if user_choice == "QUIT":
            break
        elif user_choice == "NEW":
            args = input("Enter a name and budget: ")
            name = " ".join(args.split(" ")[0:-1])
            budget = float(args.split(" ")[-1])
            add_plan(name, budget)
        elif user_choice == "EDIT":
            search = input("Enter plan name: ")
            if search in user_plans:
                pass
            else:
                print("Sorry, this plan does not exist!")
        elif user_choice == "SHOW":
            for obj in user_plans.values():
                obj.display()
