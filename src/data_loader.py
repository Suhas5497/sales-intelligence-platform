import pandas as pd
from .config import PRODUCTS_FILE, CUSTOMERS_FILE, ORDERS_FILE
from .logger import get_logger

logger = get_logger(__name__)

def load_products():

    logger.info("Loading products dataset")
    df = pd.read_csv(PRODUCTS_FILE)

    logger.info(f"Products loaded: {df.shape}")
    return df


def load_customers():

    logger.info("Loading customers dataset")
    df = pd.read_csv(CUSTOMERS_FILE)

    logger.info(f"Customers loaded: {df.shape}")
    return df


def load_orders():

    logger.info("Loading orders dataset")
    df = pd.read_csv(ORDERS_FILE)

    logger.info(f"Orders loaded: {df.shape}")
    return df