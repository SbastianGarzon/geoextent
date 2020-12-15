import os           # used to get the location of the testdata
import pytest
import tempfile
from help_functions_test import create_zip
from osgeo import gdal

def test_helptext_direct(script_runner):
    ret = script_runner.run('geoextent', '--help')
    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    assert "geoextent [-h]" in ret.stdout, "usage instructions are printed to console"


def test_helptext_no_args(script_runner):
    ret = script_runner.run('geoextent')
    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    assert "geoextent [-h]" in ret.stdout, "usage instructions are printed to console"


def test_error_no_file(script_runner):
    ret = script_runner.run('geoextent', 'doesntexist')
    assert not ret.success, "process should return failue"
    assert ret.stderr != '', "stderr should not be empty"
    assert 'doesntexist' in ret.stderr, "wrong input is printed to console"
    assert ret.stdout == ''


def test_error_no_option(script_runner):
    ret = script_runner.run('geoextent', 'README.md')
    assert not ret.success, "process should return failue"
    assert ret.stderr != '', "stderr should not be empty"
    assert 'one of extraction options' in ret.stderr
    assert ret.stdout == ''


def test_debug_output(script_runner):
    ret = script_runner.run('geoextent',
        '-b', 'tests/testdata/geojson/muenster_ring_zeit.geojson')
    assert ret.success, "process should return success"
    assert "DEBUG:geoextent" not in ret.stderr
    assert "INFO:geoextent" not in ret.stderr
    assert "DEBUG:geoextent" not in ret.stdout
    assert "INFO:geoextent" not in ret.stdout

    # FIXME
    #retd = script_runner.run('geoextent',
    #    '--debug',
    #    '-b',
    #    'tests/testdata/geojson/muenster_ring_zeit.geojson')
    #assert retd.success, "process should return success"
    #assert "DEBUG:geoextent" in retd.stdout
    #assert "geoextent" not in retd.stdout

# FIXME
#def test_debug_config_envvar(script_runner):
#    os.environ["GEOEXTENT_DEBUG"] = "1" # this is picked up by the library, BUT the stdout is empty still
#    ret = script_runner.run('geoextent', '-b', 'tests/testdata/geojson/muenster_ring_zeit.geojson')
#    print(str(ret))
#    assert ret.success, "process should return success"
#    assert "DEBUG:geoextent" in ret.stdout
#    os.environ["GEOEXTENT_DEBUG"] = None

def test_geojson_invalid_second_input(script_runner):
    ret = script_runner.run('geoextent',
        'tests/testdata/geojson/muenster_ring_zeit.geojson',
        'tests/testdata/geojson/not_existing.geojson')
    assert not ret.success, "process should return failue"
    assert ret.stderr != '', "stderr should not be empty"
    assert 'not a valid directory or file' in ret.stderr, "wrong input is printed to console"
    assert 'tests/testdata/geojson/not_existing.geojson' in ret.stderr, "wrong input is printed to console"
    assert ret.stdout == ''


def test_geojson_bbox(script_runner):
    ret = script_runner.run('geoextent', '-b','tests/testdata/geojson/muenster_ring_zeit.geojson')
    assert ret.success, "process should return success"
    result = ret.stdout
    bboxStr = result[result.find("[") + 1:result.find("]")]
    bboxList = [float(i) for i in bboxStr.split(',')]
    assert bboxList == pytest.approx([7.6016807556152335, 51.94881477206191, 7.647256851196289, 51.974624029877454])


def test_geojson_bbox_long_name(script_runner):
    ret = script_runner.run('geoextent',
        '--bounding-box', 'tests/testdata/geojson/muenster_ring_zeit.geojson')
    assert ret.success, "process should return success"
    result = ret.stdout
    bboxStr = result[result.find("[") + 1:result.find("]")]
    bboxList = [float(i) for i in bboxStr.split(',')]
    assert bboxList == pytest.approx([7.6016807556152335, 51.94881477206191, 7.647256851196289, 51.974624029877454])


def test_geojson_bbox_invalid_coordinates(script_runner):
    ret = script_runner.run('geoextent',
        '-b', 'tests/testdata/gejson/invalid_coordinate.geojson')
    assert not ret.success, "process should return success"
    assert ret.stderr is not None
    assert 'not a valid directory or file' in ret.stderr, "stderr should not be empty"


