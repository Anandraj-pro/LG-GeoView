"""Unit tests for src/data_loader.py."""

import io
import os
from unittest.mock import patch, MagicMock

import pandas as pd

from src.data_loader import (
    AREA_COORDINATES,
    assign_strength,
    get_area_summary,
    load_from_csv,
    load_from_excel,
    load_from_google_sheets,
    load_from_upload,
    _validate_and_clean,
)


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE_CSV = os.path.join(PROJECT_ROOT, "data", "sample_data.csv")


class TestLoadFromCSV:
    """Tests for load_from_csv."""

    @patch("src.data_loader.st")
    def test_load_from_csv_valid(self, mock_st):
        """Loading the bundled sample_data.csv should return rows with expected columns."""
        df = load_from_csv(SAMPLE_CSV)
        assert not df.empty
        assert len(df) == 20
        for col in ["area", "lg_group", "leader_name", "members", "latitude", "longitude"]:
            assert col in df.columns

    @patch("src.data_loader.st")
    def test_load_from_csv_exception(self, mock_st):
        """Exception during CSV read should return empty DataFrame."""
        df = load_from_csv("/nonexistent/path/to/file.csv")
        assert df.empty
        mock_st.error.assert_called_once()


class TestValidateAndClean:
    """Tests for _validate_and_clean."""

    @patch("src.data_loader.st")
    def test_validate_and_clean_missing_columns(self, mock_st):
        """A DataFrame missing required columns should return empty and call st.error."""
        df = pd.DataFrame({"area": ["A"], "lg_group": ["G1"]})
        result = _validate_and_clean(df)
        assert result.empty
        mock_st.error.assert_called_once()

    @patch("src.data_loader.st")
    def test_validate_and_clean_strips_whitespace(self, mock_st):
        """Column names with extra spaces should be normalized."""
        df = pd.DataFrame({
            " Area ": ["Kukatpally"],
            " LG_Group ": ["LG1"],
            " Leader_Name ": ["Ravi"],
            " Members ": [10],
            " Latitude ": [17.49],
            " Longitude ": [78.40],
        })
        result = _validate_and_clean(df)
        assert not result.empty
        assert "area" in result.columns
        assert "lg_group" in result.columns
        assert "leader_name" in result.columns


class TestAssignStrength:
    """Tests for assign_strength."""

    def test_assign_strength_boundaries(self, sample_df):
        """Verify boundary values: <20 Weak, 20-29 Medium, >=30 Strong."""
        df = pd.DataFrame({
            "members": [19, 20, 29, 30],
            "area": ["A"] * 4,
            "lg_group": ["G1", "G2", "G3", "G4"],
        })
        result = assign_strength(df)
        assert result.iloc[0]["strength"] == "Weak"
        assert result.iloc[1]["strength"] == "Medium"
        assert result.iloc[2]["strength"] == "Medium"
        assert result.iloc[3]["strength"] == "Strong"

    def test_assign_strength_zero(self):
        """members=0 should be categorized as Weak."""
        df = pd.DataFrame({"members": [0], "area": ["A"], "lg_group": ["G1"]})
        result = assign_strength(df)
        assert result.iloc[0]["strength"] == "Weak"


class TestGetAreaSummary:
    """Tests for get_area_summary."""

    def test_get_area_summary(self, sample_df):
        """Verify groupby produces correct aggregation counts."""
        summary = get_area_summary(sample_df)
        assert not summary.empty
        # sample_df has 3 areas: Kukatpally, Kondapur, KPHB
        assert len(summary) == 3
        assert "total_groups" in summary.columns
        assert "total_members" in summary.columns
        assert "strength" in summary.columns

        kuk = summary[summary["area"] == "Kukatpally"].iloc[0]
        assert kuk["total_groups"] == 2
        assert kuk["total_members"] == 42  # 12 + 30

    def test_get_area_summary_empty(self, empty_df):
        """Empty DataFrame should produce an empty summary."""
        empty = pd.DataFrame(columns=[
            "area", "lg_group", "leader_name", "families", "individuals",
            "members", "meeting_day", "latitude", "longitude",
        ])
        summary = get_area_summary(empty)
        assert summary.empty


