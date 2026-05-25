export const adminTokenKey = "adaptive_admin_token";
export const adminEmailKey = "adaptive_admin_email";

export function getAdminToken(): string | null {
  return localStorage.getItem(adminTokenKey);
}

export function setAdminSession(token: string, email: string) {
  localStorage.setItem(adminTokenKey, token);
  localStorage.setItem(adminEmailKey, email);
}

export function clearAdminSession() {
  localStorage.removeItem(adminTokenKey);
  localStorage.removeItem(adminEmailKey);
}
