from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .config import (
    CUSTOMERS_FILE,
    DEFAULT_END_DATE,
    DEFAULT_NUM_CUSTOMERS,
    DEFAULT_NUM_ORDERS,
    DEFAULT_NUM_PRODUCTS,
    DEFAULT_RANDOM_SEED,
    DEFAULT_START_DATE,
    ORDERS_FILE,
    PRODUCTS_FILE,
    ensure_project_directories,
)
from .logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class GenerationConfig:
    num_products: int = DEFAULT_NUM_PRODUCTS
    num_customers: int = DEFAULT_NUM_CUSTOMERS
    num_orders: int = DEFAULT_NUM_ORDERS
    start_date: str = DEFAULT_START_DATE
    end_date: str = DEFAULT_END_DATE
    random_seed: int = DEFAULT_RANDOM_SEED


CITIES = [
    "Ahmedabad",
    "Bengaluru",
    "Bhopal",
    "Chandigarh",
    "Chennai",
    "Coimbatore",
    "Delhi",
    "Faridabad",
    "Hyderabad",
    "Indore",
    "Jaipur",
    "Jodhpur",
    "Kanpur",
    "Kochi",
    "Kolkata",
    "Lucknow",
    "Ludhiana",
    "Madurai",
    "Mangalore",
    "Mumbai",
    "Mysore",
    "Nagpur",
    "Nashik",
    "Noida",
    "Patna",
    "Pune",
    "Raipur",
    "Ranchi",
    "Surat",
    "Thane",
    "Vadodara",
    "Varanasi",
    "Visakhapatnam",
]

SEGMENTS = ["Consumer", "Corporate", "Small Business", "Student"]

CATEGORY_PRODUCT_TEMPLATES = {
    "Electronics": [
        "Smartphone Max",
        "Smartphone Pro",
        "Laptop Pro",
        "Laptop Lite",
        "Noise Cancelling Headphones",
        "Tablet Air",
        "Smart Watch",
        "Bluetooth Speaker",
        "Gaming Console",
        "Wireless Router",
    ],
    "Fashion": [
        "Classic Denim Jacket",
        "Everyday Sneakers",
        "Premium Hoodie",
        "Athleisure Joggers",
        "Formal Shirt",
        "Leather Belt",
        "Running Shorts",
        "Canvas Tote",
        "Summer Dress",
        "Travel Backpack",
    ],
    "Home Appliances": [
        "Air Fryer",
        "Mixer Grinder",
        "Vacuum Cleaner",
        "Water Purifier",
        "Coffee Machine",
        "Room Heater",
        "Air Cooler",
    ],
    "Beauty": [
        "Skincare Kit",
        "Hair Dryer",
        "Makeup Palette",
        "Face Serum",
        "Body Lotion",
        "Perfume Gift Set",
        "Beard Grooming Kit",
    ],
    "Furniture": [
        "Office Chair",
        "Study Desk",
        "Bookshelf",
        "Storage Cabinet",
        "Side Table",
        "TV Unit",
    ],
    "Sports": [
        "Yoga Mat",
        "Cricket Kit",
        "Fitness Band",
        "Treadmill Lite",
        "Dumbbell Set",
        "Cycling Helmet",
    ],
    "Books": [
        "Business Strategy Book",
        "Python for Analysts",
        "Leadership Playbook",
        "Personal Finance Guide",
        "Design Thinking Handbook",
    ],
    "Accessories": [
        "Phone Case",
        "Laptop Sleeve",
        "Travel Organizer",
        "Desk Lamp",
        "USB Hub",
    ],
}

CATEGORY_BASE_PRICES = {
    "Electronics": (4_500, 78_000),
    "Fashion": (900, 7_500),
    "Home Appliances": (2_800, 24_000),
    "Beauty": (650, 4_500),
    "Furniture": (4_000, 28_000),
    "Sports": (1_200, 22_000),
    "Books": (350, 1_600),
    "Accessories": (450, 5_200),
}

CATEGORY_WEIGHTS = {
    "Electronics": 0.24,
    "Fashion": 0.20,
    "Home Appliances": 0.13,
    "Beauty": 0.11,
    "Furniture": 0.10,
    "Sports": 0.09,
    "Books": 0.07,
    "Accessories": 0.06,
}
def generate_products(config: GenerationConfig, rng: np.random.Generator) -> pd.DataFrame:
    weighted_categories = list(CATEGORY_WEIGHTS.keys())
    weights = np.array([CATEGORY_WEIGHTS[category] for category in weighted_categories], dtype=float)
    weights = weights / weights.sum()

    category_targets = np.floor(weights * config.num_products).astype(int)
    while category_targets.sum() < config.num_products:
        category_targets[np.argmax(weights - category_targets / config.num_products)] += 1

    category_counts = dict(zip(weighted_categories, category_targets))
    rows = []
    product_id = 1000
    for category in weighted_categories:
        templates = CATEGORY_PRODUCT_TEMPLATES[category]
        low, high = CATEGORY_BASE_PRICES[category]
        for index in range(category_counts[category]):
            template = templates[index % len(templates)]
            product_name = f"{template} {index // len(templates) + 1}"
            rows.append(
                {
                    "product_id": product_id,
                    "product_name": product_name,
                    "category": category,
                    "price": int(rng.integers(low, high + 1)),
                }
            )
            product_id += 1

    products = pd.DataFrame(rows).sort_values("product_id").reset_index(drop=True)
    return products


