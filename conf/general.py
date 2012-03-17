from util import dice as _dice

class game:
    # The game ends in failure after this number of rounds has passed without
    # the final dungeon being cleared.
    doom = 30

class dungeon_base:
    # These stats are added to every dungeon's individual stats.
    
    # The danger/mystery at the first level of the dungeon.
    danger_start  = 1
    mystery_start = 1
    
    # Danger/mystery will always increase by these values at each level, in
    # addition to the effect of random_step.
    danger_step   = 0
    mystery_step  = 0
    
    # By some randomly chosen increase/decrease in danger and/or mystery, the
    # total danger and mystery will increase by this amount at each level.
    random_step   = 1

class dungeon_sizes:
    # The number of levels in a dungeon of each size.
    small  = 8
    medium = 16
    large  = 24
    huge   = 32

class hero:    
    # Functions mapping skill values to damage, where damage equal or greater
    # than a dungeon's stat will defeat that level of the dungeon.
    fight_damage = lambda skill: _dice(3, 6) - 10 + skill
    lore_damage  = lambda skill: _dice(3, 6) - 10 + skill

    # Experience points needed to increment a stat.
    fight_xp_level = 3
    lore_xp_level  = 3
    
    # The starting XP for each stat; divided by xp_level gives starting stats.
    fight_xp_start = 3
    lore_xp_start  = 3
    
    # XP gained from a turn spent training.
    fight_xp_train = 3
    lore_xp_train  = 3
    
    # XP gained when succeeding/failing against a dungeon level with
    # respectively lower, equal or higher difficulty than the hero's skill.
    fight_xp_win  = 0, 1, 2
    fight_xp_lose = 0, 1, 1
    lore_xp_win   = 0, 1, 1
    lore_xp_lose  = 2, 1, 1
