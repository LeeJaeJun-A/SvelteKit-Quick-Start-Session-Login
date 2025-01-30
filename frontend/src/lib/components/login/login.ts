import fastapi from "$lib/components/utils/fastapi.ts";
import { goto } from "$app/navigation";

export async function logout(): Promise<void> {
  try {
    await new Promise<{ message: string }>((resolve, reject) => {
      fastapi("POST", "/logout", {}, resolve, reject);
    });
  } catch (error: any) {
    console.log(`Error ${error}`);
  } finally {
    goto("/login", { replaceState: true });
  }
}
