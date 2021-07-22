from . import ActionPolicy
from .constants import FALLBACK, UNKOWN
from .policy_result import PolicyResult
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import OneHotEncoder
from fastbot.models import Message, PolicyData
from fastbot.dialog.context import ContextManager
from typing import List, Text, Tuple, Dict, Any
import numpy as np


class SklearnPolicy(ActionPolicy):
    def __init__(self, max_history: int = 10, **kwargs):
        super().__init__(**kwargs)
        self.max_history = max_history
        self.state_oh = kwargs.get(
            'state_oh',
            OneHotEncoder(handle_unknown='ignore', sparse=False)
        )
        self.action_oh = kwargs.get(
            'action_oh',
            OneHotEncoder(handle_unknown='ignore', sparse=False)
        )
        self.model = kwargs.get('model', MLPClassifier(max_iter=1000))

    def _padding(self, history=List[List[Text]]):
        if len(history) < self.max_history:
            pad = [[None]]*(self.max_history-len(history))
            history = [*pad, *history]
        elif len(history) > self.max_history:
            history = history[-self.max_history:]
        return history

    def _preprocess_data(self, data: PolicyData) -> Tuple[np.ndarray]:
        X = []
        y = []
        for story in data.stories:
            history = [[step.hash] for step in story.steps[:-1]]
            action = [[story.steps[-1].action]]
            history = self._padding(history)

            history = self.state_oh.transform(history)
            history = history.reshape((1, -1))[0]
            action = self.action_oh.transform(action)[0]
            X.append(history)
            y.append(action)

        X = np.asarray(X)
        y = np.asarray(y)
        return X, y

    def train(self, data: PolicyData) -> None:
        states = np.asarray(data.states).reshape((-1, 1))
        actions = np.asarray(data.actions).reshape((-1, 1))
        self.state_oh.fit(states)
        self.action_oh.fit(actions)

        X, y = self._preprocess_data(data)
        self.model.fit(X, y)

    def _history_from_context(self, context: ContextManager):
        history = context.get_history()
        steps = []
        for step in history:
            step_hash = step.hash
            if step_hash not in self.state_oh.categories_[0]:
                if step.action:
                    step_hash = f'action__{FALLBACK}'
                else:
                    step_hash = f'intent__{UNKOWN}'
            steps.append([step_hash])

        steps = self._padding(steps)
        embed = self.state_oh.transform(steps)
        embed = embed.reshape((1, -1))
        return embed

    def _actions_ranking(self, probs: np.ndarray) -> PolicyResult:
        actions = []
        action = None
        for i, prob in enumerate(probs):
            actions.append({
                'name': self.action_oh.categories_[0][i],
                'score': prob
            })
        actions.sort(key=lambda a: a['score'], reverse=True)
        if (actions[0]['score'] >= self.confident_threshold) and (actions[0]['score']-actions[1]['score'] > self.ambiguity_threshold):
            action = actions[0]['name']
        return PolicyResult(action, actions)

    def process(self, message: Message, context: ContextManager) -> Dict[Text, Any]:
        X = self._history_from_context(context)
        y = self.model.predict_proba(X)[0]
        result = self._actions_ranking(y)
        return result
