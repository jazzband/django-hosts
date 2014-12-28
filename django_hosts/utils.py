
def normalize_scheme(scheme=None, default='//'):
    if scheme is None:
        scheme = default
    elif scheme.endswith(':'):
        scheme = '%s//' % scheme
    elif '//' not in scheme:
        scheme = '%s://' % scheme
    return scheme
