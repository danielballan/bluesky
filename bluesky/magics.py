"""
This module contains IPython magics for convenience.

This is a good place to say that bluesky *does not and will not* require
IPython for any of its core functionality. Importing this module is optional.
"""
from __future__ import print_function
from IPython.core.magic import (Magics, magics_class, line_magic,
                                cell_magic, line_cell_magic)
from IPython.terminal.prompts import Prompts, Token
from IPython.core.inputtransformer import StatelessInputTransformer


class RunModePrompts(Prompts):
    def in_prompt_tokens(self, cli=None):
        return  [(Token, 'RUNMODE'),
                 (Token.Prompt, ' ['),
                 (Token.PromptNum,
                 str(self.shell.execution_count)),
                 (Token.Prompt, ']: '),
                ]
    def rewrite_prompt_tokens(self):
        width = self._width()
        return [(Token.Prompt, ('-' * (width - 2)) + '> '),]


@magics_class
class RunEngineModalMagics(Magics):

    def __init__(self, shell, varname):
        super().__init__(shell)
        self.exit_requested = False

        def f(line):
            s = self.shell
            if self.exit_requested:
                # This is the first input after the user typed 'exit'.
                # It will pass through unaltered by the transformer.
                s.input_splitter.logical_line_transforms \
                    .remove(self.transformer)
                s.input_transformer_manager.logical_line_transforms \
                    .remove(self.rewrite_transformer)
                self.exit_requested = False
                return ''
            elif line == 'exit':
                # The user wants to exit runmode. Set a flag to remove it
                # just before the next input is processed. We cannot remove it
                # in this step because we need to catch 'exit' to avoid
                # exiting IPython.
                print('\nExiting %runmode. Back to normal IPython. Type exit '
                      'again to exit IPython.')
                s.prompts = self._old_prompts
                self.exit_requested = True
                return ''
            else:
                # runmode operation
                newcmd = '{}({})'.format(varname, line)
                return newcmd

        def f_rw(line):
            newcmd = f(line)
            self.shell.auto_rewrite_input(newcmd)
            return newcmd

        self.transformer = StatelessInputTransformer.wrap(f)()
        self.rewrite_transformer = StatelessInputTransformer.wrap(f_rw)()
        

    @line_magic
    def runmode(self, line):
        s = self.shell
        self._old_prompts = s.prompts
        s.input_splitter.logical_line_transforms.append(self.transformer)
        s.input_transformer_manager.logical_line_transforms \
            .append(self.rewrite_transformer)
        s.prompts = RunModePrompts(s)
        return line


def register_RE_magic(varname='RE'):
    # This class must then be registered with a manually created instance,
    # since its constructor has different arguments from the default:
    ip = get_ipython()
    magics = RunEngineModalMagics(ip, varname)
    ip.register_magics(magics)
