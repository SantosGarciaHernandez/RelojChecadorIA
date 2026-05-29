const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";
const DEFAULT_ENTRY_PC_NAME = import.meta.env.VITE_ENTRY_PC_NAME || "PC-ENTRADA-01";
const DEFAULT_EXIT_PC_NAME = import.meta.env.VITE_EXIT_PC_NAME || "PC-SALIDA-01";

function getApiOrigin() {
  try {
    return new URL(API_BASE_URL).origin;
  } catch {
    return "http://127.0.0.1:8000";
  }
}

function getWebSocketOrigin() {
  const origin = getApiOrigin();
  return origin.replace(/^https:/, "wss:").replace(/^http:/, "ws:");
}

async function readJsonResponse(response) {
  const text = await response.text();
  const data = text ? JSON.parse(text) : null;

  if (!response.ok) {
    const detail = data?.detail;
    const message = Array.isArray(detail)
      ? detail.map((item) => item.msg || JSON.stringify(item)).join(" | ")
      : detail || data?.message || `Error HTTP ${response.status}`;

    throw new Error(message);
  }

  return data;
}

export function getEntryPcName() {
  return DEFAULT_ENTRY_PC_NAME;
}

export function getExitPcName() {
  return DEFAULT_EXIT_PC_NAME;
}

export function getPcNameByMode(mode) {
  return mode === "Salida" ? DEFAULT_EXIT_PC_NAME : DEFAULT_ENTRY_PC_NAME;
}

export function getRecentAttendanceWsUrl() {
  return `${getWebSocketOrigin()}/ws/attendance/recent`;
}

export function getTrainingWsUrl(jobId) {
  return `${getWebSocketOrigin()}/ws/training/${encodeURIComponent(jobId)}`;
}

export async function checkApiHealth() {
  const response = await fetch(`${API_BASE_URL}/health`);
  return readJsonResponse(response);
}

export async function predictFaceCrop(imageBase64, pcName = DEFAULT_ENTRY_PC_NAME) {
  const response = await fetch(`${API_BASE_URL}/detection/predict`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      pc_name: pcName,
      image_base64: imageBase64,
    }),
  });

  return readJsonResponse(response);
}

export async function getRecentAttendance(limit = 10) {
  const response = await fetch(`${API_BASE_URL}/attendance/recent?limit=${limit}`);
  return readJsonResponse(response);
}

export async function createUser(payload) {
  const response = await fetch(`${API_BASE_URL}/users`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  return readJsonResponse(response);
}


export async function registerUserWithTraining(payload) {
  const response = await fetch(`${API_BASE_URL}/training/register-user`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  return readJsonResponse(response);
}
