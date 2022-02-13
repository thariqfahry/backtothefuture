from bttf_utilities import find
from ast import literal_eval

pathlookup= {}

def build_lookup():
    for substudy in ['High Cycle','Injection','Needle Puncture']:
        root = 'H:\\' +substudy
        for path in find(root, ".ISQ"):
            filename = path[len(root)+1:].replace('\\','_') + '.png'
            
            pathlookup[filename] = path
            
            
    with open("pathlookup.txt", "w") as f:
        f.write(str(pathlookup))


if __name__ == "__main__":
    print("regenerating lookup...")
    build_lookup()
else:
    with open("pathlookup.txt", "r") as f:
        pathlookup = literal_eval(f.read())