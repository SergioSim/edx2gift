"""Gitlint rule validating the message title matches "<gitmoji>(<scope>) <subject>"."""
from __future__ import unicode_literals

import re

import requests

from gitlint.rules import CommitMessageTitle, LineRule, RuleViolation


class GitmojiTitle(LineRule):
    """Validates commit message titles.

    This rule will enforce that each commit title is of the form
    "<gitmoji>(<scope>) <subject>" where gitmoji is an emoji from the list defined in
    https://gitmoji.carloscuesta.me and subject should be all lowercase.
    """

    id = "UC1"
    name = "title-should-have-gitmoji-and-scope"
    target = CommitMessageTitle

    def validate(self, title, _commit):
        """Checks that the title contains onee of the possible gitmojis."""
        base_url = "https://raw.githubusercontent.com"
        file_path = "carloscuesta/gitmoji/master/packages/gitmojis/src/gitmojis.json"
        gitmojis = requests.get(f"{base_url}/{file_path}").json()["gitmojis"]
        emojis = [item["emoji"] for item in gitmojis]
        pattern = r"^({:s})\(.*\)\s[a-z].*$".format("|".join(emojis))
        if not re.search(pattern, title):
            violation_msg = 'Title does not match regex "<gitmoji>(<scope>) <subject>"'
            return [RuleViolation(self.id, violation_msg, title)]