def test_geojson_time(script_runner):
    ret = script_runner.run('geoextent',
        '-t', 'tests/testdata/geojson/muenster_ring_zeit.geojson')
    assert ret.success, "process should return success"
    assert "['2018-11-14', '2018-11-14']" in ret.stdout,  "time value is printed to console"


def test_geojson_time_invalid(script_runner):
    ret = script_runner.run('geoextent',
        '-t', 'tests/testdata/geojson/invalid_time.geojson')
    assert ret.success, "process should return success"
    assert "'tbox': None" in ret.stdout


def test_print_supported_formats(script_runner):
    ret = script_runner.run('geoextent', '--formats')
    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    assert "Supported formats:" in ret.stdout,  "list of supported formats is printed to console"


@pytest.mark.skip(reason="file format not implemented yet")
def test_netcdf_bbox(script_runner):
    ret = script_runner.run('geoextent',
        '-b', 'tests/testdata/nc/ECMWF_ERA-40_subset.nc')
    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    result = ret.stdout
    bboxStr = result[result.find("[") + 1:result.find("]")]
    bboxList = [float(i) for i in bboxStr.split(',')]
    assert bboxList == pytest.approx([-90.0, 0.0, 90.0, 357.5])

@pytest.mark.skip(reason="file format not implemented yet")
def test_netcdf_time(script_runner):
    result = script_runner.run('geoextent',
        '-t', 'tests/testdata/nc/ECMWF_ERA-40_subset.nc')
    assert result.success, "process should return success"
    assert result.stderr == '', "stderr should be empty"
    assert "['2002-07-01','2002-07-31']" in result.stdout,  "time value is printed to console"


@pytest.mark.skip(reason="file format not implemented yet")
def test_netcdf_time_invalid(script_runner):
    ret = script_runner.run('geoextent',
        '-b', 'tests/testdata/nc/ECMWF_ERA-40_subset.nc')
    assert ret.success, "process should return success"
    assert ret.stderr is not None
    assert ret.stderr == 'invalid time format', "stderr should not be empty"


def test_kml_bbox(script_runner):
    ret = script_runner.run('geoextent', '-b', 'tests/testdata/kml/aasee.kml')
    result = ret.stdout
    bboxStr = result[result.find("[") + 1:result.find("]")]
    bboxList = [float(i) for i in bboxStr.split(',')]
    assert bboxList == pytest.approx([7.594213485717774, 51.94246595679555, 7.61824607849121, 51.95727846118796])


def test_kml_time(script_runner):
    ret = script_runner.run('geoextent', '-t', 'tests/testdata/kml/aasee.kml')
    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    assert "'tbox': None" in ret.stdout,  "time value is printed to console"


def test_kml_time_invalid(script_runner):
    ret = script_runner.run('geoextent', '-t', 'tests/testdata/kml/abstractviews_timeprimitive_example_error.kml')
    assert ret.success, "process should return success"
    assert ret.stderr is not None
    assert "'tbox': None" in ret.stdout


@pytest.mark.skipif(gdal.__version__.startswith("2"), reason="coordinate order mismatch for old GDAL versions")
def test_geotiff_bbox(script_runner):
    ret = script_runner.run('geoextent',
        '-b', 'tests/testdata/tif/wf_100m_klas.tif')
    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    result = ret.stdout
    assert '4326' in result
    bboxStr = result[result.find("[")+1:result.find("]")]
    bboxList = [float(i) for i in bboxStr.split(',')]
    assert bboxList == pytest.approx([50.310252, 5.9153008, 52.5307755, 9.4683987])


def test_gpkg_bbox(script_runner):
    ret = script_runner.run('geoextent','-b', 'tests/testdata/nc/nc.gpkg')
    result = ret.stdout
    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    bboxStr = result[result.find("[")+1:result.find("]")]
    bboxList = [float(i) for i in bboxStr.split(',')]
    assert bboxList == pytest.approx([-84.32383511101011, 33.882102865417494, -75.4565859451531, 36.589757993328675])


def test_csv_bbox(script_runner, tmpdir):
    ret = script_runner.run('geoextent', 
        '-b', 'tests/testdata/csv/cities_NL.csv')
    assert ret.success, "process should return success"
    result = ret.stdout
    bboxStr = result[result.find("[") + 1:result.find("]")]
    bboxList = [float(i) for i in bboxStr.split(',')]
    assert bboxList == pytest.approx([4.3175, 51.434444, 6.574722, 53.217222])

