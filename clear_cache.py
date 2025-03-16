from joblib import Memory

memory = Memory(location="D:/Darshan's Projects/The pair trading/cachedir", verbose=0)

memory.clear(warn=False)  # to clear cache