class TestAreaCoordinates:
    """Tests for AREA_COORDINATES constant."""

    def test_area_coordinates_exist(self):
        """AREA_COORDINATES should have entries with valid lat/lng tuples."""
        assert len(AREA_COORDINATES) > 0
        for area, coords in AREA_COORDINATES.items():
            assert isinstance(coords, tuple), f"{area} coords is not a tuple"
            assert len(coords) == 2, f"{area} coords does not have 2 elements"
            lat, lng = coords
            assert isinstance(lat, (int, float)), f"{area} lat is not numeric"
            assert isinstance(lng, (int, float)), f"{area} lng is not numeric"


# ---------------------------------------------------------------------------
# New tests: load_from_excel
# ---------------------------------------------------------------------------


class TestLoadFromExcel:
    """Tests for load_from_excel."""

    @patch("src.data_loader.st")
    @patch("src.data_loader.pd.read_excel")
    def test_load_from_excel_valid(self, mock_read_excel, mock_st):
        """Test loading valid Excel data with standard columns."""
        mock_data = pd.DataFrame({
            ",leader_name,": ["Ravi Kumar", "Suresh Reddy"],
            "area": ["Kukatpally", "KPHB"],
            "Families ": [5, 8],
            "Individuals ": [7, 12],
            "Total": [12, 20],
            "Sync meeting on": ["Sunday", "Saturday"],
            "Care Coordinator": ["Coord1", "Coord2"],
        })
        mock_read_excel.return_value = mock_data
        df = load_from_excel("fake.xlsx")
        assert len(df) == 2

    @patch("src.data_loader.st")
    @patch("src.data_loader.pd.read_excel")
    def test_load_from_excel_shifted_columns(self, mock_read_excel, mock_st):
        """Test the shifted column handling."""
        mock_data = pd.DataFrame({
            ",leader_name,": [None, None],
            "area": ["Leader Name1", "Leader Name2"],
            "Families ": [3, 6],
            "Individuals ": [4, 5],
            "Total": [7, 11],
            "Sync meeting on": ["Wed", "Thu"],
            "Care Coordinator": ["kukatpally", "kphb"],
        })
        mock_read_excel.return_value = mock_data
        df = load_from_excel("fake.xlsx")
        assert not df.empty

    @patch("src.data_loader.st")
    @patch("src.data_loader.pd.read_excel")
    def test_load_from_excel_skips_total_rows(self, mock_read_excel, mock_st):
        """Rows with leader 'Total' should be skipped."""
        mock_data = pd.DataFrame({
            ",leader_name,": ["Ravi Kumar", "Total"],
            "area": ["Kukatpally", ""],
            "Families ": [5, 100],
            "Individuals ": [7, 200],
            "Total": [12, 300],
            "Sync meeting on": ["Sunday", ""],
            "Care Coordinator": ["Coord1", ""],
        })
        mock_read_excel.return_value = mock_data
        df = load_from_excel("fake.xlsx")
        assert len(df) == 1

    @patch("src.data_loader.st")
    @patch("src.data_loader.pd.read_excel")
    def test_load_from_excel_missing_coordinates(self, mock_read_excel, mock_st):
        """Areas not in AREA_COORDINATES should be dropped with a warning."""
        mock_data = pd.DataFrame({
            ",leader_name,": ["Leader1"],
            "area": ["UnknownArea"],
            "Families ": [5],
            "Individuals ": [7],
            "Total": [12],
            "Sync meeting on": ["Sunday"],
            "Care Coordinator": ["Coord1"],
        })
        mock_read_excel.return_value = mock_data
        df = load_from_excel("fake.xlsx")
        assert df.empty
        mock_st.warning.assert_called_once()

    @patch("src.data_loader.st")
    @patch("src.data_loader.pd.read_excel")
    def test_load_from_excel_exception(self, mock_read_excel, mock_st):
        """Exception during Excel read should return empty DataFrame."""
        mock_read_excel.side_effect = FileNotFoundError("File not found")
        df = load_from_excel("nonexistent.xlsx")
        assert df.empty
        mock_st.error.assert_called_once()

    @patch("src.data_loader.st")
    @patch("src.data_loader.pd.read_excel")
    def test_load_from_excel_empty_rows_skipped(self, mock_read_excel, mock_st):
        """Rows where both leader_name and area are empty should be skipped."""
        mock_data = pd.DataFrame({
            ",leader_name,": [None, "Ravi"],
            "area": [None, "Kukatpally"],
            "Families ": [0, 5],
            "Individuals ": [0, 7],
            "Total": [0, 12],
            "Sync meeting on": ["", "Sun"],
            "Care Coordinator": [None, "C1"],
        })
        mock_read_excel.return_value = mock_data
        df = load_from_excel("fake.xlsx")
        assert len(df) == 1


