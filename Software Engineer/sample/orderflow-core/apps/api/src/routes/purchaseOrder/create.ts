// 研修用の架空コード。タイムアウト後の再送を考慮していない現行実装。
import type { FastifyInstance } from 'fastify';
import { purchaseOrderService } from '../../services/purchaseOrderService';

interface CreateBody {
  externalRequestId?: string;
  lines: { sku: string; quantity: number; unitPrice: number }[];
}

export async function registerCreate(app: FastifyInstance) {
  app.post<{ Body: CreateBody }>('/purchase-orders', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const body = request.body;
    if (!body.lines?.length) {
      return reply.code(400).send({ code: 'VALIDATION_ERROR', message: 'lines is required' });
    }
    const created = await purchaseOrderService.create(tenantId, body);
    request.log.info({ orderId: created.orderId, tenant: tenantId }, 'purchase order created');
    return reply.code(201).send(created);
  });
}
