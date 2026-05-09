using System;
using System.Collections.Generic;
using Godot;
using UltimaLikeRoguelike.Core;
using UltimaLikeRoguelike.Generation;
using UltimaLikeRoguelike.View;

namespace UltimaLikeRoguelike.Game;

/// <summary>
/// Top-level scene controller. Owns the world generation results and all
/// derived maps, the player, the renderer, and the UI. Routes input into
/// movement and transitions.
/// </summary>
public partial class Main : Node2D
{
	// Layout constants -- tuned for the 180x320 portrait viewport.
	private const int ViewportW = 180;
	private const int ViewportH = 320;
	private const int StatusBarH = 32;
	private const int MapAreaY = StatusBarH;
	private const int MapAreaW = MapRenderer.ViewTilesX * MapRenderer.TileSize; // 176
	private const int MapAreaX = (ViewportW - MapAreaW) / 2;                    // 2
	private const int DpadAreaY = ViewportH - 64;

	private readonly Dictionary<string, MapData> _maps = new();
	private MapData? _currentMap;
	private Player _player = new();
	private MapRenderer _renderer = null!;
	private Label _statusLabel = null!;

	public override void _Ready()
	{
		// Allow WASD as well as arrow keys.
		AddKeyBinding("ui_up", Key.W);
		AddKeyBinding("ui_down", Key.S);
		AddKeyBinding("ui_left", Key.A);
		AddKeyBinding("ui_right", Key.D);

		BuildWorld();
		BuildScene();

		ChangeMap("world", _maps["world"].EntryX, _maps["world"].EntryY);
	}

	// --- world construction --------------------------------------------

	private void BuildWorld()
	{
		int seed = (int)((long)Time.GetUnixTimeFromSystem() & 0x7fffffff);
		GD.Print($"[world] seed = {seed}");

		var world = WorldGenerator.Generate(seed);
		_maps[world.Map.Id] = world.Map;

		// Towns
		foreach (var (wx, wy, mapId, biomeName) in world.Towns)
		{
			int townSeed = unchecked(seed + mapId.GetHashCode());
			var townResult = TownGenerator.Generate(mapId, townSeed, biomeName);
			var townMap = townResult.Map;
			townMap.ParentMapId = "world";
			townMap.ParentX = wx;
			townMap.ParentY = wy;

			// Wire the southern gate to actually go back to the world tile
			// just south of the town tile (a passable spot).
			int gateX = townMap.Width / 2;
			int gateY = townMap.Height - 1;
			int landY = Math.Min(world.Map.Height - 1, wy + 1);
			// Skip impassable landing (e.g. water): try a few alternatives.
			(int wlx, int wly) = FindWalkableNear(world.Map, wx, landY);
			townMap.Transitions[(gateX, gateY)] = new MapTransition("world", wlx, wly);

			_maps[mapId] = townMap;

			// Interiors for each building, themed to the same biome as
			// the town that contains them.
			foreach (var building in townResult.Buildings)
			{
				int interiorSeed = unchecked(townSeed + building.InteriorMapId.GetHashCode());
				var interior = InteriorGenerator.Generate(building.InteriorMapId, interiorSeed, biomeName);
				interior.ParentMapId = mapId;
				interior.ParentX = building.DoorX;
				interior.ParentY = building.DoorY;

				// Door at the south of the interior leads back to the
				// tile just south of the building's door on the town map.
				int idoorX = interior.Width / 2;
				int idoorY = interior.Height - 1;
				int backX = building.DoorX;
				int backY = Math.Min(townMap.Height - 1, building.DoorY + 1);
				interior.Transitions[(idoorX, idoorY)] = new MapTransition(mapId, backX, backY);

				_maps[building.InteriorMapId] = interior;
			}
		}

		// Dungeons
		foreach (var (wx, wy, mapId, _) in world.Dungeons)
		{
			int dSeed = unchecked(seed + mapId.GetHashCode());
			var dmap = DungeonGenerator.Generate(mapId, dSeed);
			dmap.ParentMapId = "world";
			dmap.ParentX = wx;
			dmap.ParentY = wy;

			// Stairs-up tile is at (EntryX, EntryY) per the generator.
			int sx = dmap.EntryX;
			int sy = dmap.EntryY;
			int landY = Math.Min(world.Map.Height - 1, wy + 1);
			(int wlx, int wly) = FindWalkableNear(world.Map, wx, landY);
			dmap.Transitions[(sx, sy)] = new MapTransition("world", wlx, wly);

			_maps[mapId] = dmap;
		}
	}

	private static (int X, int Y) FindWalkableNear(MapData map, int x, int y)
	{
		// Search in expanding rings for a passable tile.
		for (int r = 0; r < 5; r++)
		{
			for (int dy = -r; dy <= r; dy++)
			{
				for (int dx = -r; dx <= r; dx++)
				{
					int nx = x + dx;
					int ny = y + dy;
					if (!map.InBounds(nx, ny)) continue;
					if (TileDatabase.IsPassable(map.GetTile(nx, ny)))
						return (nx, ny);
				}
			}
		}
		return (x, y);
	}

	// --- scene tree ---------------------------------------------------

