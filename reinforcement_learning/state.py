class State:
    def __init__(self):
        self.player_position = None
        self.platforms = None
        self.plat_num = None

    def get_current_state(self, player_position, platforms, plat_num, initial_state= False):
        self.player_position = player_position
        self.platforms = platforms
        self.plat_num = plat_num
        next_platforms = self.get_next_platforms(initial_state)
        distances = [self.calculate_distance(plat) for plat in next_platforms]
        return distances

    def get_next_platforms(self, initial_state):
        if initial_state:
            l_plat_raw = [((platform[1] - platform[0]) / 2, platform[2]) for platform in self.platforms]
            l_plat_sorted = sorted(l_plat_raw, key=lambda x: x[1], reverse=True)
            l_plat = l_plat_sorted[:3]
        else:
            l_plat_raw = [((platform[1] - platform[0])/2, platform[2]) for platform in self.platforms if platform[1] < self.platforms[self.plat_num][2]]
            l_plat_sorted = sorted(l_plat_raw, key=lambda x: x[1], reverse=True)
            l_plat = l_plat_sorted[:3]

        return l_plat

    def calculate_distance(self, plat_coord):
        x1, y1 = self.player_position
        x2, y2 = plat_coord
        euc_dist = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
        return euc_dist
