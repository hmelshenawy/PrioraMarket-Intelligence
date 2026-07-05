import type { ApiError, ApiErrorCategory, ApiErrorResponseDto } from "./types"

const isApiErrorResponse = (data: unknown): data is ApiErrorResponseDto => {
  if (!data || typeof data !== "object") return false
  const d = data as Record<string, unknown>
  return typeof d.statusCode === "number" && typeof d.error === "string"
}

const messageFromDto = (dto: ApiErrorResponseDto): string => {
  if (Array.isArray(dto.message)) return dto.message.join(", ")
  return dto.message
}

// Normalize any thrown value into a structured ApiError with a stable UI category.
export function normalizeApiError(error: unknown): ApiError {
  // Already normalized.
  if (typeof error === "object" && error !== null && "category" in error && "message" in error) {
    return error as ApiError
  }

  // Axios-style error.
  if (typeof error === "object" && error !== null && "isAxiosError" in error) {
    const e = error as {
      response?: { status?: number; data?: unknown }
      request?: unknown
      message?: string
      code?: string
    }

    // No response → network/offline.
    if (!e.response) {
      const offline = e.code === "ERR_NETWORK" || e.code === "ECONNABORTED"
      return {
        category: offline ? "offline" : "network",
        message: offline
          ? "Backend is unreachable. Please check your connection."
          : "Network error while contacting the backend.",
        cause: error,
      }
    }

    const status = e.response.status
    const data = e.response.data
    let requestId: string | null | undefined
    let backendMessage = ""

    if (isApiErrorResponse(data)) {
      backendMessage = messageFromDto(data)
      requestId = data.requestId
    }

    let category: ApiErrorCategory = "unexpected"
    if (status === 400) category = "badRequest"
    else if (status === 404) category = "notFound"
    else if (status && status >= 500) category = "serverError"

    return {
      category,
      status,
      message:
        backendMessage ||
        (status === 404
          ? "The requested resource was not found."
          : status && status >= 500
            ? "The backend reported an error. Please try again."
            : "Request failed."),
      requestId,
      cause: error,
    }
  }

  // Unknown error.
  if (error instanceof Error) {
    return { category: "unexpected", message: error.message, cause: error }
  }
  return { category: "unexpected", message: "An unexpected error occurred.", cause: error }
}

// Helper to throw a normalized ApiError from API modules.
export class ApiErrorImpl extends Error implements ApiError {
  category: ApiErrorCategory
  status?: number
  requestId?: string | null
  cause?: unknown
  constructor(apiError: ApiError) {
    super(apiError.message)
    this.name = "ApiError"
    this.category = apiError.category
    this.status = apiError.status
    this.requestId = apiError.requestId
    this.cause = apiError.cause
  }
}

export const toApiError = (error: unknown): ApiErrorImpl => new ApiErrorImpl(normalizeApiError(error))