# ---------------------------------------------------------------------------
# New tests: load_from_google_sheets
# ---------------------------------------------------------------------------


class TestLoadFromGoogleSheets:
    """Tests for load_from_google_sheets."""

    @patch("src.data_loader.st")
    @patch("requests.get")
    def test_google_sheets_edit_url(self, mock_get, mock_st):
        """URL with /edit should be converted to /export?format=csv."""
        csv_text = (
            "area,lg_group,leader_name,members,latitude,longitude\n"
            "Kukatpally,LG1,Ravi,10,17.49,78.40"
        )
        mock_resp = MagicMock()
        mock_resp.text = csv_text
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp
        df = load_from_google_sheets(
            "https://docs.google.com/spreadsheets/d/xxx/edit"
        )
        mock_get.assert_called_once_with(
            "https://docs.google.com/spreadsheets/d/xxx/export?format=csv",
            timeout=10,
        )
        assert not df.empty

    @patch("src.data_loader.st")
    @patch("requests.get")
    def test_google_sheets_pub_url(self, mock_get, mock_st):
        """URL with /pub should be used as-is."""
        csv_text = (
            "area,lg_group,leader_name,members,latitude,longitude\n"
            "Kukatpally,LG1,Ravi,10,17.49,78.40"
        )
        mock_resp = MagicMock()
        mock_resp.text = csv_text
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp
        load_from_google_sheets(
            "https://docs.google.com/spreadsheets/d/xxx/pub"
        )
        mock_get.assert_called_once_with(
            "https://docs.google.com/spreadsheets/d/xxx/pub",
            timeout=10,
        )

    @patch("src.data_loader.st")
    @patch("requests.get")
    def test_google_sheets_plain_url(self, mock_get, mock_st):
        """URL without /edit or /pub should get /export?format=csv appended."""
        csv_text = (
            "area,lg_group,leader_name,members,latitude,longitude\n"
            "Kukatpally,LG1,Ravi,10,17.49,78.40"
        )
        mock_resp = MagicMock()
        mock_resp.text = csv_text
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp
        load_from_google_sheets(
            "https://docs.google.com/spreadsheets/d/xxx"
        )
        mock_get.assert_called_once_with(
            "https://docs.google.com/spreadsheets/d/xxx/export?format=csv",
            timeout=10,
        )

    @patch("src.data_loader.st")
    @patch("requests.get")
    def test_google_sheets_exception(self, mock_get, mock_st):
        """Network error should return empty DataFrame."""
        mock_get.side_effect = Exception("Connection timeout")
        df = load_from_google_sheets(
            "https://docs.google.com/spreadsheets/d/xxx/edit"
        )
        assert df.empty
        mock_st.error.assert_called_once()


