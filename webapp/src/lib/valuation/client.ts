import type { ValuationResult, ApiError, MethodDefinition, Benchmark, BusinessStage } from "./types";

const API_BASE = "/api/valuation";

async function apiFetch<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  const data = await res.json();

  if (!res.ok) {
    const error = data as ApiError;
    throw new Error(error.message || error.error || `API error: ${res.status}`);
  }

  return data as T;
}

export async function calculateValuation(
  method: string,
  params: Record<string, unknown>
): Promise<ValuationResult> {
  return apiFetch<ValuationResult>(`${API_BASE}/${method}`, {
    method: "POST",
    body: JSON.stringify(params),
  });
}

export async function getMethodCatalog(): Promise<MethodDefinition[]> {
  const data = await apiFetch<{ endpoints: MethodDefinition[] }>(API_BASE);
  return data.endpoints;
}

export async function getMethodBySlug(slug: string): Promise<MethodDefinition> {
  const methods = await getMethodCatalog();
  const method = methods.find((m) => m.slug === slug);
  if (!method) throw new Error(`Method not found: ${slug}`);
  return method;
}

export async function getDashboardValuations(params?: {
  page?: number;
  limit?: number;
  method?: string;
  category?: string;
  sort?: string;
  order?: "asc" | "desc";
}) {
  const searchParams = new URLSearchParams();
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) searchParams.set(key, String(value));
    });
  }
  return apiFetch<unknown>(`/api/dashboard/valuations?${searchParams.toString()}`);
}

export async function getDashboardValuationDetail(id: string) {
  return apiFetch<unknown>(`/api/dashboard/valuations/${id}`);
}

export async function getBenchmarks(params: {
  category?: string;
  business_stage?: BusinessStage;
  asset_type?: string;
  industry?: string;
}): Promise<{ benchmarks: Benchmark[]; count: number }> {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined) searchParams.set(key, String(value));
  });
  return apiFetch<{ benchmarks: Benchmark[]; count: number }>(
    `/api/benchmarks?${searchParams.toString()}`
  );
}

export { API_BASE };