	private void BuildScene()
	{
		var atlas = GD.Load<Texture2D>("res://assets/tiles/atlas.png");
		var shader = GD.Load<Shader>("res://assets/shaders/palette_swap.gdshader");

		_renderer = new MapRenderer
		{
			Name = "MapRenderer",
			Atlas = atlas,
			PaletteShader = shader,
			Player = _player,
			Position = new Vector2(MapAreaX, MapAreaY),
		};
		AddChild(_renderer);

		var ui = new CanvasLayer { Name = "UI" };
		AddChild(ui);

		// Status label.
		_statusLabel = new Label
		{
			Name = "Status",
			Position = new Vector2(4, 4),
			Size = new Vector2(ViewportW - 8, StatusBarH - 8),
			Text = "",
			HorizontalAlignment = HorizontalAlignment.Center,
			VerticalAlignment = VerticalAlignment.Center,
		};
		_statusLabel.AddThemeColorOverride("font_color", new Color(1, 1, 1));
		ui.AddChild(_statusLabel);

		// D-pad.
		var dpad = new Control
		{
			Name = "DPad",
			Position = new Vector2(0, DpadAreaY),
			Size = new Vector2(ViewportW, 64),
		};
		ui.AddChild(dpad);

		// Layout: U on top centre, [L D R] underneath.
		const int btn = 32;
		int colCenter = (ViewportW - btn) / 2;
		int colLeft   = colCenter - btn;
		int colRight  = colCenter + btn;

		AddDpadButton(dpad, "↑", new Vector2(colCenter,  0),  Direction.North);
		AddDpadButton(dpad, "←", new Vector2(colLeft,   btn), Direction.West);
		AddDpadButton(dpad, "↓", new Vector2(colCenter, btn), Direction.South);
		AddDpadButton(dpad, "→", new Vector2(colRight,  btn), Direction.East);
	}

	private void AddDpadButton(Control parent, string text, Vector2 pos, Direction dir)
	{
		var b = new Button
		{
			Text = text,
			Position = pos,
			Size = new Vector2(32, 32),
			FocusMode = Control.FocusModeEnum.None,
		};
		b.Pressed += () => TryMove(dir);
		parent.AddChild(b);
	}

	private static void AddKeyBinding(string action, Key key)
	{
		var ev = new InputEventKey { Keycode = key };
		if (!InputMap.HasAction(action))
			InputMap.AddAction(action);
		InputMap.ActionAddEvent(action, ev);
	}

	// --- input --------------------------------------------------------

	public override void _UnhandledInput(InputEvent @event)
	{
		if (@event is not InputEventKey key || !key.Pressed || key.Echo) return;

		if (Input.IsActionPressed("ui_up"))    { TryMove(Direction.North); GetViewport().SetInputAsHandled(); }
		else if (Input.IsActionPressed("ui_down"))  { TryMove(Direction.South); GetViewport().SetInputAsHandled(); }
		else if (Input.IsActionPressed("ui_left"))  { TryMove(Direction.West);  GetViewport().SetInputAsHandled(); }
		else if (Input.IsActionPressed("ui_right")) { TryMove(Direction.East);  GetViewport().SetInputAsHandled(); }
	}

	// --- movement ----------------------------------------------------

	private void TryMove(Direction dir)
	{
		if (_currentMap == null) return;

		// Always update facing, even if movement is blocked -- this lets
		// players turn in place by attempting to move in a wall.
		_player.Facing = dir;

		var (dx, dy) = DirToDelta(dir);
		int nx = _player.X + dx;
		int ny = _player.Y + dy;

		if (!_currentMap.InBounds(nx, ny))
		{
			_renderer.QueueRedraw();
			return;
		}

		int nextTile = _currentMap.GetTile(nx, ny);
		if (!TileDatabase.IsPassable(nextTile))
		{
			_renderer.QueueRedraw();
			return;
		}

		_player.X = nx;
		_player.Y = ny;

		// Transition?
		if (_currentMap.Transitions.TryGetValue((nx, ny), out var transition))
		{
			ApplyTransition(transition);
			return;
		}

		_renderer.QueueRedraw();
	}

	private void ApplyTransition(MapTransition transition)
	{
		if (!_maps.TryGetValue(transition.TargetMapId, out var target))
		{
			GD.PushWarning($"transition target not found: {transition.TargetMapId}");
			_renderer.QueueRedraw();
			return;
		}

		int ex = transition.EntryX ?? target.EntryX;
		int ey = transition.EntryY ?? target.EntryY;
		ChangeMap(target.Id, ex, ey);
	}

	private void ChangeMap(string id, int x, int y)
	{
		_currentMap = _maps[id];
		_player.X = x;
		_player.Y = y;
		_renderer.SetMap(_currentMap);
		UpdateStatus();
	}

	private void UpdateStatus()
	{
		if (_currentMap == null) return;
		string label = _currentMap.Kind switch
		{
			MapKind.World    => "World",
			MapKind.Town     => $"Town ({IndexFromId(_currentMap.Id, "town:")})",
			MapKind.Dungeon  => $"Dungeon ({IndexFromId(_currentMap.Id, "dungeon:")})",
			MapKind.Interior => "Interior",
			_ => _currentMap.Id,
		};
		_statusLabel.Text = $"{label}  {_player.X},{_player.Y}";
	}

	private static string IndexFromId(string id, string prefix)
	{
		if (!id.StartsWith(prefix)) return id;
		var rest = id[prefix.Length..];
		int colon = rest.IndexOf(':');
		return colon < 0 ? rest : rest[..colon];
	}

	private static (int Dx, int Dy) DirToDelta(Direction d) => d switch
	{
		Direction.North => (0, -1),
		Direction.South => (0,  1),
		Direction.East  => (1,  0),
		Direction.West  => (-1, 0),
		_               => (0,  0),
	};
}