def generate_customers(config: GenerationConfig, rng: np.random.Generator) -> pd.DataFrame:
    city_weights = np.linspace(1.0, 2.1, len(CITIES))
    city_weights = city_weights / city_weights.sum()
    segment_weights = np.array([0.25, 0.26, 0.25, 0.24], dtype=float)

    customers = pd.DataFrame(
        {
            "customer_id": [f"CUST{idx:05d}" for idx in range(1, config.num_customers + 1)],
            "city": rng.choice(CITIES, size=config.num_customers, p=city_weights),
            "segment": rng.choice(SEGMENTS, size=config.num_customers, p=segment_weights),
        }
    )
    return customers


def generate_orders(
    config: GenerationConfig,
    customers: pd.DataFrame,
    products: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    start = pd.Timestamp(config.start_date)
    end = pd.Timestamp(config.end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    duration_seconds = int((end - start).total_seconds())

    category_weight_lookup = products["category"].map(CATEGORY_WEIGHTS).astype(float).to_numpy()
    product_popularity = rng.pareto(a=2.2, size=len(products)) + 1
    product_weights = category_weight_lookup * product_popularity
    product_weights = product_weights / product_weights.sum()

    customer_indices = customers.index.to_numpy()
    one_time_target = min(int(config.num_customers * 0.35), int(config.num_orders * 0.20))
    one_time_customers = rng.choice(customer_indices, size=one_time_target, replace=False)
    repeat_pool = np.setdiff1d(customer_indices, one_time_customers)
    repeat_weights = rng.pareto(a=2.4, size=len(repeat_pool)) + 1
    repeat_weights = repeat_weights / repeat_weights.sum()

    repeat_customer_index = rng.choice(
        repeat_pool,
        size=config.num_orders - one_time_target,
        p=repeat_weights,
    )
    customer_index = np.concatenate([one_time_customers, repeat_customer_index])
    rng.shuffle(customer_index)
    product_index = rng.choice(products.index.to_numpy(), size=config.num_orders, p=product_weights)

    seconds = rng.integers(0, duration_seconds + 1, size=config.num_orders)
    order_dates = start + pd.to_timedelta(seconds, unit="s")

    high_intent_hours = np.array([10, 11, 12, 17, 18, 19, 20, 21])
    hour_mask = rng.random(config.num_orders) < 0.75
    adjusted_hours = rng.choice(high_intent_hours, size=hour_mask.sum(), replace=True)
    order_dates = order_dates.to_series().reset_index(drop=True)
    order_dates.loc[hour_mask] = order_dates.loc[hour_mask].dt.normalize() + pd.to_timedelta(
        adjusted_hours, unit="h"
    ) + pd.to_timedelta(rng.integers(0, 3600, size=hour_mask.sum()), unit="s")
    order_dates = pd.to_datetime(order_dates)

    customer_slice = customers.iloc[customer_index].reset_index(drop=True)
    product_slice = products.iloc[product_index].reset_index(drop=True)

    segment_quantity_bias = customer_slice["segment"].map(
        {
            "Consumer": [0.74, 0.21, 0.05],
            "Corporate": [0.56, 0.29, 0.15],
            "Small Business": [0.58, 0.28, 0.14],
            "Student": [0.82, 0.15, 0.03],
        }
    )

    quantity = [
        rng.choice([1, 2, 3], p=probabilities)
        for probabilities in segment_quantity_bias
    ]

    price_adjustment = rng.normal(loc=1.0, scale=0.04, size=config.num_orders)
    prices = np.maximum(100, np.rint(product_slice["price"].to_numpy() * price_adjustment)).astype(int)

    orders = pd.DataFrame(
        {
            "order_id": np.arange(1, config.num_orders + 1),
            "customer_id": customer_slice["customer_id"].to_numpy(),
            "product_id": product_slice["product_id"].to_numpy(),
            "quantity": quantity,
            "price": prices,
            "order_date": order_dates.dt.strftime("%Y-%m-%d %H:%M:%S"),
            "city": customer_slice["city"].to_numpy(),
            "segment": customer_slice["segment"].to_numpy(),
        }
    )
    return orders


def generate_dataset(config: GenerationConfig | None = None) -> dict[str, pd.DataFrame]:
    ensure_project_directories()
    config = config or GenerationConfig()
    rng = np.random.default_rng(config.random_seed)

    logger.info(
        "Generating synthetic retail dataset | products=%s customers=%s orders=%s",
        config.num_products,
        config.num_customers,
        config.num_orders,
    )

    products = generate_products(config, rng)
    customers = generate_customers(config, rng)
    orders = generate_orders(config, customers, products, rng)

    products.to_csv(PRODUCTS_FILE, index=False)
    customers.to_csv(CUSTOMERS_FILE, index=False)
    orders.to_csv(ORDERS_FILE, index=False)

    logger.info("Synthetic datasets written to %s", PRODUCTS_FILE.parent)
    return {"products": products, "customers": customers, "orders": orders}
