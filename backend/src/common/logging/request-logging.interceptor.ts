import { CallHandler, ExecutionContext, Injectable, NestInterceptor } from '@nestjs/common';
import { Observable, tap } from 'rxjs';

interface RequestLike {
  method?: string;
  originalUrl?: string;
  url?: string;
  query?: Record<string, unknown>;
}

@Injectable()
export class RequestLoggingInterceptor implements NestInterceptor {
  intercept(context: ExecutionContext, next: CallHandler): Observable<unknown> {
    const startedAt = Date.now();
    const request = context.switchToHttp().getRequest<RequestLike>();

    return next.handle().pipe(
      tap((body: unknown) => {
        const rowsReturned = Array.isArray((body as { data?: unknown[] })?.data)
          ? (body as { data: unknown[] }).data.length
          : undefined;

        console.info({
          boundedContext: 'Search',
          operation: `${request.method ?? 'UNKNOWN'} ${request.originalUrl ?? request.url ?? ''}`,
          duration: Date.now() - startedAt,
          rowsReturned,
          cacheHit: undefined,
          sortType: request.query?.sort,
          freeTextUsed: Boolean(request.query?.q)
        });
      })
    );
  }
}
