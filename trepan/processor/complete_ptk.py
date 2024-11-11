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

from prompt_toolkit.completion import WordCompleter
from typing import Sequence


class Trepan3KCompleter(WordCompleter):
    def __init__(self, words: Sequence[str]):
        # Note: "words" is a parameter WordCompleter uses and sets.
        super().__init__(words)


if __name__ == "__main__":
    from prompt_toolkit import PromptSession
    from trepan import debugger
    d = debugger.Trepan()

    trepan3k_completer = Trepan3KCompleter(d.core.processor.commands.keys())

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
