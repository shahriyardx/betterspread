"""
Tests for betterspread.utils

Only covers what betterspread adds:
  - get_location  : the fixed AZ / ZZ / AAA+ edge cases
  - parse_cell_name  : new helper
  - col_label_to_index : new helper
  - run_in_executor  : new async wrapper
"""

import pytest

from betterspread.utils import (
    col_label_to_index,
    get_location,
    parse_cell_name,
    run_in_executor,
)

# ---------------------------------------------------------------------------
# get_location — focus on the cases that were broken before the rewrite
# ---------------------------------------------------------------------------


class TestGetLocation:
    def test_single_letter_first(self):
        assert get_location(1) == "A"

    def test_single_letter_last(self):
        assert get_location(26) == "Z"

    def test_first_double_letter(self):
        assert get_location(27) == "AA"

    def test_az_remainder_zero_case(self):
        # Column 52 has remainder 0 — the old ceil/modulo code returned
        # the wrong letter here due to Python's negative index wrapping.
        assert get_location(52) == "AZ"

    def test_bz_remainder_zero_case(self):
        assert get_location(78) == "BZ"

    def test_last_double_letter(self):
        assert get_location(702) == "ZZ"

    def test_first_triple_letter(self):
        # Anything above 702 caused an IndexError before the rewrite.
        assert get_location(703) == "AAA"

    def test_large_triple_letter(self):
        assert get_location(18278) == "ZZZ"

    def test_zero_raises(self):
        with pytest.raises(ValueError):
            get_location(0)

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            get_location(-1)

    def test_output_is_always_uppercase(self):
        for n in range(1, 100):
            assert get_location(n).isupper()

    def test_all_values_unique(self):
        labels = [get_location(n) for n in range(1, 730)]
        assert len(labels) == len(set(labels))


# ---------------------------------------------------------------------------
# parse_cell_name — new helper: "AA15" → ("AA", 15)
# ---------------------------------------------------------------------------


class TestParseCellName:
    def test_simple(self):
        assert parse_cell_name("A1") == ("A", 1)

    def test_multi_letter_column(self):
        assert parse_cell_name("AA15") == ("AA", 15)

    def test_triple_letter_column(self):
        assert parse_cell_name("AAA1") == ("AAA", 1)

    def test_lowercase_normalised_to_upper(self):
        assert parse_cell_name("b3") == ("B", 3)

    def test_mixed_case_normalised(self):
        assert parse_cell_name("aB10") == ("AB", 10)

    def test_multi_digit_row(self):
        assert parse_cell_name("A1000") == ("A", 1000)

    def test_leading_whitespace_stripped(self):
        assert parse_cell_name("  C7  ") == ("C", 7)

    def test_digits_first_raises(self):
        with pytest.raises(ValueError):
            parse_cell_name("1A")

    def test_letters_only_raises(self):
        with pytest.raises(ValueError):
            parse_cell_name("ABC")

    def test_digits_only_raises(self):
        with pytest.raises(ValueError):
            parse_cell_name("123")

    def test_empty_string_raises(self):
        with pytest.raises(ValueError):
            parse_cell_name("")

    def test_range_notation_raises(self):
        with pytest.raises(ValueError):
            parse_cell_name("A1:B2")


# ---------------------------------------------------------------------------
# col_label_to_index — new helper: "A" → 0, "AA" → 26
# ---------------------------------------------------------------------------


class TestColLabelToIndex:
    def test_a_is_zero(self):
        assert col_label_to_index("A") == 0

    def test_z_is_25(self):
        assert col_label_to_index("Z") == 25

    def test_aa_is_26(self):
        assert col_label_to_index("AA") == 26

    def test_az_is_51(self):
        assert col_label_to_index("AZ") == 51

    def test_ba_is_52(self):
        assert col_label_to_index("BA") == 52

    def test_zz_is_701(self):
        assert col_label_to_index("ZZ") == 701

    def test_aaa_is_702(self):
        assert col_label_to_index("AAA") == 702

    def test_lowercase_normalised(self):
        assert col_label_to_index("a") == col_label_to_index("A")
        assert col_label_to_index("aa") == col_label_to_index("AA")

    def test_roundtrip_with_get_location(self):
        """col_label_to_index(get_location(n)) must equal n - 1 for all n."""
        for n in range(1, 730):
            label = get_location(n)
            assert col_label_to_index(label) == n - 1


# ---------------------------------------------------------------------------
# run_in_executor — runs a blocking callable on the thread pool
# ---------------------------------------------------------------------------


class TestRunInExecutor:
    async def test_runs_sync_function(self):
        result = await run_in_executor(lambda: 42)
        assert result == 42

    async def test_passes_positional_args(self):
        result = await run_in_executor(lambda x, y: x + y, 3, 4)
        assert result == 7

    async def test_passes_keyword_args(self):
        result = await run_in_executor(lambda x=0: x * 2, x=5)
        assert result == 10

    async def test_propagates_exception(self):
        def boom():
            raise ValueError("from thread")

        with pytest.raises(ValueError, match="from thread"):
            await run_in_executor(boom)
