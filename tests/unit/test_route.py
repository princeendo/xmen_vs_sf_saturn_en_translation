from __future__ import annotations

import pytest

from tools.mednafen.route import (
    APOCALYPSE,
    CPU,
    FIRST_START,
    KNOCKOUT_STEPS,
    PLAYER,
    SECOND_START,
    TAG_EVERY,
    Route,
    byte_ranges,
    fixups_match,
    grid_moves,
)


def test_grid_moves_match_the_exp0032_picks() -> None:
    # EXP-0032 picked from Ken with these strings (pick_roster.py runs)
    expected = {
        0: "lll",
        1: "ll",
        2: "uull",
        3: "ull",
        4: "ulll",
        5: "uulll",
        6: "uuull",
        7: "uuulll",
        16: "u",
    }
    for slot, moves in expected.items():
        assert grid_moves(slot, FIRST_START) == moves


def test_second_cursor_moves_start_on_cyclops() -> None:
    assert grid_moves(1, SECOND_START) == ""
    assert grid_moves(9, SECOND_START) == "r"
    assert grid_moves(16, SECOND_START) == "urr"


def test_off_grid_slot_is_refused() -> None:
    with pytest.raises(ValueError, match="not on the select grid"):
        grid_moves(15, FIRST_START)


def chars(player: tuple[int, int], cpu: tuple[int, int]) -> dict[int, int]:
    return {
        PLAYER[0]: 2 * player[0],
        PLAYER[1]: 2 * player[1],
        CPU[0]: 2 * cpu[0],
        CPU[1]: 2 * cpu[1],
    }


FULL = {block: 144 for block in (*PLAYER, *CPU)}


def test_first_policy_always_zeroes_the_cpu_side() -> None:
    route = Route(16, 9, "first")
    assert route.targets(chars((16, 9), (1, 4)), FULL) == list(CPU)
    assert route.targets(chars((16, 9), (APOCALYPSE, APOCALYPSE)), FULL) == list(CPU)
    assert route.phase == "boss"
    assert route.targets(chars((16, 9), (9, 9)), FULL) == list(CPU)
    assert route.phase == "partner"


def test_second_policy_knocks_out_the_first_pick_until_the_partner_is_active() -> None:
    route = Route(16, 9, "second")
    partner_active = chars((9, 16), (APOCALYPSE, APOCALYPSE))
    first_active = chars((16, 9), (APOCALYPSE, APOCALYPSE))
    # during the boss's dialogue the partner may already be in the active block
    assert route.targets(partner_active, FULL) == [PLAYER[1]]
    for _ in range(3):
        assert route.targets(first_active, FULL) == [PLAYER[0]]
    assert route.targets(partner_active, FULL) == list(CPU)
    assert route.first_out


def test_second_policy_gives_up_after_the_cap() -> None:
    route = Route(16, 9, "second")
    first_active = chars((16, 9), (APOCALYPSE, APOCALYPSE))
    for _ in range(KNOCKOUT_STEPS):
        assert route.targets(first_active, FULL) == [PLAYER[0]]
    assert route.targets(first_active, FULL) == list(CPU)


def test_cpu_final_policy_zeroes_the_player_in_the_partner_fight_only() -> None:
    route = Route(16, 9, "cpu_final")
    assert route.targets(chars((16, 9), (16, 9)), FULL) == list(CPU)
    assert route.phase == "stages"  # a team member on the CPU side before the boss
    route.targets(chars((16, 9), (APOCALYPSE, APOCALYPSE)), FULL)
    assert route.targets(chars((16, 9), (9, 9)), FULL) == list(PLAYER)


def test_unknown_policy_is_refused() -> None:
    with pytest.raises(ValueError, match="unknown policy"):
        Route(0, 1, "both")


def test_fixups_match_accepts_relocated_longs_only() -> None:
    decoded = bytes.fromhex("0000000100000002aabb")
    delta = 0x0024D040
    relocated = (1 + delta).to_bytes(4, "big") + decoded[4:]
    assert fixups_match(decoded, relocated, delta)
    assert fixups_match(decoded, decoded, delta)
    assert not fixups_match(decoded, decoded[:-1] + b"\x00", delta)


def test_tag_policy_tags_until_the_partner_is_active() -> None:
    route = Route(16, 9, "tag")
    first_active = chars((16, 9), (APOCALYPSE, APOCALYPSE))
    assert route.targets(first_active, FULL) == []
    assert route.tag_request
    for _ in range(TAG_EVERY - 1):
        assert route.targets(first_active, FULL) == []
        assert not route.tag_request
    assert route.targets(first_active, FULL) == []
    assert route.tag_request
    assert route.targets(chars((9, 16), (APOCALYPSE, APOCALYPSE)), FULL) == list(CPU)
    assert route.first_out


def test_byte_ranges_lists_each_run_of_differences() -> None:
    old = bytes.fromhex("00112233445566")
    new = bytes.fromhex("0011ff33ffff66")
    assert byte_ranges(old, new) == [
        (2, b"\x22", b"\xff"),
        (4, b"\x44\x55", b"\xff\xff"),
    ]
    with pytest.raises(ValueError, match="lengths differ"):
        byte_ranges(old, new[:-1])
