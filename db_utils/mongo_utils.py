import requests
from datetime import datetime
import os
from gnani_sdk.logging import setup_logger
from gnani_sdk.config_parser import (
    MONGO_API_URL,
    MONGO_API_PORT, 
    MONGO_DB_NAME, 
    MONGO_INPUT_COLLECTION, 
    MONGO_OUTPUT_COLLECTION,
    MONGO_REJECT_COLLECTION,
    MONGO_SMS_COLLECTION
)

# Setup logger
logger = setup_logger("mongo_utils")


headers = {
    'app': 'mongo-db-layer',
    'Content-Type': 'application/json'
}

class MongoDB:
    def __init__(self):
        self._mongo_db = MONGO_DB_NAME
        self.input_col = MONGO_INPUT_COLLECTION
        self.output_col = MONGO_OUTPUT_COLLECTION
        self.reject_col = MONGO_REJECT_COLLECTION
        self.sms_col = MONGO_SMS_COLLECTION
        mongo_host = os.getenv('mongo_host_atlas','mongo-db-layer-v2.default.svc.cluster.local') if os.getenv("ENV","dev")!="dev" else MONGO_API_URL
        mongo_port = os.getenv('mongo_port_atlas','8080') if os.getenv("ENV","dev")!="dev" else MONGO_API_PORT
        self.mongo_url = f"http://{mongo_host}:{mongo_port}"
        logger.info(f"MongoDB API URL: {self.mongo_url}, DB: {self._mongo_db}")

    def get_collection(self, col_type):
        if col_type in ("input",):
            return self.input_col
        elif col_type in ("output", "report"):
            return self.output_col
        elif col_type in ("reject"):
            return self.reject_col
        elif col_type in ("sms"):
            return self.sms_col
        else:
            logger.info("Please mention the collection type input or output")
            return None

    def mongo_file_count(self, col_type="", q1={}):
        COL = self.get_collection(col_type)
        if COL is None:
            return ""
        mongo_url = f"{self.mongo_url}/count"
        payload = {
            "db": self._mongo_db,
            "collection": COL,
            "dict_query": q1
        }
        try:
            response = requests.post(mongo_url, headers=headers, json=payload)
            res = response.json()
            if res.get('status') == 404:
                logger.debug('Error from the server')
                return ""
            else:
                return res.get("count")
        except Exception as e:
            logger.exception(f"Exception in mongo_file_count api: {e}")
            return ""

    def mongo_delete(self, col_type="", q1={"phone_number": 11111}):
        COL = self.get_collection(col_type)
        if COL is None:
            return False
        mongo_url = f"{self.mongo_url}/remove"
        payload = {
            "db": self._mongo_db,
            "collection": COL,
            "dict_condition": q1
        }
        try:
            response = requests.post(mongo_url, headers=headers, json=payload)
            res = response.json()
            if res.get('message') == "Record Does not Exist" and res.get('status') == 200:
                logger.debug("Record Does not Exist")
                return False
            elif res.get('status') == 404:
                logger.debug('Error from the server')
                return False
            else:
                logger.debug("Record is successfully deleted")
                return True
        except Exception as e:
            logger.exception(f"Exception in mongo_delete api: {e}")
            return False

    def mongo_update(self, col_type="", record={}, upd_cond={"phone_number": 11111}):
        COL = self.get_collection(col_type)
        if COL is None:
            return False
        mongo_url = f"{self.mongo_url}/update"
        li = ["last_triggered_date", "callConnectedTime", "callEndTime", "next_trigger_date"]
        for k, v in record.items():
            if k in li and v != '':
                record[k] = str(v)
        payload = {
            "db": self._mongo_db,
            "collection": COL,
            "dict_condition": upd_cond,
            "dict_update": record
        }
        try:
            response = requests.post(mongo_url, headers=headers, json=payload)
            res = response.json()
            if res.get('message') == "Record Does not Exist" and res.get('status') == 200:
                logger.debug("Record Does not Exist")
                return False
            elif res.get('status') == 404:
                logger.debug('Error from the server')
                return False
            else:
                logger.debug("Record is successfully updated")
                return True
        except Exception as e:
            logger.exception(f"Exception in mongo_update api: {e}")
            return False

    def mongo_insert(self, col_type="", record={}):
        COL = self.get_collection(col_type)
        if COL is None:
            return False
        mongo_url = f"{self.mongo_url}/insert"
        li = ["last_triggered_date", "callConnectedTime", "callEndTime", "next_trigger_date"]
        for k, v in record.items():
            if k in li and v != '':
                record[k] = str(v)
        payload = {
            "db": self._mongo_db,
            "collection": COL,
            "data": record
        }
        try:
            response = requests.post(mongo_url, headers=headers, json=payload)
            res = response.json()
            if res.get('status') == 404:
                logger.debug('Error from the server')
                return False
            else:
                logger.debug("Record is successfully inserted")
                logger.info(res)
                return True
        except Exception as e:
            logger.exception(f"Exception in mongo_insert api: {e}")
            return False

    def mongo_get_collection_data(self, col_type, q1={}, q2={"_id": 0}):
        COL = self.get_collection(col_type)
        if COL is None:
            return None
        mongo_url = f"{self.mongo_url}/findone"
        payload = {
            "db": self._mongo_db,
            "collection": COL,
            "dict_query": q1
        }
        try:
            response = requests.post(mongo_url, headers=headers, json=payload)
            res = response.json()
            if res.get('message') == "Record Does not Exist" and res.get('status') == 200:
                logger.debug('Record Does not Exist')
                return None
            elif res.get('status') == 404:
                logger.debug('Error from the server')
                return False
            else:
                logger.debug('Record Fetched Successfully')
                retrieved_collection = res.get('result', {})
                li = ["last_triggered_date", "callConnectedTime", "callEndTime", "next_trigger_date"]
                for k, v in retrieved_collection.items():
                    if k in li and v != '':
                        logger.info(f"{k}: {v}")
                        try:
                            retrieved_collection[k] = datetime.strptime(v[0:19], '%Y-%m-%d %H:%M:%S')
                        except Exception:
                            pass
                return retrieved_collection
        except Exception as e:
            logger.exception(f"Exception in mongoget_collection_data api: {e}")
            return None

