from auth.custom_exceptions import BigqueryException
from auth.custom_exceptions import ConfigurationException
from auth.custom_exceptions import DatastoreException
from auth.custom_exceptions import GCSException
from auth.custom_exceptions import ProcessExecutionException
from auth.custom_exceptions import PubSubException
from auth.custom_exceptions import StatusException
from auth.custom_exceptions import VisualizationException


def test_bigquery_exception():
    bqe = BigqueryException(status_code=401, detail="Big Query Exception")
    assert bqe.detail == "Big Query Exception"
    assert bqe.status_code == 401


def test_pubsub_exception():
    bqe = PubSubException(status_code=401, detail="Pubsub Exception")
    assert bqe.detail == "Pubsub Exception"
    assert bqe.status_code == 401


def test_configuration_exception():
    bqe = ConfigurationException(status_code=401, detail="Configuration Exception")
    assert bqe.detail == "Configuration Exception"
    assert bqe.status_code == 401


def test_status_exception():
    bqe = StatusException(status_code=401, detail="Status Exception")
    assert bqe.detail == "Status Exception"
    assert bqe.status_code == 401


def test_gcs_exception():
    bqe = GCSException(status_code=401, detail="GCS Exception")
    assert bqe.detail == "GCS Exception"
    assert bqe.status_code == 401


def test_datastore_exception():
    bqe = DatastoreException(status_code=401, detail="Datastore Exception")
    assert bqe.detail == "Datastore Exception"
    assert bqe.status_code == 401


def test_process_execution_exception():
    bqe = ProcessExecutionException(status_code=401, detail="Process Execution Exception")
    assert bqe.detail == "Process Execution Exception"
    assert bqe.status_code == 401


def test_visualization_exception():
    bqe = VisualizationException(status_code=401, detail="Visualization Exception")
    assert bqe.detail == "Visualization Exception"
    assert bqe.status_code == 401