# ---------------------------------------------------------------------------
# New tests: load_from_upload
# ---------------------------------------------------------------------------


class TestLoadFromUpload:
    """Tests for load_from_upload."""

    @patch("src.data_loader.st")
    def test_load_from_upload_csv(self, mock_st):
        """Uploading a CSV file should parse correctly."""
        csv_content = (
            "area,lg_group,leader_name,members,latitude,longitude\n"
            "Kukatpally,LG1,Ravi,10,17.49,78.40"
        )
        uploaded = io.BytesIO(csv_content.encode())
        uploaded.name = "test.csv"
        df = load_from_upload(uploaded)
        assert not df.empty
        assert len(df) == 1

    @patch("src.data_loader.st")
    @patch("src.data_loader.pd.read_excel")
    def test_load_from_upload_excel(self, mock_read_excel, mock_st):
        """Uploading an Excel file should use pd.read_excel."""
        mock_read_excel.return_value = pd.DataFrame({
            "area": ["Kukatpally"], "lg_group": ["LG1"],
            "leader_name": ["Ravi"], "members": [10],
            "latitude": [17.49], "longitude": [78.40],
        })
        uploaded = io.BytesIO(b"fake excel content")
        uploaded.name = "test.xlsx"
        df = load_from_upload(uploaded)
        assert not df.empty

    @patch("src.data_loader.st")
    def test_load_from_upload_exception(self, mock_st):
        """Exception during upload read should return empty DataFrame."""
        uploaded = MagicMock()
        uploaded.name = "test.xlsx"
        with patch("src.data_loader.pd.read_excel", side_effect=Exception("Bad file")):
            df = load_from_upload(uploaded)
            assert df.empty
            mock_st.error.assert_called_once()


# ---------------------------------------------------------------------------
# New tests: _validate_and_clean edge cases
# ---------------------------------------------------------------------------


class TestValidateAndCleanEdgeCases:
    """Edge-case tests for _validate_and_clean."""

    @patch("src.data_loader.st")
    def test_validate_adds_missing_optional_columns(self, mock_st):
        """families, individuals, meeting_day should be added if missing."""
        df = pd.DataFrame({
            "area": ["Kukatpally"], "lg_group": ["LG1"],
            "leader_name": ["Ravi"], "members": [10],
            "latitude": [17.49], "longitude": [78.40],
        })
        result = _validate_and_clean(df)
        assert "families" in result.columns
        assert "individuals" in result.columns
        assert "meeting_day" in result.columns

    @patch("src.data_loader.st")
    def test_validate_coerces_members_to_int(self, mock_st):
        """Non-numeric members should be coerced to 0."""
        df = pd.DataFrame({
            "area": ["Kukatpally"], "lg_group": ["LG1"],
            "leader_name": ["Ravi"], "members": ["abc"],
            "latitude": [17.49], "longitude": [78.40],
        })
        result = _validate_and_clean(df)
        assert result.iloc[0]["members"] == 0

    @patch("src.data_loader.st")
    def test_validate_drops_invalid_coordinates(self, mock_st):
        """Rows with NaN latitude/longitude should be dropped."""
        df = pd.DataFrame({
            "area": ["A", "B"], "lg_group": ["G1", "G2"],
            "leader_name": ["L1", "L2"], "members": [10, 20],
            "latitude": [17.49, None], "longitude": [78.40, None],
        })
        result = _validate_and_clean(df)
        assert len(result) == 1

    @patch("src.data_loader.st")
    def test_validate_all_nan_coordinates_returns_empty(self, mock_st):
        """All rows with NaN coordinates should result in empty DataFrame."""
        df = pd.DataFrame({
            "area": ["A", "B"], "lg_group": ["G1", "G2"],
            "leader_name": ["L1", "L2"], "members": [10, 20],
            "latitude": [None, None], "longitude": [None, None],
        })
        result = _validate_and_clean(df)
        assert result.empty

    @patch("src.data_loader.st")
    def test_validate_whitespace_in_area_names(self, mock_st):
        """Area names with whitespace should be stripped."""
        df = pd.DataFrame({
            "area": ["  Kukatpally  "], "lg_group": ["  LG1  "],
            "leader_name": ["Ravi"], "members": [10],
            "latitude": [17.49], "longitude": [78.40],
        })
        result = _validate_and_clean(df)
        assert result.iloc[0]["area"] == "Kukatpally"
        assert result.iloc[0]["lg_group"] == "LG1"

    @patch("src.data_loader.st")
    def test_validate_non_numeric_coordinates(self, mock_st):
        """Non-numeric lat/lng should be coerced to NaN and row dropped."""
        df = pd.DataFrame({
            "area": ["A"], "lg_group": ["G1"],
            "leader_name": ["L1"], "members": [10],
            "latitude": ["not_a_number"], "longitude": ["also_not"],
        })
        result = _validate_and_clean(df)
        assert result.empty


