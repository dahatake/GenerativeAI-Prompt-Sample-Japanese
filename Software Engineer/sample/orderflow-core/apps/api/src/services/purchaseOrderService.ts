// 研修用の架空コード。リクエスト単位の重複検知なし(トランザクション制御のみ)。
import { randomUUID } from 'node:crypto';
import { withTransaction } from '../db/client';

export const purchaseOrderService = {
  async create(tenantId: string, body: { externalRequestId?: string; lines: { sku: string; quantity: number; unitPrice: number }[] }) {
    return withTransaction(async (tx) => {
      const orderId = randomUUID();
      const total = body.lines.reduce((sum, l) => sum + l.quantity * l.unitPrice, 0);
      await tx.query(
        'INSERT INTO purchase_orders (order_id, tenant_id, external_request_id, total_amount) VALUES ($1, $2, $3, $4)',
        [orderId, tenantId, body.externalRequestId ?? null, total],
      );
      for (const [i, l] of body.lines.entries()) {
        await tx.query(
          'INSERT INTO purchase_order_lines (order_id, line_no, sku, quantity, unit_price) VALUES ($1, $2, $3, $4, $5)',
          [orderId, i + 1, l.sku, l.quantity, l.unitPrice],
        );
      }
      return { orderId, tenantId, totalAmount: total };
    });
  },
};
