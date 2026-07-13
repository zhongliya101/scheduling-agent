import type { Candidate, ScheduleResponse } from "./types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options?.headers ?? {}) },
    ...options
  });
  if (!response.ok) {
    const detail = await response.json().catch(() => ({}));
    throw new Error(detail?.detail?.error_code ?? detail?.message ?? `HTTP ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  generateSchedule(weekStart: string) {
    return request<ScheduleResponse>("/schedule/generate", {
      method: "POST",
      body: JSON.stringify({
        store_id: "fresh_store_001",
        week_start: weekStart,
        instruction: "根据历史数据、天气和节假日生成下周半混班班表"
      })
    });
  },
  resetDemo() {
    return request<{ ok: boolean; message: string }>("/demo/reset", { method: "POST" });
  },
  chat(versionId: string, message: string, context = {}) {
    return request<{ message: string; candidates: Candidate[] }>("/agent/chat", {
      method: "POST",
      body: JSON.stringify({ version_id: versionId, message, context })
    });
  },
  recommend(versionId: string, date: string, slot: string, areaCode: string, taskCode?: string) {
    return request<{ candidates: Candidate[] }>("/agent/recommend-support", {
      method: "POST",
      body: JSON.stringify({ version_id: versionId, date, slot, area_code: areaCode, task_code: taskCode })
    });
  },
  modify(versionId: string, itemId: string, after: Record<string, unknown>, reasonText: string) {
    return request(`/schedule/${versionId}/items/${itemId}`, {
      method: "PATCH",
      body: JSON.stringify({
        after,
        reason_code: "manager_experience",
        reason_text: reasonText,
        force: true
      })
    });
  },
  optimizeHc(versionId: string) {
    return request<{ suggestions: unknown[] }>("/hc/optimize", {
      method: "POST",
      body: JSON.stringify({ version_id: versionId })
    });
  }
};

