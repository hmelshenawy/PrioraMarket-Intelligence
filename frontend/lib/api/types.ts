// UI-facing error categories produced by normalizing Axios/network/backend errors.
export type ApiErrorCategory =
  | "network"
  | "offline"
  | "badRequest"
  | "notFound"
  | "serverError"
  | "unexpected"

export interface ApiError {
  category: ApiErrorCategory
  status?: number
  message: string
  // Backend-provided request id when present; never exposed to users as a stack trace.
  requestId?: string | null
  // Original error for debugging in development only.
  cause?: unknown
}

export interface ApiErrorResponseDto {
  statusCode: number
  error: string
  message: string | string[]
  requestId?: string | null
}