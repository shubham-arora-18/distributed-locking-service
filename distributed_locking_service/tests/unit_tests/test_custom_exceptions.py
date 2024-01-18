from distributed_locking_service.exceptions import DuplicateDataException
from distributed_locking_service.exceptions import MissingDataException


def test_duplicate_data_exception():
    bqe = DuplicateDataException(status_code=403, detail="Duplicate Data Exception")
    assert bqe.detail == "Duplicate Data Exception"
    assert bqe.status_code == 403


def test_missing_data_exception():
    bqe = MissingDataException(detail="test var.")
    assert bqe.detail == "Missing data: test var."
    assert bqe.status_code == 404
