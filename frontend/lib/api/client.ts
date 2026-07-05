import axios, { type AxiosInstance } from "axios"
import { apiBaseUrl } from "@/lib/config/env"
import { toApiError } from "./errors"

// Centralized Axios instance for the Feature 003 Backend Search API.
// Pages and components never import this directly; they go through typed API modules.
let client: AxiosInstance | null = null

export function getApiClient(): AxiosInstance {
  if (client) return client
  client = axios.create({
    baseURL: `${apiBaseUrl}/api/v1`,
    timeout: 15_000,
    headers: { Accept: "application/json" },
    // No auth/secret headers for Feature 004.
  })
  // Normalize every rejection into a structured ApiError.
  client.interceptors.response.use(
    (response) => response,
    (error) => Promise.reject(toApiError(error)),
  )
  return client
}

export type { AxiosInstance }