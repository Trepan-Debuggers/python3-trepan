# Our local modules
from trepan.processor.command import base_subcmd as Mbase_subcmd


class ShowDbgTrepan(Mbase_subcmd.DebuggerShowBoolSubcommand):
    """Show debugging the debugger"""
    min_abbrev = 4  # Min 'show trep"
    short_help = 'Show debugging the debugger'
    pass
