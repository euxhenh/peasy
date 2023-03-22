from collections import UserList

import seaborn as sns


class Palette(UserList):
    """A modified palette that repeats colors if we run out.
    Also better supports extending, appending, etc.
    """

    def __init__(self, pal):
        if isinstance(pal, str):
            pal = sns.color_palette(pal).as_hex()
        super().__init__(str(item) for item in pal)

    def __getitem__(self, i):
        return self.data[i % len(self)]
