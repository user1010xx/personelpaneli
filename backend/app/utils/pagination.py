def normalize_pagination(skip: int = 0, limit: int = 100, max_limit: int = 1000):
    return max(skip or 0, 0), min(max(limit or 100, 1), max_limit)