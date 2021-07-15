import typing
from typing import Callable


def match_fun_args_call(fun: Callable, args: dict):
    fun_args = typing.get_type_hints(fun)
    call_args = dict()
    for fun_arg_name, fun_arg_t in fun_args.items():
        if fun_arg_name != 'return':
            call_args[fun_arg_name] = args[fun_arg_name]

    return fun(**call_args)
