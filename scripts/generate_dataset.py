from __future__ import annotations

import argparse

from src.data_generation import GenerationConfig, generate_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the synthetic retail source data.")
    parser.add_argument("--products", type=int, default=168, help="Number of products to generate.")
    parser.add_argument("--customers", type=int, default=25_000, help="Number of customers to generate.")
    parser.add_argument("--orders", type=int, default=300_000, help="Number of orders to generate.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for deterministic generation.")
    args = parser.parse_args()

    config = GenerationConfig(
        num_products=args.products,
        num_customers=args.customers,
        num_orders=args.orders,
        random_seed=args.seed,
    )
    generate_dataset(config)


if __name__ == "__main__":
    main()
