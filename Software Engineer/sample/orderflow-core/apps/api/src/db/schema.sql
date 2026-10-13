-- 研修用の架空スキーマ(OrderFlow Core / PostgreSQL 16)。現行状態: external_request_id にユニーク制約なし。
CREATE TABLE purchase_orders (
  order_id            uuid PRIMARY KEY,
  tenant_id           text NOT NULL,
  external_request_id text NULL,
  total_amount        numeric(12,2) NOT NULL,
  created_at          timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE purchase_order_lines (
  order_id    uuid NOT NULL REFERENCES purchase_orders(order_id),
  line_no     integer NOT NULL,
  sku         text NOT NULL,
  quantity    integer NOT NULL CHECK (quantity > 0),
  unit_price  numeric(12,2) NOT NULL,
  PRIMARY KEY (order_id, line_no)
);

CREATE INDEX ix_purchase_orders_tenant_created ON purchase_orders (tenant_id, created_at DESC);
