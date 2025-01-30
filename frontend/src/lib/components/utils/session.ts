import fastapi from "$lib/components/utils/fastapi.ts";
import { logout } from "$lib/components/login/login.ts";

export async function verifySession() {
  try {
    await new Promise<void>((resolve, reject) => {
      fastapi("GET", "/session", {}, resolve, reject);
    });
  } catch {
    await logout();
  }
}

export async function getSessionRole() {
  try {
    const response = await new Promise<{ role: string }>((resolve, reject) => {
      fastapi("GET", "/session/role", {}, resolve, reject);
    });

    if (!response || !response.role) {
      await logout();
    }
    return response;
  } catch (error) {
    await logout();
  }
}
