import math

class UserPlan:
    def __init__(self, name:str, budget:float = 0, goal:str = "None", ingredients:list = []):
        self.name = name
        self.budget = budget
        self.goal = goal
        self.ingredients = ingredients

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
def add_plan(name:str, budget:float, goal:str, ingredients:list):
    global user_plans
    user_plans[name] = UserPlan(name, budget, goal, ingredients)

if __name__ == "__main__":
    while True:
        user_choice = input("\n#-# Command (new, edit, forget, show, quit): ").upper()
        # don't use a switch so we can break easily?
        if user_choice == "QUIT":
            break
        elif user_choice == "NEW":
            args = input("Enter name [budget] [goal] [(ingredient,)+ingredient]: ")
            split = args.split(" ")

            name = split[0]
            budget = 0
            goal = "x"
            ingredients = list()
            if len(args.split(" ")) > 1:
                for token in split[1:]:
                    try:
                        budget = float(token)
                    except ValueError:
                        if "," in token:
                            ingredients = token.split(",")
                        else:
                            goal += f" {token}"
            
            if name in user_plans:
                confirm = input(f"Plan {name} already exists, overwrite?\nY/N: ")
                if confirm[0].lower() == "y":
                    add_plan(name, budget, goal, ingredients)
                    print(f"Plan {name} was updated.")
                else:
                    print(f"Plan {name} is unchanged.")
            else:
                add_plan(name, budget, goal, ingredients)
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
                        break
                        # TODO do not allow? Otherwise we need to rehash in the dict and figure out processing multi-words
                        plan_obj.setName(split[1:]) # " ".join
                    case "budget":
                        plan_obj.setBudget(float(split[1]))
                    case "goal":
                        plan_obj.setGoal(" ".join(split[1:]))
                    case "ingredients":
                        # csv
                        if "," in update:
                            split = ["ingredients"] + update.split(" ")[1].split(",")
                        # space delimited
                        plan_obj.setIngredients(split[1:])
                    case _:
                        print(f"Sorry, {split[0]} is not a member of Plan {search}.")
            else:
                print("Sorry, this plan does not exist!")

        elif user_choice == "SHOW":
            plan_name = input()
            if len(plan_name) == 0:
                for obj in user_plans.values():
                    obj.display()
            else:
                user_plans[plan_name].display()


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