def test_csv_time(script_runner, tmpdir):
    ret = script_runner.run('geoextent',
        '-t', 'tests/testdata/csv/cities_NL.csv')
    assert ret.success, "process should return success"
    #assert ret.stderr == '', "stderr should be empty"
    assert "['2017-08-01', '2019-09-30']" in ret.stdout, "time value is printed to console"


def test_csv_time_invalid(script_runner, tmpdir):
    ret = script_runner.run('geoextent',
        '-t', 'tests/testdata/csv/cities_NL_lat&long.csv')
    assert ret.success, "process should return success"
    assert ret.stderr is not None
    assert "no TemporalExtent" in ret.stderr , "stderr should not be empty"


def test_gml_bbox(script_runner):
    ret = script_runner.run('geoextent', '-b', 'tests/testdata/gml/clc_1000_PT.gml')
    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    result = ret.stdout
    bboxStr = result[result.find("[") + 1:result.find("]")]
    bboxList = [float(i) for i in bboxStr.split(',')]
    assert bboxList == pytest.approx([32.39669, -17.5420699994571, 39.30113999999999, -6.959389999772738])


def test_gml_time(script_runner):
    ret = script_runner.run('geoextent', '-t', 'tests/testdata/gml/clc_1000_PT.gml')
    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    assert "['2005-12-31', '2013-11-30']" in ret.stdout,  "time value is printed to console"


def test_gml_only_one_time_feature_valid(script_runner):
    ret = script_runner.run('geoextent','-t', 'tests/testdata/gml/mypolygon_px6_error_time_one_feature.gml')
    assert ret.stdout
    assert "'tbox': ['2012-04-15', '2012-04-15']" in ret.stdout, "time value is printed to console"


def test_shp_bbox(script_runner):
    ret = script_runner.run('geoextent', '-b', 'tests/testdata/shapefile/Abgrabungen_Kreis_Kleve_Shape.shp')
    assert ret.success, "process should return success"
    assert "'bbox': None" in ret.stdout


@pytest.mark.skip(reason="multiple input files not implemented yet")
def test_multiple_files(script_runner):
    ret = script_runner.run('python', 'geoextent',
        '-b', 'tests/testdata/shapefile/Abgrabungen_Kreis_Kleve_Shape.shp', 'tests/testdata/geojson/ausgleichsflaechen_moers.geojson')
    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    assert "[7.6016807556152335, 51.94881477206191, 7.647256851196289, 51.974624029877454]" in ret.stdout, "bboxes and time values of all files inside folder, are printed to console"
    assert "[6.574722, 51.434444, 4.3175, 53.217222]" in ret.stdout, "bboxes and time values of all files inside folder, are printed to console"
    assert "[292063.81225905, 5618144.09259115, 302531.3161606, 5631223.82854667]" in ret.stdout, "bboxes and time values of all files inside folder, are printed to console"


def test_folder(script_runner):
    ret = script_runner.run('geoextent',
                            '-b','-t', 'tests/testdata/folders/folder_two_files')
    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    result = ret.stdout
    bboxStr = result[result.find("[") + 1:result.find("]")]
    bboxList = [float(i) for i in bboxStr.split(',')]
    assert bboxList == pytest.approx([2.052333387639205, 41.31703852240476, 7.647256851196289, 51.974624029877454])
    assert "['2018-11-14', '2019-09-11']" in result,"merge time value of folder files, is printed to console"


def test_zipfile(script_runner):
    folder_name = "tests/testdata/folders/folder_one_file"
    with tempfile.NamedTemporaryFile(suffix=".zip") as tmp:
        create_zip(folder_name, tmp)
        ret = script_runner.run('geoextent','-b','-t', tmp.name)
        assert ret.success, "process should return success"
        result = ret.stdout
        bboxStr = result[result.find("[") + 1:result.find("]")]
        bboxList = [float(i) for i in bboxStr.split(',')]
        assert bboxList == pytest.approx([7.6016807556152335, 51.94881477206191, 7.647256851196289, 51.974624029877454])
        assert "['2018-11-14', '2018-11-14']" in result


@pytest.mark.skip(reason="multiple input directories not implemented yet")
def test_multiple_folders(script_runner):
    ret = script_runner.run('python', 'geoextent',
        '-b', 'tests/testdata/shapefile', 'tests/testdata/geojson', 'tests/testdata/nc')
    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    assert "full bbox" in ret.stdout, "joined bboxes of all files inside folder are printed to console"