# ---------------------------------------------------------------------------
# New tests: Google Sheets URL validation (S1.4)
# ---------------------------------------------------------------------------


class TestGoogleSheetsURLValidation:
    """Tests for Google Sheets URL validation."""

    @patch("src.data_loader.st")
    def test_google_sheets_empty_url(self, mock_st):
        """Empty URL should return empty DataFrame."""
        result = load_from_google_sheets("")
        assert result.empty
        mock_st.error.assert_called()

    @patch("src.data_loader.st")
    def test_google_sheets_none_url(self, mock_st):
        """None URL should return empty DataFrame."""
        result = load_from_google_sheets(None)
        assert result.empty
        mock_st.error.assert_called()

    @patch("src.data_loader.st")
    def test_google_sheets_invalid_url(self, mock_st):
        """Non-Google Sheets URL should be rejected."""
        df = load_from_google_sheets("https://example.com/data.csv")
        assert df.empty
        mock_st.error.assert_called()

    @patch("src.data_loader.st")
    def test_google_sheets_non_string_url(self, mock_st):
        """Non-string URL should return empty DataFrame."""
        df = load_from_google_sheets(12345)
        assert df.empty
        mock_st.error.assert_called()


# ---------------------------------------------------------------------------
# New tests: validate_data_quality
# ---------------------------------------------------------------------------


class TestValidateDataQuality:
    """Tests for validate_data_quality."""

    def test_empty_df_returns_no_warnings(self):
        """Empty DataFrame should return no warnings."""
        from src.data_loader import validate_data_quality
        df = pd.DataFrame(columns=["area", "lg_group", "leader_name", "members"])
        result_df, warnings = validate_data_quality(df)
        assert result_df.empty
        assert warnings == []

    def test_detects_duplicates(self):
        """Duplicate (leader_name, area) pairs should trigger a warning."""
        from src.data_loader import validate_data_quality
        df = pd.DataFrame({
            "leader_name": ["Ravi", "Ravi", "Suresh"],
            "area": ["Kukatpally", "Kukatpally", "KPHB"],
            "members": [10, 10, 20],
        })
        _, warnings = validate_data_quality(df)
        assert any("Duplicate" in w for w in warnings)

    def test_detects_zero_members(self):
        """Groups with 0 members should trigger a warning."""
        from src.data_loader import validate_data_quality
        df = pd.DataFrame({
            "leader_name": ["Ravi"],
            "area": ["Kukatpally"],
            "members": [0],
        })
        _, warnings = validate_data_quality(df)
        assert any("0 or fewer" in w for w in warnings)

    def test_detects_high_members(self):
        """Groups with >200 members should trigger a warning."""
        from src.data_loader import validate_data_quality
        df = pd.DataFrame({
            "leader_name": ["Ravi"],
            "area": ["Kukatpally"],
            "members": [250],
        })
        _, warnings = validate_data_quality(df)
        assert any(">200" in w for w in warnings)

    def test_detects_missing_leader_names(self):
        """Groups with empty leader names should trigger a warning."""
        from src.data_loader import validate_data_quality
        df = pd.DataFrame({
            "leader_name": ["", "  "],
            "area": ["A", "B"],
            "members": [10, 20],
        })
        _, warnings = validate_data_quality(df)
        assert any("no leader name" in w for w in warnings)

    def test_no_warnings_for_clean_data(self, sample_df):
        """Clean data should return no warnings."""
        from src.data_loader import validate_data_quality
        _, warnings = validate_data_quality(sample_df)
        assert warnings == []


