CREATE OR REFRESH MATERIALIZED VIEW bronze_orders
AS SELECT * FROM (VALUES
  (1, 'widget', 3, 9.99),
  (2, 'gadget', 1, 19.99),
  (3, 'widget', 5, 9.99),
  (4, 'gizmo', -1, 14.99)   -- intentionally invalid, to show the expectation drop it
) AS t(order_id, product, quantity, unit_price);

CREATE OR REFRESH MATERIALIZED VIEW silver_orders (
  CONSTRAINT valid_quantity EXPECT (quantity > 0) ON VIOLATION DROP ROW
)
AS SELECT order_id, product, quantity, unit_price, quantity * unit_price AS total_amount
FROM bronze_orders;

CREATE OR REFRESH MATERIALIZED VIEW gold_sales_by_product
AS SELECT product, SUM(quantity) AS total_quantity, SUM(total_amount) AS total_revenue
FROM silver_orders
GROUP BY product;
