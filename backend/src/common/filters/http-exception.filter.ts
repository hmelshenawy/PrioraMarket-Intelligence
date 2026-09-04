import { ArgumentsHost, Catch, ExceptionFilter, HttpException, HttpStatus, Logger } from '@nestjs/common';

interface ResponseLike {
  status(statusCode: number): { json(body: unknown): void };
}

@Catch()
export class HttpExceptionFilter implements ExceptionFilter {
  private readonly logger = new Logger(HttpExceptionFilter.name);

  catch(exception: unknown, host: ArgumentsHost): void {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<ResponseLike>();
    const request = ctx.getRequest<{ method?: string; url?: string }>();

    const isHttpException = exception instanceof HttpException;
    const status = isHttpException ? exception.getStatus() : HttpStatus.INTERNAL_SERVER_ERROR;
    const exceptionResponse = isHttpException ? exception.getResponse() : 'Internal server error';

    if (process.env.NODE_ENV !== 'production') {
      const path = `${request.method ?? 'UNKNOWN'} ${request.url ?? 'unknown URL'}`;
      const stack = exception instanceof Error ? exception.stack : undefined;
      const detail = exception instanceof Error ? exception.message : String(exception);
      this.logger.error(`Unhandled exception while serving ${path}: ${detail}`, stack);
    }

    const message =
      typeof exceptionResponse === 'object' && exceptionResponse !== null && 'message' in exceptionResponse
        ? (exceptionResponse as { message: string | string[] }).message
        : String(exceptionResponse);

    response.status(status).json({
      statusCode: status,
      error: isHttpException ? exception.name : 'InternalServerError',
      message
    });
  }
}
