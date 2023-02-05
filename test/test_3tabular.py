import pytest
import pandas as pd
import pytabular as p
from test.config import testingtablename, testing_parameters, get_test_path


@pytest.mark.parametrize("model", testing_parameters)
def test_basic_query(model):
    int_result = model.query("EVALUATE {1}")
    text_result = model.query('EVALUATE {"Hello World"}')
    assert int_result == 1 and text_result == "Hello World"


datatype_queries = [
    ["this is a string", '"this is a string"'],
    [1, 1],
    [1000.78, "CONVERT(1000.78,CURRENCY)"],
]


@pytest.mark.parametrize("model", testing_parameters)
def test_datatype_query(model):
    for query in datatype_queries:
        result = model.query(f"EVALUATE {{{query[1]}}}")
        assert result == query[0]


@pytest.mark.parametrize("model", testing_parameters)
def test_file_query(model):
    singlevaltest = get_test_path() + "\\singlevaltest.dax"
    dfvaltest = get_test_path() + "\\dfvaltest.dax"
    dfdupe = pd.DataFrame({"[Value1]": (1, 3), "[Value2]": (2, 4)})
    assert model.query(singlevaltest) == 1 and model.query(dfvaltest).equals(dfdupe)


@pytest.mark.parametrize("model", testing_parameters)
def test_repr_str(model):
    assert isinstance(model.__repr__(), str)


@pytest.mark.parametrize("model", testing_parameters)
def test_pytables_count(model):
    assert model.Tables[testingtablename].row_count() > 0


@pytest.mark.parametrize("model", testing_parameters)
def test_pytables_refresh(model):
    assert len(model.Tables[testingtablename].refresh()) > 0


@pytest.mark.parametrize("model", testing_parameters)
def test_pypartitions_refresh(model):
    assert len(model.Tables[testingtablename].Partitions[0].refresh()) > 0


@pytest.mark.parametrize("model", testing_parameters)
def test_pyobjects_adding(model):
    table = model.Tables.find(testingtablename)
    table += table
    assert len(table) == 2


@pytest.mark.parametrize("model", testing_parameters)
def test_nonetype_decimal_bug(model):
    query_str = """
    EVALUATE
    {
        (1, CONVERT( 1.24, CURRENCY ), "Hello"), (2, CONVERT( 87661, CURRENCY ), "World"), (3,,"Test")
    }
    """
    assert len(model.query(query_str)) == 3


@pytest.mark.parametrize("model", testing_parameters)
def test_table_last_refresh_times(model):
    """Really just testing the the function completes successfully and returns df"""
    assert isinstance(model.Tables.last_refresh(), pd.DataFrame)


@pytest.mark.parametrize("model", testing_parameters)
def test_return_zero_row_tables(model):
    """Testing that `Return_Zero_Row_Tables`"""
    assert isinstance(model.Tables.find_zero_rows(), p.pytabular.PyTables)


@pytest.mark.parametrize("model", testing_parameters)
def test_get_dependencies(model):
    dependencies = model.Measures[0].get_dependencies()
    assert len(dependencies) > 0


@pytest.mark.parametrize("model", testing_parameters)
def test_disconnect(model):
    """Tests `Disconnect()` from `Tabular` class."""
    model.disconnect()
    assert model.Server.Connected is False


@pytest.mark.parametrize("model", testing_parameters)
def test_reconnect(model):
    """Tests `Reconnect()` from `Tabular` class."""
    model.reconnect()
    assert model.Server.Connected is True


@pytest.mark.parametrize("model", testing_parameters)
def test_reconnect_savechanges(model):
    """This will test the `reconnect()` gets called in `save_changes()`"""
    model.disconnect()
    model.save_changes()
    assert model.Server.Connected is True


@pytest.mark.parametrize("model", testing_parameters)
def test_is_process(model):
    """Checks that `Is_Process()` from `Tabular` class returns bool"""
    assert isinstance(model.is_process(), bool)


@pytest.mark.parametrize("model", testing_parameters)
def test_bad_table(model):
    """Checks for unable to find table exception"""
    with pytest.raises(Exception):
        model.refresh("badtablename")


@pytest.mark.parametrize("model", testing_parameters)
def test_refresh_dict(model):
    """Checks for refreshing dictionary"""
    table = model.Tables[testingtablename]
    refresh = model.refresh({table.Name: table.Partitions[0].Name})
    assert isinstance(refresh, pd.DataFrame)


@pytest.mark.parametrize("model", testing_parameters)
def test_refresh_dict_pypartition(model):
    """Checks for refreshing dictionary"""
    table = model.Tables[testingtablename]
    refresh = model.refresh({table.Name: table.Partitions[0]})
    assert isinstance(refresh, pd.DataFrame)


@pytest.mark.parametrize("model", testing_parameters)
def test_bad_partition(model):
    """Checks for refreshing dictionary"""
    table = model.Tables[testingtablename]
    with pytest.raises(Exception):
        model.refresh({table.Name: table.Partitions[0].Name + "fail"})
