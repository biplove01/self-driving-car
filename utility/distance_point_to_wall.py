import pygame

def distance_point_to_wall(point, wall_start, wall_end):
    """
    Returns the shortest distance from `point` to the line segment (wall_start, wall_end).
    Also returns the closest point on the segment.
    """
    p = pygame.Vector2(point)
    a = pygame.Vector2(wall_start)
    b = pygame.Vector2(wall_end)

    ab = b - a
    ap = p - a

    proj = ap.dot(ab)
    ab_len_sq = ab.length_squared()

    if ab_len_sq == 0:
        # Segment is a point
        return p.distance_to(a), a

    t = max(0, min(1, proj / ab_len_sq))
    closest = a + t * ab
    distance = p.distance_to(closest)

    return distance, closest
