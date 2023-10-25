import pytest
from database import DataBase


@pytest.fixture
def db_instance():
    return DataBase()


def test_connection_pool_size(db_instance):
    connection_pool = db_instance.connection_pool
    assert connection_pool.pool_size == 5


def test_get_connection(db_instance):
    connection = db_instance.connection_pool.get_connection()
    assert connection is not None
    connection.close()


def test_insert_into_db(db_instance):
    data = {"sender_ID": 8, "reciever_ID": 11,
            "content": "Hey man sure hope you aren't up till 4am coding everynight!", "time_sent": 1698232231}
    result = db_instance.insert_into_db('user_personal_messages', data)
    assert result is True


def test_insert_into_db_invalid_table(db_instance):
    data = {"sender_ID": 8, "reciever_ID": 11,
            "content": "Hey man sure hope you aren't up till 4am coding everynight!", "timestamp": 1698232231}
    result = db_instance.insert_into_db("non_existent_table", data)
    assert result is False


def test_insert_into_db_invalid_column_data_type(db_instance):
    data = {"sender_ID": 8, "reciever_ID": "eleven",
            "content": "Hey man sure hope you aren't up till 4am coding!", "time_sent": 1698232231}
    result = db_instance.insert_into_db('user_personal_messages', data)
    assert result is False
