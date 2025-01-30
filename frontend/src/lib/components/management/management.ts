import { get, writable, type Writable } from "svelte/store";
import { verifySession } from "$lib/components/utils/session.ts";
import Swal from "sweetalert2";

export const options = ["UserManagement", "LockManagement", "UserLog"];
export const mode: Writable<string> = writable(options[0]);
export const locked_user_count: Writable<number> = writable(0);

export function getMode(): string {
  return get(mode);
}

export async function setMode(value: string): Promise<void> {
  try{
    await verifySession();
    mode.set(value);
  } catch{
    Swal.fire(
      "Error!",
      "Your session has expired or is unavailable.<br>Please login again."
    );
  }
}
