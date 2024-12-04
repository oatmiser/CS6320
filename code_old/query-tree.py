#from textblob import TextBlob
#query = "I'd like a vegan, gluten-free recipe with lentils and chickpeas"
#blob = TextBlob(query)
#print(blob.noun_phrases)  # Returns phrases like "gluten-free recipe", "lentils"


import spacy
nlp = spacy.load("en_core_web_sm")

#class Node:
#    def __init__(self, name, parent, form):
#        self.name = name
#        self.parent = parent
#        self.form = form

def build_tree(token, tree=None):
    if tree is None:
        tree = dict()

    tree[token.text] = {"dependency": token.dep_,
                        "children": list()}
    for child in token.children:
        tree[token.text]["children"].append(build_tree(child))
    return tree
def print_tree(tree, level=0):
    for token, info in tree.items():
        print(f"{'  '*level}{token} ({info['dependency']})")
        for child in info["children"]:
            print_tree(child, level + 1)

query = ''
while query != 'leave':
    query = input('\nnew query: ')
    doc = nlp(query)

    nodes = list()
    for token in doc:
        print(f"'{token.text}' is related to '{token.head}' as '{token.dep_}'")
        print('\t' + token.ent_type_)
        #nodes.append(Node(token.text, token.head, token.dep_))

    root = [t for t in doc if t.dep_=='ROOT'][0]
    t = build_tree(root)
    print()
    print_tree(t)


# Root
# make, cook, do, use

# Compound under nsubj
# vegan

# dobj
# sodium
