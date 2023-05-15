"""Utility functions for checking types and values."""
_types = {
    "numeric": (np.floating, float, _IntLike()),
    "path-like": (str, Path, os.PathLike),
    "int": (_IntLike(),),
    "callable": (_Callable(),),
}


def _check_type(item, types, item_name=None):
    """
    Check that item is an instance of types.

    Parameters
    ----------
    item : object
        Item to check.
    types : tuple of types | tuple of str
        Types to be checked against.
        If str, must be one of:
            ('int', 'str', 'numeric', 'path-like', 'callable')
    item_name : str | None
        Name of the item to show inside the error message.

    Raises
    ------
    TypeError
        When the type of the item is not one of the valid options.
    """
    check_types = sum(
        (
            (type(None),)
            if type_ is None
            else (type_,)
            if not isinstance(type_, str)
            else _types[type_]
            for type_ in types
        ),
        (),
    )

    if not isinstance(item, check_types):
        type_name = [
            "None"
            if cls_ is None
            else cls_.__name__
            if not isinstance(cls_, str)
            else cls_
            for cls_ in types
        ]
        if len(type_name) == 1:
            type_name = type_name[0]
        elif len(type_name) == 2:
            type_name = " or ".join(type_name)
        else:
            type_name[-1] = "or " + type_name[-1]
            type_name = ", ".join(type_name)
        item_name = "Item" if item_name is None else "'%s'" % item_name
        raise TypeError(
            f"{item_name} must be an instance of {type_name}, "
            f"got {type(item)} instead."
        )

    return item