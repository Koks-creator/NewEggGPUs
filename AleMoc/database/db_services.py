import os
import json
import logging
from typing import List
import shutil
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.engine.row import Row
import sqlalchemy.orm as _orm

from AleMoc.database import database
from AleMoc.database.models import Products, Reviews
from AleMoc.config import Config
from AleMoc.TurboLogger import CustomLogger

database.create_database()
db_services_logger = CustomLogger(logger_name="DbServices", log_file_name=f"{Config.PROJECT_MAIN_PATH}/{Config.LOGS_FOLDER}/dbServicesLogs.txt",
                                  logger_log_level=logging.INFO).create_logger()

FIELDS_TO_EXCLUDE = ["Id", "_sa_instance_state", "DateCreated", "Archived"]
TABLES = {
    "Products": {
        "TableObj": Products,
        "Columns": Products.__table__.columns.keys()
    },
    "Reviews": {
        "TableObj": Reviews,
        "Columns": Reviews.__table__.columns.keys()
    }
}


class SqlInjectionException(Exception):
    def __init__(self, message="We don't do that here"):
        self.message = message
        super().__init__(self.message)


def exclude_keys(d: dict, keys: list) -> dict:
    return {k: v for k, v in d.items() if k not in keys}


def retarded_anti_sql_injection(string2check: str) -> bool:
    if any(i for i in ["update", "delete", "insert", "drop", "alter", "truncate"] if i in string2check.lower()):
        return False
    return True


def get_table_count(table_name: str, where: str = "") -> int:
    where_stet = ""
    if where:
        where_stet = where
    return db.execute(text(f"SELECT COUNT(*) FROM {table_name} {where_stet}")).scalar()


def add_prod(db: database.SessionLocal, new_product: Products) -> bool:
    new_record_dict = {column: getattr(new_product, column) for column in TABLES["Products"]["Columns"]}
    active_record = db.query(Products).filter(Products.Archived == False, Products.ProductId == new_product.ProductId).first()

    # d = exclude_keys(new_record_dict, FIELDS_TO_EXCLUDE)
    # d2 = exclude_keys(active_record.__dict__, FIELDS_TO_EXCLUDE)
    # print(dict(sorted(d.items())))
    # print(dict(sorted(d2.items())))
    if active_record:
        if exclude_keys(new_record_dict, FIELDS_TO_EXCLUDE) != exclude_keys(active_record.__dict__, FIELDS_TO_EXCLUDE):
            active_record.Archived = True
            # 2 commity?
            db.commit()
            db.refresh(active_record)

            db.add(new_product)
            db.commit()
            db.refresh(new_product)
            return True
    else:
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        return True

    return False


def add_review(db: database.SessionLocal, new_review: Reviews) -> bool:

    current_review = db.query(Reviews).filter(
         Reviews.Author == new_review.Author,
         Reviews.ProductId == new_review.ProductId,
         Reviews.DatePublished == new_review.DatePublished,
         Reviews.Description == new_review.Description,
         Reviews.Rating == new_review.Rating
          ).first()

    if not current_review:
        db.add(new_review)
        db.commit()
        db.refresh(new_review)
        return True
    return False


def list_sink() -> List[str]:
    return os.listdir(f"{Config.PROJECT_MAIN_PATH}/{Config.SINK_FOLDER}")


def add_data_from_sink(db: database.SessionLocal, folders_to_process: List[str] = None) -> dict:
    # counter
    counter = {table_name: 0 for table_name in list(TABLES.keys())}

    db_services_logger.info("Adding records from sink")
    sink_path = f"{Config.PROJECT_MAIN_PATH}/{Config.SINK_FOLDER}"

    data_folders = list_sink()
    if folders_to_process:
        data_folders = [folder for folder in data_folders if folder in folders_to_process]
    for data_folder in data_folders:
        db_services_logger.info(f"Working on: {data_folder}")
        data_folder_path = f"{sink_path}/{data_folder}"

        data_files = os.listdir(data_folder_path)
        if "Product" in data_files[0]:
            products_file, reviews_file = data_files
        else:
            reviews_file, products_file = data_files

        with open(f"{sink_path}/{data_folder}/{products_file}") as products_f:
            products_json = json.load(products_f)

        with open(f"{sink_path}/{data_folder}/{reviews_file}") as products_f:
            reviews_json = json.load(products_f)

        # add product
        for product in products_json:
            product_id = list(product.keys())[0]

            product_data = product[product_id]
            product_data["ProductId"] = product_id

            if product_data["Price"]:
                product_data["Price"] = float(product_data["Price"].replace(",", ""))
            else:
                product_data["Price"] = None
            product_record = Products(**product_data)
            status = add_prod(db, product_record)
            if status:
                counter["Products"] += 1

        # add reviews
        for reviews in reviews_json:
            product_id = list(reviews.keys())[0]
            for review in reviews[product_id]:
                review["ProductId"] = product_id
                review["DatePublished"] = datetime.strptime(review["DatePublished"], "%Y-%m-%d")

                review_record = Reviews(**review)
                status = add_review(db, review_record)
                if status:
                    counter["Reviews"] += 1
        shutil.rmtree(data_folder_path)

    db_services_logger.info(f"{counter=}")
    db_services_logger.info(f"Done")

    return counter


def get_table_columns(table_name: str) -> list[str]:
    return TABLES[table_name]["Columns"]


def query_table(db: _orm.Session, table_name: str, query_filter: dict) -> List[Products]:
    return db.query(TABLES[table_name]["TableObj"]).filter_by(**query_filter).all()


