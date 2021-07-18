import argparse
import json
import yaml
from termcolor import colored


def _entity(sample, prev_entity=None):
    text = sample['text']
    has_entity = input(colored("Has entities: ",attrs=['bold']))
    latest_entity = prev_entity
    if has_entity == 'y':
        sample['entities'] = []
        substring = input(colored("Substring: ",attrs=['bold']))
        while substring:
            start = text.find(substring)
            while (start != -1):
                end = start+len(substring)
                print(f'\t{text[:start]}{colored(text[start:end], "red", attrs=["bold"])}{text[end:]}')
                is_correct= input(colored("Is correct: ",attrs=['bold']))
                if is_correct:
                    if latest_entity:
                        entity_name = input(colored(f"Entity name [{latest_entity}]: ", attrs=['bold']))
                    else:
                        entity_name = input(colored("Entity name: ",attrs=['bold']))

                    if not entity_name and latest_entity is not None:
                        entity_name = latest_entity
                    else:
                        while not entity_name:
                            if latest_entity:
                                entity_name = input(colored(f"Entity name [{latest_entity}]: ", attrs=['bold']))
                            else:
                                entity_name = input(colored("Entity name: ",attrs=['bold']))

                    sample['entities'].append({
                        'start': start,
                        'end': end,
                        'entity': entity_name,
                    })

                    latest_entity = entity_name

                    if is_correct == 'yb':
                        break
                start = text.find(substring,end)
            substring = input(colored("Substring: ",attrs=['bold']))
    return sample, latest_entity

def _generate(nlu, skip_entity=False):
    intents = nlu['intents']
    intent_samples = []
    intent = input(colored("Intent name: ", 'blue', attrs=['bold']))
    while intent:
        latest_entity = None
        if intents.get(intent):
            print(f"Intent {intent} already exist. Append samples!")
            intent_samples = intents[intent]
        print()
        text = input(colored("Sample: ", attrs=['bold']))
        while text:
            sample = {'text': text}
            if not skip_entity:
                sample, latest_entity = _entity(sample, latest_entity)
            intent_samples.append(sample)
            print("------------------------------")
            text = input(colored("Sample: ", attrs=['bold']))
        intents[intent] = intent_samples
        intent_samples = []
        print()
        print("==============================")
        intent = input(colored("Intent name: ", 'blue', attrs=['bold']))
        print()

def run(inputfile:str=None, outputfile:str='./nlu.yaml', skip_entity:bool=False):
    if inputfile != None and str(inputfile).split('.')[-1] not in ['yaml', 'yml', 'json']:
        raise Exception('input nlu file must in json / yaml format')
    if outputfile.split('.')[-1] not in ['yaml', 'yml', 'json']:
        raise Exception('output nlu file must in json / yaml format')

    if inputfile:
        with open(inputfile,'r') as fp:
            extension = inputfile.split('.')[-1]
            if extension in ['yaml', 'yml']:
                nlu = yaml.load(fp, Loader=yaml.FullLoader)
            else:
                nlu = json.load(fp)
    else:
        nlu = {"intents":{}}

    _generate(nlu, skip_entity)
    extension = outputfile.split('.')[-1]
    with open(outputfile, 'w+', encoding='utf8') as fp:
        if extension in ['yaml', 'yml']:
            yaml.dump(nlu, fp, allow_unicode=True)
        else:
            json.dump(nlu, fp, ensure_ascii=False)
