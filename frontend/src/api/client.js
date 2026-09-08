const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function handle(res) {
  let body = null;
  try {
    body = await res.json();
  } catch {
    // no body
  }
  if (!res.ok) {
    const detail = body?.detail || res.statusText || "Request failed";
    throw new Error(detail);
  }
  return body;
}

export async function listDocuments() {
  const res = await fetch(`${BASE_URL}/api/documents`);
  return handle(res);
}

export async function uploadDocuments(files) {
  const form = new FormData();
  for (const f of files) form.append("files", f);
  const res = await fetch(`${BASE_URL}/api/documents/upload`, {
    method: "POST",
    body: form,
  });
  return handle(res);
}

export async function clearDocuments() {
  const res = await fetch(`${BASE_URL}/api/documents`, { method: "DELETE" });
  return handle(res);
}

export async function askQuestion(question) {
  const res = await fetch(`${BASE_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  return handle(res);
}

export async function getDefaultTestQuestions() {
  const res = await fetch(`${BASE_URL}/api/test/default-questions`);
  return handle(res);
}

export async function runTestSuite(questions) {
  const res = await fetch(`${BASE_URL}/api/test`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ questions }),
  });
  return handle(res);
}

export async function checkHealth() {
  const res = await fetch(`${BASE_URL}/health`);
  return handle(res);
}
