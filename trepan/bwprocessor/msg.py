# -*- coding: utf-8 -*-
#   Copyright (C) 2015 Rocky Bernstein <rocky@gnu.org>
''' Common I/O routines'''

# Note for errmsg, msg, and msg_nocr we don't want to simply make
# an assignment of method names like self.msg = self.debugger.intf.msg,
# because we want to allow the interface (intf) to change
# dynamically. That is, the value of self.debugger may change
# in the course of the program and if we made such an method assignemnt
# we wouldn't pick up that change in our self.msg
def errmsg(proc_obj, message, opts={}):
    response = proc_obj.response
    if 'set_name' in opts: response['name'] = 'error'
    return response['errs'].append(message)


def msg(proc_obj, message, opts={}):
    response = proc_obj.response
    return response['msg'].append(message)


# Demo it
if __name__=='__main__':
    class Demo:
        def __init__(self):
            self.response = {'errs': [],
                             'msg' : []}
            pass
        pass

    import pprint
    demo = Demo()
    msg(demo, 'hi')
    pp = pprint.PrettyPrinter()
    pp.pprint(demo.response)
