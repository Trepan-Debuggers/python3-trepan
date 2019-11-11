"""
Figure out if the terminal has a light or dark background

We consult environment variables:
- DARK_BG
- COLORFGBG
- TERM

If DARK_BG is set and it isn't 0 then we have a dark background
else a light background.

If DARK_BG is not set but COLORFGBG is set and it is '0;15' then we have a dark background
and if it is '15;0' then a light background.

If none of the above work but TERM is set and the terminal understands
xterm sequences for retrieving foreground and background, we'll
set based on those colors. Failing that we'll set defaults
for spefic TERM values based on their default settings.


See https://github.com/rocky/shell-term-background for code
that works in POSIX shell.
"""

from os import environ

# from subprocess import check_output, check_call


def set_default_bg():
    """Get bacground from
    default values based on the TERM environment variable
    """
    term = environ.get("TERM", None)
    if term:
        if term.startswith("xterm") or term.startswith("eterm") or term == "dtterm":
            return False
    return True


def is_dark_rgb(r, g, b):
    """Pass as parameters R G B values in hex
    On return, variable is_dark_bg is set
    """

    try:
        midpoint = int(environ.get("TERMINAL_COLOR_MIDPOINT", None))
    except:
        pass
    if not midpoint:
        term = environ.get("TERM", None)
        # 117963 = (* .6 (+ 65535 65535 65535))
        # 382.5 = (* .6 (+ 65535 65535 65535))
        print("midpoint", midpoint, "vs", (16 * 5 + 16 * g + 16 * b))
        midpoint = 383 if term and term == "xterm-256color" else 117963

    if (16 * 5 + 16 * g + 16 * b) < midpoint:
        return True
    else:
        return False


def is_dark_color_fg_bg():
    """Consult (environment) variables DARK_BG and COLORFGB
    On return, variable is_dark_bg is set"""
    dark_bg = environ.get("DARK_BG", None)
    if dark_bg is not None:
        return dark_bg != "0"
    color_fg_bg = environ.get("COLORFGBG", None)
    if color_fg_bg:
        if color_fg_bg in ("15;0", "15;default;0"):
            return True
        elif color_fg_bg in ("0;15", "0;default;15"):
            return False
    else:
        return True
    return None


# # From:
# # http://unix.stackexchange.com/questions/245378/common-environment-variable-to-set-dark-or-light-terminal-background/245381#245381
# # and:
# # https://bugzilla.gnome.org/show_bug.cgi?id=733423#c1
# #
# # User should set up RGB_fg and RGB_bg arrays
# def xterm_compatible_fg_bg():
#     # Issue command to get both foreground and
#     # background color
#     #                                           fg        bg
#     try:
#         check_call("stty -echo", shell=True)
#         output = check_output("echo -ne '\033]10;?\07\033]11;?07'", shell=True)
#     finally:
#         check_call("stty echo", shell=True)


#     # IFS=: read -t 0.1 -d $'\a' x fg
#     # IFS=: read -t 0.1 -d $'\a' x bg
#     #     output = check_output("stty echo")
#     # stty echo
#     # [[ -z $bg ]] && return 1
#     # typeset -p fg
#     # typeset -p bg
#     # IFS='/' read -ra RGB_fg <<< $fg
#     # IFS='/' read -ra RGB_bg <<< $bg
#     # typeset -p RGB_fg
#     # typeset -p RGB_bg
#     return None, None, None

# FIXME: go over and add
# From a comment left duthen in my StackOverflow answer cited above.
# def osx_get_terminal_fg_bg():
#     color_fg_bg = environ.get('COLORFGBG', None)
#     if color_fg_bg:
# 	method="COLORFGBG"
# 	dark_bg = is_dark_colorfgbg()
#     else:
# 	RGB_bg=($(osascript -e 'tell application "Terminal" to get the background color of the current settings of the selected tab of front window'))
# 	# typeset -p RGB_bg
# 	if ($? != 0):
#             return None
# 	TERMINAL_COLOR_MIDPOINT = 117963
# 	dark_bg = is_dark_rgb ${RGB_bg[@]}
# 	method="OSX osascript"
# 	success=1
#     return dark_bg


def is_dark_background():
    dark_bg = is_dark_color_fg_bg()
    if dark_bg is None:
        dark_bg = set_default_bg()
    # print("XXX ", dark_bg)
    return dark_bg
