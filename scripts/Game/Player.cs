namespace UltimaLikeRoguelike.Game;

public enum Direction
{
    North,
    South,
    East,
    West,
}

/// <summary>
/// Player state. Pure data; all mutation happens in <see cref="Main"/>.
/// </summary>
public sealed class Player
{
    public int X { get; set; }
    public int Y { get; set; }
    public Direction Facing { get; set; } = Direction.South;

    public int TileId => Facing switch
    {
        Direction.North => Core.TileId.PlayerNorth,
        Direction.East  => Core.TileId.PlayerEast,
        Direction.West  => Core.TileId.PlayerWest,
        _               => Core.TileId.PlayerSouth,
    };
}
