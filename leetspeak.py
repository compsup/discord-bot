import json
import random

def encode(input: str, settings: dict) -> str:
    #go through each rule in settings file
    for setting in settings.keys():
        #replace every character with a random substitue
        input = input.replace(setting, random.choice(settings[setting]))
        #do the same with uppercase
        input = input.replace(setting.upper(), random.choice(settings[setting]))
    return input
def decode(input: str, settings: dict) -> str:
    #get values from settings dict as list
    values = list(settings.values())
    #get keys
    keys = list(settings.keys())
    #do for loop with indices of vals
    for i in range(len(values)):
        #get every possible item
        for item in values[i]:
            #replace item with key 
            input = input.replace(item, keys[i])
    return input
#only do if file is run on its own
if __name__ == "__main__":
    #open settings file
    settings_file = open("settings.json", "r")
    #load as dict
    settings: dict = json.load(settings_file)
    #get user choice
    choice = input  ("encode or decode (e/d)")
    if choice == "e":
        inp = input("What should I leetify? ")
        out = encode(inp, settings)
        print(f"Leetified: {out}")
    elif choice == "d":
        inp = input("What should I normalize? ")
        out = decode(inp, settings)
        print(f"Normalized: {out}")