def setup(app):
    """
    Register sphinx extension.

    Args:
        app: (todo): write your description
    """
    app.add_crossref_type(
        directivename = "setting",
        rolename = "setting",
        indextemplate = "pair: %s; setting",
    )