def query_table_sql(db: database.SessionLocal, table_name: str, query_filter: dict) -> List[List]:
    """

    :param db:
    :param table_name:
    :param query_filter: should have WhereQuery key with filter query and Columns
           key which is a list of columns to select, if empty then *
    :return:
    """
    unpacked_columns = "*"
    where_clause = ""
    given_columns = query_filter['Columns']
    given_where_clause = query_filter['WhereQuery']

    if query_filter['Columns']:
        unpacked_columns = ", ".join(given_columns)

    if query_filter['WhereQuery']:
        where_clause = f" WHERE {given_where_clause}"

    sql_query = f"SELECT {unpacked_columns} FROM {table_name}{where_clause}"
    if not retarded_anti_sql_injection(sql_query):
        raise SqlInjectionException()
    res = db.execute(text(sql_query))

    return [list(record) for record in res]


# ADMIN FUNCTIONS
def update_table(db: database.SessionLocal, table_name: str, query_filter: dict, updated_fields: dict,
                 rollback: bool = False) -> list[Row]:
    records = query_table(db=db, table_name=table_name, query_filter=query_filter)

    updated_records = []
    for record in records:
        for key, value in updated_fields.items():
            setattr(record, key, value)

        if not rollback:
            db.commit()
            db.refresh(record)
        else:
            db.rollback()
        updated_records.append(record)

    return updated_records


def update_table_sql(db: database.SessionLocal, table_name: str, update_query: dict, rollback: bool = False) -> int:
    given_where_clause = update_query["WhereQuery"]
    given_set_clause = update_query["SetQuery"]

    sql_update_query = f"UPDATE {table_name} SET {given_set_clause} WHERE {given_where_clause}"

    if not retarded_anti_sql_injection(given_where_clause + " " + given_set_clause):
        raise SqlInjectionException()
    row_count = db.execute(text(sql_update_query)).rowcount

    if not rollback:
        db.commit()
    else:
        db.rollback()

    return row_count


def delete_from_table(db: database.SessionLocal, table_name: str, query_filter: dict, rollback: bool = False) -> int:
    row_count = db.query(TABLES[table_name]["TableObj"]).filter_by(**query_filter).delete()
    if rollback:
        db.rollback()
    else:
        db.commit()

    return row_count


def delete_from_table_sql(db: database.SessionLocal, table_name: str, query_filter: dict, rollback: bool = False) -> int:
    given_where_clause = query_filter["WhereQuery"]

    sql_delete_query = f"DELETE FROM {table_name} WHERE {given_where_clause}"
    if not retarded_anti_sql_injection(given_where_clause):
        raise SqlInjectionException()

    row_count = db.execute(text(sql_delete_query)).rowcount

    if not rollback:
        db.commit()
    else:
        db.rollback()

    return row_count


if __name__ == '__main__':
    db = database.SessionLocal()
    print(list_sink())
    # add_data_from_sink(db)
    # from AleMoc.database.database import SessionLocal, get_db
    # import fastapi as _fastapi
    #
    # api_db : _orm.Session= _fastapi.Depends(get_db())
    # add_data_from_sink(db=db)

    # tu selecty
    # count = delete_from_table(db, "Products", {'ProductId' :'TESTUJEM324'}, rollback=False)
    # print(count)
    # xddel = {
    #     "WhereQuery": "ProductId = 'TESTUJEM22'",
    # }
    # count = delete_from_table_sql(db=db, table_name="Products", filter_query=xddel, rollback=False)
    # print(count)
    # #
    # res = delete_from_table(db, "Products", {"ProductId": "TESTUJEM22"}, rollback=True)
    # print(res)
    xd = {
        "WhereQuery": "ProductTitle LIKE '%RTX%3080%'",
        # "WhereQuery": "Archived is false limit 10",
        # "WhereQuery": "ProductTitle LIKE 'RTX%3080%'",
        "Columns": []
    }
    # res = delete_from_table_sql(db=db, table_name="Products", query_filter=xd, rollback=True)
    # # res = query_table(db, "Products", {})
    # print(res)
    # res = query_table_sql(db, "Products", xd)
    # print(res)
    # for r in res:
    #     print(r)
    # res = query_table(db, "Products", {"ProductId": "N82E16814126588T"})
    # for r in res:
    #     print(r)
    #
    # res = query_table(db, "Products", {"ProductId": "N82E16814126588T"})
    # for r in res:
    #     print(r)
    update_xd = {
        "ProductId": "test",
        "ProductTitle": "dfdsfdsf"
    }
    # # print(res)
    # res = update_table(db=db, table_name="Products", query_filter={"ProductTitle": "dfdsfdsf"}, updated_fields=update_xd
    #                    ,rollback=True)
    # print(res)
    # sql_update_xd = {
    #     "WhereQuery": "ProductId = 'TESTUJEM323'",
    #     "SetQuery": "ProductId = 'TESTUJEM324'"
    # }
    # res = update_table_sql2(db=db, table_name="Products", update_query=sql_update_xd, rollback=False)
    # print(res)
    #
    # res = query_table(db, "Products", {"ProductId": "TESTUJEM324"})
    # for r in res:
    #     print(r)

    # sql_update_xd = {
    #     "WhereQuery": "ProductId = 'TESTUJEM2'",
    #     "SetQuery": "ProductId = 'TESTUJEM3'"
    # }
    # update_table_sql(db=db, table_name="Products", update_q=sql_update_xd)
    # delete_from_table(db, "Products", {"ProductId": "TESTUJEM22"})
    # res = query_table(db, "Products", {"ProductId": "TESTUJEM3"})
    # print(res)
