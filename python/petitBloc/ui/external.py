try:
    import Qt
except:
    import sys
    import os

    sys.path.append(os.path.abspath(os.path.join(__file__, "../external")))
    import Qt


try:
    import Nodz
except:
    import sys
    import os

    sys.path.append(os.path.abspath(os.path.join(__file__, "../external")))
    import Nodz
