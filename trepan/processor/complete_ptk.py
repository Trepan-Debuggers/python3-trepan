# -*- coding: utf-8 -*-

#   Copyright (C) Rocky Bernstein <rocky@gnu.org>
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

from prompt_toolkit.completion import CompleteEvent, Completion, WordCompleter
from prompt_toolkit.document import Document
from typing import Iterable, Sequence


class Trepan3KCompleter(WordCompleter):
    def __init__(self, top_level_commands: Sequence[str], aliases):

        # Note: "words" is a parameter WordCompleter uses and sets.
        words = sorted(top_level_commands + list(aliases.keys()))
        super().__init__(words)

        self.states = {"top-level-command": words}
        self.aliases = aliases

    def add_completions(self, key: str, words: Sequence[str]):
        self.states[key] = words

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        # Get list of words.
        text = document.text_before_cursor

        input_words = text.split()
        word_count = len(input_words)
        candidate_completions = []
        if word_count == 0 or (
            word_count == 1
            and not text.endswith(" ")
        ):
            candidate_completions = self.states["top-level-command"]
            if word_count == 1:
                word0 = input_words[0]
                if word0 in self.states["top-level-command"]:
                    display = self.aliases[word0] if word0 in self.aliases else word0
                    display_meta = self.meta_dict.get(display, "")
                    word_before_cursor = document.get_word_before_cursor(
                        WORD=self.WORD, pattern=self.pattern
                    )
                    yield Completion(
                        text=display + " ",
                        start_position=-len(word_before_cursor),
                        display=display,
                        display_meta=display_meta,
                    )
                    return
        elif word_count >= 1:
            if not text.endswith(" "):
                # Matching with a partially-filled final word
                input_words = input_words[:-1]

            key = ""
            for input_word in input_words:
                key += input_word
                next_state = self.states.get(key)
                if next_state is None:
                    return
                key += " "
            candidate_completions = self.states.get(key.strip())
            if candidate_completions is None:
                return

        # Get word/text before cursor.
        word_before_cursor = document.get_word_before_cursor(
            WORD=self.WORD, pattern=self.pattern
        )

        def word_matches(word: str) -> bool:
            """True when the word before the cursor matches."""
            return word.startswith(word_before_cursor)

        for candidate_word in candidate_completions:
            if word_matches(candidate_word):
                display = self.display_dict.get(candidate_word, candidate_word)
                display_meta = self.meta_dict.get(candidate_word, "")
                yield Completion(
                    text=candidate_word,
                    start_position=-len(word_before_cursor),
                    display=display,
                    display_meta=display_meta,
                )


if __name__ == "__main__":
    from prompt_toolkit import PromptSession
    from trepan import debugger

    d = debugger.Trepan()
    proc = d.core.processor

    command_names = list(proc.commands.keys())
    trepan3k_completer = Trepan3KCompleter(command_names, proc.aliases)
    for cmd, cmd_obj in proc.commands.items():
        cmd_obj = proc.commands[cmd]
        if hasattr(cmd_obj, "cmds") and hasattr(cmd_obj.cmds, "cmdlist"):
            trepan3k_completer.add_completions(cmd, cmd_obj.cmds.cmdlist)
            for subcmd_name, subcmd_obj in cmd_obj.cmds.subcmds.items():
                subcmd_key = f"{cmd} {subcmd_name}"
                if hasattr(subcmd_obj, "completion_choices"):
                    trepan3k_completer.add_completions(subcmd_key, subcmd_obj.completion_choices)
                pass
            pass
        elif hasattr(cmd_obj, "completion_choices"):
            trepan3k_completer.add_completions(cmd, cmd_obj.completion_choices)

        pass

    def main():
        session = PromptSession(completer=trepan3k_completer)

        while True:
            try:
                text = session.prompt("> ")
            except KeyboardInterrupt:
                continue
            except EOFError:
                break
            else:
                print("You entered:", text)
        print("GoodBye!")

    main()
