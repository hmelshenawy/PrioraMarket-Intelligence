import { z } from "zod"

// Trust boundary: validate the minimal health payload at the API layer.
export const healthSchema = z.object({ status: z.literal("ok") })

export type HealthDto = z.infer<typeof healthSchema>