# ---------------------------------------------------------------------------
# New tests: _normalize_excel_columns
# ---------------------------------------------------------------------------


class TestNormalizeExcelColumns:
    """Tests for _normalize_excel_columns."""

    def test_strips_whitespace_and_lowercases(self):
        """Column names should be stripped and lowercased."""
        from src.data_loader import _normalize_excel_columns
        df = pd.DataFrame({" Leader_Name ": [1], " AREA ": [2]})
        result = _normalize_excel_columns(df)
        assert "leader_name" in result.columns
        assert "area" in result.columns

    def test_maps_comma_wrapped_leader_name(self):
        """',leader_name,' should map to 'leader_name'."""
        from src.data_loader import _normalize_excel_columns
        df = pd.DataFrame({",leader_name,": [1]})
        result = _normalize_excel_columns(df)
        assert "leader_name" in result.columns

    def test_maps_care_coordinator(self):
        """'Care Coordinator' should map to 'care_coordinator'."""
        from src.data_loader import _normalize_excel_columns
        df = pd.DataFrame({"Care Coordinator": [1]})
        result = _normalize_excel_columns(df)
        assert "care_coordinator" in result.columns

    def test_maps_sync_meeting_on(self):
        """'Sync meeting on' should map to 'meeting_day'."""
        from src.data_loader import _normalize_excel_columns
        df = pd.DataFrame({"Sync meeting on": [1]})
        result = _normalize_excel_columns(df)
        assert "meeting_day" in result.columns

    def test_fuzzy_match_substring(self):
        """Unmapped column containing a known key should fuzzy match."""
        from src.data_loader import _normalize_excel_columns
        df = pd.DataFrame({"the families count": [1]})
        result = _normalize_excel_columns(df)
        assert "families" in result.columns


# ---------------------------------------------------------------------------
# New tests: _load_area_coordinates
# ---------------------------------------------------------------------------


class TestLoadAreaCoordinates:
    """Tests for _load_area_coordinates."""

    def test_fallback_to_hardcoded(self):
        """When config file is missing, should fall back to hardcoded coords."""
        from src.data_loader import _load_area_coordinates, _HARDCODED_COORDINATES
        with patch("builtins.open", side_effect=FileNotFoundError("not found")):
            coords = _load_area_coordinates()
            assert coords == _HARDCODED_COORDINATES

    def test_loads_from_json(self, tmp_path):
        """Should load coordinates from a valid JSON file."""
        import json
        from src.data_loader import _load_area_coordinates
        config = {"test_area": [17.5, 78.4]}
        config_file = tmp_path / "area_coordinates.json"
        config_file.write_text(json.dumps(config))

        with patch("src.data_loader.os.path.join", return_value=str(config_file)):
            coords = _load_area_coordinates()
            assert "test_area" in coords
            assert coords["test_area"] == (17.5, 78.4)

    def test_invalid_json_falls_back(self, tmp_path):
        """Invalid JSON should fall back to hardcoded coords."""
        from src.data_loader import _load_area_coordinates, _HARDCODED_COORDINATES
        config_file = tmp_path / "area_coordinates.json"
        config_file.write_text("not valid json{{{")

        with patch("src.data_loader.os.path.join", return_value=str(config_file)):
            coords = _load_area_coordinates()
            assert coords == _HARDCODED_COORDINATES


