from typing import List, Optional
from .constants import FALLBACK


class PolicyResult:
    def __init__(self, action, actions_ranking: List = []):
        self.action = action
        self.actions_ranking = actions_ranking
        if self.action == FALLBACK:
            self.action = None
