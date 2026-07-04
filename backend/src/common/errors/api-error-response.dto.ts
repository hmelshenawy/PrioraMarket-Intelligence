export class ApiErrorResponseDto {
  statusCode!: number;
  error!: string;
  message!: string | string[];
  requestId?: string | null;
}
