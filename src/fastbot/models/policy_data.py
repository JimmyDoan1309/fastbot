from typing import List, Text, Optional
import random
import uuid


class Step:
    def __init__(self, intent: Optional[Text] = None, action: Optional[Text] = None, **kwargs):
        self.intent = intent
        self.action = action
        self.type = 'intent' if intent else 'action'
        self.hash = f'{self.type}__{intent if intent else action}'
        self.data = kwargs

    def __dict__(self):
        result = {
            self.type: self.intent or self.action,
            **self.data
        }
        return result

    def __repr__(self):
        return self.hash


class Story:
    def __init__(self, steps: List[Step], name: Optional[Text] = None):
        if name is None:
            name = str(uuid.uuid4())
        self.name = name
        self.steps = steps


class PolicyData:
    def __init__(self, stories: List[Story], **kwargs):
        self.stories = stories
        self._get_states_from_stories()

    def _get_states_from_stories(self):
        self.stories.append(Story([Step(intent='<UNK>'), Step(action='<FALLBACK>')]))
        self. actions = set()
        self.intents = set()
        self.states = set()
        for story in self.stories:
            for step in story.steps:
                self.states.add(step.hash)
                if step.type == 'intent':
                    self.intents.add(step.intent)
                else:
                    self.actions.add(step.action)
        self.states = list(self.states)
        self.intents = list(self.intents)
        self.actions = list(self.actions)

    def generate_extra_stories(self, factor: int = 3):
        assert factor >= 1, 'Factor must be equal or greter than 1'

        stories_count = len(self.stories)-1
        extra = int(len(self.stories)*(factor-1))
        for i in range(extra):
            r1 = random.randint(0, stories_count)
            r2 = random.randint(0, stories_count)
            unk = random.random() > 0.6  # Randomly insert <Unknown> state to the story
            story1 = self.stories[r1]
            story2 = self.stories[r2]
            unk_story = []
            if unk:
                unk_story = [Step(intent='<UNK>'), Step(action='<FALLBACK>')]

            rand = random.random()
            if rand < 0.33 and unk:
                new_story = [*story1.steps, *unk_story]
            elif rand < 0.66 and unk:
                new_story = [*unk_story, *story2.steps]
            else:
                new_story = [*story1.steps, *unk_story, *story2.steps]

            self.stories.append(Story(new_story))

            update_stories_length = random.random() > 0.6
            if update_stories_length:
                stories_count = len(self.stories)-1
