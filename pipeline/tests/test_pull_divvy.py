import io
import zipfile

import pull_divvy

_HEADER = ("ride_id,rideable_type,started_at,ended_at,start_station_name,"
           "start_station_id,end_station_name,end_station_id,"
           "start_lat,start_lng,end_lat,end_lng\n")


def _trip_row(ride_id, station_id, station_name, lat, lng):
    return (f"{ride_id},classic_bike,2026-06-01 08:00:00,2026-06-01 08:10:00,"
            f"{station_name},{station_id},Other St,999,{lat},{lng},41.9,-87.6\n")


def _zip_bytes(members):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, data in members.items():
            zf.writestr(name, data)
    return buf.getvalue()


def test_aggregate_counts_trips_per_start_station():
    csv_data = (_HEADER
                + _trip_row("a", "13022", "Streeter Dr & Grand Ave", 41.892, -87.612)
                + _trip_row("b", "13022", "Streeter Dr & Grand Ave", 41.892, -87.612)
                + _trip_row("c", "TA1307", "Clark St & Elm St", 41.903, -87.631))
    stations = pull_divvy.aggregate_station_counts(
        _zip_bytes({"202606-divvy-tripdata.csv": csv_data}))
    by_id = {s["station_id"]: s for s in stations}
    assert by_id["13022"]["trip_count"] == 2
    assert by_id["13022"]["lat"] == 41.892
    assert by_id["TA1307"]["trip_count"] == 1


def test_aggregate_skips_macosx_resource_fork_members():
    # Real Divvy zips are built on a Mac: alongside the CSV they carry a
    # binary AppleDouble member named __MACOSX/._<name>.csv, which is not
    # UTF-8 and must never be parsed as trip data (byte 0xE4 reproduces the
    # 202606 crash).
    csv_data = _HEADER + _trip_row("a", "13022", "Streeter Dr & Grand Ave",
                                   41.892, -87.612)
    junk = b"\x00\x05\x16\x07\x00\x02\x00\x00Mac OS X" + b"\xe4" * 32
    stations = pull_divvy.aggregate_station_counts(_zip_bytes({
        "202606-divvy-tripdata.csv": csv_data,
        "__MACOSX/._202606-divvy-tripdata.csv": junk,
    }))
    assert [s["station_id"] for s in stations] == ["13022"]


def test_aggregate_raises_when_only_resource_forks_match():
    junk = b"\x00\x05\x16\x07" + b"\xe4" * 8
    try:
        pull_divvy.aggregate_station_counts(
            _zip_bytes({"__MACOSX/._202606-divvy-tripdata.csv": junk}))
    except RuntimeError as exc:
        assert "no CSV" in str(exc)
    else:
        raise AssertionError("expected RuntimeError for a zip with no real CSV")
