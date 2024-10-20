import math

class UserPlan:
    def __init__(self, name:str, budget:float = float(math.inf)):
        self.name = name
        self.budget = budget
        self.goal = "No goal set."
        self.ingredients = []

    def display(self):
        str_build = f"Plan {self.name}:\n"
        for attr in dir(self):
            if not callable(getattr(self, attr)) and not attr.startswith("__"):
                str_build += f"\t{attr} {getattr(self, attr)}\n"
        print(str_build)

    def setName(self, name:str):
        self.name = name
    def setBudget(self, amount:float):
        self.budget = amount
    def setGoal(self, desc:str):
        self.goal = desc
    def setIngredients(self, food:list):
        self.ingredients = food

user_plans = dict()
def add_plan(name:str, budget:float):
    global user_plans
    user_plans[name] = UserPlan(name, budget)

if __name__ == "__main__":
    while True:
        user_choice = input("\n#-# Command (new, edit, forget, show, quit): ").upper()
        # don't use a switch so we can break easily?
        if user_choice == "QUIT":
            break
        elif user_choice == "NEW":
            args = input("Enter a name and budget: ")
            # TODO argparse instead of indexes? This would be called in the backend so maybe not necessary...
            name = " ".join(args.split(" ")[0:-1])
            budget = float(args.split(" ")[-1])
            if name in user_plans:
                confirm = input(f"Plan {name} already exists, overwrite?\nY/N: ")
                if confirm[0].lower() == "y":
                    add_plan(name, budget)
                    print(f"Plan {name} was updated.")
                else:
                    print(f"Plan {name} is unchanged.")
            else:
                add_plan(name, budget)
                print(f"Plan {name} was created.")

        elif user_choice == "EDIT":
            search = input("Enter plan name: ")
            if search in user_plans:
                plan_obj = user_plans[search]
                plan_obj.display()
                update = input("Select a variable to update: ")

                if update in dir(plan_obj): # get attrs
                    update = update +" "+ input(f"\tchange {update} = ")                
                split = update.split(" ")
                match split[0]:
                    case "name":
                        # TODO need to rehash in the dictionary!
                        plan_obj.setName(split[1:]) # " ".join
                    case "budget":
                        plan_obj.setBudget(float(split[1]))
                    case "goal":
                        plan_obj.setGoal(split[1:]) # " ".join
                    case "ingredients":
                        plan_obj.setIngredients(split[1:]) # TODO replace the split var for readability overall, and use csv here?
                    case _:
                        print(f"Sorry, {split[0]} is not a member of Plan {search}.")
            else:
                print("Sorry, this plan does not exist!")

        elif user_choice == "SHOW":
            for obj in user_plans.values():
                obj.display()

        elif user_choice == "FORGET":
            search = input("Enter plan to remove: ")
            if search in user_plans:
                confirm = input(f"Do you really want to remove Plan {search}?\nY/N: ")
                if confirm[0].lower() == "y":
                    user_plans.pop(search)
                    print(f"Plan {search} was removed.")
                else:
                    print(f"Plan {search} was NOT removed.")
            else:
                print("Sorry, this plan does not exist!")