# ---------------------------------------------------------------------------
# New tests: get_area_summary edge cases
# ---------------------------------------------------------------------------


class TestGetAreaSummaryEdgeCases:
    """Edge case tests for get_area_summary."""

    def test_single_area(self):
        """Single area should produce one summary row."""
        df = pd.DataFrame({
            "area": ["Kukatpally", "Kukatpally"],
            "lg_group": ["LG1", "LG2"],
            "leader_name": ["L1", "L2"],
            "families": [5, 3],
            "individuals": [7, 4],
            "members": [12, 7],
            "latitude": [17.49, 17.50],
            "longitude": [78.40, 78.41],
        })
        summary = get_area_summary(df)
        assert len(summary) == 1
        assert summary.iloc[0]["total_groups"] == 2
        assert summary.iloc[0]["total_members"] == 19

    def test_area_strength_assignment(self):
        """Summary strength should be based on avg_members."""
        df = pd.DataFrame({
            "area": ["A", "A"],
            "lg_group": ["G1", "G2"],
            "leader_name": ["L1", "L2"],
            "families": [0, 0],
            "individuals": [0, 0],
            "members": [35, 25],  # avg = 30
            "latitude": [17.49, 17.50],
            "longitude": [78.40, 78.41],
        })
        summary = get_area_summary(df)
        assert summary.iloc[0]["strength"] == "Strong"


# ---------------------------------------------------------------------------
# New tests: load_from_excel edge cases
# ---------------------------------------------------------------------------


class TestLoadFromExcelEdgeCases:
    """Additional edge case tests for load_from_excel."""

    @patch("src.data_loader.st")
    @patch("src.data_loader.pd.read_excel")
    def test_excel_nan_families_individuals(self, mock_read_excel, mock_st):
        """NaN families/individuals should default to 0."""
        mock_data = pd.DataFrame({
            ",leader_name,": ["Ravi"],
            "area": ["Kukatpally"],
            "Families ": [None],
            "Individuals ": [None],
            "Total": [10],
            "Sync meeting on": ["Sunday"],
            "Care Coordinator": ["Coord1"],
        })
        mock_read_excel.return_value = mock_data
        df = load_from_excel("fake.xlsx")
        assert not df.empty
        assert df.iloc[0]["families"] == 0
        assert df.iloc[0]["individuals"] == 0

    @patch("src.data_loader.st")
    @patch("src.data_loader.pd.read_excel")
    def test_excel_nan_total_uses_sum(self, mock_read_excel, mock_st):
        """When Total is NaN, members should be families + individuals."""
        mock_data = pd.DataFrame({
            ",leader_name,": ["Ravi"],
            "area": ["Kukatpally"],
            "Families ": [5],
            "Individuals ": [7],
            "Total": [None],
            "Sync meeting on": ["Sunday"],
            "Care Coordinator": ["Coord1"],
        })
        mock_read_excel.return_value = mock_data
        df = load_from_excel("fake.xlsx")
        assert not df.empty
        assert df.iloc[0]["members"] == 12  # 5 + 7

    @patch("src.data_loader.st")
    @patch("src.data_loader.pd.read_excel")
    def test_excel_nan_meeting_day(self, mock_read_excel, mock_st):
        """NaN meeting_day should become empty string."""
        mock_data = pd.DataFrame({
            ",leader_name,": ["Ravi"],
            "area": ["Kukatpally"],
            "Families ": [5],
            "Individuals ": [7],
            "Total": [12],
            "Sync meeting on": [None],
            "Care Coordinator": ["Coord1"],
        })
        mock_read_excel.return_value = mock_data
        df = load_from_excel("fake.xlsx")
        assert not df.empty
        assert df.iloc[0]["meeting_day"] == ""
