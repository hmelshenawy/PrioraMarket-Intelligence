// Route-level loading skeleton for the listing detail route.
export default function Loading() {
  return (
    <div className="flex flex-col gap-6" aria-busy="true">
      <div className="aspect-video w-full animate-pulse rounded-card bg-skeleton" aria-hidden />
      <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
        <div className="flex flex-col gap-4">
          <div className="h-8 w-2/3 animate-pulse rounded bg-skeleton" aria-hidden />
          <div className="h-5 w-1/2 animate-pulse rounded bg-skeleton" aria-hidden />
          <div className="h-40 w-full animate-pulse rounded bg-skeleton" aria-hidden />
        </div>
        <div className="h-32 w-full animate-pulse rounded bg-skeleton" aria-hidden />
      </div>
    </div>
  )
}